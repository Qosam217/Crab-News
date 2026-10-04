export type CrawlerType = "rss" | "html" | "hybrid";
export type ProcessingStatus = "pending" | "processed" | "failed";
export type CrawlRunStatus = "running" | "success" | "partial" | "failed";

export interface Source {
  id: string;
  name: string;
  slug: string;
  domain: string;
  website_url: string;
  rss_url: string | null;
  crawler_type: CrawlerType;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Article {
  id: string;
  source_id: string;
  url: string;
  title: string;
  content: string;
  author: string | null;
  published_at: string | null;
  crawled_at: string;
  content_hash: string;
  processing_status: ProcessingStatus;
  processing_error: string | null;
  created_at: string;
  updated_at: string;
  // Joins
  sources?: Source;
}

export interface ArticleWord {
  id: number;
  article_id: string;
  word: string;
  frequency: number;
  normalized_word: string | null;
  created_at: string;
}

export interface DailyKeyword {
  id: number;
  date: string;
  source_id: string | null;
  word: string;
  frequency: number;
  article_count: number;
  created_at: string;
  // Joins
  sources?: Source;
}

export interface CrawlRun {
  id: string;
  source_id: string | null;
  started_at: string;
  finished_at: string | null;
  status: CrawlRunStatus;
  discovered_count: number;
  new_count: number;
  duplicate_count: number;
  processed_count: number;
  failed_count: number;
  error_summary: string | null;
  created_at: string;
  // Joins
  sources?: Source;
}

export interface DashboardSummaryStats {
  totalArticles: number;
  totalWords: number;
  activeSources: number;
  todayArticles: number;
  latestCrawlStatus: CrawlRunStatus | "none";
}
