import { requireAdmin } from "@/lib/auth";
import { ImportForm } from "@/components/ImportForm";

export default async function ImportPage() {
  await requireAdmin();
  return (
    <div className="max-w-2xl space-y-6">
      <h1 className="text-2xl font-semibold">Import CSV</h1>
      <p className="text-sm text-zinc-600">
        Two formats are detected automatically:
      </p>
      <ul className="list-inside list-disc text-sm text-zinc-600">
        <li>
          <strong>Reel-link list</strong> (your current sheet): one column of Instagram links —
          each becomes an example stub waiting for its video upload. Junk rows and share tokens
          (<code>?stkn=…</code>) are cleaned up automatically.
        </li>
        <li>
          <strong>Hook table</strong>: columns like <code>text</code> (or <code>caption</code>/
          <code>hook</code>), <code>category</code>, <code>tags</code>, <code>notes</code> — rows
          become library hooks.
        </li>
      </ul>
      <ImportForm />
    </div>
  );
}
