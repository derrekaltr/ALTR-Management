"use server";

import { revalidatePath } from "next/cache";
import { Prisma } from "@prisma/client";
import { z } from "zod";
import { requireAdmin } from "@/lib/auth";
import { dateStringToUtc } from "@/lib/dates";
import { prisma } from "@/lib/db";

function revalidatePlan(creatorId: string) {
  revalidatePath(`/admin/creators/${creatorId}`);
}

const UpsertPlanSchema = z.object({
  creatorId: z.string().min(1),
  date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
  notes: z.string().trim().max(1000).optional(),
});

export async function upsertDayPlan(formData: FormData) {
  await requireAdmin();
  const input = UpsertPlanSchema.parse({
    creatorId: formData.get("creatorId"),
    date: formData.get("date"),
    notes: String(formData.get("notes") ?? "").trim() || undefined,
  });
  const date = dateStringToUtc(input.date);
  await prisma.dayPlan.upsert({
    where: { creatorId_date: { creatorId: input.creatorId, date } },
    create: { creatorId: input.creatorId, date, notes: input.notes ?? null },
    update: { notes: input.notes ?? null },
  });
  revalidatePlan(input.creatorId);
}

const AddVersionSchema = z.object({
  dayPlanId: z.string().min(1),
  hookId: z.string().min(1),
  exampleReelId: z.string().min(1).optional(),
  changeAudio: z.boolean(),
  changeSpeed: z.boolean(),
});

export async function addVersion(formData: FormData) {
  await requireAdmin();
  const input = AddVersionSchema.parse({
    dayPlanId: formData.get("dayPlanId"),
    hookId: formData.get("hookId"),
    exampleReelId: String(formData.get("exampleReelId") ?? "").trim() || undefined,
    changeAudio: formData.get("changeAudio") === "on",
    changeSpeed: formData.get("changeSpeed") === "on",
  });

  const plan = await prisma.dayPlan.findUniqueOrThrow({
    where: { id: input.dayPlanId },
    include: { versions: { select: { order: true } } },
  });
  const nextOrder = plan.versions.reduce((max, v) => Math.max(max, v.order), 0) + 1;

  try {
    // timesUsed is denormalized; keep it in the same transaction as the insert.
    await prisma.$transaction([
      prisma.version.create({
        data: {
          dayPlanId: input.dayPlanId,
          hookId: input.hookId,
          exampleReelId: input.exampleReelId ?? null,
          order: nextOrder,
          changeAudio: input.changeAudio,
          changeSpeed: input.changeSpeed,
        },
      }),
      prisma.hook.update({
        where: { id: input.hookId },
        data: { timesUsed: { increment: 1 } },
      }),
    ]);
  } catch (error) {
    // Duplicate hook in this plan (or an order race): silently no-op.
    if (!(error instanceof Prisma.PrismaClientKnownRequestError && error.code === "P2002")) {
      throw error;
    }
  }
  revalidatePlan(plan.creatorId);
}

export async function removeVersion(formData: FormData) {
  await requireAdmin();
  const versionId = String(formData.get("versionId") ?? "");
  const version = await prisma.version.findUniqueOrThrow({
    where: { id: versionId },
    include: { dayPlan: { select: { creatorId: true } } },
  });
  await prisma.$transaction([
    prisma.version.delete({ where: { id: versionId } }),
    prisma.hook.update({
      where: { id: version.hookId },
      data: { timesUsed: { decrement: 1 } },
    }),
  ]);
  revalidatePlan(version.dayPlan.creatorId);
}

export async function toggleVersionFlag(formData: FormData) {
  await requireAdmin();
  const versionId = String(formData.get("versionId") ?? "");
  const flag = String(formData.get("flag") ?? "");
  if (flag !== "changeAudio" && flag !== "changeSpeed") return;
  const version = await prisma.version.findUniqueOrThrow({
    where: { id: versionId },
    include: { dayPlan: { select: { creatorId: true } } },
  });
  await prisma.version.update({
    where: { id: versionId },
    data: { [flag]: !version[flag] },
  });
  revalidatePlan(version.dayPlan.creatorId);
}
