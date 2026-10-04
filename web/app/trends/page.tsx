"use client";

import { useEffect, useState } from "react";
import { Header } from "@/components/Header";
import { TrendingUp, Flame, ArrowUpRight, ArrowDownRight } from "lucide-react";

interface TrendItem {
  word: string;
  currentFreq: number;
  prevFreq: number;
  growth: number;
  category: string;
}

export default function TrendsPage() {
  const [trends, setTrends] = useState<TrendItem[]>([
    { word: "digitalisasi", currentFreq: 120, prevFreq: 45, growth: 166.7, category: "Teknologi" },
    { word: "investasi", currentFreq: 198, prevFreq: 110, growth: 80.0, category: "Ekonomi" },
    { word: "infrastruktur", currentFreq: 85, prevFreq: 52, growth: 63.5, category: "Nasional" },
    { word: "subsidi", currentFreq: 94, prevFreq: 70, growth: 34.3, category: "Kebijakan" },
    { word: "ekspor", currentFreq: 64, prevFreq: 50, growth: 28.0, category: "Bisnis" },
  ]);

  return (
    <div className="flex-1 pb-12">
      <Header
        title="Trend Velocity"
        description="Analisis akselerasi dan pertumbuhan topik berita yang sedang meningkat drastis"
      />

      <div className="p-8 space-y-6 max-w-7xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="p-6 rounded-2xl bg-gradient-to-br from-rose-900/30 via-slate-900 to-slate-900 border border-rose-500/20">
            <div className="flex items-center gap-2 text-rose-400 text-xs font-semibold uppercase tracking-wider mb-2">
              <Flame className="w-4 h-4" /> Top Trending Topic
            </div>
            <div className="text-3xl font-black text-white">{trends[0]?.word}</div>
            <p className="text-sm text-emerald-400 font-semibold mt-2 flex items-center gap-1">
              <ArrowUpRight className="w-4 h-4" /> +{trends[0]?.growth}% pertumbuhan hari ini
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800">
            <span className="text-slate-400 text-xs font-semibold uppercase tracking-wider block mb-2">
              Rata-rata Pertumbuhan Topik
            </span>
            <div className="text-3xl font-black text-white">+54.2%</div>
            <p className="text-xs text-slate-400 mt-2">Dihitung dari perbandingan 24 jam terakhir</p>
          </div>

          <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800">
            <span className="text-slate-400 text-xs font-semibold uppercase tracking-wider block mb-2">
              Model Algoritma
            </span>
            <div className="text-3xl font-black text-rose-400">Velocity Ratio</div>
            <p className="text-xs text-slate-400 mt-2">Formula delta frekuensi / frekuensi dasar</p>
          </div>
        </div>

        {/* Trends Table */}
        <div className="rounded-2xl bg-slate-900/60 border border-slate-800 overflow-hidden">
          <div className="p-5 border-b border-slate-800 flex items-center justify-between">
            <h3 className="font-bold text-white text-base flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-rose-500" />
              <span>Peringkat Kenaikan Topik (Day-over-Day)</span>
            </h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="text-xs text-slate-400 uppercase bg-slate-800/40 border-b border-slate-800">
                <tr>
                  <th className="px-5 py-3.5">Kata Kunci</th>
                  <th className="px-5 py-3.5">Kategori</th>
                  <th className="px-5 py-3.5">Frekuensi Hari Ini</th>
                  <th className="px-5 py-3.5">Frekuensi Kemarin</th>
                  <th className="px-5 py-3.5 text-right">Tingkat Pertumbuhan</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {trends.map((item) => (
                  <tr key={item.word} className="hover:bg-slate-800/30 transition-colors">
                    <td className="px-5 py-4 font-bold text-white capitalize">{item.word}</td>
                    <td className="px-5 py-4 text-xs text-slate-400">{item.category}</td>
                    <td className="px-5 py-4 font-semibold text-rose-400">{item.currentFreq}</td>
                    <td className="px-5 py-4 text-slate-400">{item.prevFreq}</td>
                    <td className="px-5 py-4 text-right">
                      <span className="inline-flex items-center gap-1 text-emerald-400 font-bold bg-emerald-500/10 px-2.5 py-1 rounded-full text-xs">
                        <ArrowUpRight className="w-3.5 h-3.5" /> +{item.growth}%
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
