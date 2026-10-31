import { NextRequest, NextResponse } from "next/server";
import { SESSION_COOKIE, verifySessionValue } from "@/lib/auth";
import { saveFile } from "@/lib/storage";

export const runtime = "nodejs";
// Reel videos + frames in one multipart request; generous for self-hosted/local.
export const maxDuration = 60;

const MAX_VIDEO_BYTES = 200 * 1024 * 1024;
const MAX_FRAME_BYTES = 2 * 1024 * 1024;

/**
 * Multipart upload endpoint (local dev / self-hosted). On Vercel with Blob
 * configured, the client uploads directly to Blob via /api/blob instead —
 * serverless request bodies cap at ~4.5 MB.
 */
export async function POST(request: NextRequest) {
  if (!verifySessionValue(request.cookies.get(SESSION_COOKIE)?.value)) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const form = await request.formData();
  const video = form.get("video");
  const frames = form.getAll("frames");

  if (frames.length === 0 || frames.length > 8) {
    return NextResponse.json({ error: "Expected 1-8 frames" }, { status: 400 });
  }

  let videoUrl: string | null = null;
  if (video instanceof File) {
    if (video.size > MAX_VIDEO_BYTES) {
      return NextResponse.json({ error: "Video over 200 MB" }, { status: 400 });
    }
    videoUrl = await saveFile(
      Buffer.from(await video.arrayBuffer()),
      "video",
      video.type || "video/mp4",
    );
  }

  const frameUrls: string[] = [];
  for (const frame of frames) {
    if (!(frame instanceof File) || frame.size > MAX_FRAME_BYTES) {
      return NextResponse.json({ error: "Invalid frame upload" }, { status: 400 });
    }
    frameUrls.push(
      await saveFile(Buffer.from(await frame.arrayBuffer()), "frame", frame.type || "image/jpeg"),
    );
  }

  return NextResponse.json({ videoUrl, frameUrls, thumbUrl: frameUrls[0] ?? null });
}
