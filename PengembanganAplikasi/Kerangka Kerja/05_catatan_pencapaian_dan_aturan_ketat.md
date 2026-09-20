# 05 - Catatan Pencapaian & Aturan Ketat Proyek Android

## A. Pencapaian Awal (Milestone 1) - Selesai
1. **Bypass Limitasi Lingkungan Windows:** Berhasil mengatasi masalah *Long Path* (260 karakter) Windows saat mengompilasi C++ React Native dengan menggunakan Virtual Drive (`subst X:`).
2. **Kompilasi Luring (Offline Standalone):** Berhasil mem-*bundle* UI React Native secara manual ke dalam folder `assets` dan mengompilasi aplikasi tanpa bergantung pada koneksi jaringan *Metro Bundler* yang tidak stabil dari *Hotspot* Android Go.
3. **Perbaikan Mesin Navigasi (Native Crash):** Berhasil menanggulangi *Force Close* saat aplikasi dibuka pertama kali dengan menambahkan metode `onCreate` yang wajib pada `MainActivity.kt` sesuai standar `react-native-screens`.
4. **Keberhasilan Uji Coba Pertama:** Aplikasi `JadwalKuApp` versi purwarupa berhasil berjalan mulus dengan navigasi *Bottom Tabs* (Agenda, Lonceng, Timer, Pengaturan) yang sepenuhnya terbaca oleh *TalkBack* di perangkat Android 13 Go pengguna.

## B. ATURAN KETAT (PERINGATAN KERAS UNTUK SEMUA AGEN AI)
Mulai dari titik ini (saat pengembangan aplikasi Android berjalan), **SELURUH AGEN AI HARUS MEMATUHI ATURAN MUTLAK BERIKUT:**

1. **DILARANG MENYENTUH KODE NVDA:** Agen **TIDAK DIIZINKAN** membaca, memodifikasi, atau menghapus satu pun file berekstensi `.py` yang berada di luar folder `PengembanganAplikasi`. Add-on NVDA Windows sudah stabil dan tidak boleh dirusak. Fokus 100% pada folder `PengembanganAplikasi/JadwalKuApp`.
2. **DILARANG MENGUNGGAH KE GITHUB TANPA IZIN:** Agen **TIDAK DIIZINKAN** melakukan eksekusi perintah `git push` ke repositori utama JadwalKu di GitHub **TANPA PERSETUJUAN EKSPLISIT** dari pengguna (Raju Laini). 
   - *Alasan:* Repositori GitHub terhubung langsung dengan sistem *Auto-Updater* milik ribuan pengguna NVDA. Melakukan *push* yang tidak perlu akan memicu notifikasi pembaruan palsu yang membahayakan dan membingungkan pengguna lain.
3. **Tinggalkan Prosedur Rilis Lama Sementara Waktu:** Aturan global mengenai pembaruan `manifest.ini` dan pembuatan file `.nvda-addon` yang ada di `AGENTS.md` **DIBEKUKAN SEMENTARA** selama fase pengembangan Android ini berlangsung, kecuali pengguna secara spesifik meminta untuk merilis pembaruan add-on PC.

## C. Fokus Selanjutnya (Milestone 2)
Implementasi Mesin Penjadwal Latar Belakang menggunakan `AlarmManager` (Native Java) dan mesin penggabung potongan suara *Voice Pack* menggunakan `AudioTrack` (pengganti `WinMM`), di mana Android tidak akan mematikan alarm meskipun layar HP mati (Doze Mode).

