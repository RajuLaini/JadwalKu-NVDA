# Catatan Revolusi Mesin Suara TTS Mandiri Latar Belakang (Standalone Background SAPI 5 Engine) - v1.6.0

## Latar Belakang & Masalah (The Problem)
Dalam penggunaan pembaca layar NVDA sehari-hari, pengguna sering kali sedang membaca dokumen panjang, menavigasi menu yang cepat, atau bekerja di aplikasi lain. Pada sistem pengingat tradisional, ketika jadwal atau pengingat waktu berkala (*Time Reminder*) dipicu di latar belakang, sistem memanggil fungsi `ui.message("Waktu sekarang pukul 09:00...")`.
Hal ini menimbulkan dua keterbatasan pokok:
1. **Tumpang Tindih & Interupsi Suara (`Speech Collision`)**: Jika NVDA sedang berbicara kalimat lain atau pengguna menekan tombol panah/Control untuk menghentikan ucapan, pesan notifikasi jadwal dapat terpotong, tertabrak, atau langsung hilang sebelum sempat didengar seutuhnya.
2. **Keterikatan dengan Perangkat Audio Utama NVDA (`Fixed Audio Route`)**: `ui.message()` selalu keluar dari speaker atau headphone tempat pembaca layar NVDA dipancarkan. Jika pengguna mengalihkan audio JadwalKu ke perangkat speaker eksternal atau *Virtual Audio Cable* melalui `AudioManager`, ucapan notifikasi jadwal tetap bocor di headset/speaker NVDA utama.

## Solusi & Arsitektur Teknis: `ttsManager.py`
Untuk mengatasi permasalahan tersebut secara permanen, pada versi 1.6.0 kita merancang dan mengimplementasikan modul khusus `ttsManager.py` (`TTSManager`) yang bekerja berdampingan dengan `audioManager.py`.

### 1. Sintesis SAPI 5 via `comtypes` ke File Sementara (*Stream-to-WAV Rendering*)
Alih-alih langsung mengirim suara ke speaker (yang dapat memblokir thread atau bentrok dengan driver COM), `TTSManager` menggunakan COM interface `SAPI.SpVoice` untuk mensintesis teks langsung ke file audio digital `.wav`:
```python
import comtypes.client

voice = comtypes.client.CreateObject("SAPI.SpVoice")
stream = comtypes.client.CreateObject("SAPI.SpFileStream")
stream.Open(wav_path, 3, False) # 3 = SSFMCreateForWrite
voice.AudioOutputStream = stream
voice.Speak(text, 0)
stream.Close()
```
File hasil sintesis disimpan secara aman di direktori temporary OS (`tempfile.gettempdir() -> jadwalku_tts.wav`).

### 2. Integrasi Penuh dengan Routing Audio WinMM (`Audio Device Independent`)
Setelah file `.wav` dari SAPI 5 selesai dirender oleh thread latar belakang (`worker` thread), `TTSManager` tidak memutarnya sendiri melainkan menyerahkannya kepada mesin **Single-Open WinMM Relooping Engine** milik JadwalKu:
```python
self.audio_manager.play_sound(wav_path, is_tts=True)
```
Dengan parameter `is_tts=True`, `AudioManager` mengetahui bahwa suara ini adalah suara sintesis ucapan mandiri (sehingga diputar sekali tanpa loop/berulang seperti alarm, namun tetap diizinkan memotong atau berdampingan sesuai antrean). Karena diputar oleh `audioManager`, suara TTS Mandiri ini **100% dipancarkan melalui perangkat output audio (Speaker / Headphone)** yang dipilih pada pengaturan Audio Manager JadwalKu (`uDeviceID`).

### 3. Pilihan Suara, Kecepatan (Rate) & Volume yang Sepenuhnya Dikustomisasi
`TTSManager` memindai seluruh suara SAPI 5 yang terinstal di komputer pengguna melalui `voice.GetTokens()`. Pengguna dapat memilih:
- **Suara SAPI 5**: Misalnya suara bahasa Indonesia (seperti Damayanti/Andika) atau suara bahasa Inggris (Microsoft Zira/David).
- **Kecepatan (`Rate`)**: Skala `-10` (sangat lambat) hingga `+10` (sangat cepat), dengan nilai default `0`.
- **Volume (`Volume`)**: Skala `0` hingga `100`% untuk mengatur keras-lembutnya ucapan mesin TTS secara independen dari volume sistem maupun penguat volume audio jadwal.

### 4. Pengecualian Pintar pada `NVDA + F12` (*Smart Separation of Duties*)
Sesuai arahan spesifik pengguna:
> *"Aku ingin punya TTS sendiri yang bisa di pilih terpisah dari NVDA... Seluruhnya akan di bacakan TTS yang berbeda itu. Kecuali, NVDA + f12. maksudnya yang sengaja di picu seperti membacakan jam Dunia, itu jangan TTS beda, tetap NVDA."*

Arsitektur kita secara ketat membedakan antara **Notifikasi Pasif Latar Belakang** dengan **Pelaporan Aktif Manual**:
- **Notifikasi Latar Belakang (`scheduler.py`)**: Pengingat waktu berkala (tiap jam/menit), alarm agenda jadwal, quick timer, dan one-time alarm di tangani oleh `scheduler.check_...()` -> memanggil `tts_manager.speak(message)`.
- **Pelaporan Manual (`NVDA + F12`, `NVDA + /, W`, `NVDA + /, J`, `NVDA + /, H`)**: Ketika pengguna secara sengaja menekan kombinasi tombol untuk menanyakan jam, tanggal, sisa tahun, atau daftar agenda, sistem tetap memanggil `ui.message()`. Dengan demikian, pembaca layar NVDA utama yang sedang merespons interaksi keyboard pengguna tetap menjadi juru bicara utama, menjaga konsistensi pengalaman navigasi yang intuitif dan natural.
