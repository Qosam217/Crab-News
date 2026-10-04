"""Repository layer for interacting with Supabase database tables."""

from datetime import datetime, date
from typing import List, Optional, Dict, Any
from uuid import UUID
from ..database.client import get_supabase_client
from ..database.models import (
    SourceModel,
    ArticleModel,
    ArticleWordModel,
    DailyKeywordModel,
    CrawlRunModel,
)
from ..utils.logger import logger


class SourceRepository:
    def __init__(self):
        self.client = get_supabase_client()

    def get_active_sources(self) -> List[SourceModel]:
        """Fetches all active news sources."""
        try:
            response = self.client.table("sources").select("*").eq("is_active", True).execute()
            return [SourceModel(**row) for row in response.data]
        except Exception as e:
            logger.error(f"Failed to fetch active sources: {e}")
            return []

    def get_by_slug(self, slug: str) -> Optional[SourceModel]:
        """Fetches a source by its slug."""
        try:
            response = self.client.table("sources").select("*").eq("slug", slug).execute()
            if response.data:
                return SourceModel(**response.data[0])
            return None
        except Exception as e:
            logger.error(f"Failed to fetch source with slug '{slug}': {e}")
            return None


class ArticleRepository:
    def __init__(self):
        self.client = get_supabase_client()

    def exists_by_url_or_hash(self, url: str, content_hash: str) -> bool:
        """Checks if an article with the same URL or content_hash already exists."""
        try:
            # Check by URL
            res_url = self.client.table("articles").select("id").eq("url", url).limit(1).execute()
            if res_url.data:
                return True

            # Check by content hash
            if content_hash:
                res_hash = (
                    self.client.table("articles")
                    .select("id")
                    .eq("content_hash", content_hash)
                    .limit(1)
                    .execute()
                )
                if res_hash.data:
                    return True
            return False
        except Exception as e:
            logger.error(f"Error checking article existence for URL {url}: {e}")
            return False

    def insert_article(self, article: ArticleModel) -> Optional[ArticleModel]:
        """Inserts a new article into the database."""
        try:
            payload = article.model_dump(exclude_none=True)
            if "id" in payload and payload["id"] is None:
                del payload["id"]
            # Convert UUID to str
            if "source_id" in payload:
                payload["source_id"] = str(payload["source_id"])
            if "published_at" in payload and isinstance(payload["published_at"], datetime):
                payload["published_at"] = payload["published_at"].isoformat()
            if "crawled_at" in payload and isinstance(payload["crawled_at"], datetime):
                payload["crawled_at"] = payload["crawled_at"].isoformat()

            response = self.client.table("articles").insert(payload).execute()
            if response.data:
                return ArticleModel(**response.data[0])
            return None
        except Exception as e:
            logger.error(f"Failed to insert article '{article.title}': {e}")
            return None

    def get_pending_articles(self, limit: int = 100) -> List[ArticleModel]:
        """Fetches articles with processing_status = 'pending'."""
        try:
            response = (
                self.client.table("articles")
                .select("*")
                .eq("processing_status", "pending")
                .limit(limit)
                .execute()
            )
            return [ArticleModel(**row) for row in response.data]
        except Exception as e:
            logger.error(f"Failed to fetch pending articles: {e}")
            return []

    def get_failed_articles(self, limit: int = 100) -> List[ArticleModel]:
        """Fetches articles with processing_status = 'failed'."""
        try:
            response = (
                self.client.table("articles")
                .select("*")
                .eq("processing_status", "failed")
                .limit(limit)
                .execute()
            )
            return [ArticleModel(**row) for row in response.data]
        except Exception as e:
            logger.error(f"Failed to fetch failed articles: {e}")
            return []

    def update_processing_status(
        self, article_id: UUID, status: str, error: Optional[str] = None
    ) -> bool:
        """Updates article processing status and optional error message."""
        try:
            payload: Dict[str, Any] = {
                "processing_status": status,
                "processing_error": error,
                "updated_at": datetime.utcnow().isoformat(),
            }
            self.client.table("articles").update(payload).eq("id", str(article_id)).execute()
            return True
        except Exception as e:
            logger.error(f"Failed to update status for article {article_id}: {e}")
            return False


class WordRepository:
    def __init__(self):
        self.client = get_supabase_client()

    def save_article_words(self, article_id: UUID, word_counts: Dict[str, int]) -> bool:
        """Saves word frequencies for an article."""
        if not word_counts:
            return True
        try:
            # First remove existing words if any (for idempotent retries)
            self.client.table("article_words").delete().eq("article_id", str(article_id)).execute()

            rows = [
                {
                    "article_id": str(article_id),
                    "word": word,
                    "frequency": freq,
                    "normalized_word": word,
                }
                for word, freq in word_counts.items()
            ]
            self.client.table("article_words").insert(rows).execute()
            return True
        except Exception as e:
            logger.error(f"Failed to save words for article {article_id}: {e}")
            return False


class KeywordRepository:
    def __init__(self):
        self.client = get_supabase_client()

    def upsert_daily_keywords(self, daily_keywords: List[DailyKeywordModel]) -> bool:
        """Upserts precomputed daily keyword statistics."""
        if not daily_keywords:
            return True
        try:
            rows = []
            for item in daily_keywords:
                rows.append({
                    "date": item.date.isoformat() if isinstance(item.date, date) else str(item.date),
                    "source_id": str(item.source_id) if item.source_id else None,
                    "word": item.word,
                    "frequency": item.frequency,
                    "article_count": item.article_count,
                })
            # Upsert on conflict (date, source_id, word)
            self.client.table("daily_keywords").upsert(
                rows, on_conflict="date,source_id,word"
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Failed to upsert daily keywords: {e}")
            return False


class CrawlRunRepository:
    def __init__(self):
        self.client = get_supabase_client()

    def create_run(self, source_id: Optional[UUID] = None) -> Optional[CrawlRunModel]:
        """Creates an initial running crawl_run record."""
        try:
            payload = {
                "source_id": str(source_id) if source_id else None,
                "started_at": datetime.utcnow().isoformat(),
                "status": "running",
                "discovered_count": 0,
                "new_count": 0,
                "duplicate_count": 0,
                "processed_count": 0,
                "failed_count": 0,
            }
            res = self.client.table("crawl_runs").insert(payload).execute()
            if res.data:
                return CrawlRunModel(**res.data[0])
            return None
        except Exception as e:
            logger.error(f"Failed to create crawl run: {e}")
            return None

    def update_run(self, run: CrawlRunModel) -> bool:
        """Updates finished crawl run record with metrics."""
        if not run.id:
            return False
        try:
            payload = {
                "finished_at": datetime.utcnow().isoformat(),
                "status": run.status,
                "discovered_count": run.discovered_count,
                "new_count": run.new_count,
                "duplicate_count": run.duplicate_count,
                "processed_count": run.processed_count,
                "failed_count": run.failed_count,
                "error_summary": run.error_summary,
            }
            self.client.table("crawl_runs").update(payload).eq("id", str(run.id)).execute()
            return True
        except Exception as e:
            logger.error(f"Failed to update crawl run {run.id}: {e}")
            return False
