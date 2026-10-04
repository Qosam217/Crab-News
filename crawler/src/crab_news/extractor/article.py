"""Data transfer model for extracted articles prior to database persistence."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ExtractedArticle:
    url: str
    title: str
    content: str
    author: Optional[str] = None
    published_at: Optional[datetime] = None
    source_id: Optional[str] = None
    content_hash: Optional[str] = None
