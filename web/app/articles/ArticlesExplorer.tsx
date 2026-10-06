"use client";

import { useState } from "react";
import { StatusBadge } from "@/components/StatusBadge";
import { formatDate } from "@/lib/utils";
import { Article, Source } from "@/types/database";
import { Search, ExternalLink } from "lucide-react";

interface ArticlesExplorerProps {
  initialArticles: Article[];
  sources: Source[];
}

export function ArticlesExplorer({ initialArticles, sources }: ArticlesExplorerProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedSource, setSelectedSource] = useState<string>("all");
  const [selectedStatus, setSelectedStatus] = useState<string>("all");

  const filteredArticles = initialArticles.filter((art) => {
    const matchesSearch = art.title.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesSource = selectedSource === "all" || art.source_id === selectedSource;
    const matchesStatus = selectedStatus === "all" || art.processing_status === selectedStatus;
    return matchesSearch && matchesSource && matchesStatus;
  });

  return (
    <div className="space-y-6">
      {/* Filters Bar */}
      <div className="flex flex-col md:flex-row gap-4 items-center justify-between bg-slate-900/60 p-4 rounded-xl border border-slate-800">
        <div className="relative w-full md:w-96">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Cari judul berita..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-slate-800/80 border border-slate-700/60 rounded-lg text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-rose-500 transition-colors"
          />
        </div>

        <div className="flex items-center gap-3 w-full md:w-auto">
          {/* Source Filter */}
          <select
            value={selectedSource}
            onChange={(e) => setSelectedSource(e.target.value)}
            className="px-3 py-2 bg-slate-800/80 border border-slate-700/60 rounded-lg text-xs text-slate-300 focus:outline-none focus:border-rose-500"
          >
            <option value="all">Semua Sumber Media</option>
            {sources.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name}
              </option>
            ))}
          </select>

          {/* Status Filter */}
          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="px-3 py-2 bg-slate-800/80 border border-slate-700/60 rounded-lg text-xs text-slate-300 focus:outline-none focus:border-rose-500"
          >
            <option value="all">Semua Status</option>
            <option value="processed">Processed</option>
            <option value="pending">Pending</option>
            <option value="failed">Failed</option>
          </select>
        </div>
      </div>

      {/* Articles Table */}
      <div className="rounded-2xl bg-slate-900/60 border border-slate-800 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="text-xs text-slate-400 uppercase bg-slate-800/40 border-b border-slate-800">
              <tr>
                <th className="px-5 py-3.5">Judul</th>
                <th className="px-5 py-3.5">Sumber</th>
                <th className="px-5 py-3.5">Penulis</th>
                <th className="px-5 py-3.5">Status</th>
                <th className="px-5 py-3.5">Dipublikasikan</th>
                <th className="px-5 py-3.5 text-right">Link</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filteredArticles.length > 0 ? (
                filteredArticles.map((art) => (
                  <tr key={art.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="px-5 py-4 font-medium text-white max-w-md truncate">
                      {art.title}
                    </td>
                    <td className="px-5 py-4 text-xs text-slate-400">
                      {art.sources?.name || "RSS"}
                    </td>
                    <td className="px-5 py-4 text-xs text-slate-400">
                      {art.author || "-"}
                    </td>
                    <td className="px-5 py-4">
                      <StatusBadge status={art.processing_status} />
                    </td>
                    <td className="px-5 py-4 text-xs text-slate-400">
                      {formatDate(art.published_at || art.crawled_at)}
                    </td>
                    <td className="px-5 py-4 text-right">
                      <a
                        href={art.url}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-1 text-xs text-rose-400 hover:text-rose-300"
                      >
                        Buka <ExternalLink className="w-3 h-3" />
                      </a>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={6} className="px-5 py-12 text-center text-slate-500 text-sm">
                    {initialArticles.length === 0
                      ? "Belum ada artikel di database."
                      : "Tidak ada artikel yang sesuai kriteria pencarian."}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
