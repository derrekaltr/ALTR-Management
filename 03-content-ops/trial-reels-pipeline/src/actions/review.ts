"use server";

import { revalidatePath } from "next/cache";
import { z } from "zod";
import { requireAdmin } from "@/lib/auth";
import { prisma } from "@/lib/db";
import { normalizeHookText } from "@/lib/normalize";

const ReviewSchema = z.object({
  hookId: z.string().min(1),
  decision: z.enum(["approve", "reject"]),
  editedText: z.string().trim().max(300).optional(),
});

export async function reviewHook(formData: FormData) {
  await requireAdmin();
  const input = ReviewSchema.parse({
    hookId: formData.get("hookId"),
    decision: formData.get("decision"),
    editedText: String(formData.get("editedText") ?? "").trim() || undefined,
  });

  const hook = await prisma.hook.findUniqueOrThrow({ where: { id: input.hookId } });

  if (input.decision === "approve" && input.editedText && input.editedText !== hook.text) {
    const normalizedText = normalizeHookText(input.editedText);
    if (!normalizedText) return { error: "Edited hook is empty" };
    const clash = await prisma.hook.findUnique({ where: { normalizedText } });
    if (clash && clash.id !== hook.id) {
      return { error: "Another hook already has that wording" };
    }
    await prisma.hook.update({
      where: { id: hook.id },
      data: {
        text: input.editedText,
        normalizedText,
        status: "APPROVED",
        reviewedAt: new Date(),
      },
    });
  } else {
    await prisma.hook.update({
      where: { id: hook.id },
      data: {
        status: input.decision === "approve" ? "APPROVED" : "REJECTED",
        reviewedAt: new Date(),
      },
    });
  }

  revalidatePath("/admin/review");
  revalidatePath("/admin/hooks");
  return {};
}

export async function approveBatchRemainder(formData: FormData) {
  await requireAdmin();
  const batchId = String(formData.get("batchId") ?? "");
  await prisma.hook.updateMany({
    where: { batchId, status: "PENDING_REVIEW" },
    data: { status: "APPROVED", reviewedAt: new Date() },
  });
  revalidatePath("/admin/review");
  revalidatePath("/admin/hooks");
}
