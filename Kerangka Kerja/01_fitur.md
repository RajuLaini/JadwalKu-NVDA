# Daftar Fitur Lengkap Add-on JadwalKu v1.2.0

Add-on **JadwalKu** didesain khusus sebagai manajer waktu dan pengingat agenda yang 100% ramah aksesibilitas screen reader NVDA.

## 1. Manajemen Agenda Rutin (Harian / Mingguan)
- **Daftar Agenda Aktif**: Menampilkan semua jadwal dalam `ListBox` yang mudah dinavigasi menggunakan panah atas/bawah.
- **Input Berbasis Combo Box**: Saat menambah atau mengedit jadwal, pengguna tidak perlu mengetik format waktu manual. Cukup pilih **Jam (00 - 23)**, **Menit (00 - 59)**, dan **Frekuensi (Setiap Hari / Hari tertentu)** melalui dropdown/combo box.
- **Mode Pemberitahuan (Chime vs Alarm Weker)**: Memungkinkan agenda diputar sekali bunyi (*chime*) atau berdering terus-menerus tanpa henti (*Alarm Jam Weker*) dengan fitur Tunda/Snooze 10 menit (`Z` / `Alt+T`).
- **Tombol Tes Suara (`Alt + T`)**: Di dalam formulir tambah/edit agenda (`AgendaDialog`), pengguna dapat menekan tombol `[ &Tes Suara ]` untuk langsung mendengarkan sampel suara dari opsi yang dipilih di Combo Box sebelum menyimpan.
- **Status Check/Uncheck Cepat**: Pengguna dapat mengaktifkan atau menonaktifkan suatu agenda dengan cepat melalui tombol `[ Check / Uncheck Status ]` atau langsung menekan Spasi di daftar agenda.

## 2. Pengingat Waktu Berkala (*Time Reminder / Hourly Chime*)
- **Interval Waktu Fleksibel**: Dapat diatur untuk mengingatkan setiap **5 menit**, **10 menit**, **15 menit**, **30 menit**, hingga **1 jam sekali (Setiap Jam)**.
- **Mode Notifikasi Pilihan**:
  - *Bicara Waktu via NVDA & Putar Chime* (Mode Lengkap)
  - *Hanya Bicara Waktu* (Tanpa Chime)
  - *Hanya Putar Chime* (Tanpa Bicara)
- **Rentang Jam Aktif (*Quiet Hours*)**: Pengguna dapat mengatur Jam Mulai (misal jam `06:00`) dan Jam Selesai (misal jam `22:00`) agar pengingat tidak berbunyi di tengah malam saat tidur.

## 3. Shortcut & Mode Perintah (*Command Layer*) Bergaya IslamicPedia
- **`NVDA + /`**: Pintu gerbang tunggal untuk masuk ke **Mode Perintah JadwalKu** (ditandai suara nada naik dan ucapan NVDA). Dalam mode ini:
  - **`L` / `Enter`**: Buka Dialog Layout Utama.
  - **`1`**: Buka Dialog Pasang Timer Mundur Cepat (Quick Timer) dengan satuan Detik, Menit (default), atau Jam. Dilengkapi input **Detik Persiapan Sebelum Mulai** yang menghitung mundur terlebih dahulu (dengan detak jam dan ucapan angka di 5 detik terakhir), memicu bunyi **Ding (`chime.wav`)** saat mencapai angka nol sebagai tanda dimulainya hitung mundur utama, serta memicu detak acak (*WaitingClock random ticking sounds*) pada 10 detik terakhir sebelum timer sesungguhnya habis dan membunyikan alarm.
  - **`2`**: Buka Dialog Pasang Alarm Sekali Pakai (One-Time Alarm) dengan presisi Jam, Menit, dan Detik.
  - **`W` / `T`**: Bacakan informasi jam sekarang dan status pengingat waktu berkala (*Current Time & Status*).
  - **`J`**: Bacakan jadwal agenda terdekat berikutnya beserta sisa waktu menuju agenda tersebut.
  - **`H`**: Bacakan seluruh daftar agenda aktif hari ini.
  - **`A`**: Check / Uncheck cepat status Aktifkan Pengingat Waktu Berkala.
  - **`S`**: Buka **JadwalKu Audio Manager** (Pengaturan Speaker & Suara).
  - **`Spasi`**: Hentikan suara audio/chime/alarm yang sedang berbunyi.
  - **`B` / `F1`**: Buka **Dialog Panduan Bantuan Read-Only (`HelpDialog`)**.
  - **`Escape`**: Keluar dari mode JadwalKu.

## 4. Dialog Bantuan Read-Only Aksesibel (`HelpDialog`)
- **Navigasi Panah Atas/Bawah & Eja Karakter**: Saat tombol `Bantuan...` (`Alt + B`) di dialog utama atau tombol `B`/`F1` di mode perintah ditekan, akan muncul dialog dengan multiline read-only text control (`wx.TE_MULTILINE | wx.TE_READONLY`).
- Pengguna dapat membaca panduan secara nyaman per baris menggunakan panah atas/bawah, atau mengeja huruf dengan panah kiri/kanan tepat seperti *read-only mode* standar NVDA.

## 5. Sistem Audio Manager & Pengaturan Perangkat Speaker Khusus (`audioManager.py` & `AudioManagerDialog`)
- **Pemutaran Mandiri di Speaker Berbeda (`Dynamic Device Routing`)**: Menggunakan mesin **Single-Open WinMM Relooping Engine** berbasis API kernel Windows yang menjamin suara 100% dipancarkan melalui perangkat output audio pilihan pengguna (*kartu suara terpisah, headphone USB, atau speaker eksternal*) tanpa pernah mandek di speaker default NVDA.
- **Perulangan Alarm Tanpa Batas & Anti-Potong (`Infinite Looping & Full Completion`)**: *Handle* audio dibuka 1 kali saja di awal perulangan sehingga alarm mampu berdering ribuan kali tanpa mengalami *error 4 (driver mengunci)* setelah putaran kedua. Suara berbunyi padat 100% dari dentaman pertama hingga akhir tanpa potongan dengan jeda konsisten 2 detik sekali.
- **Dukungan Alarm Jam Weker MP3 & WAV (`mciSendStringW` & `winmm`)**: Memungkinkan pemutaran file `.wav` berkualitas tinggi serta file `.mp3` seperti `wind-up-clock-alarm-bell.mp3` secara native.
- **Daftar Suara Dinamis**: Memuat otomatis seluruh file suara (`.wav` dan `.mp3`) yang ada di dalam folder `sounds/` add-on.

## 6. Penjadwalan Gabungan Hari Kustom (`Sesuaikan Hari`)
- Menggunakan dialog khusus dengan 7 Checkbox (`Senin` - `Minggu`) yang memungkinkan pengguna menggabungkan hari tertentu (misal: Senin, Rabu, Jumat saja) sesuai kebutuhan jadwal secara akurat dan fleksibel.

## 7. Pemeriksa Pembaruan Otomatis dengan Unduh Langsung (*Direct Background Downloader*)
- **Pemeriksaan Latar Belakang**: Secara otomatis mengecek file `version.json` dari repositori GitHub Private tanpa mengganggu performa NVDA.
- **Pemasangan Langsung Tanpa Browser**: Jika pengguna menekan `Yes / Ya` saat ada pembaruan baru, add-on akan mengunduh file `.nvda-addon` di latar belakang (*background thread*) lalu memicu dialog resmi pemasangan add-on NVDA secara langsung (`os.startfile`).

