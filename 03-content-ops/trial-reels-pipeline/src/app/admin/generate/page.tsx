import { requireAdmin } from "@/lib/auth";
import { prisma } from "@/lib/db";
import { retryBatch } from "@/actions/generation";
import { GenerateForm } from "@/components/GenerateForm";

export const maxDuration = 60;

export default async function GeneratePage() {
  await requireAdmin();

  const [seeds, recentBatches] = await Promise.all([
    prisma.hook.findMany({
      where: { status: "APPROVED" },
      orderBy: [{ proven: "desc" }, { timesUsed: "desc" }, { createdAt: "desc" }],
      take: 100,
      select: { id: true, text: true, category: true, proven: true, timesUsed: true },
    }),
    prisma.generationBatch.findMany({
      orderBy: { createdAt: "desc" },
      take: 10,
      include: { _count: { select: { hooks: true } } },
    }),
  ]);

  const usingMock = process.env.LLM_MOCK === "1" || !process.env.ANTHROPIC_API_KEY;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold">Generate hooks</h1>
        <p className="mt-1 text-sm text-zinc-500">
          Seeds + tone guidance go to the model; candidates land in the review queue.
          {usingMock && (
            <span className="ml-2 rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-800">
              mock mode — set ANTHROPIC_API_KEY for real generation
            </span>
          )}
        </p>
      </div>

      <GenerateForm seeds={seeds} />

      <section>
        <h2 className="mb-3 text-lg font-medium">Recent batches</h2>
        <div className="overflow-x-auto rounded-xl border border-zinc-200 bg-white">
          <table className="w-full text-sm">
            <thead className="border-b border-zinc-200 text-left text-xs text-zinc-500">
              <tr>
                <th className="p-3">When</th>
                <th className="p-3">Model</th>
                <th className="p-3">Requested</th>
                <th className="p-3">Inserted</th>
                <th className="p-3">Status</th>
                <th className="p-3"></th>
              </tr>
            </thead>
            <tbody>
              {recentBatches.map((batch) => (
                <tr key={batch.id} className="border-b border-zinc-100 last:border-0">
                  <td className="p-3 text-zinc-500">{batch.createdAt.toISOString().slice(0, 16).replace("T", " ")}</td>
                  <td className="p-3">{batch.model}</td>
                  <td className="p-3">{batch.count}</td>
                  <td className="p-3">{batch._count.hooks}</td>
                  <td className="p-3">
                    <span
                      className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                        batch.status === "COMPLETE"
                          ? "bg-green-100 text-green-800"
                          : batch.status === "FAILED"
                            ? "bg-red-100 text-red-800"
                            : "bg-blue-100 text-blue-800"
                      }`}
                    >
                      {batch.status.toLowerCase()}
                    </span>
                    {batch.error && <div className="mt-1 text-xs text-zinc-500">{batch.error}</div>}
                  </td>
                  <td className="p-3">
                    {batch.status === "FAILED" && (
                      <form action={retryBatch}>
                        <input type="hidden" name="batchId" value={batch.id} />
                        <button className="text-xs underline">Retry</button>
                      </form>
                    )}
                  </td>
                </tr>
              ))}
              {recentBatches.length === 0 && (
                <tr>
                  <td colSpan={6} className="p-6 text-center text-zinc-500">
                    No batches yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
