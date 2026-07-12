# Rencana Pengembangan Selanjutnya (Roadmap JadwalKu)

Dokumen ini berisi daftar ide dan konsep fitur yang dapat kita kembangkan di sesi-sesi berikutnya untuk membuat add-on **JadwalKu** semakin sempurna dan kaya fitur.

## 1. Impor & Ekspor Data Jadwal (`Backup / Restore`)
- **Fitur**: Menambahkan tombol `[ Ekspor Jadwal... ]` dan `[ Impor Jadwal... ]` di Dialog Utama.
- **Konsep**: Memungkian pengguna menyimpan konfigurasi jadwal mereka ke sebuah file misal `my_schedules.jadwalku` (atau `.json`) untuk dibagikan ke teman lain (misalnya jadwal kelas kampus, jadwal salat, atau jadwal minum obat rutin).

## 2. Pilihan Audio Kustom dari File Lokal Pengguna
- **Fitur**: Di dalam Combo Box pemilihan suara (`CbAudioFile`), tambahkan opsi `[ Pilih File WAV Kustom... ]`.
- **Konsep**: Saat opsi ini dipilih, muncul dialog `wx.FileDialog` yang memungkinkan pengguna memilih file suara `.wav` dari folder dokumen atau musik mereka sendiri untuk dijadikan suara pengingat agenda tertentu.

## 3. Fitur Tunda Sementara (*Snooze Alarm*)
- **Fitur**: Ketika alarm/chime agenda penting berbunyi, pengguna dapat menekan tombol shortcut khusus (misal `NVDA + Shift + S` atau tombol `S` di Mode Perintah) untuk menunda alarm selama 10 menit ke depan.
- **Konsep**: `scheduler.py` akan mencatat waktu *snooze* pada item agenda tersebut dan memicunya kembali saat 10 menit telah berlalu.

## 4. Agenda Berbasis Kalender / Tanggal Spesifik (*One-time Event*)
- **Fitur**: Selain frekuensi rutin (`Setiap Hari`, `Hari Kerja`, dll.), tambahkan opsi frekuensi `Tanggal Tertentu` (misal `17 Agustus 2026`).
- **Konsep**: Pengguna dapat mengatur pengingat untuk rapat penting atau ulang tahun yang hanya terjadi sekali pada tanggal tertentu di masa depan.

## 5. Profil Pengingat Waktu Berkala (*Time Reminder Profiles*)
- **Fitur**: Memungkinkan pengguna membuat beberapa profil waktu berkala (misal Profil *Kerja*: chime tiap 30 menit dari jam 08:00 s/d 16:00; Profil *Santai*: chime tiap 1 jam dari jam 17:00 s/d 21:00).
- **Konsep**: Pengguna dapat berganti profil dengan cepat melalui shortcut di Mode Perintah tanpa perlu mengatur ulang jam mulai dan jam selesai setiap kali.
