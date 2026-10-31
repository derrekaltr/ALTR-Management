import { mkdir, readFile as fsReadFile, writeFile } from "node:fs/promises";
import { randomBytes } from "node:crypto";
import path from "node:path";

/**
 * File storage abstraction: Vercel Blob when BLOB_READ_WRITE_TOKEN is set,
 * otherwise local disk under public/uploads/ (gitignored) for dev.
 */

const LOCAL_DIR = path.join(process.cwd(), "public", "uploads");

function usingBlob(): boolean {
  return Boolean(process.env.BLOB_READ_WRITE_TOKEN);
}

function extensionFor(contentType: string): string {
  if (contentType.includes("mp4")) return ".mp4";
  if (contentType.includes("quicktime")) return ".mov";
  if (contentType.includes("webm")) return ".webm";
  if (contentType.includes("jpeg") || contentType.includes("jpg")) return ".jpg";
  if (contentType.includes("png")) return ".png";
  return "";
}

/** Store a file; returns a URL usable in <video src>/<img src>. */
export async function saveFile(
  data: Buffer,
  kind: "video" | "frame" | "thumb",
  contentType: string,
): Promise<string> {
  const name = `${kind}-${Date.now()}-${randomBytes(8).toString("hex")}${extensionFor(contentType)}`;
  if (usingBlob()) {
    const { put } = await import("@vercel/blob");
    const blob = await put(`trial-reels/${name}`, data, {
      access: "public",
      contentType,
      addRandomSuffix: true,
    });
    return blob.url;
  }
  await mkdir(LOCAL_DIR, { recursive: true });
  await writeFile(path.join(LOCAL_DIR, name), data);
  return `/uploads/${name}`;
}

/** Read a stored file back (used to re-run analysis from saved frames). */
export async function readStoredFile(url: string): Promise<Buffer> {
  if (url.startsWith("/uploads/")) {
    return fsReadFile(path.join(process.cwd(), "public", url));
  }
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Failed to fetch stored file (${res.status}): ${url}`);
  return Buffer.from(await res.arrayBuffer());
}
