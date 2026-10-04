"""Pydantic data models for Crab News database entities."""

from datetime import datetime, date
from typing import Optional, Literal
from uuid import UUID
from pydantic import BaseModel, Field


class SourceModel(BaseModel):
    id: Optional[UUID] = None
    name: str
    slug: str
    domain: str
    website_url: str
    rss_url: Optional[str] = None
    crawler_type: Literal["rss", "html", "hybrid"] = "rss"
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ArticleModel(BaseModel):
    id: Optional[UUID] = None
    source_id: UUID
    url: str
    title: str
    content: str
    author: Optional[str] = None
    published_at: Optional[datetime] = None
    crawled_at: Optional[datetime] = None
    content_hash: str
    processing_status: Literal["pending", "processed", "failed"] = "pending"
    processing_error: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ArticleWordModel(BaseModel):
    id: Optional[int] = None
    article_id: UUID
    word: str
    frequency: int = 1
    normalized_word: Optional[str] = None
    created_at: Optional[datetime] = None


class DailyKeywordModel(BaseModel):
    id: Optional[int] = None
    date: date
    source_id: Optional[UUID] = None
    word: str
    frequency: int = 0
    article_count: int = 0
    created_at: Optional[datetime] = None


class CrawlRunModel(BaseModel):
    id: Optional[UUID] = None
    source_id: Optional[UUID] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    status: Literal["running", "success", "partial", "failed"] = "running"
    discovered_count: int = 0
    new_count: int = 0
    duplicate_count: int = 0
    processed_count: int = 0
    failed_count: int = 0
    error_summary: Optional[str] = None
    created_at: Optional[datetime] = None
