"use client";

import { useEffect, useState } from "react";
import { Header } from "@/components/Header";
import { StatusBadge } from "@/components/StatusBadge";
import { supabase } from "@/lib/supabase";
import { Source } from "@/types/database";
import { Globe, Rss, ExternalLink } from "lucide-react";

export default function SourcesPage() {
  const [sources, setSources] = useState<Source[]>([
    {
      id: "a0000000-0000-0000-0000-000000000001",
      name: "Antara News",
      slug: "antara",
      domain: "antaranews.com",
      website_url: "https://www.antaranews.com",
      rss_url: "https://www.antaranews.com/rss/terkini.xml",
      crawler_type: "rss",
      is_active: true,
      created_at: "",
      updated_at: "",
    },
    {
      id: "a0000000-0000-0000-0000-000000000002",
      name: "CNN Indonesia",
      slug: "cnn-indonesia",
      domain: "cnnindonesia.com",
      website_url: "https://www.cnnindonesia.com",
      rss_url: "https://www.cnnindonesia.com/nasional/rss",
      crawler_type: "rss",
      is_active: true,
      created_at: "",
      updated_at: "",
    },
    {
      id: "a0000000-0000-0000-0000-000000000003",
      name: "Kompas",
      slug: "kompas",
      domain: "kompas.com",
      website_url: "https://www.kompas.com",
      rss_url: "https://news.kompas.com/feed",
      crawler_type: "rss",
      is_active: true,
      created_at: "",
      updated_at: "",
    },
    {
      id: "a0000000-0000-0000-0000-000000000004",
      name: "Detik News",
      slug: "detik",
      domain: "detik.com",
      website_url: "https://news.detik.com",
      rss_url: "https://rss.detik.com/index.php/detikcom",
      crawler_type: "rss",
      is_active: true,
      created_at: "",
      updated_at: "",
    },
    {
      id: "a0000000-0000-0000-0000-000000000005",
      name: "Tempo",
      slug: "tempo",
      domain: "tempo.co",
      website_url: "https://www.tempo.co",
      rss_url: "https://rss.tempo.co/nasional",
      crawler_type: "rss",
      is_active: true,
      created_at: "",
      updated_at: "",
    },
  ]);
  const [loading, setLoading] = useState(false);

  async function loadSources() {
    setLoading(true);
    try {
      const { data } = await supabase.from("sources").select("*").order("name");
      if (data && data.length > 0) {
        setSources(data);
      }
    } catch (e) {
      console.warn("Failed to load sources from Supabase:", e);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadSources();
  }, []);

  return (
    <div className="flex-1 pb-12">
      <Header
        title="News Sources Management"
        description="Portal berita yang terdaftar untuk proses automated data crawling"
        onRefresh={loadSources}
        isLoading={loading}
      />

      <div className="p-8 space-y-6 max-w-7xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {sources.map((s) => (
            <div
              key={s.id}
              className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 hover:border-slate-700 transition-all flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className="w-10 h-10 rounded-xl bg-slate-800 flex items-center justify-center text-rose-400">
                    <Globe className="w-5 h-5" />
                  </div>
                  <StatusBadge status={s.is_active ? "active" : "inactive"} />
                </div>
                <h3 className="font-bold text-white text-lg">{s.name}</h3>
                <p className="text-xs text-slate-400 mt-1">{s.domain}</p>

                <div className="mt-4 pt-4 border-t border-slate-800/80 space-y-2 text-xs">
                  <div className="flex items-center justify-between text-slate-400">
                    <span>Crawler Type:</span>
                    <span className="uppercase font-mono text-slate-300 bg-slate-800 px-2 py-0.5 rounded text-[10px]">
                      {s.crawler_type}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-slate-400">
                    <span>Adapter Slug:</span>
                    <span className="font-mono text-rose-400">{s.slug}</span>
                  </div>
                </div>
              </div>

              <div className="mt-6 pt-4 border-t border-slate-800/80 flex items-center justify-between">
                <a
                  href={s.website_url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-xs text-slate-400 hover:text-slate-200 flex items-center gap-1"
                >
                  Website <ExternalLink className="w-3 h-3" />
                </a>
                {s.rss_url && (
                  <a
                    href={s.rss_url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-xs text-amber-400 hover:text-amber-300 flex items-center gap-1 font-mono"
                  >
                    <Rss className="w-3 h-3" /> RSS Feed
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
