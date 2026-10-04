# 🦀 Crab News

> News crawling, Indonesian text processing, keyword analysis, and trend intelligence platform.

[![Crawler CI](https://github.com/Qosam217/Crab-News/actions/workflows/crawler-ci.yml/badge.svg)](https://github.com/Qosam217/Crab-News/actions/workflows/crawler-ci.yml)
[![Web CI](https://github.com/Qosam217/Crab-News/actions/workflows/web-ci.yml/badge.svg)](https://github.com/Qosam217/Crab-News/actions/workflows/web-ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-rose.svg)](LICENSE)

---

## 🏛️ Arsitektur Monorepo

Crab News dirancang dengan model monorepo modular tanpa ketergantungan runtime silang:

```text
News Websites / RSS (Antara, CNN, Kompas, Detik, Tempo)
                    │
                    ▼
          ┌───────────────────┐
          │ Python Crawler CLI│
          │  (uv / pyproject) │
          └─────────┬─────────┘
                    │ (Scheduled via GitHub Actions or Local)
                    ▼
          ┌───────────────────┐
          │     Supabase      │
          │ PostgreSQL + RLS  │
          └─────────┬─────────┘
                    │ (Public read queries)
                    ▼
          ┌───────────────────┐
          │ Next.js Dashboard │
          │(Tailwind+Recharts)│
          └─────────┬─────────┘
                    │
                    ▼
                  Vercel
```

---

## 📁 Struktur Direktori

```text
Crab-News/
├── .github/                 # GitHub Actions Workflows & Issue Templates
│   └── workflows/
│       ├── crawler.yml      # Automated Daily Cron (00:00 UTC)
│       ├── crawler-ci.yml   # Python test & linting
│       └── web-ci.yml       # Next.js build & type check
│
├── crawler/                 # Python News Crawler & Text Analysis Engine
│   ├── src/crab_news/       # Core modules (CLI, sources, extractor, processor, analyzer)
│   ├── tests/               # Unit & integration tests
│   ├── pyproject.toml       # uv / pip dependency configuration
│   └── requirements.txt
│
├── supabase/                # PostgreSQL Database Migrations & Seeds
│   ├── migrations/          # 001_initial_schema.sql
│   └── seed/                # seed_sources.sql (Initial news sources)
│
├── web/                     # Next.js 15 App Router Dashboard UI
│   ├── app/                 # Overview, Articles, Keywords, Trends, Sources, Crawl Runs
│   ├── components/          # Reusable UI components & charts
│   ├── lib/                 # Supabase client & utilities
│   └── types/               # TypeScript data definitions
│
├── docs/                    # Technical & Architectural Documentation
│   ├── PROJECT_PLAN.md
│   └── PROJECT_MANAGEMENT.md
│
├── .editorconfig
├── .gitignore
└── README.md
```

---

## 🚀 Panduan Memulai Cepat (Quickstart)

### 1. Inisialisasi Database (Supabase)
1. Buat project baru di [Supabase Dashboard](https://supabase.com/dashboard).
2. Jalankan skrip DDL migrasi dari [`supabase/migrations/001_initial_schema.sql`](supabase/migrations/001_initial_schema.sql) di **SQL Editor**.
3. Jalankan seed sumber berita dari [`supabase/seed/seed_sources.sql`](supabase/seed/seed_sources.sql).

---

### 2. Menjalankan Python Crawler (`crawler/`)

Pastikan menggunakan Python 3.10+ dengan [`uv`](https://github.com/astral-sh/uv) (direkomendasikan):

```bash
cd crawler
cp .env.example .env
# Isi SUPABASE_URL dan SUPABASE_SERVICE_ROLE_KEY di .env

# Jalankan crawler untuk seluruh sumber aktif
uv run python -m crab_news.cli --all-sources

# Jalankan crawler untuk 1 sumber spesifik (misal: antara)
uv run python -m crab_news.cli --source antara

# Mode Dry-Run (tanpa write ke database)
uv run python -m crab_news.cli --source kompas --dry-run

# Menjalankan precomputed daily keyword aggregation
uv run python -m crab_news.cli --aggregate

# Menjalankan unit tests
uv run pytest
```

---

### 3. Menjalankan Web Dashboard (`web/`)

Pastikan Node.js 18+ terinstall:

```bash
cd web
cp .env.example .env.local
# Isi NEXT_PUBLIC_SUPABASE_URL dan NEXT_PUBLIC_SUPABASE_ANON_KEY di .env.local

npm install
npm run dev
```

Buka [http://localhost:3000](http://localhost:3000) pada browser Anda.

---

## ⚙️ Automated GitHub Actions Workflow

Untuk mengaktifkan automated crawler harian di GitHub Actions:
1. Buka repositori di GitHub -> **Settings** -> **Secrets and variables** -> **Actions**.
2. Tambahkan Repository Secrets:
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_ROLE_KEY`
3. Workflow di [`.github/workflows/crawler.yml`](.github/workflows/crawler.yml) akan otomatis berjalan setiap hari pukul 00:00 UTC (07:00 WIB) atau dapat dipicu secara manual melalui tab **Actions** -> **Run workflow**.

---

## 📜 Lisensi

Project ini dilisensikan di bawah [MIT License](LICENSE).