# Arsitektur Perintah Suara (Voice Command) Modular JadwalKu

Dokumen ini memuat landasan konseptual dan teknis untuk fitur **Perintah Suara Offline** yang didesain agar sangat ringan, aman secara privasi, dan tidak mengganggu kinerja perangkat keras pengguna.

## 1. Filosofi Desain Modular
Add-on JadwalKu harus dipertahankan seringan mungkin (di bawah 2 MB) untuk menghemat ruang dan waktu muat (*load time*) pada NVDA. Karenanya, mesin pengenalan suara (*Speech-to-Text*) tidak akan disertakan (*bundled*) secara langsung.
- Pengguna yang ingin mengaktifkan fitur ini diwajibkan untuk mengunduh modul ekstensi dari menu Pengaturan JadwalKu (Tab "Perintah Suara").
- Jika ekstensi tidak diunduh, antarmuka hanya akan menampilkan tombol **"Unduh & Pasang Modul (±45 MB)"** tanpa memuat dependensi berat apapun ke dalam memori.

## 2. Pengelolaan Memori & Beban Perangkat Keras
Pertanyaan utama dalam fitur semacam ini adalah dampaknya terhadap SSD/Hardisk, RAM, dan CPU. Berikut adalah jaminan arsitektur yang dirancang untuk JadwalKu:

### A. Beban Tulis / Baca pada Hardisk (Zero Disk Wear)
- **Tidak ada Audio yang Disimpan:** Berbeda dengan Perekam Suara (Voice Studio) yang menulis ke `.wav`, modul *Voice Command* akan membaca data PCM (suara mentah) dari antarmuka API `winmm.dll` dan memindahkannya **langsung ke RAM (Memory Buffer)** menggunakan *chunks* kecil (misalnya 4000 byte per putaran).
- **Penghapusan Langsung:** Begitu *chunk* diproses oleh mesin Vosk untuk mencari kata kunci, *chunk* tersebut otomatis ditumpuk ulang (dihancurkan oleh *Garbage Collector* Python).
- **Kesimpulan Disk:** Arsitektur ini **0% menulis (write) ke SSD/Hardisk** saat mikrofon aktif, sehingga usia pemakaian disk (*Disk Wear-leveling*) sama sekali tidak terpengaruh. Pembacaan (*read*) hanya terjadi satu kali saat memuat Model Bahasa ke RAM di awal NVDA dihidupkan.

### B. Beban RAM & Prosesor (Low Footprint)
- Model bahasa Indonesia yang digunakan adalah varian khusus untuk perangkat *IoT/Mobile* (misalnya `vosk-model-small-id`). Model ini hanya akan memakan RAM secara statis sekitar **~40 hingga 50 MB**.
- Penggunaan CPU untuk pemantauan kata sandi (seperti "jam berapa") oleh Vosk yang sudah sangat dioptimasi dalam C++ umumnya berfluktuasi antara **1% hingga 3%** saja pada laptop modern.

## 3. Komponen Antarmuka Pengguna (GUI)
Sebuah tab baru akan dibuat pada Pengaturan JadwalKu:
- **Status Modul:** Menampilkan status apakah modul terpasang atau tidak.
- **Aktifkan Pemantauan Mikrofon:** *Checkbox* yang juga dapat di-*toggle* secara global menggunakan kombinasi tombol (misal: `NVDA + / lalu M`).
- **Gaya Pengucapan Khusus Perintah Suara:** *Combo box* (Misal: "Sekarang jam 09:00", "Pukul 09:00 tepat", dsb).
- **Mesin Penjawab (Output Engine):** Memungkinkan pemilihan SAPI 5, eSpeak, atau Rekaman Paket Suara Tertentu secara mandiri.
- **Speaker Keluaran:** *Combo box* pemilihan perangkat audio untuk respon suara.

## 4. Alur Interaksi
1. Pengguna menekan `NVDA + /, M` (Atau mengaktifkan centang di Pengaturan).
2. Sistem mencetak log dan menyuarakan, "Mikrofon Aktif".
3. Sebuah utas (*background thread*) akan diluncurkan. Utas ini akan membuka *stream audio* via `winmm.dll` (atau Pyaudio jika dibundel di dalam modul).
4. Suara ditangkap -> dikirim ke RAM -> dianalisa oleh Vosk.
5. Vosk mengembalikan teks (Teks transkripsi).
6. Logika percabangan JadwalKu mendeteksi keberadaan *substring* seperti `"jam berapa"`, `"sekarang jam berapa"`, atau `"jam berapa ya"`.
7. Jika terdeteksi:
   - Utas akan dihentikan sebentar (atau diredam).
   - TTS atau Voice Pack yang dipilih akan menyuarakan waktu saat ini.
   - Mikrofon siaga kembali.

## 5. Keamanan & Privasi
Karena Vosk adalah mesin berbasis *offline*, aliran internet (*network I/O*) sama sekali tidak dibutuhkan dan tidak ada port eksternal yang dihubungi. Ini menjamin suara latar belakang dan privasi pengguna tetap berada di dalam lokal komputer seutuhnya.
