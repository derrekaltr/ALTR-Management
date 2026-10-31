"use client";

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";
import { reviewHook } from "@/actions/review";

interface Props {
  hookId: string;
  text: string;
  category: string | null;
  rationale: string | null;
  sourceLabel: string;
}

export function ReviewCard({ hookId, text, category, rationale, sourceLabel }: Props) {
  const [editing, setEditing] = useState(false);
  const [editedText, setEditedText] = useState(text);
  const [error, setError] = useState<string | null>(null);
  const [pending, startTransition] = useTransition();
  const router = useRouter();

  function decide(decision: "approve" | "reject") {
    const form = new FormData();
    form.set("hookId", hookId);
    form.set("decision", decision);
    if (editing && editedText !== text) form.set("editedText", editedText);
    setError(null);
    startTransition(async () => {
      const result = await reviewHook(form);
      if (result?.error) setError(result.error);
      else router.refresh();
    });
  }

  return (
    <div className="rounded-xl border border-zinc-200 bg-white p-4">
      {editing ? (
        <textarea
          value={editedText}
          onChange={(e) => setEditedText(e.target.value)}
          rows={2}
          maxLength={300}
          className="w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm"
        />
      ) : (
        <p className="text-base font-medium">“{text}”</p>
      )}
      <p className="mt-1 text-xs text-zinc-400">
        {category ?? "uncategorized"} · {sourceLabel}
        {rationale && <span className="ml-1 italic">— {rationale}</span>}
      </p>
      {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
      <div className="mt-3 flex gap-2">
        <button
          disabled={pending}
          onClick={() => decide("approve")}
          className="rounded-lg bg-green-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-green-500 disabled:opacity-50"
        >
          Approve
        </button>
        <button
          disabled={pending}
          onClick={() => decide("reject")}
          className="rounded-lg bg-red-50 px-3 py-1.5 text-sm font-medium text-red-700 hover:bg-red-100 disabled:opacity-50"
        >
          Reject
        </button>
        <button
          type="button"
          disabled={pending}
          onClick={() => setEditing((v) => !v)}
          className="rounded-lg border border-zinc-300 px-3 py-1.5 text-sm hover:border-zinc-500 disabled:opacity-50"
        >
          {editing ? "Cancel edit" : "Edit"}
        </button>
      </div>
    </div>
  );
}
