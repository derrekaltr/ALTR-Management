"use server";

import { revalidatePath } from "next/cache";
import { z } from "zod";
import { requireAdmin } from "@/lib/auth";
import { prisma } from "@/lib/db";
import { getProvider, LLMError } from "@/lib/llm";
import { canonicalizeReelUrl, normalizeHookText } from "@/lib/normalize";
import { readStoredFile } from "@/lib/storage";

/** Paste one or more IG links (one per line) -> stubs awaiting video upload. */
export async function addExampleLinks(formData: FormData) {
  await requireAdmin();
  const raw = String(formData.get("links") ?? "");
  const lines = raw
    .split(/\r?\n/)
    .map((l) => l.trim())
    .filter(Boolean);

  for (const line of lines) {
    const canonical = canonicalizeReelUrl(line);
    if (!canonical) continue;
    await prisma.exampleReel.createMany({
      data: [{ sourceUrl: canonical }],
      skipDuplicates: true,
    });
  }
  revalidatePath("/admin/examples");
}

const MediaSchema = z.object({
  exampleId: z.string().min(1).optional(),
  videoUrl: z.string().min(1),
  thumbUrl: z.string().min(1).optional(),
  frameUrls: z.array(z.string().min(1)).min(1).max(8),
  sourceHandle: z.string().max(80).optional(),
});

/**
 * Attach uploaded media (already stored via /api/upload or Vercel Blob client
 * upload) to an example stub — or create a fresh example when exampleId is
 * omitted (direct upload without a link).
 */
export async function finalizeExampleMedia(input: z.infer<typeof MediaSchema>) {
  await requireAdmin();
  const media = MediaSchema.parse(input);

  const data = {
    videoUrl: media.videoUrl,
    thumbUrl: media.thumbUrl ?? media.frameUrls[0],
    frameUrls: media.frameUrls,
    sourceHandle: media.sourceHandle || undefined,
    status: "UPLOADED" as const,
    error: null,
  };

  const example = media.exampleId
    ? await prisma.exampleReel.update({ where: { id: media.exampleId }, data })
    : await prisma.exampleReel.create({ data });

  revalidatePath("/admin/examples");
  return { exampleId: example.id };
}

/**
 * Run (or re-run) AI analysis from the example's stored frames: extracts the
 * on-screen hook into the review queue and describes the background.
 */
export async function analyzeExample(exampleId: string) {
  await requireAdmin();
  const example = await prisma.exampleReel.findUniqueOrThrow({ where: { id: exampleId } });
  if (example.frameUrls.length === 0) {
    return { ok: false as const, error: "No frames stored — upload the video first." };
  }

  try {
    const frames = await Promise.all(
      example.frameUrls.map(async (url) => ({
        data: await readStoredFile(url),
        mediaType: "image/jpeg" as const,
      })),
    );
    const provider = getProvider();
    const analysis = await provider.analyzeReel(frames, example.notes ?? undefined);

    await prisma.exampleReel.update({
      where: { id: exampleId },
      data: {
        status: "ANALYZED",
        analysis: analysis as object,
        backgroundDescription: analysis.backgroundDescription,
        tags: [analysis.tags.setting, analysis.tags.outfit, analysis.tags.energy].filter(Boolean),
        whyItWorks: analysis.whyItWorks,
        analyzedAt: new Date(),
        error: null,
      },
    });

    // Extracted hook -> review queue (deduped against the whole library).
    let hookQueued = false;
    const hookText = analysis.onScreenHookText.trim();
    if (hookText) {
      const normalizedText = normalizeHookText(hookText);
      if (normalizedText) {
        const result = await prisma.hook.createMany({
          data: [
            {
              text: hookText,
              normalizedText,
              status: "PENDING_REVIEW",
              source: "EXTRACTED",
              exampleReelId: exampleId,
            },
          ],
          skipDuplicates: true,
        });
        hookQueued = result.count > 0;
      }
    }

    revalidatePath("/admin/examples");
    revalidatePath(`/admin/examples/${exampleId}`);
    revalidatePath("/admin/review");
    return { ok: true as const, hookQueued };
  } catch (error) {
    const message =
      error instanceof LLMError ? error.message : error instanceof Error ? error.message : "Analysis failed";
    await prisma.exampleReel.update({
      where: { id: exampleId },
      data: { status: "ANALYSIS_FAILED", error: message },
    });
    revalidatePath("/admin/examples");
    revalidatePath(`/admin/examples/${exampleId}`);
    return { ok: false as const, error: message };
  }
}

const UpdateExampleSchema = z.object({
  exampleId: z.string().min(1),
  backgroundDescription: z.string().max(1000).optional(),
  whyItWorks: z.string().max(1000).optional(),
  tags: z.string().max(300).optional(),
  notes: z.string().max(1000).optional(),
  sourceHandle: z.string().max(80).optional(),
});

export async function updateExample(formData: FormData) {
  await requireAdmin();
  const input = UpdateExampleSchema.parse({
    exampleId: formData.get("exampleId"),
    backgroundDescription: formData.get("backgroundDescription") ?? undefined,
    whyItWorks: formData.get("whyItWorks") ?? undefined,
    tags: formData.get("tags") ?? undefined,
    notes: formData.get("notes") ?? undefined,
    sourceHandle: formData.get("sourceHandle") ?? undefined,
  });
  await prisma.exampleReel.update({
    where: { id: input.exampleId },
    data: {
      backgroundDescription: input.backgroundDescription || null,
      whyItWorks: input.whyItWorks || null,
      notes: input.notes || null,
      sourceHandle: input.sourceHandle || null,
      tags: input.tags
        ? input.tags
            .split(",")
            .map((t) => t.trim())
            .filter(Boolean)
        : [],
    },
  });
  revalidatePath(`/admin/examples/${input.exampleId}`);
  revalidatePath("/admin/examples");
}

export async function deleteExample(formData: FormData) {
  await requireAdmin();
  const exampleId = String(formData.get("exampleId") ?? "");
  // Versions/hooks referencing it are set null by the schema's onDelete.
  await prisma.exampleReel.delete({ where: { id: exampleId } });
  revalidatePath("/admin/examples");
}
