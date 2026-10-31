"use client";

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";
import { analyzeExample } from "@/actions/examples";

export function AnalyzeButton({ exampleId, label }: { exampleId: string; label?: string }) {
  const [pending, startTransition] = useTransition();
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  return (
    <span>
      <button
        type="button"
        disabled={pending}
        onClick={() =>
          startTransition(async () => {
            setError(null);
            const result = await analyzeExample(exampleId);
            if (!result.ok) setError(result.error);
            router.refresh();
          })
        }
        className="rounded-lg border border-zinc-300 bg-white px-3 py-1.5 text-sm hover:border-zinc-500 disabled:opacity-50"
      >
        {pending ? "Analyzing…" : (label ?? "Re-run analysis")}
      </button>
      {error && <span className="ml-2 text-sm text-red-600">{error}</span>}
    </span>
  );
}
