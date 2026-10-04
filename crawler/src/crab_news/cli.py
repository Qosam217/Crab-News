"""Crab News - Standalone Python CLI and Crawler Pipeline."""

import argparse
from datetime import datetime, date
import sys
import time
from typing import List, Optional
from uuid import UUID

from .config import settings
from .database import (
    SourceRepository,
    ArticleRepository,
    WordRepository,
    KeywordRepository,
    CrawlRunRepository,
    SourceModel,
    ArticleModel,
    CrawlRunModel,
)
from .sources import get_source_adapter
from .processor import extract_article_keywords
from .analyzer import compute_daily_keywords
from .utils.logger import logger
from .utils.hasher import compute_content_hash


def process_single_article(
    article_repo: ArticleRepository,
    word_repo: WordRepository,
    article: ArticleModel,
    dry_run: bool = False,
) -> bool:
    """Extracts keywords from an article and saves word occurrences into database."""
    try:
        keywords = extract_article_keywords(article.title, article.content)
        if dry_run:
            logger.info(f"[DRY-RUN] Processed '{article.title[:40]}...' -> {len(keywords)} distinct words")
            return True

        if not article.id:
            return False

        # Save to article_words
        saved = word_repo.save_article_words(article.id, keywords)
        if saved:
            article_repo.update_processing_status(article.id, "processed")
            return True
        else:
            article_repo.update_processing_status(article.id, "failed", "Failed to save article words")
            return False
    except Exception as e:
        logger.error(f"Error processing article {article.id}: {e}")
        if not dry_run and article.id:
            article_repo.update_processing_status(article.id, "failed", str(e))
        return False


def run_crawler_for_source(
    source: SourceModel,
    limit: int = 30,
    dry_run: bool = False,
    process_after: bool = True,
) -> CrawlRunModel:
    """Executes discovery, extraction, deduplication, and processing for a single news source."""
    logger.info(f"=== Starting crawl for source: {source.name} ({source.slug}) ===")

    article_repo = ArticleRepository()
    word_repo = WordRepository()
    run_repo = CrawlRunRepository()

    run_record: Optional[CrawlRunModel] = None
    if not dry_run:
        run_record = run_repo.create_run(source_id=source.id)

    discovered_count = 0
    new_count = 0
    duplicate_count = 0
    processed_count = 0
    failed_count = 0
    errors: List[str] = []

    adapter = get_source_adapter(source)

    try:
        candidates = adapter.discover_articles()
        discovered_count = len(candidates)
        logger.info(f"[{source.name}] Discovered {discovered_count} candidate articles from feed/index")

        if limit > 0:
            candidates = candidates[:limit]

        for idx, item in enumerate(candidates, 1):
            url = item.get("url", "")
            title = item.get("title", "")

            if not url:
                continue

            # Deduplication Check (URL check first)
            if not dry_run and article_repo.exists_by_url_or_hash(url, ""):
                duplicate_count += 1
                logger.debug(f"[{source.name}] Duplicate URL skipped: {url}")
                continue

            # Rate limiting sleep between page fetches
            time.sleep(settings.rate_limit_delay_seconds)

            try:
                # Full extraction
                extracted = adapter.extract_article(item)
                if not extracted or not extracted.content:
                    failed_count += 1
                    errors.append(f"Content extraction empty for {url}")
                    continue

                # Secondary Hash Deduplication Check
                if not dry_run and article_repo.exists_by_url_or_hash(url, extracted.content_hash or ""):
                    duplicate_count += 1
                    logger.debug(f"[{source.name}] Duplicate content hash skipped: {url}")
                    continue

                if dry_run:
                    new_count += 1
                    logger.info(f"[DRY-RUN] [{idx}/{len(candidates)}] Extracted: {extracted.title[:50]}...")
                    if process_after:
                        fake_article = ArticleModel(
                            source_id=source.id or UUID("00000000-0000-0000-0000-000000000000"),
                            url=extracted.url,
                            title=extracted.title,
                            content=extracted.content,
                            content_hash=extracted.content_hash or "",
                        )
                        process_single_article(article_repo, word_repo, fake_article, dry_run=True)
                        processed_count += 1
                    continue

                # Insert raw article
                article_data = ArticleModel(
                    source_id=source.id,  # type: ignore
                    url=extracted.url,
                    title=extracted.title,
                    content=extracted.content,
                    author=extracted.author,
                    published_at=extracted.published_at or datetime.utcnow(),
                    crawled_at=datetime.utcnow(),
                    content_hash=extracted.content_hash or compute_content_hash(extracted.content),
                    processing_status="pending",
                )

                inserted = article_repo.insert_article(article_data)
                if inserted:
                    new_count += 1
                    logger.info(f"[{source.name}] [{idx}/{len(candidates)}] Stored: {inserted.title[:50]}...")

                    if process_after:
                        ok = process_single_article(article_repo, word_repo, inserted, dry_run=False)
                        if ok:
                            processed_count += 1
                        else:
                            failed_count += 1
                else:
                    failed_count += 1
                    errors.append(f"Failed database insertion for {url}")

            except Exception as item_err:
                logger.error(f"[{source.name}] Error extracting {url}: {item_err}")
                failed_count += 1
                errors.append(f"{url}: {str(item_err)}")

    except Exception as source_err:
        logger.error(f"[{source.name}] Source run failed: {source_err}")
        errors.append(str(source_err))

    # Compute run status
    final_status = "success"
    if failed_count > 0:
        final_status = "partial" if (new_count > 0 or processed_count > 0) else "failed"

    logger.info(
        f"[{source.name}] Finished. Discovered: {discovered_count}, New: {new_count}, "
        f"Duplicates: {duplicate_count}, Processed: {processed_count}, Failed: {failed_count}"
    )

    result_model = CrawlRunModel(
        id=run_record.id if run_record else None,
        source_id=source.id,
        started_at=run_record.started_at if run_record else datetime.utcnow(),
        finished_at=datetime.utcnow(),
        status=final_status,  # type: ignore
        discovered_count=discovered_count,
        new_count=new_count,
        duplicate_count=duplicate_count,
        processed_count=processed_count,
        failed_count=failed_count,
        error_summary="; ".join(errors[:5]) if errors else None,
    )

    if not dry_run and run_record:
        run_repo.update_run(result_model)

    return result_model


