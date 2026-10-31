import Link from "next/link";
import { requireAdmin } from "@/lib/auth";
import { prisma } from "@/lib/db";
import { approveBatchRemainder } from "@/actions/review";
import { ReviewCard } from "@/components/ReviewCard";

export default async function ReviewPage() {
  await requireAdmin();

  const pending = await prisma.hook.findMany({
    where: { status: "PENDING_REVIEW" },
    orderBy: { createdAt: "desc" },
    include: {
      batch: { select: { id: true, createdAt: true, model: true, toneGuidance: true } },
      exampleReel: { select: { id: true, sourceUrl: true } },
    },
  });

  const byBatch = new Map<string, typeof pending>();
  const extracted: typeof pending = [];
  for (const hook of pending) {
    if (hook.batch) {
      const list = byBatch.get(hook.batch.id) ?? [];
      list.push(hook);
      byBatch.set(hook.batch.id, list);
    } else {
      extracted.push(hook);
    }
  }

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-semibold">Review queue</h1>
      {pending.length === 0 && (
        <p className="text-sm text-zinc-500">
          Nothing to review. <Link href="/admin/generate" className="underline">Generate a batch</Link>{" "}
          or analyze an example reel.
        </p>
      )}

      {extracted.length > 0 && (
        <section className="space-y-3">
          <h2 className="text-lg font-medium">Extracted from example reels</h2>
          <div className="grid gap-3 md:grid-cols-2">
            {extracted.map((hook) => (
              <ReviewCard
                key={hook.id}
                hookId={hook.id}
                text={hook.text}
                category={hook.category}
                rationale={null}
                sourceLabel="extracted from example"
              />
            ))}
          </div>
        </section>
      )}

      {[...byBatch.entries()].map(([batchId, hooks]) => {
        const batch = hooks[0].batch!;
        return (
          <section key={batchId} className="space-y-3">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <h2 className="text-lg font-medium">
                Batch · {batch.model} ·{" "}
                {batch.createdAt.toISOString().slice(0, 16).replace("T", " ")}
                {batch.toneGuidance && (
                  <span className="ml-2 text-sm font-normal text-zinc-500">
                    “{batch.toneGuidance}”
                  </span>
                )}
              </h2>
              <form action={approveBatchRemainder}>
                <input type="hidden" name="batchId" value={batchId} />
                <button className="rounded-lg border border-zinc-300 bg-white px-3 py-1.5 text-sm hover:border-zinc-500">
                  Approve all remaining ({hooks.length})
                </button>
              </form>
            </div>
            <div className="grid gap-3 md:grid-cols-2">
              {hooks.map((hook) => (
                <ReviewCard
                  key={hook.id}
                  hookId={hook.id}
                  text={hook.text}
                  category={hook.category}
                  rationale={hook.notes}
                  sourceLabel="generated"
                />
              ))}
            </div>
          </section>
        );
      })}
    </div>
  );
}
