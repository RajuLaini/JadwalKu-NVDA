# Aturan Wajib & Prosedur Tetap Proyek JadwalKu (Project-Scoped Rules)

Setiap kali melakukan penambahan fitur baru, perbaikan bug (*bugfix*), atau modifikasi kode apa pun pada proyek **JadwalKu**, agen AI (*Antigravity*) **WAJIB SECARA OTOMATIS DAN PROAKTIF (tanpa perlu diingatkan atau diminta oleh pengguna)** melakukan langkah-langkah pemeliharaan dokumentasi dan rilis berikut sebelum mengakhiri giliran kerja:

## 1. Pembaruan Catatan Riwayat di Tombol `V` (`ChangelogDialog` - `guiDialogs.py`)
- **Wajib Memperbarui `guiDialogs.py`**: Setiap perubahan kode atau penambahan fitur harus langsung dicatat ke dalam variabel `changelog_text` di dalam kelas `ChangelogDialog` (di bawah heading versi terbaru yang sedang berjalan).
- **Shortcut `NVDA + /` lalu `V`**: Pastikan deskripsi pada command layer (`__init__.py`) selaras, sehingga saat pengguna menekan shortcut `V`, riwayat pembaruan terbaru langsung dapat dibaca dengan mudah menggunakan panah atas/bawah.

## 2. Pemeliharaan Folder `Kerangka Kerja/`
- **Jangan Ada yang Terlewat**: Seluruh dokumen di dalam folder `Kerangka Kerja/` (`01_fitur.md`, `03_arsitektur_teknis.md`, `04_catatan_pengerjaan_dini_hari.md`, dll.) wajib ditinjau dan diperbarui setiap kali ada perubahan cara kerja sistem atau arsitektur (misal: perubahan dari WASAPI ke WinMM, atau penambahan hitung mundur persiapan timer).
- Jaga kerapian dan keutuhan format Markdown agar riwayat evolusi JadwalKu selalu terdokumentasi dengan sempurna dari versi awal hingga terkini.

## 3. Sinkronisasi Versi & Metadata (`manifest.ini` & `version.json`)
- Jika modifikasi merupakan rilis versi baru atau peningkatan *patch* (misalnya dari `1.4.1` ke `1.4.2`), perbarui nomor versi secara sinkron pada:
  1. `JadwalKu/manifest.ini` (`version = ...`)
  2. `build_and_install.py` (`ADDON_VERSION = ...`)
  3. `version.json` (`version` dan teks `changelog`)
- Pastikan teks `changelog` di `version.json` mencerminkan poin-poin terbaru agar sistem *Auto-Updater* dapat menampilkan informasi pembaruan kepada seluruh pengguna JadwalKu.

## 4. Kompilasi & Pemasangan Otomatis (`build_and_install.py`)
- Setelah seluruh kode, `ChangelogDialog` (`V`), dan dokumentasi diperbarui, selalu jalankan perintah:
  `python build_and_install.py`
- Hal ini memastikan paket `.nvda-addon` terbaru langsung terbuat di folder akar proyek dan terpasang otomatis ke folder add-on NVDA pengguna (`%appdata%\nvda\addons\JadwalKu`).
- **SANGAT PENTING (Prosedur Rilis ke GitHub):** Jika Anda merilis versi baru (atau menaikkan versi untuk Auto-Updater), Anda **WAJIB** melakukan `git add JadwalKu-vX.X.X.nvda-addon` dan mem-*push* file tersebut ke *branch main* di GitHub. Sistem Auto-Updater milik pengguna mengunduh rilis langsung dari file `.nvda-addon` yang ada di branch `main`. Mengubah kode di folder `JadwalKu/` saja TANPA melakukan build ulang dan mem-*push* file hasil `.nvda-addon` ke GitHub akan mengakibatkan pengguna gagal mendapatkan pembaruan karena file instalernya masih versi usang.

## 5. Investigasi Terarah (Research Before Assumption)
- **Wajib Menelusuri Variabel Global / Konstan**: Sebelum membuat asumsi mengenai bagaimana sebuah fitur bekerja (misalnya asumsi bahwa sistem belum mendukung perekaman angka), agen WAJIB melakukan `grep_search` pada direktori proyek untuk mencari daftar konfigurasi atau array konstan yang sudah ada (seperti `WORDS_TO_RECORD`, konfigurasi config, dll).
- **Wajib Membaca Kerangka Kerja**: Baca referensi desain di folder `Kerangka Kerja/` untuk memastikan perubahan yang dilakukan tidak melenceng dari arsitektur asli yang telah diusahakan. Jangan memodifikasi secara membabi buta tanpa melihat konteks ketersediaan data.

## 6. Hati-Hati terhadap Pembaruan String (Gunakan Replace Secara Akurat)
- **Hindari Skrip Pengganti Teks yang Mentah (Naive String Replace)**: Saat Anda diminta memperbarui riwayat versi/Changelog (misalnya pada variabel `changelog_text` di `guiDialogs.py`), JANGAN menggunakan perintah `replace()` string secara mentah (seperti skrip `bump_version.py`) karena dapat menyebabkan penggandaan awal *string* tak terduga (misalnya kurung buka ganda `changelog_text = (`) jika sebagian teks sebelumnya masih ada. **SELALU gunakan perangkat khusus modifikasi file `replace_file_content`** bawaan sistem agen yang menjamin penggantian kode dengan keakuratan tinggi dan memeriksa rentang baris secara tepat, guna menghindari *SyntaxError*.
