# Crab News — Project & Repository Management Plan

> **Repository model:** Monorepo  
> **Repository name:** `crab-news`  
> **Primary components:** Web Dashboard, Python Crawler, GitHub Actions  
> **Database:** Supabase PostgreSQL  
> **Web deployment:** Vercel

---

## Daftar Isi
- [1. Repository Strategy](#1-repository-strategy)
- [2. Why One Repository?](#2-why-one-repository)
- [3. Top-Level Repository Structure](#3-top-level-repository-structure)
- [4. Responsibility of Each Directory](#4-responsibility-of-each-directory)
  - [/web](#web)
  - [/crawler](#crawler)
  - [/supabase](#supabase)
  - [/.github](#github)
  - [/docs](#docs)
  - [/scripts](#scripts)
- [5. Application Boundaries](#5-application-boundaries)
- [6. Recommended Crawler Structure](#6-recommended-crawler-structure)
- [7. GitHub Actions Management](#7-github-actions-management)
- [8. Vercel Management](#8-vercel-management)
- [9. Supabase Management](#9-supabase-management)
- [10. Environment and Secrets](#10-environment-and-secrets)
- [11. Root .gitignore](#11-root-gitignore)
- [12. Dependency Management](#12-dependency-management)
- [13. README Strategy](#13-readme-strategy)
- [14. Documentation Hierarchy](#14-documentation-hierarchy)
- [15. Feature Management Across the Monorepo](#15-feature-management-across-the-monorepo)
- [16. Branching Strategy](#16-branching-strategy)
- [17. Commit Convention](#17-commit-convention)
- [18. Issue Management](#18-issue-management)
- [19. GitHub Project Board](#19-github-project-board)
- [20. Feature Decomposition](#20-feature-decomposition)
- [21. Pull Request Rules](#21-pull-request-rules)
- [22. File Placement Rules](#22-file-placement-rules)
- [23. Local Development Model](#23-local-development-model)
- [24. Crawler Operational Modes](#24-crawler-operational-modes)
- [25. Recovery Management](#25-recovery-management)
- [26. Database Change Workflow](#26-database-change-workflow)
- [27. Testing Organization](#27-testing-organization)
- [28. Monorepo Dependency Rules](#28-monorepo-dependency-rules)
- [29. Shared Contracts](#29-shared-contracts)
- [30. Recommended Initial Repository Creation Order](#30-recommended-initial-repository-creation-order)
- [31. Recommended MVP Repository](#31-recommended-mvp-repository)
- [32. Recommended Long-Term Repository](#32-recommended-long-term-repository)
- [33. Final Project Management Model](#33-final-project-management-model)
- [34. Core Management Rule](#34-core-management-rule)
- [35. Final Recommendation](#35-final-recommendation)

---

## 1. Repository Strategy

Crab News should use **one GitHub repository** for the whole project.

The repository contains:

- Next.js web dashboard
- Python crawler and processing pipeline
- GitHub Actions workflows
- Supabase database migrations and seeds
- Shared documentation
- Tests
- Project-level configuration

This is a **monorepo**: the components stay logically separated, but they share one source repository, issue tracker, project board, and documentation base.

The core dependency flow is:

```text
News Websites
     ↓
Python Crawler
     ↓
Supabase PostgreSQL
     ↓
Next.js Dashboard
     ↓
Vercel
```

GitHub Actions is an executor for the crawler:

```text
GitHub Actions
      ↓
Python Crawler
      ↓
Supabase
```

The same Python crawler must also work locally:

```text
Local Laptop
     ↓
Python Crawler
     ↓
Supabase
```

---

# 2. Why One Repository?

A single repository is appropriate because Web, Crawler, Database, and Automation are tightly related parts of one product.

Advantages:

- One GitHub project
- One issue tracker
- One Project Board
- One architecture source of truth
- Database changes can be reviewed together with application changes
- A feature can update crawler + database + dashboard in one Pull Request
- Easier solo/small-team development
- Easier deployment configuration
- Easier local recovery of the crawler

Separate repositories would add management overhead without a strong benefit at the current project scale.

---

# 3. Top-Level Repository Structure

Recommended initial structure:

```text
crab-news/
│
├── .github/
│   ├── workflows/
│   │   ├── crawler.yml
│   │   ├── crawler-ci.yml
│   │   └── web-ci.yml
│   └── ISSUE_TEMPLATE/
│       ├── bug_report.md
│       ├── crawler_source.md
│       └── feature_request.md
│
├── web/
│   ├── app/
│   ├── components/
│   ├── features/
│   ├── hooks/
│   ├── lib/
│   ├── types/
│   ├── public/
│   ├── tests/
│   ├── package.json
│   ├── package-lock.json
│   ├── next.config.ts
│   └── README.md
│
├── crawler/
│   ├── src/
│   │   └── crab_news/
│   │       ├── cli.py
│   │       ├── config/
│   │       ├── sources/
│   │       ├── extractor/
│   │       ├── processor/
│   │       ├── analyzer/
│   │       ├── database/
│   │       └── utils/
│   ├── tests/
│   ├── pyproject.toml
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
│
├── supabase/
│   ├── migrations/
│   ├── seed/
│   └── README.md
│
├── docs/
│   ├── architecture/
│   ├── crawler/
│   ├── database/
│   ├── web/
│   └── operations/
│
├── scripts/
│   └── README.md
│
├── .editorconfig
├── .gitignore
├── README.md
├── PROJECT_PLAN.md
└── PROJECT_MANAGEMENT.md
```

The structure should grow only when the responsibility actually exists. Do not create a large number of empty folders just for future possibilities.

---

# 4. Responsibility of Each Directory

## `/web`

Contains the user-facing Next.js application.

Responsibilities:

- Dashboard UI
- Charts and visualizations
- Article explorer
- Keyword explorer
- Filters
- Pagination
- Supabase read operations
- Client/server UI logic
- Web tests

The web application must **not** contain crawler logic.

---

## `/crawler`

Contains the complete Python data pipeline.

Responsibilities:

- Source discovery
- RSS retrieval
- HTML retrieval
- Article extraction
- Normalization
- Duplicate detection
- Text processing
- Keyword analysis
- Aggregation
- Supabase writes
- Crawl run tracking
- Retry/reprocessing
- CLI commands

The crawler must be independently executable:

```bash
cd crawler
python -m crab_news
```

GitHub Actions should call this application rather than contain the crawler implementation itself.

---

## `/supabase`

Contains version-controlled database definitions.

Responsibilities:

- SQL migrations
- Seed data
- Database documentation
- Optional local Supabase configuration if introduced later

Example:

```text
supabase/
├── migrations/
│   ├── 001_initial_schema.sql
│   ├── 002_add_processing_status.sql
│   ├── 003_add_daily_keywords.sql
│   └── 004_add_crawl_runs.sql
└── seed/
    └── seed_sources.sql
```

Every schema change should have a migration file committed to Git.

---

## `/.github`

Contains GitHub-specific automation only.

Responsibilities:

- Scheduled crawler execution
- Manual crawler execution
- CI checks
- Issue templates
- Optional Pull Request automation

GitHub Actions should orchestrate the application, not become the application itself.

---

## `/docs`

Contains technical documentation too detailed for the root README.

Recommended areas:

```text
docs/
├── architecture/
├── crawler/
├── database/
├── web/
└── operations/
```

---

## `/scripts`

Contains small project-maintenance utilities that are not core application logic.

Examples:

- local setup helpers
- validation helpers
- data maintenance scripts
- development utilities

Do not put normal crawler business logic here.

---

# 5. Application Boundaries

The components should have explicit boundaries.

### Web

```text
User
 ↓
Next.js
 ↓
Supabase Read
```

### Crawler

```text
News Website / RSS
 ↓
Python Crawler
 ↓
Supabase Write
```

### GitHub Actions

```text
Schedule / Manual Trigger
 ↓
Run Python Crawler
 ↓
Exit
```

This avoids unnecessary coupling between frontend, crawler, and automation.

---

# 6. Recommended Crawler Structure

```text
crawler/
├── src/
│   └── crab_news/
│       ├── cli.py
│       ├── config/
│       ├── sources/
│       │   ├── base.py
│       │   ├── source_a.py
│       │   └── source_b.py
│       ├── extractor/
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
│       │   └── repositories/
│       └── utils/
└── tests/
```

Source-specific selectors and extraction logic belong under `sources/`, not scattered across the rest of the project.

---

# 7. GitHub Actions Management

Recommended workflows:

```text
.github/workflows/
├── crawler.yml
├── crawler-ci.yml
└── web-ci.yml
```

## `crawler.yml`

Runs the production crawler.

It should support:

```text
schedule
+
workflow_dispatch
```

Conceptual flow:

```text
GitHub trigger
 ↓
Checkout repository
 ↓
Setup Python
 ↓
Install crawler dependencies
 ↓
Load GitHub Secrets
 ↓
python -m crab_news
 ↓
Supabase
 ↓
Finish
```

Manual inputs can later include:

```text
source = all | specific source
mode   = latest | retry | process
run_id = optional
```

## `crawler-ci.yml`

Validates crawler code:

```text
Install dependencies
 ↓
Run tests
 ↓
Optional lint/type checks
```

It should not perform a production crawl.

## `web-ci.yml`

Validates the Next.js application:

```text
Install dependencies
 ↓
Lint
 ↓
Type check
 ↓
Test
 ↓
Build
```

It should not invoke the production crawler.

---

# 8. Vercel Management

Vercel should deploy only the `/web` application.

Conceptually:

```text
crab-news repository
        ↓
      Vercel
        ↓
      /web
```

The Vercel project should use `web/` as its application/root directory so that crawler code and GitHub workflow files are not treated as part of the frontend build.

The web application reads prepared data from Supabase.

---

# 9. Supabase Management

Supabase is the persistent data layer.

Recommended logical layers:

```text
RAW
 ↓
PROCESSED
 ↓
AGGREGATED
 ↓
DASHBOARD
```

Initial tables:

```text
sources
articles
article_words
daily_keywords
crawl_runs
```

The database schema should be treated as part of the source code and versioned in `/supabase/migrations`.

---

# 10. Environment and Secrets

Real secrets must never be committed.

Recommended files:

```text
web/.env.local
crawler/.env
```

Committed templates:

```text
web/.env.example
crawler/.env.example
```

Typical crawler variables:

```env
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
```

Typical web variables may include only the keys safe for the relevant client/server context.

The Supabase service-role key must never be exposed to the browser.

GitHub Actions should receive secrets through GitHub Secrets, not from committed files.

---

# 11. Root `.gitignore`

The root `.gitignore` should cover both Node.js and Python environments.

Recommended categories:

```gitignore
# Environment
.env
.env.*
!.env.example

# Node
node_modules/
.next/
out/
dist/

# Python
__pycache__/
*.py[cod]
.venv/
venv/
.pytest_cache/
.mypy_cache/

# IDE
.idea/
.vscode/

# OS
.DS_Store
Thumbs.db

# Logs
*.log
```

The exact file should be expanded according to the tooling actually used.

---

# 12. Dependency Management

Each component manages its own dependencies.

## Web

```text
web/package.json
web/package-lock.json
```

## Crawler

```text
crawler/pyproject.toml
crawler/requirements.txt
```

Do not create one mixed dependency file at repository root.

---

# 13. README Strategy

There should be a README at three useful levels.

## Root `README.md`

Answers:

- What is Crab News?
- What problem does it solve?
- What is the architecture?
- How is the repository structured?
- How do I start each component?
- Where is deployment handled?

## `web/README.md`

Explains the frontend:

- setup
- scripts
- environment variables
- development
- deployment notes

## `crawler/README.md`

Explains the crawler:

- setup
- CLI commands
- local execution
- adding a source
- retry/reprocessing
- environment variables

## `supabase/README.md`

Explains:

- migrations
- seed data
- schema workflow
- database development

---

# 14. Documentation Hierarchy

Use the following rule:

```text
README.md
    ↓
What is the project and how do I start?

PROJECT_PLAN.md
    ↓
What are we building and why?

PROJECT_MANAGEMENT.md
    ↓
How is the repository and project organized?

docs/
    ↓
How does a specific technical area work?
```

This prevents `README.md` from becoming an oversized technical specification.

---

# 15. Feature Management Across the Monorepo

A feature may change multiple directories.

Example: **Trending Keywords**

```text
Feature: Trending Keywords
│
├── crawler/
│   └── implement trend calculation
│
├── supabase/
│   └── add/update aggregate schema
│
├── web/
│   └── add chart/table
│
└── docs/
    └── document calculation
```

These changes should normally be handled in one feature branch and one Pull Request when they represent one logical feature.

This is one of the main benefits of the monorepo approach.

---

# 16. Branching Strategy

For a solo or small project, keep branching simple:

```text
main
 ↑
feature/*
fix/*
chore/*
```

Examples:

```text
feature/trending-keywords
feature/add-news-source
feature/article-explorer
fix/rss-date-parser
fix/duplicate-article
chore/update-dependencies
```

Avoid many long-lived branches.

---

# 17. Commit Convention

Use clear conventional-style commit messages.

Examples:

```text
feat: add article crawler
feat: add keyword aggregation
feat: add dashboard keyword chart

fix: handle missing publication date
fix: prevent duplicate articles

chore: configure crawler workflow
chore: update crawler dependencies

docs: update repository architecture
```

Commits should describe the actual logical change rather than the folder edited.

Prefer:

```text
feat: add trending keyword analysis
```

over:

```text
update crawler and web folders
```

---

# 18. Issue Management

GitHub Issues should describe work independently of file locations.

Useful labels:

```text
feature
bug
crawler
web
database
infrastructure
documentation
maintenance
```

Examples:

```text
[CRAWLER] Add source adapter for Source A
[CRAWLER] Handle missing publication date
[WEB] Add trending keyword chart
[DB] Add daily keyword index
[ACTIONS] Add manual crawler dispatch
```

---

# 19. GitHub Project Board

A simple project board is enough for the MVP.

Recommended columns:

```text
Backlog
   ↓
Todo
   ↓
In Progress
   ↓
Review
   ↓
Done
```

Add `Blocked` only when it becomes useful.

Tasks should normally be small enough to finish within a focused development cycle.

---

# 20. Feature Decomposition

Large features should be split by responsibility.

Example:

```text
Parent Issue
└── Trending Keywords

    ├── crawler
    │   └── calculate trend score
    │
    ├── database
    │   └── store aggregate result
    │
    ├── web
    │   └── render trend visualization
    │
    └── docs
        └── document formula
```

This makes project progress visible without mixing unrelated work in a single task.

---

# 21. Pull Request Rules

Each Pull Request should explain:

```text
What changed?
Why was it needed?
Which components changed?
How was it tested?
```

For a cross-component feature:

```text
Changed:
- crawler
- supabase
- web
- docs

Tested:
- Python tests
- local crawler sample
- database query
- Next.js build
```

The PR should also mention database migrations when a schema change is involved.

---

# 22. File Placement Rules

When adding a new file, classify it first.

| Question | Location |
|---|---|
| User-facing web UI? | `web/` |
| Python crawl/process logic? | `crawler/` |
| Database schema/seed? | `supabase/` |
| GitHub automation? | `.github/` |
| Technical documentation? | `docs/` |
| General project overview? | root `README.md` |
| Project scope/architecture plan? | `PROJECT_PLAN.md` |
| Repository/project management rules? | `PROJECT_MANAGEMENT.md` |
| Small maintenance utility? | `scripts/` |

Do not put files in the repository root unless they are truly project-wide.

---

# 23. Local Development Model

The entire project can be developed from one repository.

```text
Developer Laptop
│
├── /web
│   └── Next.js dev server
│
├── /crawler
│   └── Python CLI
│
└── /supabase
    └── Database migrations
```

The developer can run the web and crawler independently.

This also provides the emergency recovery path:

```text
GitHub Actions unavailable/undesirable
            ↓
      Run crawler locally
            ↓
          Supabase
```

---

# 24. Crawler Operational Modes

The repository should support multiple crawler operations through one application.

Conceptual commands:

```bash
python -m crab_news
python -m crab_news --source source_a
python -m crab_news --retry-failed
python -m crab_news --process-pending
python -m crab_news --source source_a --process
python -m crab_news --dry-run
```

These modes allow the same codebase to support:

- normal daily crawl
- targeted source crawl
- local debugging
- retrying failed processing
- processing stored articles without fetching them again

---

# 25. Recovery Management

The repository design must support three operational cases.

## Case A — GitHub Actions Failure

```text
Workflow fails
 ↓
Inspect workflow logs / crawl_runs
 ↓
Run workflow again if appropriate
```

## Case B — Source HTML Changed

```text
Extraction fails
 ↓
Fix source adapter locally
 ↓
Run local test/crawl
 ↓
Verify Supabase
 ↓
Commit fix
```

## Case C — Processing Failure

```text
Articles already stored
 ↓
Some records = failed
 ↓
Retry processing
 ↓
No need to recrawl those pages
```

This distinction between **crawl failure** and **processing failure** should be preserved in the application architecture.

---

# 26. Database Change Workflow

Recommended process:

```text
Need database change
 ↓
Create migration file
 ↓
Test migration
 ↓
Update crawler/web code
 ↓
Run tests
 ↓
Commit together
```

Example:

```text
Add `trend_score`

supabase/
  migration → add column

crawler/
  analyzer → calculate value

web/
  feature → display value

docs/
  → document meaning
```

One logical feature should keep the schema, backend processing, and UI behavior synchronized.

---

# 27. Testing Organization

Tests remain inside their component.

```text
crawler/tests/
├── sources/
├── extractor/
├── processor/
└── analyzer/

web/tests/
├── components/
├── features/
└── integration/
```

CI should run component tests without triggering a production crawl.

---

# 28. Monorepo Dependency Rules

### Web may depend on

```text
Supabase
web-local modules
types generated from the database if introduced later
```

### Crawler may depend on

```text
Supabase
Python crawler modules
```

### GitHub Actions may depend on

```text
crawler
```

### Crawler must not depend on

```text
Next.js
Vercel runtime
browser UI
```

### Web must not depend on

```text
Python runtime
crawler implementation details
```

This prevents the monorepo from turning into one tightly coupled application.

---

# 29. Shared Contracts

Initially, avoid creating a complex cross-language shared package.

Use:

```text
Python → dataclasses / Pydantic models
TypeScript → interfaces / types
```

The primary shared contract is the **Supabase schema**.

If the project later needs stronger synchronization, generated database types can be introduced rather than manually duplicating large contracts.

---

# 30. Recommended Initial Repository Creation Order

Create the repository in this order:

```text
1. Root repository
2. /web
3. /crawler
4. /supabase
5. /.github/workflows
6. /docs
7. Root README
8. PROJECT_PLAN.md
9. PROJECT_MANAGEMENT.md
```

Then implement functionality in this order:

```text
Database schema
    ↓
Crawler core
    ↓
First source
    ↓
Processing
    ↓
Aggregation
    ↓
GitHub Actions
    ↓
Dashboard
    ↓
Deployment
```

---

# 31. Recommended MVP Repository

At the beginning, the repository can be intentionally small:

```text
crab-news/
├── .github/
│   └── workflows/
│       └── crawler.yml
│
├── crawler/
│   ├── src/
│   ├── tests/
│   ├── pyproject.toml
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
│
├── web/
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── package.json
│   └── README.md
│
├── supabase/
│   ├── migrations/
│   ├── seed/
│   └── README.md
│
├── docs/
│   └── architecture/
│       └── overview.md
│
├── .gitignore
├── README.md
├── PROJECT_PLAN.md
└── PROJECT_MANAGEMENT.md
```

Add `crawler-ci.yml`, `web-ci.yml`, issue templates, scripts, and specialized documentation once they become useful.

---

# 32. Recommended Long-Term Repository

After the MVP grows:

```text
crab-news/
│
├── .github/
│   ├── workflows/
│   │   ├── crawler.yml
│   │   ├── crawler-ci.yml
│   │   └── web-ci.yml
│   └── ISSUE_TEMPLATE/
│
├── web/
│   ├── app/
│   ├── components/
│   ├── features/
│   ├── hooks/
│   ├── lib/
│   ├── types/
│   ├── public/
│   └── tests/
│
├── crawler/
│   ├── src/
│   │   └── crab_news/
│   │       ├── cli.py
│   │       ├── config/
│   │       ├── sources/
│   │       ├── extractor/
│   │       ├── processor/
│   │       ├── analyzer/
│   │       ├── database/
│   │       └── utils/
│   └── tests/
│
├── supabase/
│   ├── migrations/
│   ├── seed/
│   └── README.md
│
├── docs/
│   ├── architecture/
│   ├── crawler/
│   ├── database/
│   ├── web/
│   └── operations/
│
├── scripts/
├── .editorconfig
├── .gitignore
├── README.md
├── PROJECT_PLAN.md
└── PROJECT_MANAGEMENT.md
```

---

# 33. Final Project Management Model

Crab News should be treated as **one product with multiple technical components**:

```text
                         Crab News
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
          ▼                 ▼                 ▼
         Web             Crawler          Automation
       /web              /crawler          /.github
          │                 │                 │
          └───────────┬─────┴─────────────────┘
                      │
                      ▼
                  /supabase
                      │
                      ▼
                PostgreSQL Data
```

The repository is therefore the single source of truth for:

```text
Code
Database schema
Automation
Documentation
Tests
Project management
```

---

# 34. Core Management Rule

Whenever adding a file or feature, determine its responsibility first:

```text
Web UI                 → web/
Crawler logic          → crawler/
Database schema        → supabase/
GitHub automation      → .github/
Technical documentation→ docs/
General project info   → root
Maintenance utility    → scripts/
```

Example:

```text
"Add a chart"
→ web/

"Support another news website"
→ crawler/

"Add a column to articles"
→ supabase/

"Run crawler every day"
→ .github/

"Explain trend calculation"
→ docs/
```

The project should remain one repository, while each directory has one clear responsibility.

---

# 35. Final Recommendation

**Use one GitHub repository for Crab News.**

The recommended mental model is:

```text
                ONE GITHUB REPOSITORY
                       │
       ┌───────────────┼────────────────┐
       │               │                │
       ▼               ▼                ▼
     /web           /crawler         /.github
   Next.js          Python CLI       Actions
       │               │                │
       │               └───────┐        │
       │                       ▼        │
       └─────────────────→ Supabase ←──┘
```

The repository should **not** be treated as three projects merely sharing a folder. It should be treated as one product whose components have explicit boundaries.

The most important rule is:

> **Keep application responsibilities separate, but keep the project source of truth together.**

This gives Crab News a simple development model now while leaving room to grow into a larger news-analysis platform later.
