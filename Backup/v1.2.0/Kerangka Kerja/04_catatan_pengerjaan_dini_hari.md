# Catatan Pengerjaan Dini Hari (12 - 13 Juli 2026)

Catatan ini merangkum seluruh pencapaian, keputusan desain teknis, dan alur kerja yang berhasil kita selesaikan pada sesi pemrograman intensif dini hari ini.

## Pencapaian Sesi Dini Hari Ini

### 1. Penyelesaian Entry Point `__init__.py` dan Integrasi Sistem
- Berhasil menghubungkan seluruh komponen (`ConfigManager`, `AudioManager`, `Scheduler`, `guiDialogs`) menjadi satu kesatuan add-on Global Plugin yang kokoh.
- Mendaftarkan panel pengaturan `JadwalKuSettingsPanel` ke menu **Preferences -> Settings -> JadwalKu** di NVDA.
- Menambahkan pintasan cepat ke menu **Tools -> JadwalKu - Manajemen Agenda & Pengingat...**.

### 2. Implementasi Command Layer Bergaya IslamicPedia & Shortcut Langsung
- Menambahkan shortcut **`NVDA + Shift + J`** untuk langsung membuka Dialog Utama Manajemen Jadwal tanpa melalui mode perintah.
- Menyetel shortcut **`NVDA + /`** sebagai pintu masuk ke Mode Perintah JadwalKu (*Command Layer*):
  - `L` / `Enter`: Buka dialog layout.
  - `W` / `T`: Bacakan jam saat ini dan status pengingat berkala.
  - `J`: Bacakan jadwal terdekat berikutnya beserta hitungan mundur (*countdown*).
  - `H`: Bacakan seluruh daftar agenda aktif hari ini.
  - `A`: Check / Uncheck pengingat waktu berkala secara instan.
  - `Spasi`: Hentikan suara audio/chime.
  - `B` / `F1`: Buka **Dialog Panduan Bantuan Read-Only (`HelpDialog`)**.

### 3. Pembuatan Script Otomatis `build_and_install.py`
- Membungkus folder `manifest.ini`, `globalPlugins`, dan `doc` menjadi paket standar **`JadwalKu-1.0.nvda-addon`**.
- Menyalin langsung file-file add-on ke folder `%appdata%\nvda\addons\JadwalKu` sehingga pengguna bisa langsung mengujinya hanya dengan menekan `NVDA + Ctrl + F3` (memuat ulang NVDA).

### 4. Tombol Tes Suara di Formulir Tambah & Edit Agenda (`AgendaDialog`)
- Menambahkan tombol `[ &Tes Suara ]` (`Alt + T`) di samping Combo Box pilihan audio.
- Saat ditekan, sistem langsung memutar file audio yang dipilih (`chime.wav`, `bell.wav`, atau `alarm.wav`) melalui `AudioManager.play_sound()`, memungkinkan pengguna mendengarkan sampel suara sebelum menyimpan agenda.

### 5. Dialog Panduan Bantuan Read-Only Aksesibel (`HelpDialog`)
- Menjawab kebutuhan akan navigasi panduan yang nyaman, kita menciptakan dialog bantuan berbasis `wx.TextCtrl(style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2 | wx.HSCROLL)`.
- Pengguna dapat membaca teks panduan secara tepat per baris menggunakan panah bawah/atas dan mengeja per huruf menggunakan panah kiri/kanan layaknya *read-only mode* standar NVDA. Dialog ini dapat diakses via tombol `[ &Bantuan... ]` (`Alt + B`) di dialog utama maupun via tombol `B`/`F1` di Mode Perintah `NVDA + /`.

### 6. Implementasi Fitur Pemeriksa Pembaruan Otomatis (`updateChecker.py`) & Unduh Langsung
- Menambahkan sistem auto-check di latar belakang yang menembak ke URL spesifikasi JSON (`version.json`).
- Menyetel mekanisme penolakan sesi (*session dismissal*): jika pengguna menekan `No / Tidak`, add-on otomatis berhenti mengecek hingga NVDA dimuat ulang.
- **Direct Background Downloader (Tanpa Membuka Browser)**: Ketika pengguna memilih `Yes / Ya` pada prompt pembaruan, add-on mengunduh file `.nvda-addon` secara diam-diam di latar belakang ke folder sementara (`tempfile`), lalu memanggil `os.startfile(temp_path)`. NVDA langsung memunculkan dialog asli pemasangan add-on di layar tanpa pernah membuka peramban web (*browser*).

### 7. Pengaturan Git dan Unggah Langsung ke GitHub Private (`RajuLaini/JadwalKu-NVDA`)
- Menginisialisasi repositori Git lokal dan menyetel berkas `.gitignore`.
- Mengkonfigurasi remote origin secara permanen menggunakan token akses pribadi (*PAT*) milik pengguna (`RajuLaini`).
- Berhasil melakukan *commit* dan *push* seluruh struktur proyek langsung ke *branch* `main` di GitHub Private pengguna tanpa kendala.

### 8. Pembersihan Shortcut (`NVDA + Shift + J` Dihapus) & Penyempurnaan Mode Perintah (`NVDA + /`)
- Menghapus shortcut `NVDA + Shift + J` untuk mencegah bentrok/tumpang tindih dengan add-on NVDA lain.
- Semua perintah kini terpusat dengan rapi pada satu gerbang mode perintah (`NVDA + /`), dengan penambahan shortcut baru **`S`** untuk langsung membuka **JadwalKu Audio Manager**.

### 9. Fitur Audio Manager & Pemilihan Speaker Kustom (`AudioManagerDialog`)
- Memungkinkan pemutaran suara chime dan alarm di perangkat speaker/kartu suara khusus tanpa mengikuti aturan default system soundcard (`Default (Microsoft Sound Mapper)` atau speaker eksternal khusus seperti *USB Audio / Headphone / IslamicPedia Speaker*).
- Menambahkan **Audio Manager Dialog** (`Alt + P` di dialog utama atau tombol `S` di mode perintah `NVDA + /`) yang memungkinkan pengguna memilih perangkat output audio, mengetes speaker terpilih, serta mengecek/mengetes seluruh koleksi file suara yang ada di folder add-on.

### 10. Fitur Alarm Jam Weker & Dukungan Pemutaran MP3 (`mciSendStringW`)
- Menambahkan dukungan pemutaran file `.mp3` native di Windows (menggunakan `ctypes.windll.winmm.mciSendStringW`) agar file baru **`wind-up-clock-alarm-bell.mp3`** dapat diputar langsung sebagai suara alarm jam weker.
- Pemilihan suara di formulir agenda kini memuat daftar dinamis yang mencakup `chime.wav`, `bell.wav`, `alarm.wav`, `wind-up-clock-alarm-bell.mp3`, dan suara kustom lainnya dari folder `sounds/`.

### 11. Fitur Gabungan Hari Spesifik (`Sesuaikan Hari` - Checkbox Dialog)
- Menambahkan opsi frekuensi **"Sesuaikan Hari (Pilih Hari Spesifik...)"** pada formulir tambah/edit agenda (`AgendaDialog`).
- Menyediakan tombol **`[ &Pilih Hari (Checklist)... ]`** yang membuka dialog khusus berisi 7 Checkbox (`Senin` sampai `Minggu`).
- Penjadwalan latar belakang (`scheduler.py`) kini memverifikasi kombinasi hari yang dicentang secara presisi di setiap pergantian menit.

