"use server";

import { revalidatePath } from "next/cache";
import { z } from "zod";
import { generateCreatorToken, requireAdmin } from "@/lib/auth";
import { prisma } from "@/lib/db";

const CreatorSchema = z.object({
  name: z.string().trim().min(1).max(80),
  handle: z.string().trim().max(80).optional(),
  timezone: z.string().trim().min(1).max(60),
});

function safeTimezone(timezone: string): string {
  try {
    // Throws RangeError for unknown IANA names.
    new Intl.DateTimeFormat("en-US", { timeZone: timezone });
    return timezone;
  } catch {
    return "America/New_York";
  }
}

export async function createCreator(formData: FormData) {
  await requireAdmin();
  const input = CreatorSchema.parse({
    name: formData.get("name"),
    handle: String(formData.get("handle") ?? "").trim() || undefined,
    timezone: String(formData.get("timezone") ?? "America/New_York"),
  });
  await prisma.creator.create({
    data: {
      name: input.name,
      handle: input.handle ?? null,
      timezone: safeTimezone(input.timezone),
      token: generateCreatorToken(),
    },
  });
  revalidatePath("/admin/creators");
}

export async function rotateToken(formData: FormData) {
  await requireAdmin();
  const creatorId = String(formData.get("creatorId") ?? "");
  await prisma.creator.update({
    where: { id: creatorId },
    data: { token: generateCreatorToken(), tokenRotatedAt: new Date() },
  });
  revalidatePath("/admin/creators");
  revalidatePath(`/admin/creators/${creatorId}`);
}

export async function setCreatorActive(formData: FormData) {
  await requireAdmin();
  const creatorId = String(formData.get("creatorId") ?? "");
  const active = formData.get("active") === "true";
  await prisma.creator.update({ where: { id: creatorId }, data: { active } });
  revalidatePath("/admin/creators");
  revalidatePath(`/admin/creators/${creatorId}`);
}

export async function updateCreator(formData: FormData) {
  await requireAdmin();
  const creatorId = String(formData.get("creatorId") ?? "");
  const input = CreatorSchema.parse({
    name: formData.get("name"),
    handle: String(formData.get("handle") ?? "").trim() || undefined,
    timezone: String(formData.get("timezone") ?? "America/New_York"),
  });
  await prisma.creator.update({
    where: { id: creatorId },
    data: { name: input.name, handle: input.handle ?? null, timezone: safeTimezone(input.timezone) },
  });
  revalidatePath(`/admin/creators/${creatorId}`);
  revalidatePath("/admin/creators");
}
