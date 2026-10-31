import { notFound } from "next/navigation";
import { prisma } from "@/lib/db";
import { addDays, dateStringToUtc, formatDisplayDate, todayInTimezone } from "@/lib/dates";
import { markVersionPosted } from "@/actions/creatorView";
import { CopyButton } from "@/components/CopyButton";

export default async function CreatorViewPage({
  params,
}: {
  params: Promise<{ token: string }>;
}) {
  const { token } = await params;
  const creator = await prisma.creator.findUnique({ where: { token } });
  if (!creator || !creator.active) notFound();

  const today = todayInTimezone(creator.timezone);
  const yesterday = addDays(today, -1);

  const [todayPlan, yesterdayPlan] = await Promise.all([
    prisma.dayPlan.findUnique({
      where: { creatorId_date: { creatorId: creator.id, date: dateStringToUtc(today) } },
      include: {
        versions: {
          orderBy: { order: "asc" },
          include: {
            hook: { select: { text: true } },
            exampleReel: { select: { videoUrl: true, thumbUrl: true } },
          },
        },
      },
    }),
    prisma.dayPlan.findUnique({
      where: { creatorId_date: { creatorId: creator.id, date: dateStringToUtc(yesterday) } },
      include: {
        versions: {
          orderBy: { order: "asc" },
          include: { hook: { select: { text: true } } },
        },
      },
    }),
  ]);

  const posted = todayPlan?.versions.filter((v) => v.status === "POSTED").length ?? 0;
  const total = todayPlan?.versions.length ?? 0;
  const yesterdayUnposted = yesterdayPlan?.versions.filter((v) => v.status === "PLANNED") ?? [];

  return (
    <main className="mx-auto max-w-md px-4 py-6 pb-16">
      <header>
        <h1 className="text-xl font-semibold">Hey {creator.name.split(" ")[0]} 👋</h1>
        <p className="text-sm text-zinc-500">{formatDisplayDate(today)}</p>
      </header>

      <div className="mt-4 space-y-1 rounded-xl bg-zinc-900 p-4 text-sm text-zinc-100">
        <p>📱 Film ONE base video today — blank &amp; low-action, let the text do the work.</p>
        <p>⏱️ Hook text on screen within the first 3 seconds. Every time.</p>
        <p>🎵 Where a version says “new audio”, swap the sound before posting.</p>
        <p>🛠️ Build each version in the Edits app → versions, from your original file.</p>
      </div>

      {!todayPlan || total === 0 ? (
        <div className="mt-6 rounded-xl border border-dashed border-zinc-300 bg-white p-6 text-center text-sm text-zinc-500">
          No plan for today yet — check back soon.
        </div>
      ) : (
        <>
          <div className="mt-6 flex items-center justify-between">
            <h2 className="font-medium">Today&apos;s versions</h2>
            <span
              className={`rounded-full px-2.5 py-1 text-xs font-semibold ${
                posted === total ? "bg-green-100 text-green-800" : "bg-zinc-100 text-zinc-600"
              }`}
            >
              {posted}/{total} posted
            </span>
          </div>
          {todayPlan.notes && (
            <p className="mt-1 text-sm text-zinc-500">
              🎥 Base video: <span className="font-medium text-zinc-700">{todayPlan.notes}</span>
            </p>
          )}

          <ul className="mt-3 space-y-3">
            {todayPlan.versions.map((version) => (
              <li
                key={version.id}
                className={`rounded-xl border bg-white p-4 ${
                  version.status === "POSTED" ? "border-green-200 opacity-70" : "border-zinc-200"
                }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <span className="font-mono text-xs text-zinc-400">#{version.order}</span>
                  <div className="flex gap-1.5">
                    {version.changeAudio && (
                      <span className="rounded-full bg-purple-100 px-2 py-0.5 text-xs font-medium text-purple-800">
                        🎵 new audio
                      </span>
                    )}
                    {version.changeSpeed && (
                      <span className="rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-800">
                        ⚡ speed change
                      </span>
                    )}
                  </div>
                </div>
                <p
                  className={`mt-2 text-lg font-semibold leading-snug ${
                    version.status === "POSTED" ? "line-through" : ""
                  }`}
                >
                  {version.hook.text}
                </p>
                {version.exampleReel?.videoUrl && (
                  <details className="mt-2">
                    <summary className="cursor-pointer text-xs text-zinc-500 underline">
                      See reference clip
                    </summary>
                    <video
                      src={version.exampleReel.videoUrl}
                      controls
                      playsInline
                      className="mt-2 aspect-[9/16] w-40 rounded-lg bg-black"
                    />
                  </details>
                )}
                <div className="mt-3 flex items-center gap-2">
                  <CopyButton
                    value={version.hook.text}
                    label="Copy text"
                    className="rounded-lg border border-zinc-300 bg-white px-3 py-1.5 text-sm hover:border-zinc-500"
                  />
                  <form action={markVersionPosted} className="grow">
                    <input type="hidden" name="token" value={token} />
                    <input type="hidden" name="versionId" value={version.id} />
                    {version.status === "POSTED" ? (
                      <>
                        <input type="hidden" name="undo" value="true" />
                        <button className="w-full rounded-lg border border-zinc-200 px-3 py-1.5 text-sm text-zinc-500">
                          Posted ✓ (tap to undo)
                        </button>
                      </>
                    ) : (
                      <button className="w-full rounded-lg bg-zinc-900 px-3 py-1.5 text-sm font-medium text-white">
                        Mark posted
                      </button>
                    )}
                  </form>
                </div>
              </li>
            ))}
          </ul>
        </>
      )}

      {yesterdayUnposted.length > 0 && (
        <details className="mt-6 rounded-xl border border-amber-200 bg-amber-50 p-4">
          <summary className="cursor-pointer text-sm font-medium text-amber-900">
            {yesterdayUnposted.length} unposted from yesterday
          </summary>
          <ul className="mt-2 space-y-2">
            {yesterdayUnposted.map((version) => (
              <li key={version.id} className="flex items-center justify-between gap-2 text-sm">
                <span>“{version.hook.text}”</span>
                <form action={markVersionPosted}>
                  <input type="hidden" name="token" value={token} />
                  <input type="hidden" name="versionId" value={version.id} />
                  <button className="rounded-lg bg-zinc-900 px-2.5 py-1 text-xs text-white">
                    Posted
                  </button>
                </form>
              </li>
            ))}
          </ul>
        </details>
      )}
    </main>
  );
}
