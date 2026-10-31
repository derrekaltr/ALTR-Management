import Link from "next/link";
import { requireAdmin } from "@/lib/auth";
import { logout } from "@/actions/auth";
import { prisma } from "@/lib/db";

const NAV = [
  { href: "/admin", label: "Dashboard" },
  { href: "/admin/examples", label: "Examples" },
  { href: "/admin/hooks", label: "Hooks" },
  { href: "/admin/generate", label: "Generate" },
  { href: "/admin/review", label: "Review" },
  { href: "/admin/creators", label: "Creators" },
  { href: "/admin/import", label: "Import" },
];

export default async function AdminLayout({ children }: { children: React.ReactNode }) {
  await requireAdmin();
  const pendingCount = await prisma.hook.count({ where: { status: "PENDING_REVIEW" } });

  return (
    <div className="min-h-screen">
      <header className="border-b border-zinc-200 bg-white">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center gap-1 px-4 py-3">
          <span className="mr-4 text-sm font-bold tracking-tight">🎬 Trial Reels</span>
          <nav className="flex flex-1 flex-wrap items-center gap-1 text-sm">
            {NAV.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="rounded-md px-2.5 py-1.5 text-zinc-600 hover:bg-zinc-100 hover:text-zinc-900"
              >
                {item.label}
                {item.label === "Review" && pendingCount > 0 && (
                  <span className="ml-1.5 rounded-full bg-amber-100 px-1.5 py-0.5 text-xs font-semibold text-amber-800">
                    {pendingCount}
                  </span>
                )}
              </Link>
            ))}
          </nav>
          <form action={logout}>
            <button className="rounded-md px-2.5 py-1.5 text-sm text-zinc-500 hover:bg-zinc-100">
              Log out
            </button>
          </form>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-4 py-6">{children}</main>
    </div>
  );
}
