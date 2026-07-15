# Catatan Arsitektur & Logika Audio JadwalKu

File ini mencatat secara terperinci bagaimana sistem audio pada **JadwalKu** diatur dan dibangun, agar di masa mendatang kita tidak melupakan logika kritis pemutaran suara, penguatan volume hingga 600%, pengelolaan perangkat (Audio Output Device), serta pemutaran berulang (*continuous looping*) untuk alarm dan timer.

---

## 1. Arsitektur Pemutar Suara (`AudioManager`)

JadwalKu menggunakan dua jalur pemutaran audio utama berbasis **Windows Multimedia API (`winmm.dll`)** yang diakses secara langsung melalui `ctypes`:

### A. Jalur WAV (`_play_wav_winmm`)
* Digunakan untuk file `.wav` (`alarm.wav`, `chime.wav`, `tick.wav`, dll.) atau file `.mp3` yang dikonversi ke `.wav` secara otomatis.
* **Low-Level PCM Handling**: Membaca header `WAVEFORMATEX` (Channel, Framerate, Sample Width 16-bit atau 8-bit) menggunakan modul `wave` bawaan Python.
* **Bebas Ketergantungan Eksternal**: Tidak memerlukan instalasi library berat di sisi pengguna akhir (tanpa `sounddevice`, `pyaudio`, dll.), karena langsung berinteraksi dengan API kernel Windows melalui `waveOutOpen`, `waveOutPrepareHeader`, `waveOutWrite`, dan `waveOutClose`.

### B. Jalur MP3 (`mciSendStringW`)
* Digunakan jika file `.mp3` tidak sempat dikonversi atau dijalankan via MCI (Media Control Interface).
* Menggunakan alias unik berbasis *timestamp* (`jk_mp3_...`) sehingga beberapa file MP3 atau suara latar dapat diputar atau dihentikan tanpa saling bentrok.

---

## 2. Penguatan Volume Hingga 600% (Boost Volume)

Karena beberapa laptop memiliki speaker internal yang kecil, JadwalKu mendukung pengaturan volume dari `0%` hingga `600%` (nilai standar `100%`).

### Logika Penguatan (`_boost_pcm_16bit`):
1. **Faktor Pengali (`factor`)**:
   Jika volume diatur ke `600%`, faktor pengalinya adalah `6.0`.
2. **Pemrosesan Cepat Berbasis Array**:
   Data *raw PCM bytes* diubah ke `array.array('h')` (signed 16-bit integers).
3. **Pencegahan Distorsi / Clipping (`clamping`)**:
   Setiap sampel dikalikan dengan faktor pengali, lalu dipastikan tidak melebihi batas integer 16-bit (`-32768` hingga `32767`):
   ```python
   int_arr = array.array('h')
   int_arr.frombytes(pcm_bytes)
   for i in range(len(int_arr)):
       val = int(int_arr[i] * factor)
       if val > 32767:
           val = 32767
       elif val < -32768:
           val = -32768
       int_arr[i] = val
   ```
4. **Efek Suara Slider (`Override Volume`)**:
   Saat pengguna menggeser panah kiri/kanan/atas/bawah di `Audio Manager Dialog`, JadwalKu memutar nada *chime* sementara menggunakan nilai volume slider saat itu (melalui atribut `_override_volume`), tanpa memuat ulang konfigurasi utama.

---

## 3. Pemutaran Berulang (Continuous Looping) untuk Alarm & Timer

### Masalah yang Pernah Terjadi:
1. **Penolakan Flag Hardware Loop**: Mengatur `hdr.dwFlags |= WHDR_BEGINLOOP | WHDR_ENDLOOP` dan `hdr.dwLoops = 99999` langsung pada `WAVEHDR` sering kali ditolak oleh driver audio Windows moderen (`error 33 / WAVERR_BADFORMAT` atau `error 11 / MMSYSERR_INVALPARAM`), menyebabkan suara bisu total.
2. **Device Busy (`MMSYSERR_ALLOCATED / error 4`)**: Jika perangkat audio ditutup (`waveOutClose`) lalu langsung dibuka kembali (`waveOutOpen`) dalam hitungan milidetik, Windows kernel driver belum sempat melepaskan *handle*, sehingga pemutaran ulang gagal.