## D. Pencapaian Mesin Latar Belakang (Milestone 2) - Selesai
1. **Kompilasi Kotlin & Bridge RN:** Berhasil memprogram arsitektur Native Android (Kotlin) untuk JadwalKu yang terdiri dari JadwalKuModule (Jembatan React Native), JadwalKuAlarmReceiver (Penerima Alarm), AudioService (Layanan Latar Depan / Foreground Service), dan GaplessAudioPlayer (Pemutar WAV tanpa jeda).
2. **Menembus Doze Mode & Standby:** Sukses menggunakan AlarmManager.setExactAndAllowWhileIdle yang mampu membangunkan HP dari keadaan tertidur lelap tanpa campur tangan pengguna.
3. **Uji Coba Lonceng Latar Belakang:** Berhasil membunyikan file audio (	ada.wav) pada saat aplikasi sepenuhnya ditutup (diminimalkan) setelah 5 detik, mengonfirmasi bahwa mesin latar belakang Android kita berfungsi sempurna.

## E. Fokus Selanjutnya (Milestone 3)
Menghubungkan mesin alarm (Native Kotlin) ini dengan logika Timer React Native agar sistem hitung mundur (Pomodoro/Custom) bisa mendaftarkan target waktu nyatanya ke OS Android, dan membangun logika antrean file audio (Voice Pack) sungguhan untuk alarm JadwalKu.


### Milestone 3: Sistem Pengingat Waktu Berkala & Audio Engine (19 September 2026)
- **Problem**: Suara voice pack menjadi sangat rendah dan kata terakhir selalu terpotong oleh Hardware Buffer Flush.
- **Solution**: Mengubah sample rate AudioTrack menjadi 44100Hz dan menambahkan Thread.sleep(1000) sebelum rilis.
- **Hasil**: Sistem Pengingat Waktu Berkala berhasil bertahan dari MIUI Task Killer berkat AlarmManager RTC_WAKEUP.

### Milestone 4: Sinkronisasi Lonceng Klasik Grandfather Clock (19 September 2026)
- **Problem**: AudioTrack stream tidak bisa memutar overlapping audio. Jeda antar ketukan sempat tidak akurat.
- **Solution**: Mengembangkan Overlapping MediaPlayer Threads khusus di dalam AudioService.kt saat classic_lonceng dipicu, dan memperbaiki jeda ketukan kembali ke 1.8 detik sesuai kode NVDA.
- **Hasil**: Lonceng berdentang alami dan menyatu dengan UI Lonceng & Waktu.

### Milestone 5: Kustomisasi Lanjut (Jam Tenang, 24-Jam, dan TTS) (19 September 2026)
- **Pencapaian**: Menambahkan sakelar Format 24 Jam dan UI Jam Tenang (Quiet Hours) dengan menggunakan ndroid.app.TimePickerDialog murni (Native Module) yang 100% ramah pembaca layar (TalkBack).
- **Logika Latar Belakang**: Memprogram JadwalKuAlarmReceiver.kt agar secara cerdas mengecek apakah jam saat ini berada dalam zona Jam Tenang (misal 22:00 - 06:00). Jika iya, seluruh eksekusi alarm latar belakang akan dilompati, dan langsung dijadwalkan ulang ke siklus berikutnya tanpa bersuara.
- **Integrasi Text-to-Speech (TTS)**: Menambahkan antarmuka pemilihan Mesin Pembaca Waktu (Voice Packs vs Google TTS). Khusus untuk TTS, memprogram inisialisasi ndroid.speech.tts.TextToSpeech dengan Locale Indonesia (id, ID) di dalam AudioService.kt lengkap dengan UtteranceProgressListener untuk mencegah memori bocor (memory leak) dan membebaskan layanan Foreground setelah selesai berbicara.
- **Saluran Audio**: Memastikan baik mesin Lonceng (MediaPlayer), *Voice Packs* (AudioTrack), maupun *TTS*, ketiganya dikunci ke dalam saluran USAGE_ALARM agar volumenya sejalan dengan pengaturan Alarm HP dan menembus mode senyap Android.

## F. Rencana Berikutnya (Milestone 6)
Setelah seluruh mesin suara latar belakang bekerja sempurna, fokus berikutnya adalah menghubungkan **Tab Agenda** dan **Tab Timer**, menyusun formulir pengingat tugas (Rutinitas), dan menyimpan data-data tersebut ke dalam memori aplikasi Android.
