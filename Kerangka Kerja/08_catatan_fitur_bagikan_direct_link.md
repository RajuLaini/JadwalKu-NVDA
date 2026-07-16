# Catatan Arsitektur Fitur Bagikan Add-on Direct Link (v1.6.1)

## 1. Latar Belakang & Tujuan
Pada versi sebelumnya, ketika seorang pengguna ingin merekomendasikan dan membagikan add-on **JadwalKu** kepada teman sesama pengguna NVDA, mereka harus mengirimkan tautan repositori GitHub biasa. Hal ini seringkali membingungkan bagi pengguna tunanetra pemula karena mereka harus membuka browser, menavigasi struktur halaman GitHub, mencari bagian *Releases* atau kode sumber, dan mengunduh file `.nvda-addon`.

Untuk memberikan pengalaman berbagi (*sharing experience*) yang instan, ramah aksesibilitas, dan tanpa hambatan (*frictionless*), JadwalKu v1.6.1 menghadirkan fitur **Bagikan Add-on Direct Link**.

## 2. Cara Kerja Teknis
Fitur ini memanfaatkan modul `api` internal NVDA (`api.copyToClip(url)`) yang aman secara thread dan langsung menyalin teks ke clipboard sistem operasi Windows tanpa memerlukan antarmuka visual atau objek `wx.TheClipboard` yang kompleks.

Tautan yang disalin adalah tautan unduhan langsung (*Direct Download Link*) ke file `.nvda-addon` dari repositori GitHub:
`https://raw.githubusercontent.com/RajuLaini/JadwalKu-NVDA/main/JadwalKu-v1.6.1.nvda-addon`

### Keunggulan Direct Link:
1. **Langsung Mengunduh (*One-Click Download*)**: Saat penerima menempel (*paste*) link tersebut di browser (seperti Chrome, Firefox, Edge) atau aplikasi *Download Manager*, browser tidak akan membuka halaman web HTML, melainkan langsung memulai proses pengunduhan file `JadwalKu-v1.6.1.nvda-addon`.
2. **Siap Pasang**: Setelah terunduh, penerima cukup menekan *Enter* pada file `.nvda-addon` tersebut dan NVDA akan langsung menanyakan konfirmasi pemasangan.

## 3. Titik Akses Fitur (*Access Points*)
Untuk kenyamanan maksimal, fitur ini dapat diakses melalui 4 jalur:
1. **Shortcut Mode Perintah (`NVDA + /` lalu `G`)**: Pemicu tercepat saat berada di aplikasi apa pun tanpa membuka dialog.
2. **Tombol di Panel Pengaturan NVDA (*Settings -> JadwalKu*)**: Tombol `&Bagikan Add-on (Copy Link ke Clipboard)...`.
3. **Tombol di Tab 1 & Tab 2 Dialog Utama**: Tersedia di bagian bawah atau sizer tombol navigasi dialog utama JadwalKu agar mudah dijangkau saat pengguna sedang mengatur agenda.
4. **Panduan & Bantuan (`NVDA + /` lalu `B` / `F1`)**: Tercatat lengkap di dalam panduan interaktif beserta penjelasan fungsinya.

## 4. Pelaporan Status & Umpan Balik Suara
Saat tombol atau shortcut `G` ditekan, sistem memberikan umpan balik suara instan melalui `ui.message()`:
`"Tautan unduhan langsung JadwalKu v1.6.1 berhasil disalin ke clipboard!"`
Jika terjadi kesalahan pada clipboard sistem Windows, sistem menangani dengan pesan kegagalan yang ramah dan mencatatnya pada `logHandler` NVDA.
