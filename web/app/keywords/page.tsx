import { Header } from "@/components/Header";
import { supabase } from "@/lib/supabase";
import { DailyKeyword } from "@/types/database";
import { KeywordsExplorer } from "./KeywordsExplorer";

export const dynamic = "force-dynamic";

export default async function KeywordsPage() {
  const { data: keywordsData } = await supabase
    .from("daily_keywords")
    .select("*, sources(name)")
    .order("frequency", { ascending: false })
    .limit(100);

  const keywords: DailyKeyword[] = keywordsData || [];

  return (
    <div className="flex-1 pb-12">
      <Header
        title="Keyword Intelligence"
        description="Analisis frekuensi dan distribusi kata kunci Bahasa Indonesia hasil ekstraksi teks"
      />

      <div className="p-8 max-w-7xl mx-auto">
        <KeywordsExplorer initialKeywords={keywords} />
      </div>
    </div>
  );
}
