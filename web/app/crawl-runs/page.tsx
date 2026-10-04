"use client";

import { useEffect, useState } from "react";
import { Header } from "@/components/Header";
import { StatusBadge } from "@/components/StatusBadge";
import { supabase } from "@/lib/supabase";
import { formatDate } from "@/lib/utils";
import { CrawlRun } from "@/types/database";
import { Activity, CheckCircle2, AlertTriangle, XCircle, Clock } from "lucide-react";

export default function CrawlRunsPage() {
  const [runs, setRuns] = useState<CrawlRun[]>([]);
  const [loading, setLoading] = useState(true);

  async function loadRuns() {
    setLoading(true);
    try {
      const { data } = await supabase
        .from("crawl_runs")
        .select("*, sources(name)")
        .order("started_at", { ascending: false })
        .limit(50);

      if (data && data.length > 0) {
        setRuns(data);
      } else {
        // Fallback demo data
        setRuns([
          {
            id: "run-001",
            source_id: null,
            started_at: "2026-10-04T00:00:00Z",
            finished_at: "2026-10-04T00:04:12Z",
            status: "success",
            discovered_count: 142,
            new_count: 45,
            duplicate_count: 97,
            processed_count: 45,
            failed_count: 0,
            error_summary: null,
            created_at: "2026-10-04T00:00:00Z",
          },
          {
            id: "run-002",
            source_id: null,
            started_at: "2026-10-03T00:00:00Z",
            finished_at: "2026-10-03T00:03:45Z",
            status: "partial",
            discovered_count: 120,
            new_count: 38,
            duplicate_count: 80,
            processed_count: 36,
            failed_count: 2,
            error_summary: "Content extraction empty for 2 tempo articles",
            created_at: "2026-10-03T00:00:00Z",
          },
        ]);
      }
    } catch (e) {
      console.warn("Failed to load crawl runs:", e);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadRuns();
  }, []);

  return (
    <div className="flex-1 pb-12">
      <Header
        title="Crawler Health & Audit Runs"
        description="Monitoring riwayat eksekusi crawler dari GitHub Actions dan eksekusi lokal"
        onRefresh={loadRuns}
        isLoading={loading}
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
                {runs.map((r) => (
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
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
