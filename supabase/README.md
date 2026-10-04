# Supabase Database Migrations & Seeds

Direktori ini berisi skema database PostgreSQL untuk platform **Crab News**.

## 📁 Struktur

- `migrations/`: Skrip DDL untuk inisialisasi tabel, indeks, constraint, dan RLS policies.
  - `001_initial_schema.sql`: Skema utama tabel `sources`, `articles`, `article_words`, `daily_keywords`, dan `crawl_runs`.
- `seed/`: Data awal untuk sumber berita.
  - `seed_sources.sql`: Seed untuk 5 sumber berita awal Indonesia (Antara, CNN Indonesia, Kompas, Detik, Tempo).

## 🚀 Cara Menjalankan Migrasi ke Cloud Supabase

1. Buka dashboard project Anda di [Supabase Dashboard](https://supabase.com/dashboard).
2. Masuk ke menu **SQL Editor**.
3. Buka dan salin isi file `migrations/001_initial_schema.sql`, lalu klik **Run**.
4. Buka dan salin isi file `seed/seed_sources.sql`, lalu klik **Run**.

## 🔑 Kunci Akses (Security & RLS)

- **Web Dashboard:** Menggunakan `SUPABASE_ANON_KEY` (akses dibatasi hanya membaca/SELECT via Row Level Security).
- **Python Crawler:** Menggunakan `SUPABASE_SERVICE_ROLE_KEY` (memiliki izin penuh untuk insert/update artikel dan metadata agregasi).
