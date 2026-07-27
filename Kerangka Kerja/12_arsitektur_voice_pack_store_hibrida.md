# Catatan Arsitektur: Voice Pack Store Hibrida (Cloudflare + Hugging Face)

**Tanggal:** 20 Juli 2026
**Penulis:** Antigravity (Agen AI)

## Latar Belakang
Fitur "Voice Pack Store" dirancang agar pengguna JadwalKu dapat saling berbagi dan mengunduh paket suara kustom dari seluruh dunia langsung dari dalam add-on NVDA.
Syarat mutlak dari arsitektur ini adalah **"Satu Pengguna, Satu Voice Pack"** untuk mencegah spam dan penyalahgunaan.

Awalnya, arsitektur ini dirancang menggunakan Cloudflare Workers dan Cloudflare R2 (Object Storage). Namun, karena aktivasi R2 mewajibkan penambahan metode pembayaran (Kartu Kredit/PayPal) meskipun layanannya gratis, kami memutuskan untuk membatalkan R2 demi memastikan kebebasan finansial bagi pengembang (Raju Laini).

Sebagai gantinya, kami merancang **Sistem Hibrida 100% Gratis** yang mengombinasikan kekuatan komputasi Cloudflare dengan keleluasaan penyimpanan dari Hugging Face Hub.

## Arsitektur Hibrida
Arsitektur backend diimplementasikan menggunakan pemisahan tegas dari akun utama (Akun A/Bot Aileen) dengan menggunakan **Akun Cloudflare B** untuk backend ini.

### 1. Cloudflare Workers (`jadwalku-vp-api`)
Berfungsi sebagai **Otak (Compute API)**.
- Menerima permintaan unggah dari pengguna NVDA.
- Membaca dan menvalidasi Hardware ID pengguna.
- Beroperasi murni pada *edge network* Cloudflare tanpa memungut biaya.
- Alamat API saat ini: `https://jadwalku-vp-api.onionknight610.workers.dev`

### 2. Cloudflare KV Namespace (`VP_STORE_DB`)
Berfungsi sebagai **Buku Catatan (Database)**.
- Database *key-value* cepat yang mencatat relasi `HardwareID -> Nama_File_VoicePack.jvp`.
- Saat pengguna mencoba mengunggah paket kedua, Worker akan mengecek ke KV dan dapat menolaknya atau menimpa paket lama mereka.

### 3. Hugging Face Datasets (`OrionWood/JadwalKu-VoicePacks`)
Berfungsi sebagai **Gudang File Tak Berbatas (Storage)**.
- Repositori publik yang aman.
- Saat Worker selesai memverifikasi izin pengguna, Worker tidak menyimpan file tersebut secara lokal, melainkan langsung menyuntikkannya (*forward/upload*) ke repositori Hugging Face menggunakan *Hugging Face Hub API*.
- NVDA Add-on akan mengunduh paket suara orang lain menggunakan tautan *Direct Download* murni dari Hugging Face yang stabil dan memiliki *bandwidth* tanpa batas (berbeda dengan GitHub yang rawan *rate limit* untuk unduhan berulang).

## Alur Data
1. **Upload:** NVDA Add-on -> `POST /upload` (Cloudflare Worker) -> Verifikasi KV -> Upload ke Hugging Face LFS API -> Catat sukses di KV -> Kirim respons sukses ke NVDA.
2. **List:** NVDA Add-on -> `GET /list` (Cloudflare Worker) -> Minta `/tree` dari Hugging Face API -> Filter khusus file `.jvp` -> Kembalikan format JSON ringkas ke NVDA.
3. **Delete (Patch 1.7.1):** NVDA Add-on -> `DELETE /delete` (Cloudflare Worker) dengan header `User-Agent: JadwalKu-NVDA` (wajib untuk lolos dari filter WAF Cloudflare 1010) -> Verifikasi KV & Sandi -> Hapus dari Hugging Face via Commit API (`deletedFile`) -> Hapus dari KV -> Kirim respons sukses ke NVDA.

## Kredensial dan Keamanan
Semua kredensial disembunyikan menggunakan Cloudflare Secrets.
- `HF_TOKEN`: Token rahasia *Hugging Face* dengan izin *Write*. Tidak pernah diekspos ke publik.
- Worker diprogram untuk secara ketat membersihkan (*sanitize*) nama file dengan fungsi Regex untuk mencegah *Path Traversal Attack* atau karakter aneh yang dapat merusak repositori. File dinamakan dengan gabungan hash HardwareID pendek dan nama paket bersih.
- **Master Password Darurat:** Diatur menggunakan Cloudflare Secret (`MASTER_PASSWORD`) untuk memberikan hak istimewa (*override*) bagi Admin agar dapat menghapus paket suara pengguna yang terkunci akibat lupa sandi, langsung melalui antarmuka NVDA. Tidak di-*hardcode* di dalam skrip demi keamanan.
