"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Newspaper,
  KeyRound,
  TrendingUp,
  Globe2,
  Activity,
  Github,
} from "lucide-react";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { href: "/", label: "Overview", icon: LayoutDashboard },
  { href: "/articles", label: "Articles", icon: Newspaper },
  { href: "/keywords", label: "Keywords", icon: KeyRound },
  { href: "/trends", label: "Trends", icon: TrendingUp },
  { href: "/sources", label: "Sources", icon: Globe2 },
  { href: "/crawl-runs", label: "Crawl Runs", icon: Activity },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col justify-between shrink-0 min-h-screen text-slate-300">
      <div>
        {/* Brand Header */}
        <div className="h-16 flex items-center px-6 border-b border-slate-800 gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-rose-600 to-amber-500 flex items-center justify-center text-white font-bold shadow-lg shadow-rose-900/30">
            🦀
          </div>
          <div>
            <h1 className="font-bold text-white text-lg tracking-tight">Crab News</h1>
            <p className="text-xs text-slate-400">News & Trends Pipeline</p>
          </div>
        </div>

        {/* Navigation Menu */}
        <nav className="p-4 space-y-1">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive =
              item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);

            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-colors",
                  isActive
                    ? "bg-rose-600/15 text-rose-400 border border-rose-500/30 font-semibold"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/60"
                )}
              >
                <Icon className={cn("w-4 h-4", isActive ? "text-rose-400" : "text-slate-400")} />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Footer Info */}
      <div className="p-4 border-t border-slate-800 text-xs text-slate-500 space-y-2">
        <div className="flex items-center justify-between">
          <span>Engine v0.1.0</span>
          <span className="inline-flex items-center gap-1 text-emerald-400 font-medium">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
            Online
          </span>
        </div>
        <Link
          href="https://github.com/Qosam217/Crab-News"
          target="_blank"
          className="flex items-center gap-2 text-slate-400 hover:text-slate-300 transition-colors"
        >
          <Github className="w-3.5 h-3.5" />
          <span>GitHub Repository</span>
        </Link>
      </div>
    </aside>
  );
}
