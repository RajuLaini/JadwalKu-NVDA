# Catatan Pengembangan JadwalKu v1.7.6.5: Stabilitas Snooze, Presisi Lonceng & Perbaikan TTS

Dokumen ini mencatat pembaruan struktural pada rilis v1.7.6.5, berfokus pada ketahanan (resilience) fitur *auto-snooze* Habit Tracker dan presisi waktu pada pemutar audio.

## 1. Penyimpanan Permanen Penundaan Harian (`daily_overrides`)
Sebelumnya, fitur *Auto-Snooze* (Penundaan Otomatis 1 jam) dan *Snooze Manual* pada Habit Tracker hanya disimpan di RAM (variabel `self.daily_overrides` di dalam objek `Scheduler`). Akibatnya, jika NVDA dimuat ulang (*restart*) atau *add-on* dimuat ulang sebelum jadwal tersebut berbunyi, seluruh memori penundaan akan hilang. Jadwal yang ditunda gagal memicu alarm lanjutan.

**Solusi Arsitektur:**
Properti `self.daily_overrides` kini direkayasa untuk menulis (dan membaca) langsung dari konfigurasi utama JSON (`self.config.data["daily_overrides"]`).
Setiap kali jadwal ditunda (via `snooze_schedule` atau ditekan tombol Belum/Tunda), perubahan ini langsung dikomit ke *disk* melalui `self.config.save_data()`. Hal ini menjamin status tunda bertahan 100% meskipun komputer dimatikan atau NVDA dimuat ulang.

## 2. Penghapusan Celah Drift Waktu (Anti-Drift Timer)
Fungsi `check_schedules` awalnya membandingkan kesamaan menit secara eksak (`eff_minute == now.minute`). Namun, *timer* WxPython dapat sedikit meleset apabila *thread* utama NVDA sedang sibuk memproses peristiwa lain. Jika detak `check_schedules` melompat dari detik ke-59 ke detik ke-01 di menit berikutnya, jadwal yang harusnya berbunyi pada menit ke-00 akan terlewat dan hangus selamanya pada jam tersebut.

**Solusi Arsitektur:**
Mengganti pengecekan `!= now.minute` dengan kalkulasi selisih waktu (`diff_minutes = (now.hour * 60 + now.minute) - (eff_start_hour * 60 + eff_minute)`). Jika selisihnya bernilai `0` (tepat waktu) atau `1` (terlambat 1 menit), alarm tetap diizinkan berbunyi. (Untuk versi ini, kita telah mengimplementasikan ini via patch khusus pada `scheduler.py`).

## 3. Pengecualian RAM Cache untuk `jadwalku_tts.wav`
Serupa dengan *Voice Pack Sequence*, teks hasil bacaan jadwal yang dilempar ke `ttsManager.py` akan menghasilkan audio `jadwalku_tts.wav`.
Bila 2 jadwal berbunyi bersamaan, jadwal kedua akan menimpa file ini. Namun mesin pemutar `audioManager.py` melihat "nama file yang sama" lalu menyuapkan *audio* dari jadwal pertama yang masih terjebak di RAM *Cache*.

**Solusi Arsitektur:**
Modifikasi variabel `bypass_cache` di `audioManager.py` untuk menyertakan string `"jadwalku_tts.wav"`.

## 4. Waktu Absolut untuk Presisi Lonceng
Menghitung `elapsed = 0.0` dan menambahkannya melalui `elapsed += 0.1` sambil menunggu `time.sleep(0.1)` menghasilkan pergeseran waktu (drift) yang besar pada mesin Windows (akibat *sleep overhead* ~15ms per siklus). Jeda lonceng 16.5 detik bisa melar menjadi 19 detik.

**Solusi Arsitektur:**
Menggunakan target waktu absolut: `target_time = time.time() + 16.5`, kemudian di-loop dengan `while time.time() < target_time:`. Metode ini kebal terhadap *overhead* internal karena selalu mengacu pada jam sistem (*system clock*). Irama lonceng kini berbunyi dengan tingkat akurasi tinggi.
