import Link from "next/link";
import { notFound } from "next/navigation";
import { requireAdmin } from "@/lib/auth";
import { prisma } from "@/lib/db";
import { addDays, dateStringToUtc, formatDisplayDate, todayInTimezone, utcToDateString } from "@/lib/dates";
import { addVersion, removeVersion, toggleVersionFlag, upsertDayPlan } from "@/actions/plans";
import { updateCreator } from "@/actions/creators";
import { CopyLinkButton } from "@/components/CopyLinkButton";

export default async function CreatorDetailPage({
  params,
  searchParams,
}: {
  params: Promise<{ id: string }>;
  searchParams: Promise<{ date?: string }>;
}) {
  await requireAdmin();
  const { id } = await params;
  const query = await searchParams;

  const creator = await prisma.creator.findUnique({ where: { id } });
  if (!creator) notFound();

  const today = todayInTimezone(creator.timezone);
  const date = /^\d{4}-\d{2}-\d{2}$/.test(query.date ?? "") ? query.date! : today;

  const plan = await prisma.dayPlan.findUnique({
    where: { creatorId_date: { creatorId: id, date: dateStringToUtc(date) } },
    include: {
      versions: {
        orderBy: { order: "asc" },
        include: { hook: true, exampleReel: { select: { id: true, thumbUrl: true } } },
      },
    },
  });

  // Hooks available to add: approved, not already in this plan, not used for
  // this creator in the last 14 days.
  const usedHookIds = new Set(plan?.versions.map((v) => v.hookId) ?? []);
  const recentCutoff = dateStringToUtc(addDays(date, -14));
  const recentlyUsed = await prisma.version.findMany({
    where: {
      dayPlan: { creatorId: id, date: { gte: recentCutoff, lt: dateStringToUtc(date) } },
    },
    select: { hookId: true },
  });
  for (const v of recentlyUsed) usedHookIds.add(v.hookId);

  const [availableHooks, exampleOptions, history] = await Promise.all([
    prisma.hook.findMany({
      where: { status: "APPROVED", id: { notIn: [...usedHookIds] } },
      orderBy: [{ proven: "desc" }, { timesUsed: "asc" }],
      take: 100,
    }),
    prisma.exampleReel.findMany({
      where: { status: "ANALYZED" },
      orderBy: { createdAt: "desc" },
      take: 50,
      select: { id: true, backgroundDescription: true, tags: true },
    }),
    prisma.dayPlan.findMany({
      where: { creatorId: id },
      orderBy: { date: "desc" },
      take: 14,
      include: { versions: { select: { status: true } } },
    }),
  ]);

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold">{creator.name}</h1>
          <p className="text-sm text-zinc-500">
            {creator.handle ?? "no handle"} · {creator.timezone}
            {!creator.active && " · deactivated"}
          </p>
        </div>
        <div className="flex gap-2">
          <CopyLinkButton token={creator.token} />
          <Link href="/admin/creators" className="self-center text-sm text-zinc-500 underline">
            ← All creators
          </Link>
        </div>
      </div>

      <section className="rounded-xl border border-zinc-200 bg-white p-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h2 className="text-lg font-medium">
            Plan for {formatDisplayDate(date)}
            {date === today && <span className="ml-2 text-sm text-green-700">(today)</span>}
          </h2>
          <div className="flex items-center gap-2 text-sm">
            <Link
              href={`/admin/creators/${id}?date=${addDays(date, -1)}`}
              className="rounded-md border border-zinc-300 px-2 py-1"
            >
              ←
            </Link>
            <span className="text-zinc-500">{date}</span>
            <Link
              href={`/admin/creators/${id}?date=${addDays(date, 1)}`}
              className="rounded-md border border-zinc-300 px-2 py-1"
            >
              →
            </Link>
          </div>
        </div>

        <form action={upsertDayPlan} className="mt-4 flex flex-wrap items-end gap-3">
          <input type="hidden" name="creatorId" value={id} />
          <input type="hidden" name="date" value={date} />
          <label className="grow text-sm">
            <span className="block text-xs text-zinc-500">
              Base video concept (what the creator films — keep it blank & low-action)
            </span>
            <input
              name="notes"
              defaultValue={plan?.notes ?? ""}
              placeholder="e.g. mirror fit-check, slow pan, no talking"
              className="mt-1 w-full rounded-lg border border-zinc-300 px-3 py-1.5 text-sm"
            />
          </label>
          <button className="rounded-lg bg-zinc-900 px-3 py-1.5 text-sm font-medium text-white hover:bg-zinc-700">
            {plan ? "Update plan" : "Create plan"}
          </button>
        </form>

        {plan && (
          <>
            <h3 className="mt-6 text-sm font-medium text-zinc-500">
              Versions ({plan.versions.length}) — each is the same base video re-posted with a new
              hook via Edits → versions
            </h3>
            <ul className="mt-2 space-y-2">
              {plan.versions.map((version) => (
                <li
                  key={version.id}
                  className="flex flex-wrap items-center gap-3 rounded-lg border border-zinc-100 bg-zinc-50 p-3 text-sm"
                >
                  <span className="font-mono text-xs text-zinc-400">#{version.order}</span>
                  <span className="grow font-medium">“{version.hook.text}”</span>
                  <form action={toggleVersionFlag}>
                    <input type="hidden" name="versionId" value={version.id} />
                    <input type="hidden" name="flag" value="changeAudio" />
                    <button
                      className={`rounded-full px-2 py-0.5 text-xs ${version.changeAudio ? "bg-purple-100 text-purple-800" : "bg-zinc-100 text-zinc-400"}`}
                    >
                      new audio
                    </button>
                  </form>
                  <form action={toggleVersionFlag}>
                    <input type="hidden" name="versionId" value={version.id} />
                    <input type="hidden" name="flag" value="changeSpeed" />
                    <button
                      className={`rounded-full px-2 py-0.5 text-xs ${version.changeSpeed ? "bg-blue-100 text-blue-800" : "bg-zinc-100 text-zinc-400"}`}
                    >
                      speed change
                    </button>
                  </form>
                  {version.exampleReel && (
                    <Link
                      href={`/admin/examples/${version.exampleReel.id}`}
                      className="text-xs underline"
                    >
                      ref
                    </Link>
                  )}
                  <span
                    className={`rounded-full px-2 py-0.5 text-xs ${
                      version.status === "POSTED"
                        ? "bg-green-100 text-green-800"
                        : "bg-zinc-100 text-zinc-500"
                    }`}
                  >
                    {version.status.toLowerCase()}
                  </span>
                  <form action={removeVersion}>
                    <input type="hidden" name="versionId" value={version.id} />
                    <button className="text-xs text-red-600 underline">remove</button>
                  </form>
                </li>
              ))}
              {plan.versions.length === 0 && (
                <li className="text-sm text-zinc-500">No versions yet — add hooks below.</li>
              )}
            </ul>

            <form action={addVersion} className="mt-4 flex flex-wrap items-end gap-3">
              <input type="hidden" name="dayPlanId" value={plan.id} />
              <label className="grow text-sm">
                <span className="block text-xs text-zinc-500">
                  Hook (excludes ones used in the last 14 days)
                </span>
                <select
                  name="hookId"
                  required
                  className="mt-1 w-full rounded-lg border border-zinc-300 px-3 py-1.5 text-sm"
                >
                  {availableHooks.map((hook) => (
                    <option key={hook.id} value={hook.id}>
                      {hook.proven ? "★ " : ""}
                      {hook.text}
                    </option>
                  ))}
                </select>
              </label>
              <label className="text-sm">
                <span className="block text-xs text-zinc-500">Reference example (optional)</span>
                <select
                  name="exampleReelId"
                  className="mt-1 max-w-56 rounded-lg border border-zinc-300 px-3 py-1.5 text-sm"
                >
                  <option value="">None</option>
                  {exampleOptions.map((example) => (
                    <option key={example.id} value={example.id}>
                      {(example.tags.join("/") || example.backgroundDescription || example.id).slice(0, 40)}
                    </option>
                  ))}
                </select>
              </label>
              <label className="flex items-center gap-1.5 pb-2 text-sm">
                <input type="checkbox" name="changeAudio" defaultChecked /> new audio
              </label>
              <label className="flex items-center gap-1.5 pb-2 text-sm">
                <input type="checkbox" name="changeSpeed" /> speed change
              </label>
              <button className="rounded-lg bg-zinc-900 px-3 py-1.5 text-sm font-medium text-white hover:bg-zinc-700">
                Add version
              </button>
            </form>
            {availableHooks.length === 0 && (
              <p className="mt-2 text-xs text-amber-700">
                No unused approved hooks available — approve more in Review or relax reuse by
                picking a different date.
              </p>
            )}
          </>
        )}
      </section>

      <section>
        <h2 className="mb-3 text-lg font-medium">Recent plans</h2>
        <div className="flex flex-wrap gap-2">
          {history.map((p) => {
            const d = utcToDateString(p.date);
            const posted = p.versions.filter((v) => v.status === "POSTED").length;
            return (
              <Link
                key={p.id}
                href={`/admin/creators/${id}?date=${d}`}
                className={`rounded-lg border px-3 py-1.5 text-sm ${d === date ? "border-zinc-900" : "border-zinc-200 bg-white"}`}
              >
                {d} · {posted}/{p.versions.length}
              </Link>
            );
          })}
          {history.length === 0 && <p className="text-sm text-zinc-500">No plans yet.</p>}
        </div>
      </section>

      <section className="max-w-lg rounded-xl border border-zinc-200 bg-white p-4">
        <h2 className="mb-3 text-sm font-medium text-zinc-500">Creator settings</h2>
        <form action={updateCreator} className="flex flex-wrap items-end gap-3">
          <input type="hidden" name="creatorId" value={id} />
          <label className="text-sm">
            <span className="block text-xs text-zinc-500">Name</span>
            <input
              name="name"
              defaultValue={creator.name}
              required
              className="mt-1 rounded-lg border border-zinc-300 px-3 py-1.5 text-sm"
            />
          </label>
          <label className="text-sm">
            <span className="block text-xs text-zinc-500">Handle</span>
            <input
              name="handle"
              defaultValue={creator.handle ?? ""}
              className="mt-1 rounded-lg border border-zinc-300 px-3 py-1.5 text-sm"
            />
          </label>
          <label className="text-sm">
            <span className="block text-xs text-zinc-500">Timezone</span>
            <input
              name="timezone"
              defaultValue={creator.timezone}
              className="mt-1 rounded-lg border border-zinc-300 px-3 py-1.5 text-sm"
            />
          </label>
          <button className="rounded-lg border border-zinc-300 px-3 py-1.5 text-sm hover:border-zinc-500">
            Save
          </button>
        </form>
      </section>
    </div>
  );
}
