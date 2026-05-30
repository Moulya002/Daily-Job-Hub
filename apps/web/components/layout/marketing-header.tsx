import Link from "next/link";

import { AuthActions } from "@/components/common/auth-actions";

const links = [
  { href: "/jobs", label: "Jobs" },
  { href: "/search", label: "AI Search" },
  { href: "/dashboard", label: "Dashboard" }
] as const;

export async function MarketingHeader() {
  return (
    <header className="border-b border-slate-800">
      <nav className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 md:px-6">
        <div className="flex items-center gap-6">
          <Link href="/" className="font-semibold">
            Daily Job Hub
          </Link>
          <div className="hidden items-center gap-4 md:flex">
            {links.map((link) => (
              <Link key={link.href} href={link.href} className="text-sm text-slate-300 hover:text-white">
                {link.label}
              </Link>
            ))}
          </div>
        </div>
        <AuthActions />
      </nav>
    </header>
  );
}
