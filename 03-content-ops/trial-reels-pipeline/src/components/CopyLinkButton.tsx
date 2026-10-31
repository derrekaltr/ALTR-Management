"use client";

import { useState } from "react";

/** Copies the creator's tokenized link without ever rendering it on screen. */
export function CopyLinkButton({ token }: { token: string }) {
  const [copied, setCopied] = useState(false);
  return (
    <button
      type="button"
      className="rounded-lg border border-zinc-300 bg-white px-2.5 py-1 text-xs hover:border-zinc-500"
      onClick={async () => {
        await navigator.clipboard.writeText(`${window.location.origin}/c/${token}`);
        setCopied(true);
        setTimeout(() => setCopied(false), 1500);
      }}
    >
      {copied ? "Link copied ✓" : "Copy creator link"}
    </button>
  );
}
