# Crab News — Project Planning

> News crawling, text processing, keyword analysis, and visualization platform.

**Project name:** Crab News  
**Type:** News Crawling & Analysis Web Application  
**Status:** Planning / Architecture finalized  
**Primary stack:** Python + GitHub Actions + Supabase PostgreSQL + Next.js/React/TypeScript + Vercel

---

## 1. Project Overview

**Crab News** is a web application and data pipeline for collecting news articles from multiple sources, processing their text, generating analytical information, and displaying the results through a dashboard.

The system is intentionally designed without a permanently running crawler server. The crawler is a **standalone Python CLI application** that can be executed from both GitHub Actions and a local laptop.

```text
News Sources / RSS
        ↓
Python Crawler CLI
        ↓
Raw Articles
        ↓
Text Processing
        ↓
Keyword / Trend Analysis
        ↓
Aggregated Data
        ↓
Supabase PostgreSQL
        ↓
Next.js Dashboard
        ↓
Vercel
```

The dashboard should consume data that has already been processed or aggregated. Heavy crawling, NLP, and batch calculations should not happen on normal web requests.

---

## 2. Why "Crab News"

The name is intentionally playful:

- **crawler** → a program that crawls web pages
- **crab** → an animal associated with crawling/moving
- **Crab News** → a less formal and more memorable project identity

The name is a project name, not an indication of editorial affiliation with a real-world news organization.

---

## 3. Main Objectives

### MVP objectives

1. Crawl articles from multiple news sources.
2. Store article metadata and content in PostgreSQL.
3. Detect duplicate articles.
4. Process article text into word-level information.
5. Calculate word frequency and article/document frequency.
6. Generate daily keyword and trend aggregates.
7. Provide a dashboard for exploring the results.
8. Execute the crawler automatically once per day through GitHub Actions.
9. Allow manual GitHub Actions execution when needed.
10. Allow the exact same crawler to run locally for debugging and emergency recovery.
11. Retry failed processing without recrawling articles that are already stored.

### Longer-term objectives

Expand from basic word frequency into a broader news-intelligence project:

- keyword trends
- source comparison
- keyword co-occurrence
- named entity recognition
- topic detection
- sentiment estimation
- duplicate / similar article detection
- article-volume anomaly detection
- search and filters
- historical timelines
- crawler monitoring

---

## 4. Finalized Architecture

```text
                          ┌─────────────────────┐
                          │   News Websites     │
                          │   / RSS Feeds       │
                          └──────────┬──────────┘
                                     │
                                     ▼
                     ┌──────────────────────────────┐
                     │      Python Crawler CLI      │
                     │                              │
                     │ Crawl → Extract → Process   │
                     │              → Aggregate    │
                     └──────────────┬───────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
             GitHub Actions                       Local
              Daily Cron                         Laptop
              / Manual                           / Debug
                    │                               │
                    └───────────────┬───────────────┘
                                    │
                                    ▼
                         ┌────────────────────┐
                         │      Supabase      │
                         │    PostgreSQL      │
                         │                    │
                         │ Raw                │
                         │ Processed          │
                         │ Aggregated         │
                         │ Operational data   │
                         └─────────┬──────────┘
                                   │
                              Read queries
                                   │
                                   ▼
                       ┌────────────────────────┐
                       │ Next.js + React + TS   │
                       │       Dashboard        │
                       └───────────┬────────────┘
                                   │
                                   ▼
                                Vercel
```

### Key architectural decisions

- **No persistent Python crawler API is required.**
- The crawler is a reusable CLI application.
- GitHub Actions is an execution environment, not the crawler itself.
- Local execution and GitHub Actions use the same Python codebase.
- Supabase is the persistent source of truth.
- Raw, processed, and aggregated data are separated logically.
- Dashboard-heavy calculations are precomputed during crawler/processing runs.
- Next.js can read suitable public/read-only dashboard data directly from Supabase.
- Pagination and bounded queries are expected to prevent huge data transfers.

---

## 5. Runtime Responsibilities

### Python Crawler

Responsible for:

- source discovery
- HTTP/RSS retrieval
- article extraction
- URL normalization
- duplicate detection
- text normalization
- word/keyword processing
- aggregation
- retry logic
- database writes

### GitHub Actions

Responsible for:

- daily scheduling
- manual workflow dispatch
- creating the Python runtime
- supplying secrets
- running the crawler
- reporting execution success/failure

### Local laptop

Responsible for:

