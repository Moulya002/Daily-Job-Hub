import Link from "next/link";
import { BriefcaseBusiness, FileText, LayoutDashboard, Search, Settings, Sparkles } from "lucide-react";

import { auth } from "@/auth";
import { Avatar } from "@/components/ui/avatar";
import { Separator } from "@/components/ui/separator";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/jobs", label: "Jobs", icon: BriefcaseBusiness },
  { href: "/search", label: "AI Search", icon: Search },
  { href: "/saved-jobs", label: "Saved", icon: Sparkles },
  { href: "/resume-analysis", label: "Resume", icon: FileText },
  { href: "/settings", label: "Settings", icon: Settings }
] as const;

export async function AppShell({ children }: { children: React.ReactNode }) {
  const session = await auth();
  const name = session?.user?.name ?? "User";
  const email = session?.user?.email ?? "unknown@user.com";

  return (
    <div className="grid min-h-screen md:grid-cols-[240px_1fr]">
      <aside className="border-r border-slate-800 bg-slate-950 p-4">
        <Link href="/dashboard" className="mb-6 inline-flex text-lg font-semibold">
          Daily Job Hub
        </Link>
        <nav className="space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                className="flex items-center gap-2 rounded-md px-3 py-2 text-sm text-slate-300 hover:bg-slate-900 hover:text-white"
              >
                <Icon className="h-4 w-4" />
                {item.label}
              </Link>
            );
          })}
        </nav>
        <Separator className="my-4" />
        <div className="flex items-center gap-3">
          <Avatar name={name} image={session?.user?.image} />
          <div className="min-w-0">
            <p className="truncate text-sm font-medium">{name}</p>
            <p className="truncate text-xs text-slate-500">{email}</p>
          </div>
        </div>
      </aside>
      <main className="p-4 md:p-8">{children}</main>
    </div>
  );
}
