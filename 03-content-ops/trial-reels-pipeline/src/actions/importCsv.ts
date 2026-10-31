"use server";

import Papa from "papaparse";
import { z } from "zod";
import { requireAdmin } from "@/lib/auth";
import { prisma } from "@/lib/db";
import { canonicalizeReelUrl, looksLikeUrl, normalizeHookText } from "@/lib/normalize";
import { revalidatePath } from "next/cache";

export interface ImportReport {
  mode: "links" | "hooks";
  imported: number;
  duplicates: number;
  invalid: { row: number; value: string; reason: string }[];
  error?: string;
}

const HOOK_TEXT_ALIASES = ["text", "caption", "hook", "hook text", "caption text"];
const CATEGORY_ALIASES = ["category", "tone", "type"];
const TAGS_ALIASES = ["tags", "tag"];
const NOTES_ALIASES = ["notes", "note", "comments"];

const HookRowSchema = z.object({
  text: z.string().trim().min(1, "empty text").max(300, "over 300 chars"),
  category: z.string().trim().max(60).optional(),
  tags: z.array(z.string().trim().min(1)).optional(),
  notes: z.string().trim().max(1000).optional(),
});

function splitTags(raw: string): string[] {
  return raw
    .split(/[,;|]/)
    .map((t) => t.trim())
    .filter(Boolean);
}

/**
 * Imports either format:
 * - link list (the agency's current sheet): one column of IG reel URLs ->
 *   ExampleReel stubs awaiting video upload
 * - hook table: text/category/tags/notes columns -> Hook rows
 */
export async function importCsv(formData: FormData): Promise<ImportReport> {
  await requireAdmin();

  const file = formData.get("file");
  const markProven = formData.get("markProven") === "on";
  if (!(file instanceof File)) {
    return { mode: "hooks", imported: 0, duplicates: 0, invalid: [], error: "No file uploaded" };
  }
  if (file.size > 2 * 1024 * 1024) {
    return { mode: "hooks", imported: 0, duplicates: 0, invalid: [], error: "File over 2 MB" };
  }

  // Strip the UTF-8 BOM Excel/Sheets exports often prepend — it breaks
  // header matching on the first column.
  const text = (await file.text()).replace(/^﻿/, "");

  const parsed = Papa.parse<string[]>(text, { skipEmptyLines: true });
  const rows = (parsed.data as string[][]).filter((r) => r.some((c) => c && c.trim()));
  if (rows.length === 0) {
    return { mode: "hooks", imported: 0, duplicates: 0, invalid: [], error: "File is empty" };
  }

  // Detect format: majority of first-column values being IG URLs = link list.
  const body = rows.slice(1);
  const sample = body.length > 0 ? body : rows;
  const urlish = sample.filter((r) => looksLikeUrl(r[0] ?? "")).length;
  const isLinkList = urlish >= Math.max(1, Math.ceil(sample.length / 2));

  const report: ImportReport = isLinkList
    ? await importLinkList(rows)
    : await importHookTable(text, markProven);

  revalidatePath("/admin/examples");
  revalidatePath("/admin/hooks");
  return report;
}

async function importLinkList(rows: string[][]): Promise<ImportReport> {
  const report: ImportReport = { mode: "links", imported: 0, duplicates: 0, invalid: [] };
  const seen = new Set<string>();

  // Skip a header row if its first cell isn't a URL.
  const start = looksLikeUrl(rows[0]?.[0] ?? "") ? 0 : 1;

  for (let i = start; i < rows.length; i++) {
    const value = (rows[i][0] ?? "").trim();
    if (!value) continue;
    const canonical = canonicalizeReelUrl(value);
    if (!canonical) {
      report.invalid.push({ row: i + 1, value, reason: "not an Instagram reel/post link" });
      continue;
    }
    if (seen.has(canonical)) {
      report.duplicates++;
      continue;
    }
    seen.add(canonical);
    const result = await prisma.exampleReel.createMany({
      data: [{ sourceUrl: canonical }],
      skipDuplicates: true,
    });
    if (result.count === 0) report.duplicates++;
    else report.imported++;
  }
  return report;
}

async function importHookTable(text: string, markProven: boolean): Promise<ImportReport> {
  const report: ImportReport = { mode: "hooks", imported: 0, duplicates: 0, invalid: [] };

  const parsed = Papa.parse<Record<string, string>>(text, {
    header: true,
    skipEmptyLines: true,
    transformHeader: (h) => h.trim().toLowerCase(),
  });

  const headers = parsed.meta.fields ?? [];
  const textCol = headers.find((h) => HOOK_TEXT_ALIASES.includes(h));
  if (!textCol) {
    report.error = `No hook text column found. Expected one of: ${HOOK_TEXT_ALIASES.join(", ")}`;
    return report;
  }
  const categoryCol = headers.find((h) => CATEGORY_ALIASES.includes(h));
  const tagsCol = headers.find((h) => TAGS_ALIASES.includes(h));
  const notesCol = headers.find((h) => NOTES_ALIASES.includes(h));

  const seen = new Set<string>();
  for (let i = 0; i < parsed.data.length; i++) {
    const raw = parsed.data[i];
    const candidate = HookRowSchema.safeParse({
      text: raw[textCol] ?? "",
      category: categoryCol ? raw[categoryCol] || undefined : undefined,
      tags: tagsCol && raw[tagsCol] ? splitTags(raw[tagsCol]) : undefined,
      notes: notesCol ? raw[notesCol] || undefined : undefined,
    });
    if (!candidate.success) {
      report.invalid.push({
        row: i + 2, // 1-indexed + header row
        value: (raw[textCol] ?? "").slice(0, 80),
        reason: candidate.error.issues[0]?.message ?? "invalid row",
      });
      continue;
    }
    const normalizedText = normalizeHookText(candidate.data.text);
    if (!normalizedText) {
      report.invalid.push({ row: i + 2, value: candidate.data.text, reason: "empty after normalizing" });
      continue;
    }
    if (seen.has(normalizedText)) {
      report.duplicates++;
      continue;
    }
    seen.add(normalizedText);
    const result = await prisma.hook.createMany({
      data: [
        {
          text: candidate.data.text,
          normalizedText,
          category: candidate.data.category ?? null,
          tags: candidate.data.tags ?? [],
          notes: candidate.data.notes ?? null,
          status: "APPROVED",
          source: "IMPORT",
          proven: markProven,
        },
      ],
      skipDuplicates: true,
    });
    if (result.count === 0) report.duplicates++;
    else report.imported++;
  }
  return report;
}
