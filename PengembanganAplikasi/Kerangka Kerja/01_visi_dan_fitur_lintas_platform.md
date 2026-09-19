# Visi dan Fitur Lintas Platform: JadwalKu App

## 1. Visi Proyek
Membawa pengalaman pengingat waktu dan manajemen rutinitas paling aksesibel dari lingkungan Windows (NVDA) ke ranah *mobile* (Android & iOS) dan *Desktop Standalone* (Windows). Aplikasi ini akan tetap mempertahankan prinsip utama: **100% Aksesibel (Screen Reader First)**, ringan, berorientasi pada produktivitas tunanetra, dan memiliki kontrol tingkat rendah (*low-level*) terhadap mesin audio dan TTS.

## 2. Fitur Utama yang Dipertahankan & Diadaptasi
1. **Habit Tracker & Agenda Rutin**:
   - Mempertahankan sistem *Force-Trigger* (memaksa bunyi jika terlewat).
   - Mempertahankan Lencana Ketekunan (Gamifikasi).
   - *Adaptasi*: Akan menggunakan database lokal (seperti SQLite) yang tangguh.

2. **Mesin Notifikasi Latar Belakang & TTS Mandiri**:
   - Mempertahankan notifikasi waktu dan alarm yang dibacakan oleh suara sintesis tanpa mematikan suara bacaan layar utama.
   - *Adaptasi*: Menggunakan jembatan (bridge) ke *TextToSpeech* (Android) dan *AVSpeechSynthesizer* (iOS).

3. **Lonceng Klasik (Grandfather Clock) & Volume Ekstrem (1200%)**:
   - Mempertahankan pemutaran rentetan lonceng setiap pergantian jam.
   - *Adaptasi*: Algoritma volume 1200% akan ditangani di level Native (C++/Java) agar tidak menguras baterai HP.

4. **Kustomisasi Voice Pack**:
   - Kemampuan merekam kata dan merangkainya menjadi pengingat jam dipertahankan.
   - *Adaptasi*: Manajemen file akan disesuaikan dengan izin *Storage* mobile.

5. **Voice Command (Perintah Suara Offline)**:
   - *Adaptasi*: Vosk berjalan di Android/iOS secara lokal, model diunduh ke ruang penyimpanan aplikasi.

## 3. Paradigma Interaksi Baru (Touch vs Keyboard)
- Karena tidak ada *shortcut* fisik `NVDA + /`, UI akan mengandalkan gestur *TalkBack*/*VoiceOver* dan navigasi layar penuh.
