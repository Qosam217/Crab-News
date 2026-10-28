# Crab News — Python Crawler & Data Pipeline

CLI engine mandiri untuk melakukan crawling berita, pembersihan teks, ekstraksi kata kunci Bahasa Indonesia, dan agregasi data harian ke Supabase PostgreSQL.

Menggunakan arsitektur **Pagination Index Crawler** dengan filter rentang tanggal (*date range*) presisi dan mekanisme *early stopping* cerdas untuk penelusuran artikel historis.

---

## 📰 Sumber Berita yang Didukung (7 Sources)

| Sumber | Slug | Tipe Penelusuran | URL Indeks / Pagination | Catatan |
| :--- | :--- | :--- | :--- | :--- |
| **Antara News** | `antara` | Pagination Indeks | `https://www.antaranews.com/terkini/{page}` | **Utama** (auto-scraping harian aktif) |
| **CNN Indonesia** | `cnn-indonesia` | Pagination Indeks | `https://www.cnnindonesia.com/indeks/2?page={page}` | Timestamp presisi hingga detik dari URL |
| **Detik News** | `detik` | Pagination Indeks | `https://news.detik.com/indeks?page={page}` | Timestamp dari atribut `d-time` / `title` |
| **Kompas** | `kompas` | Pagination Indeks | `https://news.kompas.com/?source=navbar&page={page}` | Timestamp dari URL pattern `/read/YYYY/MM/DD/...` |
| **Tempo** | `tempo` | Pagination + Fallback | `https://www.tempo.co/indeks?page={page}` | Dilengkapi otomatis fallback RSS jika diblokir Cloudflare |
| **Jawa Pos** | `jawapos` | GraphQL API / Index | `https://api.jawapos.com/api-jp-graphql` | Filter rentang tanggal via query GraphQL internal |
| **IDN Times** | `idntimes` | Per-Date Pagination | `https://www.idntimes.com/index?category=all&date={date}&page={page}` | Penelusuran indeks per tanggal publikasi |

---

Note: Untuk scraping by tanggal perlu perbaikan khusus sources Antara, Tempo, dan Kompas.

## 🚀 Quickstart

### Menggunakan `uv` (Direkomendasikan)
```bash
cd crawler
# Sinkronisasi environment
uv sync

# Sinkronisasi environment test
uv sync --extra dev

# Running tests
uv run pytest

# 1. Menjalankan crawler untuk 1 sumber spesifik (misal: antara)
uv run python -m crab_news.cli --source antara

# 2. Menjalankan crawler dengan rentang tanggal tertentu (Backfill / Date Range)
uv run python -m crab_news.cli --source cnn-indonesia --from-date 2026-10-15 --to-date 2026-10-18 --limit 50

# 3. Menjalankan crawler seluruh sumber berita aktif
uv run python -m crab_news.cli --all-sources

# 4. Mode Dry-Run (crawling & ekstraksi tanpa menyimpan ke database)
uv run python -m crab_news.cli --source kompas --dry-run

# 5. Agregasi kata kunci harian (Precomputed Daily Keywords)
uv run python -m crab_news.cli --aggregate
# atau untuk tanggal spesifik:
uv run python -m crab_news.cli --aggregate --aggregate-date 2026-10-18

# 6. Memproses ulang artikel pending / retry failed
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

---

## ⚙️ Opsi Perintah CLI

| Argumen | Deskripsi | Contoh |
| :--- | :--- | :--- |
| `-s`, `--source` | Menjalankan crawler untuk slug portal berita spesifik. | `--source antara` |
| `-a`, `--all-sources` | Menjalankan crawler untuk seluruh portal berita yang aktif. | `--all-sources` |
| `--from-date` | Batas awal tanggal publikasi artikel (inklusif, format `YYYY-MM-DD`). Harus dipakai bersama `--to-date`. | `--from-date 2026-10-01` |
| `--to-date` | Batas akhir tanggal publikasi artikel (inklusif, format `YYYY-MM-DD`). | `--to-date 2026-10-07` |
| `--limit` | Batas maksimum artikel yang diambil per sumber (default: 30). | `--limit 100` |
| `--dry-run` | Menjalankan proses discovery, ekstraksi, dan tokenisasi tanpa menyimpan ke database. | `--dry-run` |
| `--aggregate` | Menghitung statistik frekuensi kata harian untuk hari ini. | `--aggregate` |
| `--aggregate-date` | Menghitung statistik frekuensi kata untuk tanggal spesifik (`YYYY-MM-DD`). | `--aggregate-date 2026-10-18` |
| `--process-pending` | Memproses artikel berstatus pending yang belum diekstrak kata kuncinya. | `--process-pending` |
| `--retry-failed` | Mencoba kembali pemrosesan artikel yang sebelumnya gagal. | `--retry-failed` |

> [!TIP]
> **Mekanisme Early Stopping**:
> Karena halaman indeks berita terurut menurun (terbaru ke terlama), ketika crawler menemukan artikel dengan tanggal publikasi yang lebih tua dari `--from-date`, proses penelusuran halaman (*pagination loop*) akan langsung dihentikan otomatis untuk menghemat bandwidth dan waktu eksekusi.

---

## ⚙️ Environment Variables

Salin `.env.example` menjadi `.env` di dalam folder `crawler/`:
```bash
cp .env.example .env
```
Variabel yang diperlukan:
* `SUPABASE_URL`: Endpoint REST project Supabase.
* `SUPABASE_SERVICE_ROLE_KEY`: Service role key untuk hak akses penuh penulisan data crawler.
* `LOG_LEVEL`: Tingkat log (`INFO`, `DEBUG`, `WARNING`).
* `RATE_LIMIT_DELAY_SECONDS`: Jeda waktu antar request (default: `1.0` detik).

---

## 🧪 Testing

Jalankan seluruh rangkaian unit testing menggunakan `pytest`:
```bash
uv run pytest
```
Testing mencakup:
* Normalisasi URL & deduplikasi konten hash.
* Parser waktu & tanggal Bahasa Indonesia (relatif, absolut, timestamp URL).
* Adapter pagination, filter rentang tanggal, dan simulasi Cloudflare fallback.
* Pembersihan teks HTML dan tokenisasi stopwords.
