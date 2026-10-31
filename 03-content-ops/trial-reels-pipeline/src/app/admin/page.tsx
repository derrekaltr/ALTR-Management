import Link from "next/link";
import { requireAdmin } from "@/lib/auth";
import { prisma } from "@/lib/db";
import { todayInTimezone, dateStringToUtc } from "@/lib/dates";

export default async function Dashboard() {
  await requireAdmin();

  const [approved, proven, pending, examplesTotal, needsVideo, analyzed, creators] =
    await Promise.all([
      prisma.hook.count({ where: { status: "APPROVED" } }),
      prisma.hook.count({ where: { status: "APPROVED", proven: true } }),
      prisma.hook.count({ where: { status: "PENDING_REVIEW" } }),
      prisma.exampleReel.count(),
      prisma.exampleReel.count({ where: { status: "NEEDS_VIDEO" } }),
      prisma.exampleReel.count({ where: { status: "ANALYZED" } }),
      prisma.creator.findMany({ where: { active: true }, orderBy: { name: "asc" } }),
    ]);

  const todayPlans = await Promise.all(
    creators.map(async (creator) => {
      const date = dateStringToUtc(todayInTimezone(creator.timezone));
      const plan = await prisma.dayPlan.findUnique({
        where: { creatorId_date: { creatorId: creator.id, date } },
        include: { versions: true },
      });
      return { creator, plan };
    }),
  );

  const stats = [
    { label: "Approved hooks", value: approved, href: "/admin/hooks" },
    { label: "Proven hooks", value: proven, href: "/admin/hooks?proven=1" },
    { label: "Awaiting review", value: pending, href: "/admin/review" },
    { label: "Example reels", value: examplesTotal, href: "/admin/examples" },
    { label: "Examples needing video", value: needsVideo, href: "/admin/examples?status=NEEDS_VIDEO" },
    { label: "Examples analyzed", value: analyzed, href: "/admin/examples?status=ANALYZED" },
  ];

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-semibold">Dashboard</h1>

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
        {stats.map((s) => (
          <Link
            key={s.label}
            href={s.href}
            className="rounded-xl border border-zinc-200 bg-white p-4 hover:border-zinc-400"
          >
            <div className="text-2xl font-semibold">{s.value}</div>
            <div className="mt-1 text-xs text-zinc-500">{s.label}</div>
          </Link>
        ))}
      </div>

      <section>
        <h2 className="mb-3 text-lg font-medium">Today&apos;s plans</h2>
        {todayPlans.length === 0 && (
          <p className="text-sm text-zinc-500">
            No active creators yet. <Link className="underline" href="/admin/creators">Add one</Link>.
          </p>
        )}
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {todayPlans.map(({ creator, plan }) => {
            const posted = plan?.versions.filter((v) => v.status === "POSTED").length ?? 0;
            const total = plan?.versions.length ?? 0;
            return (
              <Link
                key={creator.id}
                href={`/admin/creators/${creator.id}`}
                className="rounded-xl border border-zinc-200 bg-white p-4 hover:border-zinc-400"
              >
                <div className="font-medium">{creator.name}</div>
                <div className="text-xs text-zinc-500">{creator.handle ?? "—"}</div>
                <div className="mt-2 text-sm">
                  {plan ? (
                    <span className={posted === total && total > 0 ? "text-green-700" : ""}>
                      {posted}/{total} versions posted today
                    </span>
                  ) : (
                    <span className="text-amber-700">No plan for today</span>
                  )}
                </div>
              </Link>
            );
          })}
        </div>
      </section>
    </div>
  );
}