- development
- debugging
- testing source adapters
- emergency reruns
- backfills/reprocessing when required

### Supabase

Responsible for:

- persistent relational storage
- raw article records
- processed records
- aggregated statistics
- crawl execution history
- RLS/access control

### Next.js

Responsible for:

- dashboard UI
- charts/tables
- filtering
- pagination
- Supabase reads
- optional server-side routes where custom logic is actually needed

### Vercel

Responsible for hosting the Next.js web application.

---

## 6. Data Pipeline

The canonical processing model is:

```text
RAW
 ↓
PROCESSED
 ↓
AGGREGATED
 ↓
DASHBOARD
```

### RAW

Article-level information as collected from sources.

### PROCESSED

Derived information such as normalized words, word frequency, entities, topics, etc.

### AGGREGATED

Precomputed data designed specifically for common dashboard queries.

### DASHBOARD

Data consumed by the web UI.

The project should **not** store the entire system's analytical result as a single giant JSON blob. Relational tables make filtering, indexing, pagination, updates, and incremental processing much easier.

---

## 7. Database Design

Initial tables:

```text
sources
articles
article_words
daily_keywords
crawl_runs
```

Future tables may include:

```text
entities
article_entities
topics
article_topics
article_similarity
keyword_trends
dashboard_daily_summary
```

### 7.1 `sources`

Stores source configuration.

Suggested fields:

```text
id
name
domain
website_url
rss_url
crawler_type
is_active
created_at
updated_at
```

Possible crawler types:

```text
rss
html
hybrid
```

### 7.2 `articles`

Suggested fields:

```text
id
source_id
url
title
content
author
published_at
crawled_at
content_hash
processing_status
processing_error
created_at
updated_at
```

Suggested processing states:

```text
pending
processed
failed
```

A dedicated `processing` state may be added later if required.

### 7.3 `article_words`

Suggested fields:

```text
id
article_id
word
frequency
```

Potential future fields:

```text
normalized_word
language
```

### 7.4 `daily_keywords`

Dashboard-oriented aggregate table.

Suggested fields:

```text
date
source_id
word
frequency
article_count
```

This supports queries such as:

- top keywords today
- top keywords by source
- keyword history
- frequency changes
- source comparison

### 7.5 `crawl_runs`

Tracks crawler execution.

Suggested fields:

```text
id
source_id
started_at
finished_at
status
discovered_count
new_count
duplicate_count
processed_count
failed_count
error_summary
```

Suggested statuses:

```text
running
success
partial
failed
```

This makes it possible to investigate questions such as: "What happened during yesterday's crawl?"

---

## 8. Constraints and Indexing

Potential unique constraints:

```text
articles:
(source_id, normalized_url)

article_words:
(article_id, word)

daily_keywords:
(date, source_id, word)
```

Potential indexes:

```text
articles.source_id
articles.published_at
articles.processing_status
articles.content_hash
article_words.article_id
article_words.word
daily_keywords.date
daily_keywords.word
daily_keywords.source_id
```

These are starting points. Final constraints and indexes should be validated against actual query patterns and data volume.

---

## 9. Duplicate Detection

The crawler should use more than raw URL equality.

### Primary check

Normalize URLs and compare normalized values.

### Secondary check

Create a content hash from normalized article content or another stable article fingerprint.

This helps handle:

- URL query parameters
- duplicated pages
- multiple URLs pointing to identical content
- exact republication

A future similarity engine can handle near-duplicates that differ slightly.

---

## 10. Text Processing Pipeline

Initial pipeline:

```text
Article Content
      ↓
HTML cleanup
      ↓
Text normalization
      ↓
Tokenization
      ↓
Lowercase normalization
      ↓
Stopword removal
      ↓
Noise filtering
      ↓
Word frequency
      ↓
Article-level statistics
```

For Indonesian news, processing should consider:

- Indonesian stopwords
- punctuation
- numbers
- URLs
- HTML artifacts
- whitespace
- boilerplate text
- abbreviations
- common inflection/morphological variants

Stemming can be introduced later after evaluating its effect on the resulting keyword data.

---

## 11. Keyword Analysis

Word frequency alone is not enough to identify useful trends.

The system should separate at least:

### Frequency

How many times a word appears.

### Article count

How many different articles contain the word.

### Trend

How the frequency or article count changes relative to an earlier period.

Conceptual example:

```text
trend_change = current_frequency - previous_frequency
```

or normalized growth:

```text
growth = (current - previous) / max(previous, 1)
```

