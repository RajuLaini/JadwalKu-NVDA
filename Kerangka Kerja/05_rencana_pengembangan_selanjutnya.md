# Rencana Pengembangan Selanjutnya (Roadmap JadwalKu)

Dokumen ini berisi daftar ide dan konsep fitur yang dapat kita kembangkan di sesi-sesi berikutnya untuk membuat add-on **JadwalKu** semakin sempurna dan kaya fitur.

## 1. Impor & Ekspor Data Jadwal (`Backup / Restore`)
- **Fitur**: Menambahkan tombol `[ Ekspor Jadwal... ]` dan `[ Impor Jadwal... ]` di Dialog Utama.
- **Konsep**: Memungkian pengguna menyimpan konfigurasi jadwal mereka ke sebuah file misal `my_schedules.jadwalku` (atau `.json`) untuk dibagikan ke teman lain (misalnya jadwal kelas kampus, jadwal salat, atau jadwal minum obat rutin).

## 2. Pilihan Audio Kustom dari File Lokal Pengguna
- **Fitur**: Di dalam Combo Box pemilihan suara (`CbAudioFile`), tambahkan opsi `[ Pilih File WAV Kustom... ]`.
- **Konsep**: Saat opsi ini dipilih, muncul dialog `wx.FileDialog` yang memungkinkan pengguna memilih file suara `.wav` dari folder dokumen atau musik mereka sendiri untuk dijadikan suara pengingat agenda tertentu.

## 3. [SELESAI di v1.2.0] Fitur Alarm Berdering Berulang & Tunda Sementara (*Alarm Looper & Snooze*)
- **Status**: Telah berhasil diterapkan di versi 1.2.0! Pengguna dapat memilih mode 'Alarm Jam Weker' pada formulir agenda yang berdering berulang hingga dimatikan (`Spasi`) atau ditunda 10 menit (`Z` / `Alt+T`).

## 4. Agenda Berbasis Kalender / Tanggal Spesifik (*One-time Event*)
- **Fitur**: Selain frekuensi rutin (`Setiap Hari`, `Hari Kerja`, dll.), tambahkan opsi frekuensi `Tanggal Tertentu` (misal `17 Agustus 2026`).
- **Konsep**: Pengguna dapat mengatur pengingat untuk rapat penting atau ulang tahun yang hanya terjadi sekali pada tanggal tertentu di masa depan.

## 5. Profil Pengingat Waktu Berkala (*Time Reminder Profiles*)
- **Fitur**: Memungkinkan pengguna membuat beberapa profil waktu berkala (misal Profil *Kerja*: chime tiap 30 menit dari jam 08:00 s/d 16:00; Profil *Santai*: chime tiap 1 jam dari jam 17:00 s/d 21:00).
- **Konsep**: Pengguna dapat berganti profil dengan cepat melalui shortcut di Mode Perintah tanpa perlu mengatur ulang jam mulai dan jam selesai setiap kali.

## 6. [SELESAI di v1.3.0] Timer Mundur Cepat & Alarm Sekali Pakai Presisi Detik
- **Status**: Telah berhasil diterapkan di versi 1.3.0! Pengguna dapat menekan `NVDA + /` lalu `1` untuk memasang Quick Timer (satuan Detik, Menit, Jam), atau `2` untuk memasang Alarm Sekali Pakai (dengan presisi Jam, Menit, Detik, serta opsi suara & snooze lengkap).

## 7. [SELESAI di v1.5.0] Waktu, Kalender, Tanggal Merah & Jam Dunia (*Time & Calendar Expansion*)
- **Status**: Telah berhasil diterapkan di versi 1.5.0! Pengguna dapat mengakses pengaturan lengkap melalui Tab 2 di Dialog Utama (`Ctrl+Tab`), mengatur penggantian/override `NVDA + F12` (1x jam, 2x tanggal, 3x sisa akhir tahun), membuka Kalender & Tanggal Merah (`NVDA + /, K`), serta membuka Jam Dunia & Kalkulator Konversi Waktu (`NVDA + /, D`).

## 8. [SELESAI di v1.6.0] Mesin Suara TTS Mandiri SAPI 5 untuk Latar Belakang (*Background Standalone TTS Engine*)
- **Status**: Telah berhasil diterapkan di versi 1.6.0! Pengguna dapat mengaktifkan mesin TTS terpisah berbasis `comtypes` SAPI 5 melalui `NVDA + /` lalu `M` atau dari Tab 2 & Pengingat Waktu. Mesin ini membacakan seluruh pemberitahuan latar belakang (pengingat waktu, timer, dan alarm) di thread terpisah dan meremajakannya melalui `audioManager` sehingga 100% mengikuti routing perangkat audio pilihan (Speaker/Headphone) tanpa pernah bertumpuk dengan suara pembacaan layar NVDA utama! Pengecualian pada `NVDA + F12` yang tetap dibacakan oleh NVDA utama sesuai keinginan pengguna.

## 9. [SELESAI di v1.6.1] Fitur Bagikan Add-on Instan Direct Link (*Clipboard Downloader URL Copy*)
- **Status**: Telah berhasil diterapkan di versi 1.6.1! Pengguna dapat menekan shortcut cepat `NVDA + /` lalu `G`, atau menekan tombol `Bagikan Add-on` di panel pengaturan NVDA (*Settings -> JadwalKu*). Fitur ini secara instan menyalin tautan unduhan `.nvda-addon` terbaru (`raw.githubusercontent.com/.../JadwalKu-v1.6.1.nvda-addon`) ke clipboard, memungkinkan distribusi mudah tanpa perlu membuka browser.

## 10. [SELESAI di v1.6.2] Fitur Laporan, Kritik & Saran Terintegrasi Bot Telegram via Web API Proxy (*Feedback & Bug Diagnosis*)
- **Status**: Telah berhasil diterapkan di versi 1.6.2! Pengguna dapat menekan shortcut `NVDA + /` lalu `R` (maupun dari tombol `Kirim Laporan & Saran` di panel pengaturan NVDA) untuk memilih kategori (`Minta Fitur Baru`, `Laporkan Kesalahan`, `Kritik Saran`). Sistem secara otomatis mengekstrak log diagnostik terbaru dari NVDA dan menampilkannya secara transparan yang bisa diedit. Pengiriman dilakukan secara aman melalui Web API Proxy PHP (`jadwalku_telegram_proxy.php`) ke Bot Telegram Aileen, dilengkapi pembatasan kuota 1 laporan/hari per user dan fitur fallback salin otomatis ke clipboard jika offline/gagal.


