# Catatan Pengembangan: Pelacak Kebiasaan & Lonceng Klasik (v1.7.6.1)

## 1. Fitur Pelacak Kebiasaan (Habit Tracker)
JadwalKu kini bertransformasi menjadi Pelacak Kebiasaan (Habit Tracker)!
Fitur ini diakses melalui shortcut `NVDA + /` lalu `J`.
- Memungkinkan penandaan jadwal yang sudah lewat sebagai "Sudah Selesai", "Lewati", atau "Tunda (Snooze)".
- **Integritas Data:** Tombol Selesai hanya dapat diakses jika waktu alarm benar-benar sudah tiba (mencegah *cheating*/kecurangan menyelesaikan habit sebelum waktunya).
- **Persistence:** Logika penyimpanannya diubah dari Addon Dir (yang terhapus saat instalasi) menjadi tersimpan aman di Config Dir NVDA (`habit_stats.json`), sehingga Lencana dan *streak* pengguna tersimpan secara permanen antar rilis versi!

## 2. Fitur Jam Lonceng Klasik (Grandfather Clock)
Menghadirkan nuansa jam dinding kuno berkelas (Grandfather Clock) pada JadwalKu.
- **Background Ticking (Suara Detik Latar):** Memanfaatkan file `WatingClock.wav` yang diputar dengan `_play_wav_winmm` dari Audio Manager tanpa tumpang tindih. Metode pembacaan RAM mencegah file terkunci, sehingga installer `.nvda-addon` masa depan aman dari `FileExistsError`.
- **Harmoni Melodi (16.0s Sweet Spot):** Memiliki durasi persiapan melodi `mulaiLonceng.wav` yang dikalibrasi presisi dengan jeda `time.sleep(16.0)`. Pada detik ke-16 persis, dentangan palu gong mekanik `ketukanLonceng.wav` akan dibunyikan.
- **Irama Ketukan Cepat:** Jeda antar pukulan gong (`time.sleep(0.5)`) atau 500ms menciptakan ritme tegas persis seperti mesin jam raksasa mekanik.
- **Dynamic Cancellation Button:** Di dalam UI, fitur "Tes Lonceng" menggunakan sistem tombol pintar. Tombol "Tes Lonceng Saat Ini" berubah *real-time* menjadi "Hentikan Tes Lonceng" saat berdering, dan thread akan melakukan *polling* `_is_playing` setiap 0.1 detik untuk interupsi pembatalan seketika! Tombol akan kembali normal secara otomatis ketika rotasi lonceng selesai.
- **Volume Super Boost (Hingga 1200%):** Memanfaatkan perutean `pcm_16bit_boost`, slider volume lonceng dan detik dapat ditingkatkan ekstrem hingga 1200%.
- **Rute Output Akurat:** Sistem lonceng dibangun menggunakan `_play_wav_winmm` milik JadwalKu, BUKAN Windows `mciSendString`. Ini menjamin setiap dentangan mendarat persis di perangkat output (Headphone/Virtual Cable) sesuai Pengaturan Audio Manager JadwalKu Anda!
