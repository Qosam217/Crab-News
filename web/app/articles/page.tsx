import { Header } from "@/components/Header";
import { supabase } from "@/lib/supabase";
import { Article, Source } from "@/types/database";
import { ArticlesExplorer } from "./ArticlesExplorer";

export const dynamic = "force-dynamic";

export default async function ArticlesPage() {
  // Fetch sources
  const { data: sourcesData } = await supabase
    .from("sources")
    .select("*")
    .order("name");
  const sources: Source[] = sourcesData || [];

  // Fetch articles
  const { data: articlesData } = await supabase
    .from("articles")
    .select("*, sources(name, slug)")
    .order("crawled_at", { ascending: false })
    .limit(100);
  const articles: Article[] = articlesData || [];

  return (
    <div className="flex-1 pb-12">
      <Header
        title="Article Explorer"
        description="Eksplorasi seluruh artikel berita yang telah dikumpulkan dan dianalisis"
      />

      <div className="p-8 max-w-7xl mx-auto">
        <ArticlesExplorer initialArticles={articles} sources={sources} />
      </div>
    </div>
  );
}
