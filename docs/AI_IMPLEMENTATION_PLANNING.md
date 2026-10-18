# Crab News — Rencana Pengembangan AI dan Analisis Berita
> **Dokumen lengkap** • Visi produk, metode ML, rancangan arsitektur, data, evaluasi, dan roadmap

---

## 1. Latar Belakang dan Visi
Crab News pada awalnya dirancang untuk mengumpulkan berita dari sejumlah situs dan menghitung kata yang sering muncul pada setiap sumber setiap hari. Pengembangan yang diusulkan memperluas tujuan tersebut: isi artikel ikut dianalisis untuk menemukan topik, mengelompokkan berita terkait, melacak peristiwa secara historis, serta mempelajari pola perubahan pemberitaan.

* **Visi yang Disarankan:** Crab News adalah platform *news intelligence* yang mengumpulkan, memproses, dan menganalisis artikel berita untuk menemukan topik baru, melacak perkembangan peristiwa, dan mengidentifikasi pola pemberitaan dari waktu ke waktu.
* **Batas Interpretasi:** Hasil analisis hanya menggambarkan data yang berhasil dikumpulkan dari sumber yang dipantau. Volume artikel bukan ukuran langsung opini publik, dan urutan pemberitaan tidak dengan sendirinya membuktikan hubungan sebab-akibat.

---

## 2. Tujuan Produk dan Pertanyaan yang Ingin Dijawab

### 2.1 News Topic Analysis
* Topik apa yang paling banyak dibicarakan dalam periode tertentu?
* Kapan topik mulai terlihat, meningkat, mencapai puncak, dan menurun?
* Apakah topik yang sama muncul kembali setelah beberapa minggu atau bulan?
* Sumber mana yang membahas topik tersebut dan bagaimana volume pemberitaannya berbeda?

### 2.2 Historical Event Analysis
* Kapan suatu isu pertama kali muncul dalam data yang dikumpulkan?
* Artikel mana yang membahas peristiwa spesifik yang sama?
* Bagaimana rangkaian pemberitaan berubah dan aktor apa yang disebut?
* Apakah dua peristiwa berkaitan menurut bukti yang tersedia?

### 2.3 News Intelligence
* Mendeteksi lonjakan topik yang tidak biasa.
* Membandingkan fokus dan *framing* antar-sumber.
* Menelusuri aktor, organisasi, lokasi, dan hubungan yang muncul dalam berita.
* Menjawab pertanyaan historis dengan artikel, tanggal, dan tautan sumber sebagai bukti.

---

## 3. Konsep yang Perlu Dibedakan

| Konsep | Pertanyaan Utama | Contoh |
| :--- | :--- | :--- |
| **Keyword analysis** | Kata apa yang sering muncul? | Kata “subsidi” meningkat. |
| **Topic modeling** | Tema apa yang mengelompokkan banyak artikel? | Kebijakan subsidi energi. |
| **Event detection** | Peristiwa spesifik apa yang diberitakan? | Pengumuman kebijakan pada tanggal tertentu. |
| **Relationship analysis** | Aktor/topik/peristiwa mana yang terhubung? | Organisasi mengkritik suatu kebijakan. |
| **Time-series analysis** | Bagaimana volume berubah dari waktu ke waktu? | Volume artikel naik tajam pada satu hari. |
| **RAG** | Bagaimana menjawab pertanyaan dengan bukti dari artikel? | Ringkasan perkembangan isu beserta sumber. |

*Keyword trend* dan *semantic trend* saling melengkapi. Kata yang sama dapat muncul dalam konteks berbeda, sedangkan satu topik dapat tetap sama meskipun istilah yang digunakan media berubah.

---

## 4. Metode AI/ML yang Direkomendasikan

