-- =====================================================================
-- Migration 002: Fix daily_keywords unique constraint to handle NULL source_id
-- =====================================================================

-- In PostgreSQL, standard UNIQUE constraints treat NULL values as distinct.
-- This migration updates the constraint to use NULLS NOT DISTINCT (PostgreSQL 15+)
-- so that rows with source_id = NULL (global aggregation) are properly upserted
-- without creating duplicate rows for the same date and word.

ALTER TABLE public.daily_keywords
    DROP CONSTRAINT IF EXISTS uq_daily_keywords_date_source_word;

ALTER TABLE public.daily_keywords
    ADD CONSTRAINT uq_daily_keywords_date_source_word
    UNIQUE NULLS NOT DISTINCT (date, source_id, word);
