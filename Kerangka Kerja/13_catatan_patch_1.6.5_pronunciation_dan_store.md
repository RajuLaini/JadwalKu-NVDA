# Catatan Pemeliharaan Patch 1.6.5: Stabilisasi UI, Transmisi Backend, dan Naturalisasi Voice Pack

Dokumen ini mencatat berbagai perbaikan spesifik (hotfixes) yang dilakukan terhadap pembaruan JadwalKu v1.6.5, yang pada awalnya memperkenalkan fitur Store namun memiliki beberapa celah teknis dan desain aksesibilitas.

## 1. Migrasi API Hugging Face (Format NDJSON)
Pada implementasi awal Store, pengunggahan biner base64 melalui format JSON murni ke Hugging Face seringkali diabaikan atau gagal diproses (terjadi Error HTTP 403 / Payload bermasalah). Hal ini telah diperbaiki dengan merestrukturisasi payload *commit API* menggunakan skema `application/x-ndjson` (New-line Delimited JSON) untuk menggabungkan header commit dengan file content ke dalam satu HTTP request stream. Hasilnya, pengunggahan file .jvp berukuran besar menjadi jauh lebih stabil.

## 2. Penyelesaian Isu Sinkronisasi Daftar Store (Cache-Busting)
Hugging Face menerapkan sistem cache (`CDN Edge Cache`) yang sangat ketat pada Tree API mereka, sehingga file baru tidak akan muncul di repositori setidaknya selama 3 hingga 5 menit setelah proses *commit*. Karena NVDA secara terus-menerus mencoba memvalidasi ketersediaan file ini di repositori (mengakibatkan daftar Store terlihat kosong padahal upload sukses), kami merombak Worker:
- API Cloudflare KV kini bertindak sebagai sumber kebenaran (Source of Truth) utama untuk list API (`/list`), alih-alih mencocokkan silang datanya dengan API GitHub/Hugging Face yang laggy.

## 3. Resolusi UI Freeze (Deadlock & Array Indexing)
- **Deadlock wx.ProgressDialog**: NVDA akan diam mematung (Freeze) saat mencoba memunculkan pesan error HTTP dari Hugging Face yang bertabrakan dengan antrean perusakan/penutupan jendela progres (`APP_MODAL`). Solusi: `wx.ProgressDialog.Destroy()` kini selalu dieksekusi secara ketat secara prosedural sebelum pemanggilan `wx.CallAfter(wx.MessageBox)`.
- **Indeks Kotak Dropdown (KeyError 'filename')**: Terdapat kesalahan array *indexing* di mana kotak dialog mengeleminasi indeks rekaman "Draft", namun pointer array (`sel_idx`) masih menggunakan susunan mentah yang mengandung Draft. Ini menyebabkan pointer salah arah saat pengguna menekan Unggah, mencoba mengidentifikasi nama file yang belum pernah dirender. Perbaikan dilakukan dengan mem-filter array terlebih dahulu (`[p for p in packs if not is_draft]`) di dalam jendela *UploadDialog*.

## 4. Estetika dan Keamanan (Aksesibilitas UI)
- Memastikan layar NVDA tidak secara naif jatuh pada tombol "OK" saat dialog Store diluncurkan agar pesan peringatan unggah dapat dicerna dengan baik. Kursor kini ditetapkan pada dropdown `cb_pack` secara implisit menggunakan `wx.CallAfter(self.cb_pack.SetFocus)`.
- Memotong prefix acak (`HardwareID_`) di daftar UI sehingga pengunduh hanya membaca nama murni (misal: "Suara Raju Laini") saat menelusuri daftar paket.

## 5. Naturalisasi Algoritma Pronunciation (Pintasan `NVDA + / W`)
Sistem terjemahan jam TTS yang sebelumnya bersifat generik (berdasarkan format fallback seperti "10:30") terkadang hanya diartikan oleh TTS menjadi gabungan angka `"sepuluh"`, `"tiga"`, `"puluh"`. JadwalKu Voice Pack kini memintas proses parsial teks ini:
- Menggantikan fungsi `string.replace(":00", " ")` murni dengan algoritma dinamis yang langsung membedah detak jam internal OS (`datetime.now()`).
- Jika menit = 0, kata "tepat" disisipkan.
- Jika menit > 0, digunakan kata eksplisit "lewat" dan "menit".
- Menambahkan parameter detik "detik" agar pengucapan menjadi lebih alami layaknya manusia (Contoh: "sekarang jam 10 lewat 30 menit 45 detik am").
