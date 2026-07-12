# Daftar Fitur Lengkap Add-on JadwalKu v1.0.0

Add-on **JadwalKu** didesain khusus sebagai manajer waktu dan pengingat agenda yang 100% ramah aksesibilitas screen reader NVDA.

## 1. Manajemen Agenda Rutin (Harian / Mingguan)
- **Daftar Agenda Aktif**: Menampilkan semua jadwal dalam `ListBox` yang mudah dinavigasi menggunakan panah atas/bawah.
- **Input Berbasis Combo Box**: Saat menambah atau mengedit jadwal, pengguna tidak perlu mengetik format waktu manual. Cukup pilih **Jam (00 - 23)**, **Menit (00 - 59)**, dan **Frekuensi (Setiap Hari / Hari tertentu)** melalui dropdown/combo box.
- **Status Check/Uncheck Cepat**: Pengguna dapat mengaktifkan atau menonaktifkan suatu agenda dengan cepat melalui tombol `[ Check / Uncheck Status ]` atau langsung menekan Spasi di daftar agenda.

## 2. Pengingat Waktu Berkala (*Time Reminder / Hourly Chime*)
- **Interval Waktu Fleksibel**: Dapat diatur untuk mengingatkan setiap **5 menit**, **10 menit**, **15 menit**, **30 menit**, hingga **1 jam sekali (Setiap Jam)**.
- **Mode Notifikasi Pilihan**:
  - *Bicara Waktu via NVDA & Putar Chime* (Mode Lengkap)
  - *Hanya Bicara Waktu* (Tanpa Chime)
  - *Hanya Putar Chime* (Tanpa Bicara)
- **Rentang Jam Aktif (*Quiet Hours*)**: Pengguna dapat mengatur Jam Mulai (misal jam `06:00`) dan Jam Selesai (misal jam `22:00`) agar pengingat tidak berbunyi di tengah malam saat tidur.

## 3. Shortcut & Mode Perintah (*Command Layer*) Bergaya IslamicPedia
- **`NVDA + Shift + J`**: Langsung membuka **Dialog Utama Manajemen Jadwal & Pengaturan** tanpa lewat mode perintah.
- **`NVDA + /`**: Masuk ke **Mode Perintah JadwalKu** (ditandai suara nada naik dan ucapan NVDA). Dalam mode ini:
  - **`L` / `Enter`**: Buka Dialog Layout Utama.
  - **`W` / `T`**: Bacakan informasi jam sekarang dan status pengingat waktu berkala (*Current Time & Status*).
  - **`J`**: Bacakan jadwal agenda terdekat berikutnya beserta sisa waktu menuju agenda tersebut.
  - **`H`**: Bacakan seluruh daftar agenda aktif hari ini.
  - **`A`**: Check / Uncheck cepat status Aktifkan Pengingat Waktu Berkala.
  - **`Spasi`**: Hentikan suara audio/chime yang sedang berbunyi.
  - **`B` / `F1`**: Bacakan bantuan daftar perintah cepat.
  - **`Escape`**: Keluar dari mode JadwalKu.

## 4. Sistem Audio & Notifikasi Mandiri (`audioManager.py`)
- Menggunakan modul `nvwave` bawaan NVDA untuk memutar file `.wav` di latar belakang secara non-blocking (tanpa membuat NVDA macet).
- Dilengkapi 5 suara bawaan berkualitas tinggi:
  - `chime.wav`: Suara pengingat waktu berkala yang lembut.
  - `bell.wav`: Suara pengingat agenda rutin standar.
  - `alarm.wav`: Suara pengingat agenda penting.
  - `on.wav` & `off.wav`: Suara indikator saat masuk dan keluar dari Mode Perintah JadwalKu.

## 5. Pemeriksa Pembaruan Otomatis dengan Unduh Langsung (*Direct Background Downloader*)
- **Pemeriksaan Latar Belakang**: Secara otomatis mengecek file `version.json` dari repositori GitHub Private setiap beberapa jam tanpa mengganggu performa NVDA.
- **Pemasangan Langsung Tanpa Browser**: Jika pengguna menekan `Yes / Ya` saat ada pembaruan baru, add-on akan mengunduh file `.nvda-addon` di latar belakang (*background thread*) lalu memicu dialog resmi pemasangan add-on NVDA secara langsung (`os.startfile`).
- **Opsi Batal Sesi (*Session-based Dismissal*)**: Jika pengguna memilih `No / Tidak`, pemeriksaan otomatis langsung dihentikan hingga sesi NVDA dimulai ulang (*restart*).
