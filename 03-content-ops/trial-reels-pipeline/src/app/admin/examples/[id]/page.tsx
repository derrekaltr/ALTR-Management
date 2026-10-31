import Link from "next/link";
import { notFound } from "next/navigation";
import { requireAdmin } from "@/lib/auth";
import { prisma } from "@/lib/db";
import { deleteExample, updateExample } from "@/actions/examples";
import { AnalyzeButton } from "@/components/AnalyzeButton";
import { ExampleUploader } from "@/components/ExampleUploader";

export default async function ExampleDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  await requireAdmin();
  const { id } = await params;
  const example = await prisma.exampleReel.findUnique({
    where: { id },
    include: { hooks: { orderBy: { createdAt: "desc" } } },
  });
  if (!example) notFound();

  const useBlobClientUpload = Boolean(process.env.BLOB_READ_WRITE_TOKEN);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Example reel</h1>
        <Link href="/admin/examples" className="text-sm text-zinc-500 underline">
          ← All examples
        </Link>
      </div>

      <div className="grid gap-6 lg:grid-cols-[320px_1fr]">
        <div className="space-y-3">
          {example.videoUrl ? (
            <video
              src={example.videoUrl}
              controls
              playsInline
              className="aspect-[9/16] w-full rounded-xl bg-black object-contain"
            />
          ) : (
            <div className="flex aspect-[9/16] items-center justify-center rounded-xl bg-zinc-100 text-sm text-zinc-400">
              No video uploaded yet
            </div>
          )}
          <ExampleUploader
            exampleId={example.id}
            useBlobClientUpload={useBlobClientUpload}
            compact
          />
          {example.frameUrls.length > 0 && (
            <>
              <AnalyzeButton exampleId={example.id} />
              {example.error && <p className="text-sm text-red-600">{example.error}</p>}
            </>
          )}
          {example.sourceUrl && (
            <a
              href={example.sourceUrl}
              target="_blank"
              rel="noreferrer"
              className="block truncate text-xs text-zinc-500 underline"
            >
              {example.sourceUrl}
            </a>
          )}
        </div>

        <div className="space-y-6">
          <section className="rounded-xl border border-zinc-200 bg-white p-4">
            <h2 className="mb-3 text-sm font-medium text-zinc-500">Extracted hooks</h2>
            {example.hooks.length === 0 ? (
              <p className="text-sm text-zinc-500">
                None yet — upload the video and run analysis.
              </p>
            ) : (
              <ul className="space-y-2">
                {example.hooks.map((hook) => (
                  <li key={hook.id} className="flex items-center justify-between gap-2 text-sm">
                    <span>“{hook.text}”</span>
                    <span className="shrink-0 rounded-full bg-zinc-100 px-2 py-0.5 text-xs text-zinc-600">
                      {hook.status.toLowerCase().replace("_", " ")}
                    </span>
                  </li>
                ))}
              </ul>
            )}
            {example.hooks.some((h) => h.status === "PENDING_REVIEW") && (
              <Link href="/admin/review" className="mt-2 inline-block text-xs underline">
                Review pending hooks →
              </Link>
            )}
          </section>

          <form
            action={updateExample}
            className="space-y-3 rounded-xl border border-zinc-200 bg-white p-4"
          >
            <input type="hidden" name="exampleId" value={example.id} />
            <h2 className="text-sm font-medium text-zinc-500">Analysis & notes</h2>
            <label className="block text-sm">
              <span className="text-xs text-zinc-500">Background description</span>
              <textarea
                name="backgroundDescription"
                rows={2}
                defaultValue={example.backgroundDescription ?? ""}
                className="mt-1 w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm"
              />
            </label>
            <label className="block text-sm">
              <span className="text-xs text-zinc-500">Why it works</span>
              <textarea
                name="whyItWorks"
                rows={2}
                defaultValue={example.whyItWorks ?? ""}
                className="mt-1 w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm"
              />
            </label>
            <div className="grid gap-3 sm:grid-cols-2">
              <label className="block text-sm">
                <span className="text-xs text-zinc-500">Tags (comma-separated)</span>
                <input
                  name="tags"
                  defaultValue={example.tags.join(", ")}
                  className="mt-1 w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm"
                />
              </label>
              <label className="block text-sm">
                <span className="text-xs text-zinc-500">Source handle</span>
                <input
                  name="sourceHandle"
                  defaultValue={example.sourceHandle ?? ""}
                  placeholder="@creator"
                  className="mt-1 w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm"
                />
              </label>
            </div>
            <label className="block text-sm">
              <span className="text-xs text-zinc-500">Agency notes (fed to the AI on re-analysis)</span>
              <textarea
                name="notes"
                rows={2}
                defaultValue={example.notes ?? ""}
                className="mt-1 w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm"
              />
            </label>
            <button className="rounded-lg bg-zinc-900 px-3 py-1.5 text-sm font-medium text-white hover:bg-zinc-700">
              Save
            </button>
          </form>

          <form action={deleteExample}>
            <input type="hidden" name="exampleId" value={example.id} />
            <button className="text-sm text-red-600 underline">Delete example</button>
          </form>
        </div>
      </div>
    </div>
  );
}
