import { Header } from "@/components/Header";
import { supabase } from "@/lib/supabase";
import { TrendingUp, Flame, ArrowUpRight, ArrowDownRight } from "lucide-react";

export const dynamic = "force-dynamic";

interface TrendItem {
  word: string;
  currentFreq: number;
  prevFreq: number;
  growth: number;
}

export default async function TrendsPage() {
  // 1. Fetch latest distinct dates from daily_keywords (global aggregation)
  const { data: dateRows } = await supabase
    .from("daily_keywords")
    .select("date")
    .is("source_id", null)
    .order("date", { ascending: false })
    .limit(200);

  const uniqueDates = Array.from(new Set((dateRows || []).map((d) => d.date)));
  const latestDate = uniqueDates[0];
  const prevDate = uniqueDates[1];

  let trends: TrendItem[] = [];
  let avgGrowth = 0;

  if (latestDate && prevDate) {
    const { data: latestData } = await supabase
      .from("daily_keywords")
      .select("word, frequency")
      .eq("date", latestDate)
      .is("source_id", null);

    const { data: prevData } = await supabase
      .from("daily_keywords")
      .select("word, frequency")
      .eq("date", prevDate)
      .is("source_id", null);

    const prevMap = new Map<string, number>();
    (prevData || []).forEach((row) => {
      prevMap.set(row.word, (prevMap.get(row.word) || 0) + row.frequency);
    });

    const currMap = new Map<string, number>();
    (latestData || []).forEach((row) => {
      currMap.set(row.word, (currMap.get(row.word) || 0) + row.frequency);
    });

    currMap.forEach((currentFreq, word) => {
      const prevFreq = prevMap.get(word) || 0;
      const growth =
        prevFreq > 0
          ? Math.round(((currentFreq - prevFreq) / prevFreq) * 1000) / 10
          : currentFreq > 5
          ? 100
          : 0;

      trends.push({
        word,
        currentFreq,
        prevFreq,
        growth,
      });
    });

    // Sort by growth desc, then frequency desc
    trends.sort((a, b) => b.growth - a.growth || b.currentFreq - a.currentFreq);
    trends = trends.slice(0, 20);

    if (trends.length > 0) {
      const sumGrowth = trends.reduce((acc, t) => acc + t.growth, 0);
      avgGrowth = Math.round((sumGrowth / trends.length) * 10) / 10;
    }
  } else if (latestDate) {
    // Only 1 date available
    const { data: latestData } = await supabase
      .from("daily_keywords")
      .select("word, frequency")
      .eq("date", latestDate)
      .is("source_id", null)
      .order("frequency", { ascending: false })
      .limit(20);

    trends = (latestData || []).map((row) => ({
      word: row.word,
      currentFreq: row.frequency,
      prevFreq: 0,
      growth: 0,
    }));
  }

  const topTrend = trends[0];

  return (
    <div className="flex-1 pb-12">
      <Header
        title="Trend Velocity"
        description="Analisis akselerasi dan pertumbuhan topik berita yang sedang meningkat drastis"
      />

      <div className="p-8 space-y-6 max-w-7xl mx-auto">
        {trends.length > 0 ? (
          <>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="p-6 rounded-2xl bg-gradient-to-br from-rose-900/30 via-slate-900 to-slate-900 border border-rose-500/20">
                <div className="flex items-center gap-2 text-rose-400 text-xs font-semibold uppercase tracking-wider mb-2">
                  <Flame className="w-4 h-4" /> Top Trending Topic
                </div>
                <div className="text-3xl font-black text-white capitalize">
                  {topTrend?.word || "-"}
                </div>
                <p className="text-sm text-emerald-400 font-semibold mt-2 flex items-center gap-1">
                  <ArrowUpRight className="w-4 h-4" /> +{topTrend?.growth}% pertumbuhan
                </p>
              </div>

              <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800">
                <span className="text-slate-400 text-xs font-semibold uppercase tracking-wider block mb-2">
                  Rata-rata Pertumbuhan Topik
                </span>
                <div className="text-3xl font-black text-white">
                  {avgGrowth >= 0 ? `+${avgGrowth}%` : `${avgGrowth}%`}
                </div>
                <p className="text-xs text-slate-400 mt-2">
                  {prevDate
                    ? `Perbandingan ${latestDate} vs ${prevDate}`
                    : "Data 1 tanggal pengamatan"}
                </p>
              </div>

              <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800">
                <span className="text-slate-400 text-xs font-semibold uppercase tracking-wider block mb-2">
                  Model Algoritma
                </span>
                <div className="text-3xl font-black text-rose-400">Velocity Ratio</div>
                <p className="text-xs text-slate-400 mt-2">
                  Formula delta frekuensi / frekuensi dasar
                </p>
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
                      <th className="px-5 py-3.5">Frekuensi Hari Ini</th>
                      <th className="px-5 py-3.5">Frekuensi Sebelumnya</th>
                      <th className="px-5 py-3.5 text-right">Tingkat Pertumbuhan</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {trends.map((item) => (
                      <tr key={item.word} className="hover:bg-slate-800/30 transition-colors">
                        <td className="px-5 py-4 font-bold text-white capitalize">
                          {item.word}
                        </td>
                        <td className="px-5 py-4 font-semibold text-rose-400">
                          {item.currentFreq}
                        </td>
                        <td className="px-5 py-4 text-slate-400">{item.prevFreq}</td>
                        <td className="px-5 py-4 text-right">
                          <span
                            className={`inline-flex items-center gap-1 font-bold px-2.5 py-1 rounded-full text-xs ${
                              item.growth >= 0
                                ? "text-emerald-400 bg-emerald-500/10"
                                : "text-rose-400 bg-rose-500/10"
                            }`}
                          >
                            {item.growth >= 0 ? (
                              <ArrowUpRight className="w-3.5 h-3.5" />
                            ) : (
                              <ArrowDownRight className="w-3.5 h-3.5" />
                            )}
                            {item.growth >= 0 ? `+${item.growth}%` : `${item.growth}%`}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        ) : (
          <div className="p-12 text-center rounded-2xl bg-slate-900/60 border border-slate-800 text-slate-400">
            Belum ada data daily_keywords di database untuk analisis tren.
          </div>
        )}
      </div>
    </div>
  );
}
