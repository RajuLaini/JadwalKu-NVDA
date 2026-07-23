# Panduan Multi-Akun Cloudflare dengan Wrangler 2

Dokumen ini mencatat sejarah dan prosedur mengelola peluncuran (*deploy*) Cloudflare Worker ke beberapa akun Cloudflare yang berbeda (misalnya akun utama dan akun kedua) menggunakan antarmuka baris perintah (CLI) Wrangler versi terbaru.

## Latar Belakang Masalah
Dalam proyek JadwalKu, Cloudflare Worker untuk *Voice Pack Store* berada di **Akun Cloudflare Kedua**, bukan di akun utama.
Saat mencoba melakukan peluncuran otomatis menggunakan Token API (melalui variabel `CLOUDFLARE_API_TOKEN`), terjadi penolakan izin `Authentication error [code: 10000]`. Hal ini sering kali disebabkan karena Token tersebut tidak memiliki cakupan otorisasi lintas akun yang tepat, atau *Wrangler* kebingungan saat tidak menemukan `account_id` yang sesuai di `wrangler.toml`.

## Solusi Paling Tangguh: Profil Autentikasi Wrangler (`wrangler auth`)

Wrangler terbaru sangat mendukung multi-akun melalui fitur **Profil (Profile)**. Berikut adalah cara untuk menghubungkan dan mengatur peluncuran ke akun kedua tanpa pusing berurusan dengan pengaturan izin Token API manual:

### 1. Membuat Profil Baru untuk Akun Kedua
Buka terminal dan jalankan perintah berikut:
```bash
npx wrangler auth create akun_kedua
```
*Catatan: Ganti `akun_kedua` dengan nama profil apa pun yang Anda inginkan.*

**Proses yang terjadi:**
1. Perintah ini akan memicu *Wrangler* untuk membuka halaman login/otorisasi Cloudflare di *browser* bawaan komputer Anda.
2. Di dalam *browser*, pastikan Anda **telah login menggunakan akun Cloudflare Kedua** (akun yang dituju).
3. Klik tombol **"Allow"** (Izinkan).
4. *Wrangler* akan menyimpan kredensial sesi tersebut dengan nama profil `akun_kedua` secara aman di sistem lokal Anda.

### 2. Meluncurkan Worker menggunakan Profil Tersebut
Setelah profil berhasil dibuat, Anda bisa menyuruh *Wrangler* untuk menggunakan profil tersebut secara spesifik saat meluncurkan Worker, mengabaikan akun default yang sedang login.

Jalankan perintah peluncuran dengan menyertakan *flag* `--profile`:
```bash
npx wrangler deploy --profile akun_kedua
```

Dengan tambahan perintah `--profile akun_kedua`, seluruh proses peluncuran (termasuk deteksi ID Akun dan izin KV Namespace) akan diarahkan dengan mulus ke akun Cloudflare kedua.

### Kesimpulan
Metode `--profile` pada Wrangler sangat dianjurkan saat bekerja secara kolaboratif atau mengelola beberapa agen/proyek di bawah akun Cloudflare yang berbeda-beda, karena menghilangkan kebutuhan untuk mengingat kata sandi atau menyalin ulang Token API secara berulang setiap kali sesi kedaluwarsa.