def run_process_pending(limit: int = 100, dry_run: bool = False):
    """Processes pending articles that haven't been tokenized yet."""
    logger.info("=== Processing Pending Articles ===")
    article_repo = ArticleRepository()
    word_repo = WordRepository()

    pending_articles = article_repo.get_pending_articles(limit=limit)
    logger.info(f"Found {len(pending_articles)} pending articles to process.")

    success_count = 0
    for article in pending_articles:
        ok = process_single_article(article_repo, word_repo, article, dry_run=dry_run)
        if ok:
            success_count += 1

    logger.info(f"Completed processing pending articles: {success_count}/{len(pending_articles)} success.")


def run_retry_failed(limit: int = 100, dry_run: bool = False):
    """Retries processing on articles previously marked as failed."""
    logger.info("=== Retrying Failed Articles ===")
    article_repo = ArticleRepository()
    word_repo = WordRepository()

    failed_articles = article_repo.get_failed_articles(limit=limit)
    logger.info(f"Found {len(failed_articles)} failed articles to retry.")

    success_count = 0
    for article in failed_articles:
        ok = process_single_article(article_repo, word_repo, article, dry_run=dry_run)
        if ok:
            success_count += 1

    logger.info(f"Completed retrying failed articles: {success_count}/{len(failed_articles)} recovered.")


def run_aggregation(target_date: Optional[date] = None, dry_run: bool = False):
    """Precomputes daily keyword statistics for dashboard consumption."""
    if target_date is None:
        target_date = date.today()

    logger.info(f"=== Aggregating Daily Keywords for date: {target_date} ===")
    keyword_repo = KeywordRepository()

    daily_records = compute_daily_keywords(target_date)
    if not dry_run and daily_records:
        keyword_repo.upsert_daily_keywords(daily_records)
        logger.info(f"Upserted {len(daily_records)} daily keyword aggregates into database.")
    elif dry_run:
        logger.info(f"[DRY-RUN] Computed {len(daily_records)} daily keyword aggregates.")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="crab-crawler",
        description="Crab News - Web Crawler & Keyword Analysis Pipeline",
    )

    parser.add_argument(
        "-s", "--source",
        type=str,
        help="Run crawler for a specific news source by slug (e.g. antara, kompas, detik, cnn-indonesia, tempo)",
    )
    parser.add_argument(
        "-a", "--all-sources",
        action="store_true",
        help="Run crawler across all active news sources in database",
    )
    parser.add_argument(
        "--process-pending",
        action="store_true",
        help="Process all pending articles in database",
    )
    parser.add_argument(
        "--retry-failed",
        action="store_true",
        help="Retry processing for failed articles",
    )
    parser.add_argument(
        "--aggregate-date",
        type=str,
        help="Compute daily keyword aggregates for a specific date (YYYY-MM-DD), defaults to today if used with --aggregate",
    )
    parser.add_argument(
        "--aggregate",
        action="store_true",
        help="Trigger daily keyword aggregation for today",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=settings.max_articles_per_source,
        help=f"Max articles to extract per source (default: {settings.max_articles_per_source})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run discovery & extraction without committing changes to Supabase",
    )

    args = parser.parse_args()

    # Check if any action is provided
    if not (args.source or args.all_sources or args.process_pending or args.retry_failed or args.aggregate or args.aggregate_date):
        parser.print_help()
        sys.exit(1)

    source_repo = SourceRepository()

    # 1. Specific source crawling
    if args.source:
        source = source_repo.get_by_slug(args.source)
        if not source:
            logger.error(f"Source with slug '{args.source}' not found in database.")
            # Fallback mock source if in dry-run
            if args.dry_run:
                logger.info(f"[DRY-RUN] Using mock source for '{args.source}'")
                source = SourceModel(
                    name=args.source.title(),
                    slug=args.source,
                    domain=f"{args.source}.com",
                    website_url=f"https://www.{args.source}.com",
                    rss_url="",
                    crawler_type="rss",
                )
            else:
                sys.exit(1)

        run_crawler_for_source(source, limit=args.limit, dry_run=args.dry_run)

    # 2. All active sources crawling
    if args.all_sources:
        active_sources = source_repo.get_active_sources()
        if not active_sources:
            logger.warning("No active sources found in database.")
        for src in active_sources:
            run_crawler_for_source(src, limit=args.limit, dry_run=args.dry_run)

    # 3. Process Pending
    if args.process_pending:
        run_process_pending(limit=args.limit, dry_run=args.dry_run)

    # 4. Retry Failed
    if args.retry_failed:
        run_retry_failed(limit=args.limit, dry_run=args.dry_run)

    # 5. Aggregation
    if args.aggregate or args.aggregate_date:
        target_d = None
        if args.aggregate_date:
            target_d = datetime.strptime(args.aggregate_date, "%Y-%m-%d").date()
        run_aggregation(target_date=target_d, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
