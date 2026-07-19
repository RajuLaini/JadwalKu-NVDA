# Catatan Stabilitas Voice Pack & Manajemen Audio (v1.6.11 - v1.6.12)

Dokumen ini mencatat dua perbaikan arsitektur krusial pada fitur Voice Pack JadwalKu untuk mencegah regresi di masa depan. Jika Anda memodifikasi `audioManager.py` atau `__init__.py` di bagian pengumuman waktu, **patuhi panduan di bawah ini dengan ketat**.

## 1. Toleransi Kata Hilang (*Missing Word Tolerance*)
**Latar Belakang (Sebelum 1.6.11):** 
Sistem perakit kalimat audio (`play_voice_pack_sequence`) sebelumnya memiliki sistem validasi yang sangat kaku. Ia akan memeriksa setiap kata yang dibutuhkan untuk merangkai jam (contoh: "15", "24", "waktu", "sekarang"). Jika *ada satu saja* kata yang gagal ditemukan di dalam folder ZIP `.jvp` (karena pengguna tidak merekamnya), variabel `valid` langsung diset menjadi `False`, dan sistem membatalkan seluruh pemutaran lalu beralih (*fallback*) secara diam-diam ke TTS bawaan. Pengguna mengira fitur *Voice Pack* (tekan W) rusak.

**Implementasi Saat Ini:**
Sistem kini tidak lagi menggagalkan seluruh rangkaian jika ada file yang hilang. Ia akan melewatkan (*skip*) kata tersebut dan tetap memutar audio file WAV yang berhasil ditemukan.
* **Aturan Main**: Dilarang mengembalikan logika `valid = False` yang membatalkan eksekusi `vp_files` secara penuh hanya karena ada satu file audio yang absen.

## 2. Race Condition pada Antrian Audio WinMM (Thread Conflict)
**Latar Belakang (Sebelum 1.6.12):**
Suara sering kali terpotong atau "hanya terdengar belnya saja, tapi suara rekaman hilang" saat mengeksekusi `NVDA + /, W`. Hal ini diakibatkan oleh *Race Condition* antara dua utas (*thread*):
1. **Thread Bel (`worker1`)**: Mulai memutar `chime.wav`.
2. **Thread Utama**: Memerintahkan bel untuk berhenti setelah 350 milidetik menggunakan `stop_sound()`, agar bisa mulai memutar Voice Pack.
3. **Thread Voice Pack (`worker2`)**: Mulai menginisiasi `waveOutOpen` untuk memutar audio gabungan `.wav`.

Di versi lama, `worker1` memiliki blok `finally` yang secara sepihak mengeksekusi `self._is_playing = False` ketika ia berhasil membersihkan memori dirinya sendiri (*waveOutClose*). Karena `worker1` terkadang lambat menutup dirinya, ia menembakkan sinyal `False` tersebut **SETELAH** `worker2` hidup. `worker2` yang sedang memutar Voice Pack menangkap sinyal `False` ini, dan seketika membunuh dirinya sendiri dalam waktu nol koma sekian milidetik, tanpa sempat membunyikan suara.

**Implementasi Saat Ini:**
* Logika primitif `self._is_playing = False` di dalam blok `finally` (baik untuk utas MP3 maupun WAV) telah dihapus sepenuhnya.
* Penentuan apakah sistem sedang memainkan audio atau tidak (`is_playing()`, `has_active_playback()`, `has_active_sounds()`) kini dihitung secara dinamis (*real-time*) dengan menghitung panjang Set `_active_wave_outs`, `_active_mp3_aliases`, dsb.
* Metode `stop_sound()` tetap diperbolehkan men-set `self._is_playing = False` hanya sebagai penanda (bendera) bagi utas yang sedang berjalan agar menghentikan putarannya (`break`), setelah itu utas baru yang dipanggil akan me-*reset*-nya kembali ke `True`.

* **Aturan Main**: **JANGAN PERNAH** memodifikasi variabel `self._is_playing` di ujung akhir eksekusi thread latar belakang. Utas yang sudah mati tidak boleh mengatur regulasi bagi utas baru yang sedang hidup.

## 3. Modifikasi Volume Dinamis Berbasis Paket
Untuk pengembangan selanjutnya, Voice Pack akan memiliki tingkat volume (*gain boost*) tersendiri untuk mengimbangi hasil rekaman mikrofon pengguna yang mungkin pelan. Hal ini menuntut `play_voice_pack_sequence` untuk menerapkan modifikasi amplitudo PCM (`_boost_pcm_16bit`) sebelum diteruskan ke WinMM, terpisah dari volume alarm/TTS global.