The exact formula should be selected after observing real project data. Generic words should not automatically dominate the definition of a "trend."

---

## 12. Source Adapters

Each source should have isolated crawling/extraction logic.

Conceptual structure:

```text
BaseSource
   │
   ├── SourceA
   ├── SourceB
   ├── SourceC
   └── SourceD
```

Typical adapter responsibilities:

```text
discover_articles()
fetch_article()
extract_article()
```

This prevents source-specific HTML selectors from spreading throughout the rest of the application.

When a site changes its HTML, ideally only that adapter needs to be updated.

---

## 13. Crawling Strategy

Preferred order:

```text
RSS / structured feed
        ↓
HTML extraction when necessary
```

The crawler should support:

- request timeouts
- reasonable retries
- rate limiting
- configurable user agent
- error logging
- duplicate detection
- source-specific extraction logic

The implementation should not attempt to bypass:

- authentication
- CAPTCHA
- paywalls
- access controls

The project should also consider each target website's robots rules and applicable terms of service.

---

## 14. Standalone Python CLI

The crawler must be executable locally and in CI without changing the core logic.

Example commands:

```bash
python -m crawler
```

Specific source:

```bash
python -m crawler --source kompas
```

Retry failed processing:

```bash
python -m crawler --retry-failed
```

Process pending records:

```bash
python -m crawler --process-pending
```

Source + processing:

```bash
python -m crawler --source kompas --process
```

Dry run:

```bash
python -m crawler --source kompas --dry-run
```

These are CLI concepts. The final argument names can be adjusted during implementation.

---

## 15. Suggested Crawler Repository Structure

```text
crawler/
├── src/
│   └── crawler/
│       ├── __init__.py
│       ├── cli.py
│       ├── config/
│       ├── sources/
│       │   ├── base.py
│       │   ├── source_a.py
│       │   └── ...
│       ├── extractor/
│       │   ├── article.py
│       │   ├── rss.py
│       │   └── html.py
│       ├── processor/
│       │   ├── cleaner.py
│       │   ├── tokenizer.py
│       │   ├── stopwords.py
│       │   └── keywords.py
│       ├── analyzer/
│       │   ├── trends.py
│       │   └── aggregation.py
│       ├── database/
│       │   ├── client.py
│       │   ├── repositories/
│       │   └── models/
│       └── utils/
│
├── tests/
│   ├── sources/
│   ├── extractor/
│   ├── processor/
│   └── analyzer/
│
├── requirements.txt
├── pyproject.toml
├── .env.example
└── README.md
```

The structure may be simplified during MVP implementation if doing so keeps development clearer.

---

## 16. Incremental Processing

The system should process only new or pending data.

Example:

```text
Existing articles: 500,000
New articles:        1,200
```

Daily processing should approximately become:

```text
500,000 existing
        +
1,200 new
        ↓
process 1,200
```

not:

```text
process 501,200 every day
```

Historical recalculation should be an explicit backfill/reprocessing operation.

---

## 17. Retry and Recovery Design

Example:

```text
100 articles crawled
80 processed successfully
20 failed
```

The system should allow:

```bash
python -m crawler --retry-failed
```

without recrawling all 100 webpages.

### Recovery flow

```text
GitHub Actions run fails
        ↓
Inspect crawl_runs / logs
        ↓
Fix issue when necessary
        ↓
Retry through GitHub Actions or local laptop
        ↓
Supabase updated
```

### Website structure changed

```text
Extraction fails
      ↓
Fix source adapter locally
      ↓
Run crawler locally
      ↓
Verify data in Supabase
```

### Articles stored but processing failed

```text
articles
  ├── processed
  └── failed
        ↓
retry failed records
```

This separation is important for operational reliability.

---

## 18. Backfill / Reprocessing

A dedicated reprocessing mode should be considered for situations such as:

- stopword list changes
- tokenizer changes
- stemming introduction
- keyword algorithm changes
- NLP bug fixes
- addition of a new derived field

Conceptual command:

```bash
python -m crawler --reprocess --from 2026-01-01 --to 2026-03-01
```

Backfills should be deliberate because they can be computationally expensive.

---

## 19. GitHub Actions Workflow

### Daily scheduled execution

Conceptual flow:

```text
cron
 ↓
checkout repository
 ↓
setup Python
 ↓
install dependencies
 ↓
load secrets
 ↓
run crawler
 ↓
write to Supabase
 ↓
exit
```

### Manual execution

