import Link from "next/link";
import type { ExampleStatus } from "@prisma/client";
import { requireAdmin } from "@/lib/auth";
import { prisma } from "@/lib/db";
import { addExampleLinks } from "@/actions/examples";
import { ExampleUploader } from "@/components/ExampleUploader";
import { AnalyzeButton } from "@/components/AnalyzeButton";

const STATUS_LABELS: Record<ExampleStatus, string> = {
  NEEDS_VIDEO: "Needs video",
  UPLOADED: "Uploaded",
  ANALYZED: "Analyzed",
  ANALYSIS_FAILED: "Analysis failed",
};

const STATUS_STYLES: Record<ExampleStatus, string> = {
  NEEDS_VIDEO: "bg-amber-100 text-amber-800",
  UPLOADED: "bg-blue-100 text-blue-800",
  ANALYZED: "bg-green-100 text-green-800",
  ANALYSIS_FAILED: "bg-red-100 text-red-800",
};

export default async function ExamplesPage({
  searchParams,
}: {
  searchParams: Promise<{ status?: string }>;
}) {
  await requireAdmin();
  const params = await searchParams;
  const statusFilter =
    params.status && params.status in STATUS_LABELS ? (params.status as ExampleStatus) : undefined;

  const examples = await prisma.exampleReel.findMany({
    where: statusFilter ? { status: statusFilter } : undefined,
    orderBy: { createdAt: "desc" },
    include: { hooks: { select: { id: true, text: true, status: true } } },
  });

  const useBlobClientUpload = Boolean(process.env.BLOB_READ_WRITE_TOKEN);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-semibold">Example reels</h1>
        <div className="flex gap-2 text-sm">
          <Link
            href="/admin/examples"
            className={`rounded-md px-2 py-1 ${!statusFilter ? "bg-zinc-900 text-white" : "bg-white border border-zinc-300"}`}
          >
            All
          </Link>
          {(Object.keys(STATUS_LABELS) as ExampleStatus[]).map((s) => (
            <Link
              key={s}
              href={`/admin/examples?status=${s}`}
              className={`rounded-md px-2 py-1 ${statusFilter === s ? "bg-zinc-900 text-white" : "bg-white border border-zinc-300"}`}
            >
              {STATUS_LABELS[s]}
            </Link>
          ))}
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <form
          action={addExampleLinks}
          className="rounded-xl border border-zinc-200 bg-white p-4 space-y-2"
        >
          <h2 className="text-sm font-medium">Add reel links</h2>
          <textarea
            name="links"
            rows={3}
            placeholder={"One Instagram reel link per line\nhttps://www.instagram.com/reel/…"}
            className="w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm focus:border-zinc-900 focus:outline-none"
          />
          <button className="rounded-lg bg-zinc-900 px-3 py-1.5 text-sm font-medium text-white hover:bg-zinc-700">
            Add stubs
          </button>
          <p className="text-xs text-zinc-500">
            Links become stubs — upload each reel&apos;s saved video to analyze it.
          </p>
        </form>
        <div className="rounded-xl border border-zinc-200 bg-white p-4 space-y-2">
          <h2 className="text-sm font-medium">Direct upload (no link)</h2>
          <ExampleUploader useBlobClientUpload={useBlobClientUpload} compact />
          <p className="text-xs text-zinc-500">
            For reels you saved without keeping the link.
          </p>
        </div>
      </div>

      {examples.length === 0 && (
        <p className="text-sm text-zinc-500">
          No examples yet. Import your sheet on the{" "}
          <Link href="/admin/import" className="underline">
            Import
          </Link>{" "}
          page or paste links above.
        </p>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {examples.map((example) => (
          <div key={example.id} className="rounded-xl border border-zinc-200 bg-white p-4">
            <div className="flex items-start justify-between gap-2">
              <span
                className={`rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_STYLES[example.status]}`}
              >
                {STATUS_LABELS[example.status]}
              </span>
              <Link
                href={`/admin/examples/${example.id}`}
                className="text-xs text-zinc-500 underline"
              >
                Open
              </Link>
            </div>

            {example.thumbUrl ? (
              <Link href={`/admin/examples/${example.id}`}>
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={example.thumbUrl}
                  alt=""
                  className="mt-3 aspect-[9/16] w-full rounded-lg object-cover"
                />
              </Link>
            ) : (
              <div className="mt-3 flex aspect-[9/16] w-full items-center justify-center rounded-lg bg-zinc-100 text-xs text-zinc-400">
                no video yet
              </div>
            )}

            <div className="mt-3 space-y-1">
              {example.hooks[0] && (
                <p className="line-clamp-2 text-sm font-medium">“{example.hooks[0].text}”</p>
              )}
              {example.tags.length > 0 && (
                <p className="text-xs text-zinc-500">{example.tags.join(" · ")}</p>
              )}
              {example.sourceUrl && (
                <a
                  href={example.sourceUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="block truncate text-xs text-zinc-400 underline"
                >
                  {example.sourceUrl.replace("https://www.instagram.com/", "ig: ")}
                </a>
              )}
            </div>

            <div className="mt-3 flex flex-wrap gap-2">
              {example.status === "NEEDS_VIDEO" && (
                <ExampleUploader
                  exampleId={example.id}
                  useBlobClientUpload={useBlobClientUpload}
                  compact
                />
              )}
              {(example.status === "UPLOADED" || example.status === "ANALYSIS_FAILED") && (
                <AnalyzeButton
                  exampleId={example.id}
                  label={example.status === "ANALYSIS_FAILED" ? "Retry analysis" : "Analyze"}
                />
              )}
            </div>
            {example.error && <p className="mt-2 text-xs text-red-600">{example.error}</p>}
          </div>
        ))}
      </div>
    </div>
  );
}
