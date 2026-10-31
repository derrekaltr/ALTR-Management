import Link from "next/link";
import type { HookStatus, Prisma } from "@prisma/client";
import { requireAdmin } from "@/lib/auth";
import { prisma } from "@/lib/db";
import { createHookManual, restoreHook, retireHook, setHookProven } from "@/actions/hooks";

const STATUSES: HookStatus[] = ["APPROVED", "PENDING_REVIEW", "REJECTED", "RETIRED"];

export default async function HooksPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string; status?: string; category?: string; proven?: string }>;
}) {
  await requireAdmin();
  const params = await searchParams;
  const status: HookStatus = STATUSES.includes(params.status as HookStatus)
    ? (params.status as HookStatus)
    : "APPROVED";

  const where: Prisma.HookWhereInput = { status };
  if (params.q) where.text = { contains: params.q, mode: "insensitive" };
  if (params.category) where.category = params.category;
  if (params.proven === "1") where.proven = true;

  const [hooks, categories] = await Promise.all([
    prisma.hook.findMany({
      where,
      orderBy: [{ proven: "desc" }, { createdAt: "desc" }],
      take: 300,
      include: { exampleReel: { select: { id: true } } },
    }),
    prisma.hook.groupBy({ by: ["category"], where: { category: { not: null } } }),
  ]);

  const queryBase = new URLSearchParams();
  if (params.q) queryBase.set("q", params.q);
  if (params.category) queryBase.set("category", params.category);
  if (params.proven) queryBase.set("proven", params.proven);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Hook library</h1>

      <form className="flex flex-wrap items-end gap-3" method="get">
        <input type="hidden" name="status" value={status} />
        <label className="text-sm">
          <span className="block text-xs text-zinc-500">Search</span>
          <input
            name="q"
            defaultValue={params.q ?? ""}
            placeholder="Search hook text…"
            className="mt-1 rounded-lg border border-zinc-300 px-3 py-1.5 text-sm"
          />
        </label>
        <label className="text-sm">
          <span className="block text-xs text-zinc-500">Category</span>
          <select
            name="category"
            defaultValue={params.category ?? ""}
            className="mt-1 rounded-lg border border-zinc-300 px-3 py-1.5 text-sm"
          >
            <option value="">All</option>
            {categories.map((c) => (
              <option key={c.category} value={c.category!}>
                {c.category}
              </option>
            ))}
          </select>
        </label>
        <label className="flex items-center gap-1.5 pb-1.5 text-sm">
          <input type="checkbox" name="proven" value="1" defaultChecked={params.proven === "1"} />
          Proven only
        </label>
        <button className="rounded-lg border border-zinc-300 bg-white px-3 py-1.5 text-sm">
          Filter
        </button>
      </form>

      <div className="flex gap-2 text-sm">
        {STATUSES.map((s) => {
          const query = new URLSearchParams(queryBase);
          query.set("status", s);
          return (
            <Link
              key={s}
              href={`/admin/hooks?${query}`}
              className={`rounded-md px-2 py-1 ${status === s ? "bg-zinc-900 text-white" : "border border-zinc-300 bg-white"}`}
            >
              {s.toLowerCase().replace("_", " ")}
            </Link>
          );
        })}
      </div>

      <form
        action={createHookManual}
        className="flex flex-wrap items-end gap-3 rounded-xl border border-zinc-200 bg-white p-4"
      >
        <label className="grow text-sm">
          <span className="block text-xs text-zinc-500">Add a hook manually</span>
          <input
            name="text"
            required
            maxLength={300}
            placeholder="POV: …"
            className="mt-1 w-full rounded-lg border border-zinc-300 px-3 py-1.5 text-sm"
          />
        </label>
        <label className="text-sm">
          <span className="block text-xs text-zinc-500">Category</span>
          <input
            name="category"
            placeholder="funny / sexy / goofy"
            className="mt-1 rounded-lg border border-zinc-300 px-3 py-1.5 text-sm"
          />
        </label>
        <button className="rounded-lg bg-zinc-900 px-3 py-1.5 text-sm font-medium text-white hover:bg-zinc-700">
          Add
        </button>
      </form>

      <div className="overflow-x-auto rounded-xl border border-zinc-200 bg-white">
        <table className="w-full text-sm">
          <thead className="border-b border-zinc-200 text-left text-xs text-zinc-500">
            <tr>
              <th className="p-3">Hook</th>
              <th className="p-3">Category</th>
              <th className="p-3">Source</th>
              <th className="p-3">Used</th>
              <th className="p-3">Proven</th>
              <th className="p-3"></th>
            </tr>
          </thead>
          <tbody>
            {hooks.map((hook) => (
              <tr key={hook.id} className="border-b border-zinc-100 last:border-0">
                <td className="max-w-md p-3">
                  “{hook.text}”
                  {hook.exampleReel && (
                    <Link
                      href={`/admin/examples/${hook.exampleReel.id}`}
                      className="ml-2 text-xs text-zinc-400 underline"
                    >
                      example
                    </Link>
                  )}
                </td>
                <td className="p-3 text-zinc-500">{hook.category ?? "—"}</td>
                <td className="p-3 text-zinc-500">{hook.source.toLowerCase()}</td>
                <td className="p-3 text-zinc-500">{hook.timesUsed}×</td>
                <td className="p-3">
                  <form action={setHookProven}>
                    <input type="hidden" name="hookId" value={hook.id} />
                    <input type="hidden" name="proven" value={hook.proven ? "false" : "true"} />
                    <button
                      title={hook.proven ? "Unmark proven" : "Mark proven"}
                      className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                        hook.proven ? "bg-green-100 text-green-800" : "bg-zinc-100 text-zinc-500"
                      }`}
                    >
                      {hook.proven ? "proven ✓" : "mark proven"}
                    </button>
                  </form>
                </td>
                <td className="p-3 text-right">
                  {hook.status === "RETIRED" ? (
                    <form action={restoreHook}>
                      <input type="hidden" name="hookId" value={hook.id} />
                      <button className="text-xs text-zinc-500 underline">restore</button>
                    </form>
                  ) : (
                    hook.status === "APPROVED" && (
                      <form action={retireHook}>
                        <input type="hidden" name="hookId" value={hook.id} />
                        <button className="text-xs text-zinc-500 underline">retire</button>
                      </form>
                    )
                  )}
                </td>
              </tr>
            ))}
            {hooks.length === 0 && (
              <tr>
                <td colSpan={6} className="p-6 text-center text-zinc-500">
                  No hooks match. Import a CSV, analyze examples, or generate a batch.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
