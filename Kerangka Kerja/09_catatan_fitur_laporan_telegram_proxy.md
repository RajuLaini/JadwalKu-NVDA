# Catatan Pengembangan: Fitur Kirim Laporan, Kritik, Saran & Bug Fix via Web API Proxy Telegram (v1.6.2)

## 1. Latar Belakang & Filosofi Keamanan (*Security by Design*)
Dalam pengembangan add-on NVDA berbasis Python, seluruh kode sumber (*source code*) bersifat terbuka (*open-source*) di dalam folder `%appdata%\nvda\addons\JadwalKu\globalPlugins\jadwalku`. Jika pengembang menyimpan Token Bot Telegram langsung ke dalam script Python add-on untuk mengirimkan laporan bug dari komputer pengguna, pihak yang tidak bertanggung jawab dapat dengan mudah mengekstrak token tersebut dan melakukan penyalahgunaan (*spamming/hacking* pada bot pengembang).

Oleh karena itu, pada **v1.6.2**, kita menerapkan rancangan arsitektur **Serverless Web API Proxy / Forwarder**. Add-on JadwalKu di komputer pengguna **tidak pernah** berhubungan langsung dengan server API Telegram maupun menyimpan API Token bot. Add-on hanya berkomunikasi dengan script proxy PHP sederhana (`jadwalku_telegram_proxy.php`) yang ditempatkan di server/hosting pengembang (misalnya di domain `rajulaini.com`). Proxy inilah yang menyimpan Token Bot **Aileen** secara rahasia dan meneruskan pesan ke Telegram.

## 2. Fitur & Alur Kerja di Sisi Pengguna (Add-on JadwalKu)
1. **Pemicu Mudah & Aksesibel**: Pengguna dapat menekan kombinasi `NVDA + /` lalu `R`, ataupun menekan tombol `&Kirim Laporan, Kritik & Saran...` dari Panel Pengaturan JadwalKu di preferensi NVDA.
2. **Pemilihan Kategori & Sub-Fitur Diagnostik**:
   - **Minta Fitur Baru**: Untuk saran fitur baru. Kotak judul terisi otomatis dan dapat diedit.
   - **Laporkan Kesalahan (Bug/Error)**: Menampilkan dropdown tambahan berisi **10 Modul Utama JadwalKu** (`Manajemen Agenda`, `Pengingat Waktu Berkala`, `Timer Mundur Cepat`, `Alarm Sekali Pakai`, `Kalender & Tanggal Merah`, `Jam Dunia`, `Mesin Suara TTS Mandiri`, `Audio Manager / Speaker`, `Auto-Updater`, atau `Lainnya`).
   - **Kritik & Saran Umum**: Untuk masukan umum perihal pengalaman pengguna.
3. **Transparansi Log Diagnostik**: Khusus saat kategori "Laporkan Kesalahan" dipilih, sistem secara otomatis mengekstrak **15 baris log terakhir** terkait JadwalKu dari buffer log NVDA (`reportSender.extract_recent_logs()`) dan menampilkannya pada kotak teks read/write transparan di bagian bawah dialog. Pengguna dapat meninjau, membaca, dan mengedit log tersebut sebelum dikirimkan.
4. **Metadata Sistem Otomatis**: Laporan secara otomatis melampirkan informasi non-sensitif untuk keperluan debugging:
   - Nama Pengguna & Nama Komputer (`os.getlogin()`, `platform.node()`)
   - Versi NVDA & Versi Windows (`versionInfo.version`, `platform.platform()`)
   - Waktu Lokal Pengguna (`datetime.datetime.now()`)
5. **Pengiriman Asinkron Tanpa Freeze (*Non-blocking Async Post*)**: Pengiriman laporan dilakukan di *background thread* menggunakan `threading.Thread` dan `urllib.request`. Jika pengiriman selesai atau gagal, antarmuka diperbarui secara mulus menggunakan `wx.CallAfter` sehingga NVDA tidak pernah mengalami *freeze* atau *lag*.

## 3. Sistem Proteksi & Batasan Kuota (*Rate Limiting & Anti-Spam*)
Untuk mencegah terjadinya penyalahgunaan atau *spamming* ke bot Telegram pengembang, arsitektur ini menerapkan proteksi berlapis baik di sisi client (add-on) maupun server (PHP proxy):
1. **Batasan Sisi Client (Add-on)**: Add-on menyimpan tanggal laporan terakhir (`last_report_date`) ke dalam file JSON (`jadwalku_data.json`). Satu komputer pengguna hanya diizinkan mengirimkan **1 laporan per hari**. Jika mencoba mengirim lagi di hari yang sama, add-on akan memberi tahu pengguna dengan santun.
2. **Batasan Sisi Server (PHP Proxy - `jadwalku_telegram_proxy.php`)**:
   - **IP Rate Limiting**: Server mencatat daftar IP yang telah mengirim laporan pada hari tersebut (`daily_reports_counter.json`).
   - **Global Daily Quota**: Server membatasi total maksimal **10 laporan per hari** dari seluruh pengguna digabungkan. Jika kuota 10 laporan sudah habis, server merespons dengan HTTP status 429 dan pesan yang ramah agar pengguna mencoba kembali keesokan harinya.
3. **Penyelamat Kontribusi (*Clipboard Fallback Engine*)**: Jika komputer pengguna sedang offline, server proxy sedang down, atau kuota laporan harian telah penuh, add-on secara otomatis **menyalin seluruh isi laporan beserta log diagnostik ke Clipboard pengguna** (`api.copyToClip`) dan memberitahukan agar laporan dapat ditempel (*paste*) dan dikirim secara manual melalui Telegram pengembang. Tidak ada kontribusi atau laporan yang terbuang sia-sia!

## 4. Migrasi ke Cloudflare Workers & Endpoint Proxy (`v1.6.2`)
Untuk meningkatkan kecepatan, keandalan, dan skalabilitas pengiriman laporan dari add-on NVDA ke Bot Telegram Aileen, server penerima laporan (Feedback Webhook Proxy) kini telah dimigrasikan ke **Cloudflare Workers** berkecepatan tinggi milik Butterfly Universe:
1. **Endpoint Utama**: `https://butterflywings.my.id/api/jadwalku/proxy`
2. **Endpoint Backup (Direct Worker)**: `https://butterflywings-universe.rajulaini20.workers.dev/api/jadwalku/proxy`

Arsitektur baru ini mendukung spesifikasi penuh:
- HTTP GET `?action=check_limit` untuk memeriksa kuota harian (`allowed: bool`, `message: str`).
- HTTP POST JSON untuk mengirimkan laporan secara asinkron dengan payload spesifik (`username`, `machine_name`, `nvda_version`, `os_version`, `category`, `sub_feature`, `title`, `description`, `logs`, `client_time`).
- Proteksi Timeout 15 detik dan penanganan respons HTTP 200, 400, dan 429 yang langsung disampaikan ke pengguna melalui suara NVDA & pesan UI tanpa membekukan pembaca layar. Jika terjadi koneksi offline atau masalah jaringan, laporan tetap otomatis disalin ke clipboard pengguna sebagai jaminan kontribusi antat!
