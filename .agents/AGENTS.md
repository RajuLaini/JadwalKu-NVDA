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
