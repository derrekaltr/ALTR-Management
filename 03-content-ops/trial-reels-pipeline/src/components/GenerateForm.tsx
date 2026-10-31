"use client";

import { useState, useTransition } from "react";
import { startGenerationBatch } from "@/actions/generation";

interface SeedOption {
  id: string;
  text: string;
  category: string | null;
  proven: boolean;
  timesUsed: number;
}

export function GenerateForm({ seeds }: { seeds: SeedOption[] }) {
  const [error, setError] = useState<string | null>(null);
  const [pending, startTransition] = useTransition();

  return (
    <form
      className="space-y-4"
      onSubmit={(e) => {
        e.preventDefault();
        const form = new FormData(e.currentTarget);
        setError(null);
        startTransition(async () => {
          const result = await startGenerationBatch(form);
          if (result?.error) setError(result.error);
        });
      }}
    >
      <div className="rounded-xl border border-zinc-200 bg-white">
        <div className="border-b border-zinc-200 p-3 text-sm font-medium">
          Pick seed hooks (proven winners work best)
        </div>
        <div className="max-h-96 space-y-1 overflow-y-auto p-3">
          {seeds.length === 0 && (
            <p className="text-sm text-zinc-500">
              No approved hooks yet — import or approve some first.
            </p>
          )}
          {seeds.map((seed) => (
            <label
              key={seed.id}
              className="flex cursor-pointer items-start gap-2 rounded-lg p-2 text-sm hover:bg-zinc-50"
            >
              <input type="checkbox" name="seedIds" value={seed.id} className="mt-1" />
              <span>
                “{seed.text}”
                <span className="ml-2 text-xs text-zinc-400">
                  {seed.category ?? "uncategorized"}
                  {seed.proven && " · proven"}
                  {seed.timesUsed > 0 && ` · used ${seed.timesUsed}×`}
                </span>
              </span>
            </label>
          ))}
        </div>
      </div>

      <div className="flex flex-wrap items-end gap-3">
        <label className="grow text-sm">
          <span className="block text-xs text-zinc-500">Tone guidance (optional)</span>
          <input
            name="toneGuidance"
            placeholder="e.g. lean goofier, gym-day vibe, no coffee jokes"
            className="mt-1 w-full rounded-lg border border-zinc-300 px-3 py-1.5 text-sm"
          />
        </label>
        <label className="text-sm">
          <span className="block text-xs text-zinc-500">How many</span>
          <input
            type="number"
            name="count"
            defaultValue={10}
            min={1}
            max={25}
            className="mt-1 w-24 rounded-lg border border-zinc-300 px-3 py-1.5 text-sm"
          />
        </label>
        <button
          disabled={pending}
          className="rounded-lg bg-zinc-900 px-4 py-1.5 text-sm font-medium text-white hover:bg-zinc-700 disabled:opacity-50"
        >
          {pending ? "Generating…" : "Generate batch"}
        </button>
      </div>
      {error && <p className="text-sm text-red-600">{error}</p>}
      {pending && (
        <p className="text-sm text-zinc-500">
          Talking to the model — this can take up to ~30 seconds…
        </p>
      )}
    </form>
  );
}