### 4.1 Text Embedding
Embedding mengubah teks menjadi vektor numerik yang merepresentasikan makna. Artikel yang semantiknya serupa diharapkan memiliki vektor yang berdekatan. Embedding dapat dipakai untuk *semantic search*, *clustering*, rekomendasi artikel terkait, deteksi duplikasi semantik, dan *retrieval* historis.
* Pilih model *pretrained* yang mendukung Bahasa Indonesia atau multibahasa, lalu evaluasi dengan contoh artikel lokal.
* Tentukan apakah embedding dibuat dari judul, ringkasan, isi penuh, atau potongan artikel. Untuk artikel panjang, pertimbangkan *chunking*.
* Menyimpan embedding artikel baru tidak sama dengan melatih ulang model embedding.
* Pertimbangkan `pgvector` di PostgreSQL/Supabase jika membutuhkan pencarian *nearest-neighbor*.

### 4.2 Topic Modeling
BERTopic merupakan kandidat awal karena memadukan embedding, clustering, dan ekstraksi kata representatif. Sistem dapat menemukan kelompok artikel tanpa label topik manual dalam jumlah besar.
* Mulai dengan *batch topic modeling* pada subset artikel yang cukup beragam.
* Tinjau contoh artikel dari setiap cluster; jangan menganggap label otomatis selalu benar.
* Satu artikel bisa berkaitan dengan lebih dari satu topik.
* Cluster dapat pecah atau bergabung ketika data atau konfigurasi berubah; identitas topik perlu dikelola terpisah dari nomor cluster.

### 4.3 Event Detection
*Event detection* bertujuan mengelompokkan artikel yang membahas peristiwa tertentu, bukan hanya tema umum. Topik “politik” dapat bertahan lama, sedangkan pemilu, demonstrasi, dan pengumuman kebijakan merupakan peristiwa berbeda.
* Hitung atau gunakan embedding untuk mengukur kemiripan semantik artikel.
* Batasi kandidat berdasarkan waktu yang relevan tanpa menganggap semua peristiwa berlangsung singkat.
* Kelompokkan artikel berdasarkan kemiripan makna dan konteks waktu.
* Ekstrak entitas, lokasi, tanggal, kata kunci, dan artikel representatif.
* Tentukan apakah artikel baru memperluas peristiwa lama atau merupakan peristiwa baru.
* Simpan bukti dan tingkat keyakinan dengan definisi yang jelas; skor kemiripan bukan otomatis probabilitas.

### 4.4 Entity Extraction dan Relationship Analysis
Named Entity Recognition (NER) membantu menemukan orang, organisasi, lokasi, dan entitas lain. Ekstraksi relasi dapat menghubungkan entitas dengan tindakan atau peristiwa, lalu menyajikannya sebagai graf.
* **Node:** Dapat berupa orang, organisasi, topik, dan peristiwa.
* **Edge:** Dapat merepresentasikan hubungan seperti menyebut, mengumumkan, mengkritik, atau terlibat.
* Hubungan harus didukung konteks teks; kemunculan dua nama dalam artikel tidak cukup untuk membuktikan hubungan tertentu.
* NetworkX dapat menjadi alat analisis graf awal sebelum mempertimbangkan database graf khusus.

### 4.5 Sentiment, Stance, dan Framing

| Jenis Analisis | Fokus | Catatan |
| :--- | :--- | :--- |
| **Sentiment analysis** | Kecenderungan sentimen teks | Sentimen negatif tidak otomatis berarti media menentang kebijakan. |
| **Stance detection** | Posisi terhadap klaim/isu | Memerlukan target klaim yang jelas. |
| **Framing analysis** | Aspek yang ditonjolkan | Perlu definisi kategori dan validasi yang konsisten. |
| **Subjectivity analysis**| Perkiraan fakta vs opini | Bukan penentu kebenaran suatu pernyataan. |

Untuk isu politik, *stance* dan *framing* bisa lebih informatif daripada sentimen saja. Bedakan sikap penulis dari kutipan narasumber dan laporan tentang kritik pihak lain.

