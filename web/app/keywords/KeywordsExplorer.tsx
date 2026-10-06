"use client";

import { useState } from "react";
import { formatNumber } from "@/lib/utils";
import { DailyKeyword } from "@/types/database";
import { Search, Hash } from "lucide-react";

interface KeywordsExplorerProps {
  initialKeywords: DailyKeyword[];
}

export function KeywordsExplorer({ initialKeywords }: KeywordsExplorerProps) {
  const [search, setSearch] = useState("");

  const filtered = initialKeywords.filter((k) =>
    k.word.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between bg-slate-900/60 p-4 rounded-xl border border-slate-800">
        <div className="relative w-full md:w-96">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Cari kata kunci..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-slate-800/80 border border-slate-700/60 rounded-lg text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-rose-500 transition-colors"
          />
        </div>
        <span className="text-xs text-slate-400">
          Menampilkan {filtered.length} dari {initialKeywords.length} kata kunci
        </span>
      </div>

      {filtered.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {filtered.map((item, idx) => (
            <div
              key={item.id || idx}
              className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-rose-500/40 transition-colors flex items-center justify-between"
            >
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-rose-500/10 text-rose-400 flex items-center justify-center font-bold text-xs">
                  <Hash className="w-4 h-4" />
                </div>
                <div>
                  <h4 className="font-bold text-white capitalize">{item.word}</h4>
                  <p className="text-[11px] text-slate-400">
                    {item.article_count} artikel • {item.sources?.name || "Global"}
                  </p>
                </div>
              </div>
              <div className="text-right">
                <span className="text-lg font-bold text-rose-400">
                  {formatNumber(item.frequency)}
                </span>
                <span className="block text-[10px] text-slate-500">kemunculan</span>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="p-12 text-center rounded-2xl bg-slate-900/60 border border-slate-800 text-slate-400 text-sm">
          {initialKeywords.length === 0
            ? "Belum ada data daily_keywords di database."
            : "Tidak ada kata kunci yang sesuai dengan pencarian."}
        </div>
      )}
    </div>
  );
}