Use `workflow_dispatch` so the workflow can be started manually.

Possible inputs:

```text
source: all / specific source
mode: latest / retry / process
run_id: optional
```

The exact inputs should be finalized during implementation.

### Important limitation

GitHub Actions is not treated as a permanently running worker. The workflow starts, executes the Python program, writes results, and exits.

---

## 20. Local Environment

Example local environment variables:

```env
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
```

`.env` should never be committed.

GitHub Actions should use repository/environment secrets with the equivalent values.

The Supabase service-role key is privileged and must remain server-side/trusted-environment only.

---

## 21. Web Application Architecture

### Stack

```text
Next.js
React
TypeScript
Vercel
Supabase
```

The initial dashboard is primarily a read application.

### Direct Supabase reads

The frontend can directly query suitable dashboard data from Supabase when:

- the data is safe to expose
- access is read-only where appropriate
- RLS policies are configured correctly
- queries are bounded and paginated

Conceptually:

```text
Browser
   ↓
Supabase
   ↓
Precomputed dashboard tables
```

The browser must never receive the Supabase service-role key.

---

## 22. Why Precomputed Data Is Preferred

Avoid expensive computation during normal requests:

```text
Browser
 ↓
Next.js
 ↓
Read 500,000 articles
 ↓
Run NLP
 ↓
Calculate keyword frequency
 ↓
Return result
```

Preferred:

```text
Crawler / Processor
 ↓
Calculate statistics
 ↓
Store daily_keywords
 ↓
Browser
 ↓
Read daily_keywords
 ↓
Display result
```

This reduces repeated work and makes dashboard response times more predictable.

---

## 23. Direct Supabase vs Next.js API

### Direct Supabase reads

Useful for:

- dashboard summaries
- top keywords
- trend charts
- latest public articles
- simple filters
- paginated tables

### Next.js API/server route

Useful when the application needs:

- custom business logic
- complex validation
- privileged operations
- custom response shapes
- server-only credentials
- external API integrations
- custom caching behavior

The project does **not** require an application API for every normal dashboard query.

---

## 24. Pagination and Bounded Queries

The web application should never request unlimited datasets.

Examples:

```text
Latest articles → 20 per page
Top keywords    → 50 records
Historical chart → bounded date range
Search results  → paginated
```

Offset pagination is acceptable for MVP-sized datasets.

Cursor pagination can be introduced for larger datasets or frequently changing lists.

---

## 25. Dashboard MVP

### Summary cards

```text
Total Articles
Active Sources
Last Crawl
Processing Status
```

### Keyword section

```text
Top Keywords
Trending Keywords
Keyword Frequency
Article Count
```

### Article volume

```text
Articles per Day
Articles per Source
```

### Source comparison

Compare article volume and keyword distribution across sources.

### Latest articles

Display:

- title
- source
- publication date/time
- crawl date/time when useful
- original URL

The dashboard should favor metadata and derived analysis instead of unnecessarily republishing complete article text.

---

## 26. Potential Web Pages

```text
/
Dashboard

/articles
Article Explorer

/keywords
Keyword Explorer

/trends
Trend Analysis

/sources
Source Comparison

/topics
Topic Analysis

/entities
Named Entities

/runs
Crawler Runs / Monitoring
```

Only the first dashboard and basic article/keyword views are required for MVP.

---

## 27. Crawler Monitoring Dashboard

The `crawl_runs` table can support an operational page.

Example:

```text
Run #1042
Date: 2026-09-18
Source: Example News
Status: partial

Discovered: 120
New: 76
Duplicate: 44
Processed: 72
Failed: 4
```

This makes failures easier to understand without manually inspecting CI logs every time.

---

## 28. Future NLP Features

### Named Entity Recognition

Potential entities:

- people
- organizations
- government institutions
- companies
- locations
- countries

### Topic Detection

Potential categories:

```text
Politics
Economy
Energy
Technology
Health
Sports
International
Science
Environment
```

These categories may initially be implemented with rules or explicit classifiers before more advanced ML approaches are considered.

### Keyword Co-occurrence

Example concept:

```text
nuclear
 ├── reactor
 ├── energy
 ├── uranium
 └── safety
```

### Sentiment

Potential output:

```text
positive / neutral / negative
```

Sentiment should be treated as an analytical estimate rather than an objective fact.

### Similar Article Detection

Potential approaches:

- TF-IDF
- cosine similarity
- embeddings
- semantic similarity

This can evolve into cross-source event clustering.

