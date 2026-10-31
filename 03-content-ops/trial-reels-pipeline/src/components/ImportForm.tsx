"use client";

import { useState, useTransition } from "react";
import { importCsv, type ImportReport } from "@/actions/importCsv";

export function ImportForm() {
  const [report, setReport] = useState<ImportReport | null>(null);
  const [pending, startTransition] = useTransition();

  return (
    <div className="space-y-4">
      <form
        className="space-y-3 rounded-xl border border-zinc-200 bg-white p-4"
        onSubmit={(e) => {
          e.preventDefault();
          const form = new FormData(e.currentTarget);
          startTransition(async () => {
            setReport(await importCsv(form));
          });
        }}
      >
        <label className="block text-sm">
          <span className="text-xs text-zinc-500">CSV file</span>
          <input
            type="file"
            name="file"
            accept=".csv,text/csv"
            required
            className="mt-1 block w-full text-sm"
          />
        </label>
        <label className="flex items-center gap-2 text-sm">
          <input type="checkbox" name="markProven" defaultChecked />
          Mark imported hooks as proven (hook-table imports only)
        </label>
        <button
          disabled={pending}
          className="rounded-lg bg-zinc-900 px-3 py-1.5 text-sm font-medium text-white hover:bg-zinc-700 disabled:opacity-50"
        >
          {pending ? "Importing…" : "Import"}
        </button>
      </form>

      {report && (
        <div className="rounded-xl border border-zinc-200 bg-white p-4 text-sm">
          {report.error ? (
            <p className="text-red-600">{report.error}</p>
          ) : (
            <>
              <p className="font-medium">
                {report.mode === "links" ? "Reel-link import" : "Hook import"} finished:
              </p>
              <ul className="mt-2 list-inside list-disc text-zinc-600">
                <li>
                  {report.imported} {report.mode === "links" ? "example stubs created" : "hooks imported"}
                </li>
                <li>{report.duplicates} duplicates skipped</li>
                <li>{report.invalid.length} invalid rows</li>
              </ul>
              {report.invalid.length > 0 && (
                <details className="mt-2">
                  <summary className="cursor-pointer text-xs text-zinc-500">
                    Show invalid rows
                  </summary>
                  <ul className="mt-1 space-y-1 text-xs text-zinc-500">
                    {report.invalid.map((row) => (
                      <li key={row.row}>
                        Row {row.row}: “{row.value || "(empty)"}” — {row.reason}
                      </li>
                    ))}
                  </ul>
                </details>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
}
