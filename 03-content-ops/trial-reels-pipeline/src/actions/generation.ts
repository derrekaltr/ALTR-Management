"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { z } from "zod";
import { requireAdmin } from "@/lib/auth";
import { prisma } from "@/lib/db";
import { getProvider, LLMError, type HookCandidate } from "@/lib/llm";
import { normalizeHookText } from "@/lib/normalize";

const StartBatchSchema = z.object({
  seedIds: z.array(z.string().min(1)).min(1, "Pick at least one seed hook").max(30),
  toneGuidance: z.string().trim().max(1000).optional(),
  count: z.coerce.number().int().min(1).max(25).default(10),
});

export async function startGenerationBatch(formData: FormData) {
  await requireAdmin();
  const parsed = StartBatchSchema.safeParse({
    seedIds: formData.getAll("seedIds").map(String),
    toneGuidance: String(formData.get("toneGuidance") ?? "") || undefined,
    count: formData.get("count") ?? 10,
  });
  if (!parsed.success) {
    return { error: parsed.error.issues[0]?.message ?? "Invalid input" };
  }
  const input = parsed.data;

  const seeds = await prisma.hook.findMany({
    where: { id: { in: input.seedIds } },
    include: { exampleReel: { select: { tags: true } } },
  });
  if (seeds.length === 0) return { error: "Seed hooks not found" };

  const rejected = await prisma.hook.findMany({
    where: { status: "REJECTED" },
    orderBy: { reviewedAt: "desc" },
    take: 30,
    select: { text: true },
  });

  const provider = getProvider();
  const batch = await prisma.generationBatch.create({
    data: {
      status: "RUNNING",
      seedIds: input.seedIds,
      toneGuidance: input.toneGuidance ?? null,
      count: input.count,
      model: provider.modelName,
    },
  });

  let candidates: HookCandidate[] | null = null;
  let failure: string | null = null;
  try {
    candidates = await provider.generateHooks({
      seeds: seeds.map((s) => ({
        text: s.text,
        category: s.category,
        backgroundTags: s.exampleReel?.tags,
      })),
      rejectedExamples: rejected.map((r) => r.text),
      toneGuidance: input.toneGuidance,
      count: input.count,
    });
  } catch (error) {
    failure =
      error instanceof LLMError
        ? error.message
        : error instanceof Error
          ? error.message
          : "Generation failed";
  } finally {
    // Never orphan a RUNNING batch: settle status before anything else.
    if (candidates) {
      await prisma.generationBatch.update({
        where: { id: batch.id },
        data: { status: "COMPLETE", rawResponse: { candidates } as object },
      });
    } else {
      await prisma.generationBatch.update({
        where: { id: batch.id },
        data: { status: "FAILED", error: failure ?? "Unknown failure" },
      });
    }
  }

  if (!candidates) {
    revalidatePath("/admin/generate");
    return { error: failure ?? "Generation failed", batchId: batch.id };
  }

  // Dedupe within the batch and against the whole library. The DB unique
  // constraint (skipDuplicates) is the backstop against races.
  let inserted = 0;
  const seen = new Set<string>();
  for (const candidate of candidates) {
    const normalizedText = normalizeHookText(candidate.text);
    if (!normalizedText || seen.has(normalizedText)) continue;
    seen.add(normalizedText);
    const result = await prisma.hook.createMany({
      data: [
        {
          text: candidate.text.trim(),
          normalizedText,
          category: candidate.category || null,
          notes: candidate.rationale || null,
          status: "PENDING_REVIEW",
          source: "GENERATED",
          batchId: batch.id,
        },
      ],
      skipDuplicates: true,
    });
    inserted += result.count;
  }

  await prisma.generationBatch.update({
    where: { id: batch.id },
    data: {
      error:
        inserted < candidates.length
          ? `${candidates.length - inserted} of ${candidates.length} candidates were duplicates and skipped`
          : null,
    },
  });

  revalidatePath("/admin/review");
  revalidatePath("/admin/generate");
  redirect(`/admin/review?batch=${batch.id}`);
}

export async function retryBatch(formData: FormData): Promise<void> {
  await requireAdmin();
  const batchId = String(formData.get("batchId") ?? "");
  const batch = await prisma.generationBatch.findUniqueOrThrow({ where: { id: batchId } });

  const retryForm = new FormData();
  for (const id of batch.seedIds) retryForm.append("seedIds", id);
  if (batch.toneGuidance) retryForm.set("toneGuidance", batch.toneGuidance);
  retryForm.set("count", String(batch.count));
  // On success this redirects to the review queue; on failure the batch table
  // shows the new FAILED row, so a returned error object isn't needed here.
  await startGenerationBatch(retryForm);
}
