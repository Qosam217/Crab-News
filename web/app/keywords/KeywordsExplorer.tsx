"use client";

import { useState, useMemo } from "react";
import { formatNumber } from "@/lib/utils";
import { DailyKeyword, Source } from "@/types/database";
import { Search, Hash, Globe, Filter } from "lucide-react";

interface KeywordsExplorerProps {
  initialKeywords: DailyKeyword[];
  sources: Source[];
}

export function KeywordsExplorer({ initialKeywords, sources }: KeywordsExplorerProps) {
  const [search, setSearch] = useState("");
  const [selectedSource, setSelectedSource] = useState<string>("global");

  const filtered = useMemo(() => {
    return initialKeywords.filter((k) => {
      // Filter by source
      if (selectedSource === "global") {
        if (k.source_id !== null) return false;
      } else if (selectedSource !== "all") {
        if (k.source_id !== selectedSource) return false;
      }

      // Filter by search query
      if (search.trim() !== "") {
        return k.word.toLowerCase().includes(search.toLowerCase());
      }

      return true;
    });
  }, [initialKeywords, selectedSource, search]);

  return (
    <div className="space-y-6">
      {/* Control Bar: Search & Source Selector */}
      <div className="flex flex-col md:flex-row gap-4 items-stretch md:items-center justify-between bg-slate-900/60 p-4 rounded-xl border border-slate-800">
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Cari kata kunci..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-slate-800/80 border border-slate-700/60 rounded-lg text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-rose-500 transition-colors"
          />
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 text-xs text-slate-400 bg-slate-800/80 px-3 py-2 rounded-lg border border-slate-700/60">
            <Filter className="w-3.5 h-3.5 text-slate-400" />
            <span>Sumber:</span>
            <select
              value={selectedSource}
              onChange={(e) => setSelectedSource(e.target.value)}
              aria-label="Filter berdasarkan sumber berita"
              className="bg-transparent text-slate-200 font-medium focus:outline-none cursor-pointer"
            >
              <option value="global" className="bg-slate-900 text-slate-200">
                🌐 Global (Semua Portal)
              </option>
              {sources.map((s) => (
                <option key={s.id} value={s.id} className="bg-slate-900 text-slate-200">
                  📰 {s.name}
                </option>
              ))}
              <option value="all" className="bg-slate-900 text-slate-200">
                Semua Record (Tanpa Filter)
              </option>
            </select>
          </div>

          <span className="text-xs text-slate-400 hidden sm:inline">
            Menampilkan <strong className="text-slate-200">{filtered.length}</strong> kata
          </span>
        </div>
      </div>

      {/* Keywords Grid */}
      {filtered.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {filtered.map((item, idx) => (
            <div
              key={item.id || idx}
              className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-rose-500/40 transition-colors flex items-center justify-between"
            >
              <div className="flex items-center gap-3 overflow-hidden">
                <div className="w-8 h-8 rounded-lg bg-rose-500/10 text-rose-400 flex items-center justify-center font-bold text-xs shrink-0">
                  <Hash className="w-4 h-4" />
                </div>
                <div className="truncate">
                  <h4 className="font-bold text-white capitalize truncate">{item.word}</h4>
                  <p className="text-[11px] text-slate-400 flex items-center gap-1.5 truncate">
                    <span>{item.article_count} artikel</span>
                    <span>•</span>
                    <span className="flex items-center gap-1">
                      {item.source_id ? (
                        item.sources?.name || "Source"
                      ) : (
                        <>
                          <Globe className="w-3 h-3 text-cyan-400 inline" />
                          <span className="text-cyan-400">Global</span>
                        </>
                      )}
                    </span>
                  </p>
                </div>
              </div>
              <div className="text-right shrink-0 ml-2">
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
            : "Tidak ada kata kunci yang sesuai dengan filter atau pencarian."}
        </div>
      )}
    </div>
  );
}
