"use client";

import { RefreshCw, Search } from "lucide-react";

interface HeaderProps {
  title: string;
  description?: string;
  onRefresh?: () => void;
  isLoading?: boolean;
}

export function Header({ title, description, onRefresh, isLoading }: HeaderProps) {
  return (
    <header className="h-16 border-b border-slate-800 px-8 flex items-center justify-between bg-slate-900/50 backdrop-blur-md sticky top-0 z-10">
      <div>
        <h2 className="text-xl font-bold text-white tracking-tight">{title}</h2>
        {description && <p className="text-xs text-slate-400">{description}</p>}
      </div>

      <div className="flex items-center gap-3">
        {onRefresh && (
          <button
            onClick={onRefresh}
            disabled={isLoading}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium border border-slate-700/60 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? "animate-spin text-rose-400" : ""}`} />
            <span>Refresh</span>
          </button>
        )}
      </div>
    </header>
  );
}
