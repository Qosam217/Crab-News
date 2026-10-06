import { Header } from "@/components/Header";
import { StatsCard } from "@/components/StatsCard";
import { TrendChart } from "@/components/TrendChart";
import { KeywordsBarChart } from "@/components/KeywordsBarChart";
import { StatusBadge } from "@/components/StatusBadge";
import { supabase } from "@/lib/supabase";
import { formatDate, formatNumber } from "@/lib/utils";
import {
  Newspaper,
  KeyRound,
  Globe2,
  Activity,
  Flame,
  ArrowRight,
} from "lucide-react";
import Link from "next/link";

export const dynamic = "force-dynamic";

export default async function OverviewPage() {
  // 1. Fetch total articles count
  const { count: totalArticles } = await supabase
    .from("articles")
    .select("*", { count: "exact", head: true });

  // 2. Fetch active sources count
  const { count: activeSourcesCount } = await supabase
    .from("sources")
    .select("*", { count: "exact", head: true })
    .eq("is_active", true);

  // 3. Fetch top keywords overall
  const { data: topKeywordsData } = await supabase
    .from("daily_keywords")
    .select("*")
    .order("frequency", { ascending: false })
    .limit(10);
  const topKeywords = topKeywordsData || [];
  const totalKeywords = topKeywords.reduce((acc, k) => acc + (k.frequency || 0), 0);

  // 4. Fetch recent articles
  const { data: articlesData } = await supabase
    .from("articles")
    .select("*, sources(name, slug)")
    .order("crawled_at", { ascending: false })
    .limit(6);
  const recentArticles = articlesData || [];

  // 5. Fetch recent crawl runs
  const { data: runsData } = await supabase
    .from("crawl_runs")
    .select("*, sources(name)")
    .order("started_at", { ascending: false })
    .limit(4);
  const recentRuns = runsData || [];

  // 6. Fetch trend history from daily_keywords
  const { data: trendData } = await supabase
    .from("daily_keywords")
    .select("date, frequency, article_count")
    .order("date", { ascending: true })
    .limit(50);

  const dateMap = new Map<string, { date: string; articles: number; words: number }>();
  (trendData || []).forEach((item) => {
    const d = item.date;
    const existing = dateMap.get(d) || { date: d, articles: 0, words: 0 };
    existing.words += item.frequency || 0;
    existing.articles = Math.max(existing.articles, item.article_count || 0);
    dateMap.set(d, existing);
  });
  const trendHistory = Array.from(dateMap.values()).slice(-7);

  const latestRunStatus = recentRuns[0]?.status || "operational";

  return (
    <div className="flex-1 pb-12">
      <Header
        title="Overview Intelligence"
        description="Ringkasan pemrosesan berita terkini dan dinamika topik media Indonesia"
      />

      <div className="p-8 space-y-8 max-w-7xl mx-auto">
        {/* Metric Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
          <StatsCard
            title="Total Articles"
            value={formatNumber(totalArticles ?? 0)}
            subtitle="Tersimpan di Supabase"
            icon={Newspaper}
            color="rose"
          />
          <StatsCard
            title="Word Occurrences"
            value={formatNumber(totalKeywords)}
            subtitle="Total frekuensi kata teratas"
            icon={KeyRound}
            color="amber"
          />
          <StatsCard
            title="Active Sources"
            value={activeSourcesCount ?? 0}
            subtitle="Portal berita aktif"
            icon={Globe2}
            color="emerald"
          />
          <StatsCard
            title="Crawler Status"
            value={latestRunStatus === "success" ? "Operational" : latestRunStatus}
            subtitle="GitHub Actions & Audit Log"
            icon={Activity}
            color="blue"
          />
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Article Volume Trend */}
          <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-sm">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <span>Volume Berita Harian</span>
                </h3>
                <p className="text-xs text-slate-400">Tren artikel terkumpul per hari</p>
              </div>
            </div>
            <TrendChart data={trendHistory} />
          </div>

          {/* Top Keywords Frequency */}
          <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-sm">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <Flame className="w-4 h-4 text-rose-500" />
                  <span>Top Kata Kunci Populer</span>
                </h3>
                <p className="text-xs text-slate-400">Frekuensi kata kunci dominan</p>
              </div>
              <Link
                href="/keywords"
                className="text-xs text-rose-400 hover:text-rose-300 flex items-center gap-1 font-medium"
              >
                Lihat Semua <ArrowRight className="w-3 h-3" />
              </Link>
            </div>
            <KeywordsBarChart
              data={topKeywords.map((k) => ({ word: k.word, frequency: k.frequency }))}
            />
          </div>
        </div>

        {/* Tables Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Recent Articles */}
          <div className="lg:col-span-2 p-6 rounded-2xl bg-slate-900/60 border border-slate-800">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-base font-bold text-white">Artikel Terbaru</h3>
                <p className="text-xs text-slate-400">Artikel yang baru saja selesai di-crawl</p>
              </div>
              <Link
                href="/articles"
                className="text-xs text-rose-400 hover:text-rose-300 flex items-center gap-1 font-medium"
              >
                Explorer <ArrowRight className="w-3 h-3" />
              </Link>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-300">
                <thead className="text-xs text-slate-400 uppercase bg-slate-800/40 border-b border-slate-800">
                  <tr>
                    <th className="px-4 py-3">Judul Berita</th>
                    <th className="px-4 py-3">Sumber</th>
                    <th className="px-4 py-3">Status</th>
                    <th className="px-4 py-3 text-right">Waktu</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {recentArticles.length > 0 ? (
                    recentArticles.map((art) => (
                      <tr key={art.id} className="hover:bg-slate-800/30 transition-colors">
                        <td className="px-4 py-3 font-medium text-white max-w-md truncate">
                          <a
                            href={art.url}
                            target="_blank"
                            rel="noreferrer"
                            className="hover:text-rose-400 transition-colors"
                          >
                            {art.title}
                          </a>
                        </td>
                        <td className="px-4 py-3 text-xs text-slate-400">
                          {art.sources?.name || "RSS Feed"}
                        </td>
                        <td className="px-4 py-3">
                          <StatusBadge status={art.processing_status} />
                        </td>
                        <td className="px-4 py-3 text-xs text-slate-400 text-right">
                          {formatDate(art.crawled_at)}
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={4} className="px-4 py-8 text-center text-slate-500 text-sm">
                        Belum ada artikel di database.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

          {/* Recent Crawl Activity */}
          <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-base font-bold text-white">Log Eksekusi</h3>
                <Link
                  href="/crawl-runs"
                  className="text-xs text-rose-400 hover:text-rose-300 flex items-center gap-1 font-medium"
                >
                  Detail <ArrowRight className="w-3 h-3" />
                </Link>
              </div>

              <div className="space-y-3">
                {recentRuns.length > 0 ? (
                  recentRuns.map((run) => (
                    <div
                      key={run.id}
                      className="p-3.5 rounded-xl bg-slate-800/50 border border-slate-700/40 text-xs space-y-1.5"
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-slate-200">
                          {run.sources?.name || "Global Run"}
                        </span>
                        <StatusBadge status={run.status} />
                      </div>
                      <div className="flex items-center justify-between text-slate-400 text-[11px]">
                        <span>Ditemukan: {run.discovered_count}</span>
                        <span>Baru: {run.new_count}</span>
                        <span>Gagal: {run.failed_count}</span>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="p-4 rounded-xl bg-slate-800/30 border border-slate-800 text-center text-slate-500 text-xs">
                    Belum ada audit log crawl_runs di database.
                  </div>
                )}
              </div>
            </div>

            <div className="mt-6 pt-4 border-t border-slate-800 text-xs text-slate-400 flex items-center justify-between">
              <span>Next Schedule:</span>
              <span className="font-medium text-slate-300">Setiap Hari 00:00 UTC</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
