# Crab News — Python Crawler & Data Pipeline

CLI engine mandiri untuk melakukan crawling berita, pembersihan teks, ekstraksi kata kunci Bahasa Indonesia, dan agregasi data harian ke Supabase PostgreSQL.

## 🚀 Quickstart

### Menggunakan `uv` (Direkomendasikan)
```bash
cd crawler
# Sinkronisasi environment
uv sync

# Menjalankan crawler seluruh sumber berita aktif
uv run python -m crab_news.cli --all-sources

# Menjalankan crawler untuk 1 sumber spesifik (misal: antara)
uv run python -m crab_news.cli --source antara

# Mode Dry-Run (crawling tanpa menyimpan ke database)
uv run python -m crab_news.cli --source kompas --dry-run

# Memproses ulang artikel pending / retry failed
uv run python -m crab_news.cli --process-pending
uv run python -m crab_news.cli --retry-failed
```

### Menggunakan standard `venv` + `pip`
```bash
cd crawler
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
python -m crab_news.cli --help
```

## ⚙️ Environment Variables

Salin `.env.example` menjadi `.env` di dalam folder `crawler/`:
```bash
cp .env.example .env
```
Isi kredensial Supabase (`SUPABASE_URL` dan `SUPABASE_SERVICE_ROLE_KEY`).

## 🧪 Testing

```bash
uv run pytest
```
