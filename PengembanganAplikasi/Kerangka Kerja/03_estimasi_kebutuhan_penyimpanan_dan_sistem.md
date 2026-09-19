# Estimasi Kebutuhan Penyimpanan & Lingkungan Sistem

Pengembangan aplikasi lintas platform (Android, iOS, Windows) membutuhkan ruang penyimpanan (Hardisk/SSD) dan spesifikasi sistem yang jauh lebih besar dibandingkan pengembangan add-on NVDA murni (Python). 

Berikut adalah rincian estimasi kasarnya:

## 1. Kebutuhan Dasar & Node.js
- **Node.js & npm/yarn (Cache Global)**: ~1 GB hingga 3 GB.
- **Folder `node_modules` Proyek**: Setiap kali kita menginstal pustaka (React Native, dll), folder ini akan membengkak antara 500 MB hingga 1.5 GB.

## 2. Lingkungan Android (Kapasitas Terbesar)
- **Android Studio (IDE)**: ~2 GB.
- **Android SDK (Software Development Kit)**: Termasuk platform tools, build tools, dan berbagai versi API (misal SDK 33, 34). Butuh sekitar **5 GB - 10 GB**.
- **Android Emulator (Virtual Device / AVD)**: Jika Anda ingin menguji di komputer tanpa menancapkan HP fisik, satu citra emulator Android membutuhkan setidaknya **3 GB - 6 GB** per HP virtual.
- **Total Lingkungan Android**: Minimal **10 GB - 15 GB** kosong di partisi C: atau drive pengembangan Anda.

## 3. Lingkungan Windows Standalone (React Native for Windows)
- **Visual Studio Build Tools & Windows SDK**: Diperlukan compiler C++ dan .NET untuk mengompilasi aplikasi React Native menjadi aplikasi `.exe` / MSIX Windows.
- **Total Lingkungan Windows**: Sekitar **5 GB - 10 GB**.

## 4. Lingkungan iOS (Hanya Jika Menggunakan Mac)
*Catatan Penting: Mengompilasi aplikasi untuk iPhone/iOS secara lokal MUTLAK membutuhkan sistem operasi macOS (MacBook / Mac Mini) atau solusi komputasi awan (Cloud Build / EAS).*
- **Xcode IDE & iOS SDK**: Sangat besar, membutuhkan setidaknya **15 GB - 25 GB**.

## Kesimpulan Total Estimasi Penyimpanan
Untuk mengembangkan JadwalKu ke Android dan Windows dari komputer yang Anda gunakan saat ini, persiapkan ruang kosong pada hardisk / SSD Anda setidaknya:
**± 30 GB hingga 40 GB ruang bebas.**

Hal ini karena ekosistem *Mobile Development* (khususnya Android SDK dan Node_Modules) sangat haus akan memori penyimpanan dibandingkan skrip Python biasa.
