import { Header } from "@/components/Header";
import { supabase } from "@/lib/supabase";
import { DailyKeyword, Source } from "@/types/database";
import { KeywordsExplorer } from "./KeywordsExplorer";

export const dynamic = "force-dynamic";

export default async function KeywordsPage() {
  const [{ data: keywordsData }, { data: sourcesData }] = await Promise.all([
    supabase
      .from("daily_keywords")
      .select("*, sources(id, name, slug)")
      .order("frequency", { ascending: false })
      .limit(500),
    supabase
      .from("sources")
      .select("*")
      .order("name", { ascending: true }),
  ]);

  const keywords: DailyKeyword[] = keywordsData || [];
  const sources: Source[] = sourcesData || [];

  return (
    <div className="flex-1 pb-12">
      <Header
        title="Keyword Intelligence"
        description="Analisis frekuensi dan distribusi kata kunci Bahasa Indonesia hasil ekstraksi teks"
      />

      <div className="p-8 max-w-7xl mx-auto">
        <KeywordsExplorer initialKeywords={keywords} sources={sources} />
      </div>
    </div>
  );
}