### 4.6 Time-Series dan Emerging Topic Detection
Setelah artikel dipetakan ke topik, hitung volume artikel per topik per hari atau minggu. Mulai dengan *moving average*, persentase perubahan, *baseline* historis, atau deteksi anomali sederhana sebelum memakai model *forecasting* yang kompleks.
* Bandingkan volume dengan baseline historis, bukan hanya angka mentah.
* Perhitungkan jumlah sumber aktif, kegagalan crawling, duplikasi, dan perubahan total volume berita.
* Lonjakan pemberitaan bukan bukti otomatis bahwa sebuah peristiwa lebih penting atau bahwa opini publik berubah.

### 4.7 Historical Search dan RAG
Retrieval-Augmented Generation (RAG) menggabungkan pencarian artikel yang relevan dengan model bahasa untuk menyusun jawaban. Pengguna dapat bertanya tentang perkembangan suatu isu selama periode tertentu.
1. Tafsirkan pertanyaan dan rentang waktu.
2. Cari artikel relevan menggunakan metadata, keyword, dan semantic search.
3. Susun artikel secara kronologis dan kelompokkan berdasarkan topik/peristiwa.
4. Buat ringkasan hanya berdasarkan artikel yang berhasil ditemukan.
5. Tampilkan sumber, tanggal, tautan, dan kutipan pendukung untuk klaim penting.
6. Nyatakan bila bukti tidak cukup; jangan mengarang kronologi atau hubungan sebab-akibat.

---

## 5. Perlukah Melatih Model Sendiri?

| Pendekatan | Penjelasan | Rekomendasi |
| :--- | :--- | :--- |
| **Pretrained model** | Memakai model yang telah dilatih sebelumnya. | Mulai di sini. |
| **Unsupervised learning**| Mencari struktur/cluster tanpa label manual. | Cocok untuk *topic discovery*. |
| **Fine-tuning** | Menyesuaikan model *pretrained* dengan data tugas khusus. | Pertimbangkan setelah ada label & masalah terukur. |
| **Training from scratch**| Melatih model baru dari awal. | Tidak disarankan untuk tahap awal. |

Jangan melakukan *fine-tuning* hanya agar proyek terlihat menggunakan AI. Lakukan jika evaluasi menunjukkan kekurangan yang terukur. Kumpulan artikel mentah saja belum tentu cukup untuk melatih model supervisi; sering kali dibutuhkan label atau sinyal pelatihan yang dirancang dengan baik.

---

## 6. Arsitektur Repository
Pertahankan satu monorepo. Pisahkan proses crawling, analisis ML, dashboard, dan database.

```text
Crab-News/
├── web/                         # Next.js dashboard
├── crawler/                     # RSS/HTML extraction dan penyimpanan
├── ml/
│   ├── preprocessing/
│   ├── embeddings/
│   ├── topic_modeling/
│   ├── event_detection/
│   ├── entity_extraction/
│   ├── sentiment/
│   ├── evaluation/
│   └── pipelines/
├── supabase/
│   ├── migrations/
│   └── seeds/
├── .github/workflows/
│   ├── crawl.yml
│   └── analyze.yml
├── scripts/
├── docs/
│   ├── architecture.md
│   ├── data-model.md
│   └── ml-pipeline.md
└── README.md
```

*Struktur ini adalah target konseptual, bukan kewajiban untuk membuat semua direktori sekarang. Mulai dengan modul yang benar-benar digunakan dan tambahkan bagian lain sesuai fase pengembangan.*

---

## 7. Alur Pemrosesan Data
1. **Crawling:** Ambil judul, isi, URL, sumber, tanggal publikasi, dan waktu crawling.
2. **Validasi:** Cek konten kosong/terlalu pendek, URL duplikat, status ekstraksi, dan kualitas metadata.
3. **Preprocessing:** Bersihkan HTML dan elemen non-artikel; hindari normalisasi agresif yang menghilangkan konteks.
4. **Embedding:** Hasilakan vektor menggunakan model dan versi yang dicatat.
5. **Topic Modeling:** Temukan kelompok artikel dan kata representatif.
6. **Event Detection:** Hubungkan artikel ke kandidat peristiwa menggunakan semantik, waktu, dan entitas.
7. **Aggregation:** Hitung tren berdasarkan hari/minggu, sumber, topik, dan peristiwa.
8. **Dashboard:** Tampilkan grafik, kronologi, artikel pendukung, dan tautan sumber.

