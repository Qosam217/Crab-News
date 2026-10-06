import { Header } from "@/components/Header";
import { StatusBadge } from "@/components/StatusBadge";
import { supabase } from "@/lib/supabase";
import { formatDate } from "@/lib/utils";
import { CrawlRun } from "@/types/database";

export const dynamic = "force-dynamic";

export default async function CrawlRunsPage() {
  const { data: runsData } = await supabase
    .from("crawl_runs")
    .select("*, sources(name)")
    .order("started_at", { ascending: false })
    .limit(50);
  const runs: CrawlRun[] = runsData || [];

  return (
    <div className="flex-1 pb-12">
      <Header
        title="Crawler Health & Audit Runs"
        description="Monitoring riwayat eksekusi crawler dari GitHub Actions dan eksekusi lokal"
      />

      <div className="p-8 space-y-6 max-w-7xl mx-auto">
        {/* Runs Table */}
        <div className="rounded-2xl bg-slate-900/60 border border-slate-800 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="text-xs text-slate-400 uppercase bg-slate-800/40 border-b border-slate-800">
                <tr>
                  <th className="px-5 py-3.5">Sumber Berita</th>
                  <th className="px-5 py-3.5">Status</th>
                  <th className="px-5 py-3.5">Ditemukan</th>
                  <th className="px-5 py-3.5">Artikel Baru</th>
                  <th className="px-5 py-3.5">Duplikat</th>
                  <th className="px-5 py-3.5">Terproses</th>
                  <th className="px-5 py-3.5">Gagal</th>
                  <th className="px-5 py-3.5">Waktu Mulai</th>
                  <th className="px-5 py-3.5">Waktu Selesai</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {runs.length > 0 ? (
                  runs.map((r) => (
                    <tr key={r.id} className="hover:bg-slate-800/30 transition-colors">
                      <td className="px-5 py-4 font-semibold text-white">
                        {r.sources?.name || "Global / All Sources"}
                      </td>
                      <td className="px-5 py-4">
                        <StatusBadge status={r.status} />
                      </td>
                      <td className="px-5 py-4 font-mono text-slate-300">{r.discovered_count}</td>
                      <td className="px-5 py-4 font-mono text-emerald-400 font-bold">{r.new_count}</td>
                      <td className="px-5 py-4 font-mono text-slate-400">{r.duplicate_count}</td>
                      <td className="px-5 py-4 font-mono text-blue-400 font-semibold">{r.processed_count}</td>
                      <td className="px-5 py-4 font-mono text-rose-400">{r.failed_count}</td>
                      <td className="px-5 py-4 text-xs text-slate-400">{formatDate(r.started_at)}</td>
                      <td className="px-5 py-4 text-xs text-slate-400">{formatDate(r.finished_at)}</td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={9} className="px-5 py-12 text-center text-slate-500 text-sm">
                      Belum ada riwayat audit crawl_runs di database.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
