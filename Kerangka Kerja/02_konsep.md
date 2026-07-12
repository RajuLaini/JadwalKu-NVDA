# Konsep & Filosofi Desain Add-on JadwalKu

## 1. 100% Aksesibel & Ramah Screen Reader (Screen Reader First)
- **Hindari Ketik Manual yang Rentan Error**: Dalam pengembangan GUI untuk tunanetra, kolom input teks bebas (`TextCtrl`) sering kali menyebabkan kesalahan pengetikan format waktu (seperti mengetik `23.15` atau `23;15` bukannya `23:15`). JadwalKu menggantikan seluruh input waktu menggunakan **Combo Box (Dropdown)** yang terstandarisasi.
- **Navigasi Cepat dengan Keyboard**: Seluruh elemen antarmuka dilengkapi *keyboard accelerators* (`Alt + T`, `Alt + E`, `Alt + P`, dll.) dan mendukung tombol `Enter` serta `Spasi` untuk interaksi langsung.
- **Manajemen Fokus yang Ketat**: Setiap dialog dilindungi oleh `gui.mainFrame.prePopup()` dan `postPopup()` sehingga fokus NVDA tidak pernah terlepas atau berpindah secara liar saat dialog dibuka/ditutup.

## 2. Non-Blocking & Background Execution
- **Pemisahan Logika & UI**: Logika pemeriksaan waktu berjalan terpisah di modul `scheduler.py` menggunakan `wx.Timer` yang terpicu setiap 1.000 milidetik (1 detik).
- **Deduplikasi Menit (*Deduplication Caching*)**: Agar alarm atau chime tidak berbunyi berulang-ulang di dalam satu menit yang sama, scheduler menyimpan *state* `last_triggered_minute` baik pada pengingat waktu berkala maupun pada setiap item agenda rutin.
- **Unduhan Latar Belakang (*Threaded Networking*)**: Pengecekan versi JSON dan pengunduhan file `.nvda-addon` selalu dieksekusi di dalam `threading.Thread(daemon=True)`. Hal ini menjamin NVDA tetap responsif dan suara screen reader tidak pernah macet saat menunggu respons jaringan.

## 3. Persistensi Data di Luar Folder Add-on (*Safe Update Architecture*)
- **Lokasi Penyimpanan Data**: Seluruh jadwal agenda dan konfigurasi pengingat disimpan dalam file JSON:
  `%appdata%\NVDA\jadwalku_data.json`
- **Keuntungan Besar**: Karena data disimpan di folder konfigurasi global NVDA (bukan di dalam folder `addons/JadwalKu/`), pengguna dapat menimpa, memperbarui (*update*), atau bahkan mencopot dan memasang ulang add-on JadwalKu tanpa risiko kehilangan satu pun data agenda yang sudah mereka buat.

## 4. Distribusi Private GitHub & Pembaruan Tanpa Ribet
- Menggunakan repositori **GitHub Private** (`RajuLaini/JadwalKu-NVDA`) untuk kolaborasi terbatas dan *beta testing*.
- Fitur **Direct Background Downloader** menghapus hambatan teknis bagi pengguna awam: mereka tidak perlu mengerti cara kerja browser atau GitHub untuk memperbarui add-on. Cukup klik `Yes` pada dialog NVDA, dan sistem akan mengunduh serta memunculkan dialog instalasi secara otomatis.
