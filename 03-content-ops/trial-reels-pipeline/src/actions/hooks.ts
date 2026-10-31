"use server";

import { revalidatePath } from "next/cache";
import { z } from "zod";
import { requireAdmin } from "@/lib/auth";
import { prisma } from "@/lib/db";
import { normalizeHookText } from "@/lib/normalize";

function revalidateHookViews() {
  revalidatePath("/admin/hooks");
  revalidatePath("/admin/review");
  revalidatePath("/admin/generate");
}

const ManualHookSchema = z.object({
  text: z.string().trim().min(1).max(300),
  category: z.string().trim().max(60).optional(),
  tags: z.string().max(300).optional(),
});

export async function createHookManual(formData: FormData) {
  await requireAdmin();
  const input = ManualHookSchema.parse({
    text: formData.get("text"),
    category: formData.get("category") || undefined,
    tags: formData.get("tags") || undefined,
  });
  const normalizedText = normalizeHookText(input.text);
  if (!normalizedText) return;

  await prisma.hook.createMany({
    data: [
      {
        text: input.text,
        normalizedText,
        category: input.category || null,
        tags: input.tags
          ? input.tags
              .split(",")
              .map((t) => t.trim())
              .filter(Boolean)
          : [],
        status: "APPROVED",
        source: "MANUAL",
      },
    ],
    skipDuplicates: true, // silently skips if the same wording already exists
  });
  revalidateHookViews();
}

export async function setHookProven(formData: FormData) {
  await requireAdmin();
  const id = String(formData.get("hookId") ?? "");
  const proven = formData.get("proven") === "true";
  await prisma.hook.update({ where: { id }, data: { proven } });
  revalidateHookViews();
}

export async function retireHook(formData: FormData) {
  await requireAdmin();
  const id = String(formData.get("hookId") ?? "");
  await prisma.hook.update({ where: { id }, data: { status: "RETIRED" } });
  revalidateHookViews();
}

export async function restoreHook(formData: FormData) {
  await requireAdmin();
  const id = String(formData.get("hookId") ?? "");
  await prisma.hook.update({ where: { id }, data: { status: "APPROVED" } });
  revalidateHookViews();
}

const UpdateHookSchema = z.object({
  hookId: z.string().min(1),
  category: z.string().trim().max(60).optional(),
  tags: z.string().max(300).optional(),
  notes: z.string().max(1000).optional(),
});

export async function updateHookMeta(formData: FormData) {
  await requireAdmin();
  const input = UpdateHookSchema.parse({
    hookId: formData.get("hookId"),
    category: formData.get("category") ?? undefined,
    tags: formData.get("tags") ?? undefined,
    notes: formData.get("notes") ?? undefined,
  });
  await prisma.hook.update({
    where: { id: input.hookId },
    data: {
      category: input.category || null,
      notes: input.notes || null,
      tags: input.tags
        ? input.tags
            .split(",")
            .map((t) => t.trim())
            .filter(Boolean)
        : [],
    },
  });
  revalidateHookViews();
}
