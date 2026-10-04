# Crab News — Web Dashboard

Web Dashboard analitik berita dan visualisasi tren kata kunci berbasis Next.js App Router, TypeScript, Tailwind CSS, Lucide Icons, dan Recharts.

## 🚀 Memulai Development

1. Masuk ke direktori web:
   ```bash
   cd web
   ```
2. Salin environment variables:
   ```bash
   cp .env.example .env.local
   ```
3. Install dependensi dan jalankan dev server:
   ```bash
   npm install
   npm run dev
   ```
4. Buka browser di [http://localhost:3000](http://localhost:3000).

## 📄 Halaman Dashboard

- `/` — **Overview Dashboard**: Statistik harian, grafik tren kata kunci teratas, distribusi kategori berita.
- `/articles` — **Article Explorer**: Pencarian berita, filter per sumber, status pemrosesan, dan paginasi.
- `/keywords` — **Keyword Explorer**: Frekuensi kata per artikel dan per sumber media.
- `/trends` — **Trend Tracker**: Analisis kenaikan dan kecepatan pertumbuhan topik berita harian.
- `/sources` — **Media Sources**: Monitoring status keaktifan sumber portal berita.
- `/crawl-runs` — **Crawler Health**: Log eksekusi crawler dan audit riwayat crawling.