---

## 8. Rancangan Data dan Database

### 8.1 Tabel yang Sudah Ada
* `sources`: daftar sumber berita.
* `articles`: metadata dan isi artikel.
* `article_words`: kata atau statistik kata per artikel.
* `daily_keywords`: agregasi kata harian.
* `crawl_runs`: status dan hasil proses crawling.

### 8.2 Perbaikan pada `articles`

| Kolom | Kegunaan |
| :--- | :--- |
| `id`, `source_id` | Identitas artikel dan sumber. |
| `url`, `title`, `content` | URL, judul, dan isi artikel yang berhasil diekstrak. |
| `published_at` | Waktu publikasi menurut sumber. |
| `crawled_at` | Waktu artikel dikumpulkan. |
| `content_hash` | Membantu mendeteksi duplikasi konten. |
| `status` | Status validasi atau pemrosesan konten. |

*Jangan menyamakan `published_at` dengan `crawled_at`.*

### 8.3 Tabel Tambahan yang Dapat Dipertimbangkan

| Tabel | Peran dan Contoh Kolom |
| :--- | :--- |
| `article_embeddings` | `article_id`, `embedding`, `model_name`, `model_version`, `created_at`. |
| `topics` | `id`, `name`, `description`, `first_seen_at`, `last_seen_at`, `model_version`. |
| `article_topics` | `article_id`, `topic_id`, `score/confidence` dengan makna yang terdokumentasi. |
| `events` | `id`, `title`, `summary`, `start_at`, `last_seen_at`, `status`. |
| `article_events` | `article_id`, `event_id`, `relation_type`, `score/confidence`. |
| `entities` / `article_entities` | Entitas yang diekstrak dan kaitannya dengan artikel. |
| `entity_relations` | Relasi antarentitas/peristiwa beserta sumber atau bukti. |

---

## 9. Fitur Dashboard

| Fitur | Fungsi | Prioritas Relatif |
| :--- | :--- | :--- |
| **Daily Keyword Trend** | Frekuensi kata harian. | Fondasi yang sudah ada |
| **Topic Explorer** | Melihat cluster, label, dan artikel representatif. | Sangat tinggi |
| **Topic Timeline** | Melihat perubahan volume topik lintas waktu. | Sangat tinggi |
| **Event Timeline** | Melihat kronologi artikel terkait peristiwa. | Tinggi, setelah topic modeling |
| **Historical Search** | Pencarian artikel lama berdasarkan makna dan filter. | Tinggi |
| **Related Articles** | Menemukan artikel semantik terkait. | Tinggi |
| **Source Comparison** | Membandingkan volume dan fokus pemberitaan. | Tinggi |
| **Emerging Topics** | Menandai kenaikan yang tidak biasa. | Menengah–tinggi |
| **Entity Graph** | Menjelajahi aktor dan relasi yang ditemukan. | Menengah |
| **AI Summary** | Ringkasan dengan bukti dan tautan artikel. | Menengah |

---

## 10. Roadmap Implementasi

* **Fase 1 — Data Quality:** Audit kualitas konten dan tanggal publikasi. Perkuat deduplikasi, validasi, dan pencatatan kegagalan.
* **Fase 2 — Embedding dan Topic Modeling:** Buat lingkungan Python terpisah di `ml/`. Uji model embedding Bahasa Indonesia. Jalankan BERTopic pada subset data, lalu tinjau cluster secara manual.
* **Fase 3 — Topic Timeline:** Agregasikan jumlah artikel per topik per hari/minggu. Buat baseline historis, deteksi lonjakan, dan rancang pencocokan identitas topik.
* **Fase 4 — Event Detection:** Buat kelompok artikel untuk peristiwa spesifik. Tambahkan ekstraksi entitas/tanggal dan metadata bukti.
* **Fase 5 — Historical Search dan RAG:** Bangun retrieval berbasis metadata, keyword, dan embedding. Susun kronologi dan ringkasan dari artikel relevan berserta bukti.
* **Fase 6 — Fine-tuning Selektif:** Kumpulkan contoh kesalahan, tentukan metrik, dan lakukan fine-tune hanya jika ada peningkatan terukur.

