# Crab News — Ringkasan Rencana Pengembangan AI
> **Dokumen ringkas** • Arah produk, metode, arsitektur, dan tahapan implementasi

---

## 1. Visi Proyek
Crab News dikembangkan dari news crawler dan dashboard tren kata menjadi platform analisis berita yang membantu menemukan topik, melacak perkembangan peristiwa, dan menganalisis pola pemberitaan dari waktu ke waktu. Analisis dibatasi pada kumpulan sumber yang berhasil dikumpulkan; hasilnya tidak otomatis mewakili seluruh media atau membuktikan hubungan sebab-akibat.

---

## 2. Sasaran Utama
* **News Topic Analysis:** menemukan topik yang sedang dibicarakan dan mengukur perubahan popularitasnya.
* **Historical Event Analysis:** melacak kapan topik muncul dalam data, kapan memuncak, dan bagaimana rangkaian pemberitaannya berkembang.
* **News Intelligence:** membandingkan cakupan antarsumber, mendeteksi lonjakan topik, menelusuri aktor/peristiwa, serta menjawab pertanyaan berdasarkan artikel dan sumbernya.

---

## 3. Pendekatan AI/ML yang Disarankan

| Kebutuhan | Metode awal | Training dari nol? |
| :--- | :--- | :--- |
| **Menemukan topik** | Embedding + BERTopic / clustering | Tidak |
| **Mencari artikel berdasarkan makna** | Semantic search + embedding | Tidak |
| **Mengelompokkan peristiwa** | Kemiripan semantik + waktu + entitas | Tidak harus |
| **Mengukur tren** | Agregasi time-series, moving average, deteksi anomali | Tidak |
| **Ekstraksi orang/organisasi/lokasi** | NER model yang sesuai bahasa Indonesia | Tidak harus |
| **Sentimen/stance/framing** | Model klasifikasi yang dievaluasi; fine-tuning jika diperlukan | Mungkin |
| **Tanya jawab histori berita** | RAG: retrieval artikel + LLM + sitasi sumber | Tidak harus |

> **Prinsip utama:** Mulai dengan *pretrained model* dan metode *unsupervised*. Jangan melatih model bahasa dari nol. *Fine-tuning* dipertimbangkan setelah tersedia contoh berlabel dan kelemahan model awal dapat diukur.

---

## 4. Arsitektur yang Disarankan
Pertahankan satu repository. Pisahkan crawler, pipeline ML, dashboard, dan skema database agar analisis dapat dijalankan ulang tanpa crawling ulang.

* `web/` — Dashboard Next.js: Topic Explorer, Topic Timeline, Event Timeline, Source Comparison, Historical Search.
* `crawler/` — Pengambilan RSS/HTML, normalisasi konten, deduplikasi, dan penyimpanan artikel.
* `ml/` — Preprocessing, embeddings, topic modeling, event detection, entity extraction, evaluation, pipelines.
* `supabase/` — Migrations dan seeds.
* `.github/workflows/` — Workflow crawl dan analisis terjadwal.
* `docs/` — Architecture, data model, dan dokumentasi ML pipeline.

---

## 5. Pengembangan Data
* **Tabel Awal:** Pertahankan `sources`, `articles`, `article_words`, `daily_keywords`, dan `crawl_runs`. Pastikan `articles` menyimpan `judul`, `isi`, `URL`, `source_id`, `published_at`, `crawled_at`, `content_hash`, dan `status ekstraksi`.
* `article_embeddings`: `article_id`, `embedding`, `model_name/version`, `created_at`. Pertimbangkan `pgvector` untuk pencarian vektor.
* `topics` & `article_topics`: Identitas topik, label/deskripsi, versi model, serta relasi *many-to-many* artikel–topik.
* `events` & `article_events`: Kandidat peristiwa, rentang waktu, ringkasan, relasi artikel, dan tingkat keyakinan yang didefinisikan dengan jelas.

*Simpan versi model dan metadata pemrosesan agar hasil historis dapat ditafsirkan ketika algoritma berubah.*

---

## 6. Roadmap Implementasi
1. **Fase 1 — Perkuat data:** Kualitas isi artikel, tanggal publikasi vs crawling, deduplikasi, validasi, dan status kegagalan.
2. **Fase 2 — Embedding dan topic modeling:** Uji model multibahasa yang mendukung Bahasa Indonesia, clustering, dan Topic Explorer.
3. **Fase 3 — Topic timeline:** Volume harian, perubahan tren, lonjakan tidak biasa, dan identitas topik lintas waktu.
4. **Fase 4 — Event detection:** Kelompok artikel per peristiwa, ekstraksi entitas/tanggal, dan kronologi berbasis sumber.
5. **Fase 5 — Historical search dan RAG:** Pencarian semantik, ringkasan, jawaban dengan tautan dan bukti artikel.
6. **Fase 6 — Fine-tuning selektif:** Hanya untuk tugas yang memiliki masalah terukur dan data evaluasi yang memadai.

---

## 7. Evaluasi dan Risiko
* Evaluasi cluster dengan inspeksi manusia dan metrik yang sesuai; *silhouette score* saja tidak cukup.
* Uji *event detection* dengan contoh artikel yang dikelompokkan manual; gunakan *precision/recall/F1* bila ada label.
* Jangan menyamakan frekuensi berita dengan popularitas masyarakat atau keberpihakan media.
* Perhitungkan kegagalan crawling, perbedaan cakupan sumber, artikel duplikat/sindikasi, dan tanggal yang tidak akurat.
* RAG harus menunjukkan sumber, tanggal, dan bagian artikel yang mendukung klaim; model dapat tetap salah.
* Hormati ketentuan situs dan hak penggunaan konten. Hindari menyimpulkan sebab-akibat hanya dari urutan waktu.

---

## 8. Rekomendasi Prioritas
> Mulai dari **Kualitas Data** $\rightarrow$ **Embedding dan Topic Modeling** $\rightarrow$ **Topic Timeline** $\rightarrow$ **Event Detection** $\rightarrow$ **Historical Search/RAG**. 

Gunakan satu repository dan Supabase yang sudah ada; jangan menambah kompleksitas infrastruktur sebelum volume data dan kebutuhan komputasi benar-benar menuntutnya.

---

## 9. Keputusan Produk
* **Fondasi Jangka Dekat:** *News Topic Intelligence* — topik, volume, perubahan popularitas, dan perbandingan sumber.
* **Tujuan Jangka Panjang:** *Historical Event Intelligence* — rangkaian peristiwa, aktor, hubungan, dan kronologi yang dapat ditelusuri ke sumber.