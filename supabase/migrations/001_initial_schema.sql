-- Crab News - Initial PostgreSQL Schema for Supabase
-- Version: 001_initial_schema.sql

-- Enable UUID extension if not enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================================
-- 1. Table: sources
-- =====================================================================
CREATE TABLE IF NOT EXISTS public.sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(50) UNIQUE NOT NULL,
    domain VARCHAR(150) NOT NULL,
    website_url TEXT NOT NULL,
    rss_url TEXT,
    crawler_type VARCHAR(20) NOT NULL DEFAULT 'rss' CHECK (crawler_type IN ('rss', 'html', 'hybrid')),
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =====================================================================
-- 2. Table: articles
-- =====================================================================
CREATE TABLE IF NOT EXISTS public.articles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id UUID NOT NULL REFERENCES public.sources(id) ON DELETE CASCADE,
    url TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    author VARCHAR(150),
    published_at TIMESTAMPTZ,
    crawled_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    content_hash VARCHAR(64) NOT NULL,
    processing_status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (processing_status IN ('pending', 'processed', 'failed')),
    processing_error TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexing for high-performance querying and deduplication
CREATE INDEX IF NOT EXISTS idx_articles_source_id ON public.articles(source_id);
CREATE INDEX IF NOT EXISTS idx_articles_content_hash ON public.articles(content_hash);
CREATE INDEX IF NOT EXISTS idx_articles_processing_status ON public.articles(processing_status);
CREATE INDEX IF NOT EXISTS idx_articles_published_at ON public.articles(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_articles_crawled_at ON public.articles(crawled_at DESC);

-- =====================================================================
-- 3. Table: article_words
-- =====================================================================
CREATE TABLE IF NOT EXISTS public.article_words (
    id BIGSERIAL PRIMARY KEY,
    article_id UUID NOT NULL REFERENCES public.articles(id) ON DELETE CASCADE,
    word VARCHAR(100) NOT NULL,
    frequency INTEGER NOT NULL DEFAULT 1,
    normalized_word VARCHAR(100),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_article_word UNIQUE (article_id, word)
);

CREATE INDEX IF NOT EXISTS idx_article_words_word ON public.article_words(word);
CREATE INDEX IF NOT EXISTS idx_article_words_article_id ON public.article_words(article_id);

-- =====================================================================
-- 4. Table: daily_keywords (Precomputed Aggregations for Dashboard)
-- =====================================================================
CREATE TABLE IF NOT EXISTS public.daily_keywords (
    id BIGSERIAL PRIMARY KEY,
    date DATE NOT NULL,
    source_id UUID REFERENCES public.sources(id) ON DELETE CASCADE,
    word VARCHAR(100) NOT NULL,
    frequency INTEGER NOT NULL DEFAULT 0,
    article_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_daily_keywords_date_source_word UNIQUE NULLS NOT DISTINCT (date, source_id, word)
);

CREATE INDEX IF NOT EXISTS idx_daily_keywords_date ON public.daily_keywords(date DESC);
CREATE INDEX IF NOT EXISTS idx_daily_keywords_word ON public.daily_keywords(word);
CREATE INDEX IF NOT EXISTS idx_daily_keywords_source ON public.daily_keywords(source_id);

-- =====================================================================
-- 5. Table: crawl_runs (Operational & Audit Log)
-- =====================================================================
CREATE TABLE IF NOT EXISTS public.crawl_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id UUID REFERENCES public.sources(id) ON DELETE SET NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at TIMESTAMPTZ,
    status VARCHAR(20) NOT NULL DEFAULT 'running' CHECK (status IN ('running', 'success', 'partial', 'failed')),
    discovered_count INTEGER NOT NULL DEFAULT 0,
    new_count INTEGER NOT NULL DEFAULT 0,
    duplicate_count INTEGER NOT NULL DEFAULT 0,
    processed_count INTEGER NOT NULL DEFAULT 0,
    failed_count INTEGER NOT NULL DEFAULT 0,
    error_summary TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_crawl_runs_started_at ON public.crawl_runs(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_crawl_runs_status ON public.crawl_runs(status);

-- =====================================================================
-- 6. Row Level Security (RLS) Configuration
-- =====================================================================
ALTER TABLE public.sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.articles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.article_words ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.daily_keywords ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.crawl_runs ENABLE ROW LEVEL SECURITY;

-- Allow public read-only access for Next.js Web Dashboard
CREATE POLICY "Allow public read-only access on sources" ON public.sources FOR SELECT USING (true);
CREATE POLICY "Allow public read-only access on articles" ON public.articles FOR SELECT USING (true);
CREATE POLICY "Allow public read-only access on article_words" ON public.article_words FOR SELECT USING (true);
CREATE POLICY "Allow public read-only access on daily_keywords" ON public.daily_keywords FOR SELECT USING (true);
CREATE POLICY "Allow public read-only access on crawl_runs" ON public.crawl_runs FOR SELECT USING (true);

-- Crawler uses service_role key which bypasses RLS automatically.
