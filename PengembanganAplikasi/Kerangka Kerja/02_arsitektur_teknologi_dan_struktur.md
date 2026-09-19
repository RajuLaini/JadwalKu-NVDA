# Arsitektur Teknologi & Struktur Proyek Lintas Platform

## 1. Kerangka Kerja Utama (Tech Stack)
Direkomendasikan menggunakan **React Native (dengan TypeScript)**.
**Alasan:** React Native membungkus komponen UI menjadi *Native Views* asli (seperti `android.view.View` di Android dan `UIView` di iOS). Hal ini memastikan pembaca layar bawaan (*TalkBack* dan *VoiceOver*) dapat berinteraksi dengan aplikasi secara natural, seolah-olah itu adalah aplikasi yang ditulis dalam Java atau Swift asli. Ini sangat krusial untuk standar aksesibilitas JadwalKu.

## 2. Abstraksi Latar Belakang (Background Polling)
Sistem operasi *mobile* melarang aplikasi berjalan terus-menerus di latar belakang menggunakan *timer* per-detik. Oleh karena itu, *scheduler.py* tidak bisa direplikasi mentah-mentah.
- **Android**: Menggunakan `AlarmManager` (dengan izin `SCHEDULE_EXACT_ALARM`) atau `WorkManager` untuk membangunkan aplikasi pada menit yang tepat.
- **iOS**: Menggunakan `Local Notifications` (`UNUserNotificationCenter`) untuk memicu alarm, atau *Background Tasks* untuk eksekusi logika.
- **Strategi Abstraksi**: Di folder `src/`, kita membangun `JadwalKuScheduler` (TS) yang akan mendelegasikan tugas penjadwalan ke *Native Modules* Android dan iOS.

## 3. Abstraksi Audio dan TTS
- **Audio Engine (Pengganti WinMM)**: Kita perlu membuat *React Native Custom Module* yang menjembatani perintah ke *AudioTrack* (Android) dan *AVAudioEngine* (iOS). Logika pengali *PCM* 1200% akan diletakkan di *Native Code* C++ atau Java/Swift untuk efisiensi CPU dan menghindari *delay* di jembatan Javascript.
- **TTS Engine (Pengganti SAPI 5)**: Memanggil API sintesis bawaan masing-masing OS. Kita tidak bisa menggunakan comtypes.

## 4. Struktur Folder (`PengembanganAplikasi/`)
```text
PengembanganAplikasi/
├── Kerangka Kerja/    # Folder Dokumentasi Arsitektur
├── src/               # Kode utama (React Native TypeScript), UI, Logika Scheduler Abstraksi, State Management
├── android/           # Native Android Wrapper & Jembatan Audio/Alarm (Java/Kotlin)
├── ios/               # Native iOS Wrapper & Jembatan Audio/Alarm (Objective-C/Swift)
├── windows/           # Native Windows (React Native for Windows) C++ / C#
├── package.json       # Manajemen pustaka (npm/yarn)
└── index.js           # Titik masuk utama aplikasi (Entry Point)
```