---

## 29. Performance Strategy

### Crawler

Use:

- incremental crawling
- timeouts
- rate limiting
- sensible retries
- duplicate detection

### Processor

Use:

- batch operations where practical
- processing-status filtering
- incremental aggregation
- no unnecessary historical recalculation

### Database

Use appropriate indexes and constraints.

### Web

Use:

- precomputed aggregates
- pagination
- bounded date ranges
- caching where beneficial

Actual optimization should be based on measured query and data characteristics.

---

## 30. Error Handling

One failed article should not necessarily stop the complete run.

Example:

```text
Article 1 → success
Article 2 → success
Article 3 → failed
Article 4 → success
Article 5 → success
```

The run can continue and finish with:

```text
status = partial
```

Possible processing failure categories:

```text
extract_failed
parse_failed
database_failed
nlp_failed
unknown
```

---

## 31. Logging

Useful crawler logs should contain:

- source
- article URL when appropriate
- execution stage
- timestamp
- failure type
- concise error message

Example:

```text
[INFO] Starting source: Example News
[INFO] Discovered: 142 URLs
[INFO] New articles: 37
[ERROR] Extraction failed: <url>
[INFO] Processing completed: 35/37
```

Secrets must never be written to logs.

---

## 32. Security

Supabase access should be separated into public and privileged use cases.

```text
Public dashboard data
        ↓
RLS / read-only access
        ↓
Web client
```

```text
Crawler / privileged operations
        ↓
Service-role access
        ↓
GitHub Actions / local trusted environment
```

Never expose the service-role key through:

- client JavaScript
- Git repository
- public environment variables
- browser storage

---

## 33. Project Repository Structure

A monorepo is a practical starting point:

```text
crab-news/
│
├── crawler/
│   ├── src/
│   ├── tests/
│   ├── requirements.txt
│   ├── pyproject.toml
│   ├── .env.example
│   └── README.md
│
├── web/
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── types/
│   ├── public/
│   ├── package.json
│   └── README.md
│
├── supabase/
│   ├── migrations/
│   └── seed/
│
├── .github/
│   └── workflows/
│       └── crawler.yml
│
├── docs/
│   ├── architecture.md
│   ├── data-model.md
│   └── crawling.md
│
├── PROJECT_PLAN.md
└── README.md
```

This structure can later be split into separate repositories if project scale or deployment requirements make that useful.

---

## 34. Testing Strategy

### Unit tests

Cover:

- URL normalization
- duplicate detection
- RSS parsing
- HTML extraction
- text cleaning
- tokenization
- stopword filtering
- frequency calculation
- trend calculation

### Integration tests

Verify the pipeline:

```text
crawler
 → extractor
 → processor
 → Supabase
```

### Source adapter tests

Each adapter should have representative fixtures so HTML changes are easier to detect.

### End-to-end test

A small complete run should verify:

```text
discover
 → extract
 → store
 → process
 → aggregate
 → dashboard query
```

---

## 35. Data Integrity

The system should enforce, where appropriate:

- valid source relationships
- unique article identity
- valid processing states
- unique article/word combinations
- unique aggregate/date/source/word combinations
- deterministic aggregate updates
- execution timestamps

The final schema should be reviewed after the first real crawler output is available.

---

## 36. Legal and Operational Considerations

Crab News should be implemented as a crawling and analysis system, not as a mechanism for bypassing restrictions.

The crawler should:

- respect relevant robots rules
- respect applicable website terms
- use reasonable request rates
- avoid unnecessary repeated requests
- prefer RSS/public feeds where practical
- avoid bypassing CAPTCHA, authentication, or paywalls

For public-facing pages, prioritize:

```text
source
headline/title
publication date
original URL
derived analytical data
```

rather than republishing full article content unnecessarily.

Source attribution should remain available in the application.

---

## 37. Development Roadmap

### Phase 1 — Repository & Environment

- Create repository
- Create crawler and web folders
- Configure Python project
- Configure Next.js project
- Configure Supabase project
- Create `.env.example`
- Add basic testing setup

### Phase 2 — Database

Create:

```text
sources
articles
article_words
daily_keywords
crawl_runs
```

Add:

- relationships
- unique constraints
- indexes
- RLS policies
- seed/config data

### Phase 3 — Crawler Core

Implement:

- CLI
- configuration
- source registry
- HTTP/RSS handling
- retries
- logging
- crawl-run tracking

### Phase 4 — First Source

Complete one source adapter:

