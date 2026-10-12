"""Daily Keyword Aggregation Engine."""

from collections import defaultdict
from datetime import date, datetime
from typing import List, Dict, Tuple, Optional
from uuid import UUID
from ..database.client import get_supabase_client
from ..database.models import DailyKeywordModel
from ..utils.logger import logger


def compute_daily_keywords(target_date: Optional[date] = None) -> List[DailyKeywordModel]:
    """Aggregates word occurrences across articles published on the target date.

    Generates records both for individual sources (source_id != None) and global aggregate (source_id = None).
    """
    client = get_supabase_client()
    if target_date is None:
        target_date = date.today()

    start_ts = datetime.combine(target_date, datetime.min.time()).isoformat()
    end_ts = datetime.combine(target_date, datetime.max.time()).isoformat()

    try:
        # Fetch articles for the date
        articles_res = (
            client.table("articles")
            .select("id, source_id")
            .gte("published_at", start_ts)
            .lte("published_at", end_ts)
            .eq("processing_status", "processed")
            .execute()
        )

        articles = articles_res.data
        if not articles:
            logger.info(f"No processed articles found for aggregation date {target_date}")
            return []

        article_ids = [a["id"] for a in articles]
        article_source_map = {a["id"]: a["source_id"] for a in articles}

        # Fetch words for these articles in chunks
        chunk_size = 200
        all_words = []
        for i in range(0, len(article_ids), chunk_size):
            chunk = article_ids[i : i + chunk_size]
            words_query = (
                client.table("article_words")
                .select("article_id, word, frequency")
                .in_("article_id", chunk)
                .order("article_id")
                .order("word")
            )
            all_words.extend(fetch_all_rows(words_query))

        # source_id -> word -> (total_freq, article_ids_set)
        source_aggregates: Dict[Optional[str], Dict[str, Dict]] = defaultdict(
            lambda: defaultdict(lambda: {"freq": 0, "articles": set()})
        )

        for row in all_words:
            art_id = row["article_id"]
            word = row["word"]
            freq = row["frequency"]
            src_id = article_source_map.get(art_id)

            # Per-source
            source_aggregates[src_id][word]["freq"] += freq
            source_aggregates[src_id][word]["articles"].add(art_id)

            # Global aggregate (source_id = None)
            source_aggregates[None][word]["freq"] += freq
            source_aggregates[None][word]["articles"].add(art_id)

        results: List[DailyKeywordModel] = []
        for src_id, words_dict in source_aggregates.items():
            for word, data in words_dict.items():
                results.append(
                    DailyKeywordModel(
                        date=target_date,
                        source_id=UUID(src_id) if src_id else None,
                        word=word,
                        frequency=data["freq"],
                        article_count=len(data["articles"]),
                    )
                )

        logger.info(f"Generated {len(results)} daily keyword aggregation records for {target_date}")
        return results

    except Exception as e:
        logger.error(f"Failed to compute daily keywords for {target_date}: {e}")
        return []

def fetch_all_rows(query, page_size: int = 1000) -> list:
    """Fetch all rows using range-based pagination."""
    rows = []
    offset = 0

    while True:
        response = (
            query
            .range(offset, offset + page_size - 1)
            .execute()
        )

        batch = response.data or []
        rows.extend(batch)

        if len(batch) < page_size:
            break

        offset += page_size

    return rows