---

## 11. Evaluasi Model dan Hasil

| Komponen | Evaluasi yang Disarankan |
| :--- | :--- |
| **Embedding / semantic search** | Periksa relevansi hasil pencarian pada query dan artikel contoh. |
| **Topic modeling** | Inspeksi koherensi cluster, kata representatif, dan artikel yang salah kelompok. |
| **Event detection** | Bandingkan hasil dengan kelompok peristiwa manual (precision/recall/F1). |
| **Sentiment / stance** | Bandingkan prediksi dengan anotasi manusia. |
| **Historical search** | Ukur apakah artikel relevan berhasil ditemukan dan urutannya tepat. |
| **RAG / summarization** | Verifikasi tiap klaim terhadap artikel sumber; cek atribusi dan tanggal. |
| **Emerging topic** | Tinjau apakah lonjakan mencerminkan peningkatan nyata dan bukan error crawling. |

---

## 12. Risiko, Keterbatasan, dan Mitigasi
* **12.1 Bias Cakupan Sumber:** Hasil hanya menggambarkan tren dari media yang dipantau.
* **12.2 Kegagalan Crawling:** Sertakan status crawling agar kegagalan sistem tidak disalahartikan sebagai penurunan tren topik.
* **12.3 Duplikasi dan Sindikasi:** Bedakan duplikasi persis, artikel mirip, dan artikel berbeda tentang peristiwa sama.
* **12.4 Perubahan Model:** Simpan versi model, parameter, dan waktu pemrosesan agar histori dapat dipahami.
* **12.5 Biaya dan Komputasi:** Gunakan proses embedding inkremental untuk artikel baru.
* **12.6 Hak Penggunaan Konten:** Patuhi ketentuan situs dan batas akses. Jangan menyimpulkan sebab-akibat hanya dari urutan waktu.

---

## 13. Rekomendasi Teknis Akhir
1. Pertahankan satu repository dan gunakan folder `ml/` untuk pipeline analisis.
2. Prioritaskan kualitas data artikel dan metadata waktu.
3. Mulai dengan *pretrained embedding* dan BERTopic/clustering; hindari *training from scratch*.
4. Simpan embedding, hasil topik, dan versi model dengan skema yang dapat berkembang.
5. Bangun *topic timeline* sebelum *event detection*.
6. Gunakan RAG untuk pencarian dan ringkasan historis setelah retrieval memadai.
7. Evaluasi hasil secara manual sebelum mengklaim model menemukan pola.

---

## 14. Arah Produk yang Disarankan
* **Fondasi Jangka Dekat:** *News Topic Intelligence* — menemukan topik, mengukur volume, melihat perubahan popularitas, dan membandingkan sumber.
* **Tujuan Jangka Panjang:** *Historical Event Intelligence* — menyusun rangkaian peristiwa, mengidentifikasi aktor dan relasi, serta menampilkan kronologi yang dapat ditelusuri kembali ke artikel sumber.

---

## 15. Pertanyaan Produk untuk Tahap Perencanaan Berikutnya
1. Apakah fokus MVP adalah *topic discovery* dan tren, sementara *event intelligence* menjadi fase berikutnya?
2. Apakah analisis awal dibatasi pada berita Bahasa Indonesia dan sumber yang sudah terdaftar?
3. Apakah semua artikel disimpan penuh, atau ada batas panjang/retensi sesuai ketentuan sumber?
4. Apakah ringkasan AI hanya menjadi fitur eksplorasi internal atau akan ditampilkan sebagai hasil publik?
5. Apa batas biaya dan waktu eksekusi yang tersedia untuk job ML pada GitHub Actions atau lingkungan lain?