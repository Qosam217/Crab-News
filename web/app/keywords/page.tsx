"use client";

import { useEffect, useState } from "react";
import { Header } from "@/components/Header";
import { supabase } from "@/lib/supabase";
import { formatNumber } from "@/lib/utils";
import { DailyKeyword } from "@/types/database";
import { Search, Hash } from "lucide-react";

export default function KeywordsPage() {
  const [keywords, setKeywords] = useState<DailyKeyword[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  async function loadKeywords() {
    setLoading(true);
    try {
      const { data } = await supabase
        .from("daily_keywords")
        .select("*, sources(name)")
        .order("frequency", { ascending: false })
        .limit(100);

      if (data && data.length > 0) {
        setKeywords(data);
      } else {
        // Fallback sample keywords for initial display
        setKeywords([
          { id: 1, date: "2026-10-04", source_id: null, word: "ekonomi", frequency: 184, article_count: 32, created_at: "" },
          { id: 2, date: "2026-10-04", source_id: null, word: "pemerintah", frequency: 156, article_count: 28, created_at: "" },
          { id: 3, date: "2026-10-04", source_id: null, word: "presiden", frequency: 142, article_count: 25, created_at: "" },
          { id: 4, date: "2026-10-04", source_id: null, word: "digital", frequency: 98, article_count: 18, created_at: "" },
          { id: 5, date: "2026-10-04", source_id: null, word: "investasi", frequency: 89, article_count: 16, created_at: "" },
          { id: 6, date: "2026-10-04", source_id: null, word: "teknologi", frequency: 75, article_count: 14, created_at: "" },
          { id: 7, date: "2026-10-04", source_id: null, word: "industri", frequency: 68, article_count: 12, created_at: "" },
          { id: 8, date: "2026-10-04", source_id: null, word: "pasar", frequency: 62, article_count: 11, created_at: "" },
        ]);
      }
    } catch (e) {
      console.warn("Failed to load keywords:", e);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadKeywords();
  }, []);

  const filtered = keywords.filter((k) =>
    k.word.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="flex-1 pb-12">
      <Header
        title="Keyword Intelligence"
        description="Analisis frekuensi dan distribusi kata kunci Bahasa Indonesia hasil ekstraksi teks"
        onRefresh={loadKeywords}
        isLoading={loading}
      />

      <div className="p-8 space-y-6 max-w-7xl mx-auto">
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
          <span className="text-xs text-slate-400">Menampilkan {filtered.length} kata kunci</span>
        </div>

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
      </div>
    </div>
  );
}