```text
discover
 → fetch
 → extract
 → normalize
 → deduplicate
 → store
```

Do not add many sources before the first adapter is stable.

### Phase 5 — Text Processing

Implement:

```text
cleaning
 → tokenization
 → stopword filtering
 → frequency calculation
 → article_words storage
```

### Phase 6 — Aggregation

Implement:

```text
daily frequency
article count
source statistics
trend calculations
```

### Phase 7 — Reliability

Implement:

- processing status
- failed-record retry
- crawl_runs summaries
- local recovery execution
- reprocessing/backfill mode where needed

### Phase 8 — GitHub Actions

Implement:

- daily cron
- manual workflow dispatch
- secrets
- workflow failure handling

### Phase 9 — Dashboard

Build:

1. summary cards
2. top keywords
3. trending keywords
4. article-volume chart
5. source comparison
6. latest articles

### Phase 10 — Deployment

```text
Web        → Vercel
Database   → Supabase
Scheduler  → GitHub Actions
Crawler    → Python CLI
```

### Phase 11 — Expansion

Add more sources and advanced NLP only after the core pipeline is reliable.

---

## 38. MVP Success Criteria

### Crawler

- At least one source can be crawled reliably.
- Duplicate articles are handled.
- Failed articles can be retried.
- Same code works locally and in GitHub Actions.
- Daily scheduled execution works.
- Manual execution works.

### Database

- Article data is stored correctly.
- Processing status is tracked.
- Keyword data is queryable.
- Daily aggregates are generated.
- Crawl execution history is available.

### Dashboard

- Dashboard is deployed on Vercel.
- Data is read successfully from Supabase.
- Keyword statistics are displayed.
- Article volume is displayed.
- Source comparison is displayed.
- Latest articles are browsable.
- Queries are bounded/paginated.

### Recovery

- A failed run can be rerun.
- The crawler can be run from a laptop.
- Stored-but-unprocessed articles can be processed without recrawling them.

---

## 39. Long-Term Vision

Crab News can gradually evolve from a crawler into a compact news intelligence platform.

```text
Stage 1
News Crawler
    ↓
Word Frequency

Stage 2
Keyword Trends
    ↓
Source Comparison

Stage 3
Entities
    ↓
Topics
    ↓
Co-occurrence

Stage 4
Similar Articles
    ↓
Event Clustering

Stage 5
Historical News Intelligence
    ↓
Search
    ↓
Timelines
    ↓
Cross-source Analysis
```

The core pipeline remains:

```text
Collect
  ↓
Normalize
  ↓
Process
  ↓
Analyze
  ↓
Aggregate
  ↓
Visualize
```

---

## 40. Final Architecture Summary

```text
Frontend
    Next.js
    React
    TypeScript
       │
       ▼
    Vercel
       │
       ▼
Supabase PostgreSQL
       ▲
       │
Python Crawler CLI
       ▲
       │
 ┌─────┴─────┐
 │           │
GitHub     Local
Actions    Laptop
```

### Core principle

> **The crawler is a standalone Python application. GitHub Actions is only one executor of that application.**

This enables:

```text
Automatic daily crawl
        +
Manual GitHub Actions crawl
        +
Local emergency crawl
        +
Local debugging/testing
        +
Retry without unnecessary recrawling
```

The web application then reads processed and aggregated data from Supabase so that dashboard requests remain lightweight and predictable.

---

## 41. Initial Implementation Priority

```text
1. Supabase schema
2. Python crawler CLI
3. First source adapter
4. Article persistence
5. Processing pipeline
6. Keyword aggregation
7. crawl_runs + retry
8. GitHub Actions cron
9. GitHub Actions manual dispatch
10. Next.js dashboard
11. Vercel deployment
12. Additional sources
13. Advanced NLP
```

The project should stabilize the basic:

```text
crawl → store → process → aggregate → visualize
```

pipeline before adding sophisticated NLP or large-scale crawling.

---

## 42. Final MVP Stack

| Area | Technology |
|---|---|
| Crawler | Python |
| Crawler execution | GitHub Actions + Local laptop |
| Database | Supabase PostgreSQL |
| Frontend | Next.js |
| UI | React |
| Language | TypeScript |
| Web deployment | Vercel |
| Scheduler | GitHub Actions cron |
| Manual execution | GitHub Actions workflow dispatch |
| Data model | Raw → Processed → Aggregated |

---

**Project status:** Planning / ready for implementation design and scaffolding.
