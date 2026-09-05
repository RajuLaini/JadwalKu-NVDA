# Standar Operasional Prosedur (SOP) Pengujian Rilis JadwalKu

Dokumen ini adalah daftar periksa (*checklist*) komprehensif yang **wajib** dilalui sebelum sebuah versi baru di-*push* ke GitHub atau dirilis ke publik. Tujuannya adalah memastikan stabilitas 99% untuk berbagai selera pengguna yang berbeda-rata.

---

## 💡 Trik Pengujian Cepat untuk Agenda (Agar Tidak Menunggu Lama)
Untuk menguji agenda, Anda tidak perlu menunggu berjam-jam. Cukup atur jadwal **1 atau 2 menit dari waktu komputer Anda saat ini**. Misalnya sekarang pukul 14:05, atur jadwal di pukul 14:07, lalu tunggu sebentar.

---

## 1. Pengujian Agenda & Pelacak Kebiasaan (Habit Tracker)
- [ ] **Buat Jadwal Rutin Harian:** Buat satu jadwal yang berulang setiap hari. Pastikan alarm berbunyi sesuai mode (Audio/Suara/Keduanya).
- [ ] **Buat Jadwal Sekali Saja (Tanggal Spesifik):** Pastikan input penanggalan bekerja dan alarm berbunyi pada tanggal yang ditentukan.
- [ ] **Uji Habit Tracker (Selesai):** Saat jadwal berbunyi, tekan `NVDA + /` lalu `J`. Pilih "Sudah Selesai". Pastikan riwayat beruntun (Streak) bertambah.
- [ ] **Uji Habit Tracker (Snooze):** Pilih "Tunda (Snooze)". Tunggu hingga waktu tunda tiba, pastikan alarm berbunyi kembali.
- [ ] **Uji Auto-Snooze (Abaikan):** Biarkan alarm berbunyi tanpa menekan apa pun di menu Habit Tracker. Pastikan jadwal tersebut menunda dirinya sendiri (1 jam).
- [ ] **Uji Lencana (Gamifikasi):** Tekan `NVDA + /` lalu `L` untuk membuka Etalase Lencana. Pastikan lencana terbaca oleh NVDA dengan benar.

## 2. Pengujian Waktu Berkala (Time Reminder) & Lonceng
- [ ] **Toggle Waktu Berkala:** Tekan `NVDA + /` lalu `A`. Pastikan statusnya menyala/mati dengan benar.
- [ ] **Uji Laporan Waktu Manual:** Tekan `NVDA + /` lalu `W`. Pastikan TTS melaporkan waktu dengan ringkas dan akurat.
- [ ] **Uji Interval Waktu:** Atur pengingat berkala ke interval tercepat (misal 5 menit). Pastikan berbunyi tepat pada kelipatan menit tersebut.
- [ ] **Uji Voice Pack vs TTS:** Nyalakan Voice Pack. Pastikan suara yang keluar adalah rekaman audio. Lalu matikan Voice Pack, pastikan suara yang keluar adalah TTS Neural/SAPI5. (Cabut koneksi internet sejenak untuk menguji *fallback* NVDA jika menggunakan TTS Online).
- [ ] **Uji Lonceng Utama:** Atur jam komputer Anda mendekati pergantian jam (misal 14:59). Tunggu hingga 15:00. Pastikan Lonceng Utama berbunyi dengan ayunan 16.5 detik tanpa terpotong.
- [ ] **Uji Lonceng Perempat Jam:** Pastikan opsi perempat jam dicentang. Atur waktu ke menit 14, 29, atau 44. Pastikan lonceng perempat berbunyi tepat pada menit 15, 30, dan 45.

## 3. Pengujian Utilitas & Fitur Ekstra
- [ ] **Pomodoro Timer:** Tekan `NVDA + /` lalu `3`. Mulai sesi fokus singkat (misal 1 menit). Pastikan alarm fokus selesai berbunyi dan masuk ke mode istirahat.
- [ ] **Alarm Sekali Pakai (One-Time Alarm):** Tekan `NVDA + /` lalu `2`. Buat alarm hitung mundur 1 menit. Uji fitur "Jeda" (Pause) dan "Lanjutkan" (Resume).
- [ ] **Kalender & Hari Libur:** Tekan `NVDA + /` lalu `K`. Pastikan kalender bisa dinavigasi dan hari libur nasional (Tanggal Merah) diumumkan dengan benar.
- [ ] **Jam Dunia:** Tekan `NVDA + /` lalu `D`. Pastikan konversi zona waktu bekerja dan tidak *crash*.
- [ ] **Perintah Suara (Voice Command):** Tekan tombol mikrofon (*shortcut* perintah suara). Ucapkan "Jam berapa?". Pastikan *WhatTimeRing* berbunyi dan waktu dibacakan.

## 4. Pengujian Antarmuka (UI) & Aksesibilitas
- [ ] **Uji Navigasi Tab:** Buka Pengaturan Agenda (`NVDA + /` lalu `1`). Navigasikan menggunakan tombol `Tab`. Pastikan semua elemen (terutama *Slider* volume dan *Combo Box*) dibacakan nama dan fungsinya oleh NVDA tanpa harus menggunakan Object Navigation.
- [ ] **Uji Jendela Pembaruan (Updater):** Buka pemeriksa pembaruan. Pastikan riwayat Changelog bisa ditelusuri menggunakan Panah Atas/Bawah.
- [ ] **Uji Log Terisolasi:** Tekan `NVDA + /` lalu `I`. Pastikan Notepad terbuka dan menampilkan log *debug* JadwalKu.

## 5. Ceklis Pre-Flight (Administratif & Rilis)
Lakukan ini **Tepat Sebelum** menjalankan `build_and_install.py` dan *Push* ke GitHub:
- [ ] **Nomor Versi Sama:** Pastikan variabel versi sudah dinaikkan secara identik di 3 tempat: `manifest.ini`, `version.json`, dan `build_and_install.py`.
- [ ] **Changelog Diperbarui:** Teks riwayat versi baru sudah dimasukkan di `version.json` dan kelas `ChangelogDialog` (`guiDialogs.py`). Cek `NVDA + /` lalu `V`.
- [ ] **Panduan Selaras:** Jika ada fitur/shortcut baru, dokumentasi bantuan (`Kerangka Kerja/`, `JadwalKu/doc/readme.html`, `doc/id/readme.html`, `doc/en/readme.html`, dan teks di `guiDialogs.py` tombol `B`) sudah diperbarui.
- [ ] **Kompilasi Sukses:** Anda sudah menjalankan skrip instalasi lokal, me-restart NVDA, dan tidak terjadi *error syntax* (crash awal).

---
*Jika semua kotak ini berhasil dicentang, pembaruan Anda sudah mencapai 99% aman untuk dinikmati seluruh pengguna!*
