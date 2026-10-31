"use client";

import { useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { analyzeExample, finalizeExampleMedia } from "@/actions/examples";

const FRAME_MAX_WIDTH = 720;

/**
 * Captures JPEG frames from the chosen video in the browser (hook window at
 * ~0.3/1.5/2.8s plus two spread frames), uploads video + frames, then links
 * them to the example and kicks off AI analysis. No server-side ffmpeg.
 */
async function captureFrames(file: File): Promise<Blob[]> {
  const url = URL.createObjectURL(file);
  const video = document.createElement("video");
  video.src = url;
  video.muted = true;
  video.playsInline = true;
  video.preload = "auto";

  await new Promise<void>((resolve, reject) => {
    video.onloadedmetadata = () => resolve();
    video.onerror = () => reject(new Error("Could not read this video file"));
  });

  const duration = Number.isFinite(video.duration) ? video.duration : 10;
  const hookWindow = [0.3, 1.5, 2.8].filter((t) => t < duration);
  const spread = [duration * 0.45, duration * 0.85];
  const times = [...hookWindow, ...spread].map((t) => Math.min(t, Math.max(duration - 0.1, 0)));

  const scale = Math.min(1, FRAME_MAX_WIDTH / (video.videoWidth || FRAME_MAX_WIDTH));
  const canvas = document.createElement("canvas");
  canvas.width = Math.round((video.videoWidth || 720) * scale);
  canvas.height = Math.round((video.videoHeight || 1280) * scale);
  const ctx = canvas.getContext("2d");
  if (!ctx) throw new Error("Canvas unavailable");

  const frames: Blob[] = [];
  for (const time of times) {
    await new Promise<void>((resolve, reject) => {
      const onSeeked = () => {
        video.removeEventListener("seeked", onSeeked);
        resolve();
      };
      video.addEventListener("seeked", onSeeked);
      video.onerror = () => reject(new Error("Seek failed"));
      video.currentTime = time;
    });
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    const blob = await new Promise<Blob | null>((resolve) =>
      canvas.toBlob(resolve, "image/jpeg", 0.8),
    );
    if (blob) frames.push(blob);
  }
  URL.revokeObjectURL(url);
  if (frames.length === 0) throw new Error("Could not capture frames from this video");
  return frames;
}

interface Props {
  exampleId?: string; // attach to an existing stub; omit to create a new example
  useBlobClientUpload: boolean;
  compact?: boolean;
}

export function ExampleUploader({ exampleId, useBlobClientUpload, compact }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function uploadViaBlob(file: File, frames: Blob[]) {
    const { upload } = await import("@vercel/blob/client");
    setStatus("Uploading video…");
    const video = await upload(`trial-reels/video-${Date.now()}.mp4`, file, {
      access: "public",
      handleUploadUrl: "/api/blob",
    });
    setStatus("Uploading frames…");
    const frameUrls: string[] = [];
    for (let i = 0; i < frames.length; i++) {
      const frame = await upload(`trial-reels/frame-${Date.now()}-${i}.jpg`, frames[i], {
        access: "public",
        handleUploadUrl: "/api/blob",
      });
      frameUrls.push(frame.url);
    }
    return { videoUrl: video.url, frameUrls, thumbUrl: frameUrls[0] };
  }

  async function uploadViaServer(file: File, frames: Blob[]) {
    setStatus("Uploading…");
    const form = new FormData();
    form.set("video", file);
    frames.forEach((frame, i) => form.append("frames", frame, `frame-${i}.jpg`));
    const res = await fetch("/api/upload", { method: "POST", body: form });
    const json = (await res.json()) as {
      videoUrl?: string;
      frameUrls?: string[];
      thumbUrl?: string;
      error?: string;
    };
    if (!res.ok || !json.videoUrl || !json.frameUrls) {
      throw new Error(json.error ?? "Upload failed");
    }
    return { videoUrl: json.videoUrl, frameUrls: json.frameUrls, thumbUrl: json.thumbUrl };
  }

  async function handleFile(file: File) {
    setBusy(true);
    setError(null);
    try {
      setStatus("Capturing frames…");
      const frames = await captureFrames(file);
      const media = useBlobClientUpload
        ? await uploadViaBlob(file, frames)
        : await uploadViaServer(file, frames);

      setStatus("Saving…");
      const { exampleId: id } = await finalizeExampleMedia({
        exampleId,
        videoUrl: media.videoUrl,
        thumbUrl: media.thumbUrl,
        frameUrls: media.frameUrls,
      });

      setStatus("Analyzing with AI…");
      const result = await analyzeExample(id);
      if (!result.ok) {
        setError(`Uploaded, but analysis failed: ${result.error}. You can retry from the example page.`);
      } else {
        setStatus("Done — analyzed ✓");
      }
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
      setStatus(null);
    } finally {
      setBusy(false);
      if (inputRef.current) inputRef.current.value = "";
    }
  }

  return (
    <div className={compact ? "" : "rounded-xl border border-dashed border-zinc-300 bg-white p-4"}>
      <input
        ref={inputRef}
        type="file"
        accept="video/mp4,video/quicktime,video/webm"
        className="hidden"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) void handleFile(file);
        }}
      />
      <button
        type="button"
        disabled={busy}
        onClick={() => inputRef.current?.click()}
        className="rounded-lg bg-zinc-900 px-3 py-1.5 text-sm font-medium text-white hover:bg-zinc-700 disabled:opacity-50"
      >
        {busy ? (status ?? "Working…") : exampleId ? "Upload video" : "Upload a saved reel"}
      </button>
      {!busy && status && <span className="ml-2 text-sm text-green-700">{status}</span>}
      {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
      {!compact && (
        <p className="mt-2 text-xs text-zinc-500">
          Save the reel to your device first, then upload it here. Frames are captured in your
          browser and the AI extracts the hook + background details automatically.
        </p>
      )}
    </div>
  );
}
