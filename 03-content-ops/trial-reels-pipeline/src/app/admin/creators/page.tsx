import Link from "next/link";
import { requireAdmin } from "@/lib/auth";
import { prisma } from "@/lib/db";
import { createCreator, rotateToken, setCreatorActive } from "@/actions/creators";
import { CopyLinkButton } from "@/components/CopyLinkButton";

export default async function CreatorsPage() {
  await requireAdmin();
  const creators = await prisma.creator.findMany({
    orderBy: [{ active: "desc" }, { name: "asc" }],
    include: { _count: { select: { dayPlans: true } } },
  });

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Creators</h1>

      <form
        action={createCreator}
        className="flex flex-wrap items-end gap-3 rounded-xl border border-zinc-200 bg-white p-4"
      >
        <label className="text-sm">
          <span className="block text-xs text-zinc-500">Name</span>
          <input
            name="name"
            required
            className="mt-1 rounded-lg border border-zinc-300 px-3 py-1.5 text-sm"
          />
        </label>
        <label className="text-sm">
          <span className="block text-xs text-zinc-500">IG handle</span>
          <input
            name="handle"
            placeholder="@handle"
            className="mt-1 rounded-lg border border-zinc-300 px-3 py-1.5 text-sm"
          />
        </label>
        <label className="text-sm">
          <span className="block text-xs text-zinc-500">Timezone</span>
          <input
            name="timezone"
            defaultValue="America/New_York"
            className="mt-1 rounded-lg border border-zinc-300 px-3 py-1.5 text-sm"
          />
        </label>
        <button className="rounded-lg bg-zinc-900 px-3 py-1.5 text-sm font-medium text-white hover:bg-zinc-700">
          Add creator
        </button>
      </form>

      <div className="overflow-x-auto rounded-xl border border-zinc-200 bg-white">
        <table className="w-full text-sm">
          <thead className="border-b border-zinc-200 text-left text-xs text-zinc-500">
            <tr>
              <th className="p-3">Name</th>
              <th className="p-3">Handle</th>
              <th className="p-3">Timezone</th>
              <th className="p-3">Plans</th>
              <th className="p-3">Access</th>
              <th className="p-3"></th>
            </tr>
          </thead>
          <tbody>
            {creators.map((creator) => (
              <tr key={creator.id} className="border-b border-zinc-100 last:border-0">
                <td className="p-3">
                  <Link href={`/admin/creators/${creator.id}`} className="font-medium underline">
                    {creator.name}
                  </Link>
                  {!creator.active && (
                    <span className="ml-2 rounded-full bg-zinc-100 px-2 py-0.5 text-xs text-zinc-500">
                      deactivated
                    </span>
                  )}
                </td>
                <td className="p-3 text-zinc-500">{creator.handle ?? "—"}</td>
                <td className="p-3 text-zinc-500">{creator.timezone}</td>
                <td className="p-3 text-zinc-500">{creator._count.dayPlans}</td>
                <td className="p-3">
                  <div className="flex flex-wrap gap-2">
                    <CopyLinkButton token={creator.token} />
                    <form action={rotateToken}>
                      <input type="hidden" name="creatorId" value={creator.id} />
                      <button
                        className="rounded-lg border border-zinc-300 bg-white px-2.5 py-1 text-xs hover:border-zinc-500"
                        title="Old link stops working immediately"
                      >
                        Rotate link
                      </button>
                    </form>
                  </div>
                </td>
                <td className="p-3">
                  <form action={setCreatorActive}>
                    <input type="hidden" name="creatorId" value={creator.id} />
                    <input type="hidden" name="active" value={creator.active ? "false" : "true"} />
                    <button className="text-xs text-zinc-500 underline">
                      {creator.active ? "Deactivate" : "Reactivate"}
                    </button>
                  </form>
                </td>
              </tr>
            ))}
            {creators.length === 0 && (
              <tr>
                <td colSpan={6} className="p-6 text-center text-zinc-500">
                  No creators yet — add one above.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
