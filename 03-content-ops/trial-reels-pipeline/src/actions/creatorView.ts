"use server";

import { revalidatePath } from "next/cache";
import { prisma } from "@/lib/db";

/**
 * The only mutation reachable without an admin session. The creator token IS
 * the credential: the version must belong to that token's (active) creator.
 */
export async function markVersionPosted(formData: FormData) {
  const token = String(formData.get("token") ?? "");
  const versionId = String(formData.get("versionId") ?? "");
  const undo = formData.get("undo") === "true";
  if (!token || !versionId) return;

  const version = await prisma.version.findFirst({
    where: {
      id: versionId,
      dayPlan: { creator: { token, active: true } },
    },
    select: { id: true },
  });
  if (!version) return; // wrong token or foreign version: silently no-op

  await prisma.version.update({
    where: { id: versionId },
    data: undo
      ? { status: "PLANNED", postedAt: null }
      : { status: "POSTED", postedAt: new Date() },
  });
  revalidatePath(`/c/${token}`);
}