### Solusi Permanen (`Single-Open WinMM Relooping Engine` & Device Routing):
Di dalam fungsi `_play_wav_winmm`:
1. **Mengapa `nvwave` / WASAPI Tidak Bisa Dipakai untuk Pemilihan Speaker Khusus (`Why nvwave Ignores Custom Device IDs`)**:
   Meskipun `nvwave.playWaveFile` sangat bagus untuk memutar suara ke speaker default NVDA, *engine* WASAPI internal NVDA secara arsitektur mengabaikan parameter ID/Nama perangkat dari plugin eksternal dan selalu mengalirkan suara ke *output device* utama yang dikonfigurasi di dalam `config.conf['speech']['outputDevice']`. Oleh karena itu, agar suara alarm 100% bisa berpindah ke speaker lain pilihan pengguna di JadwalKu (`device_id != -1`), kita **harus menggunakan API kernel Windows (`winmm.waveOutOpen`) yang menerima parameter `device_id` (`0, 1, 2...`) secara langsung**.
2. **Pembukaan Handle Tunggal di Luar Perulangan (`Single-Open Handle outside Loop`)**:
   Untuk mengatasi kelemahan lama di mana `winmm.waveOutOpen` dan `waveOutClose` dipanggil berulang-ulang setiap putaran alarm (*yang menyebabkan driver kartu suara mengunci/error 4 atau terpotong setelah 2 putaran*), kini `winmm.waveOutOpen(..., device_id, ...)` **hanya dibuka 1 kali di awal thread `worker()`**.
3. **Penyuapan Ulang Tanpa Tutup-Buka (`Seamless Re-Feeding & Natural Completion`)**:
   Di dalam perulangan `while True:`, sistem hanya melakukan `waveOutPrepareHeader -> waveOutWrite -> tunggu durasi penuh -> tunggu WHDR_DONE -> waveOutUnprepareHeader`. *Handle hWaveOut* tetap terbuka bersih tanpa pernah ditutup di antara putaran. Hal ini menjamin:
   - Suara berdering utuh 100% dari awal sampai akhir tanpa pernah terpotong (*tidak ada pemaksaan close saat DAC buffer masih berjalan*).
   - Perulangan berjalan tak terbatas (sampai dimatikan) dengan jeda 2 detik bersih antar putaran (`for _ in range(20): time.sleep(0.1)`), bebas dari `error 4 / MMSYSERR_ALLOCATED`.
4. **Penghentian Seketika (`Instant Reset via waveOutReset`)**:
   Saat pengguna menekan **Spasi / Enter (`Matikan Alarm`)**, fungsi `stop_sound()` memanggil `waveOutReset(hWaveOut)`. Perintah ini menghentikan pemutaran hardware DAC seketika (< 50ms), mematahkan loop, dan menutup *handle* satu kali saja di blok `finally:`.

---

## 4. Sinkronisasi Thread & Keamanan Concurrency (`self._lock`)

Semua operasi penambahan atau penghapusan *handle* audio (`self._active_wave_outs` dan `self._active_mp3_aliases`) diamankan menggunakan `threading.Lock()` (`self._lock`).

### Penghentian Suara (`stop_sound` / `stop_alarm`):
1. Mengubah `self.is_alarm_ringing = False`.
2. Membersihkan `self._active_wave_outs.clear()`.
3. Memanggil `winmm.waveOutReset(hw)`.
   * Pemanggilan `waveOutReset` seketika itu juga menghentikan pemutaran di tingkat driver Windows dan mengeset flag `WHDR_DONE`.
   * Loop yang sedang menunggu di dalam *worker thread* langsung terputus, membersihkan *header* (`waveOutUnprepareHeader`), menutup *handle* (`waveOutClose`), dan mengakhiri thread secara rapi.
