# Dokumen Referensi 17: Catatan Kegagalan RAM Cache & Tragedi Auto-Updater

Dokumen ini mencatat dua buah insiden "kutu" (bug) paling epik dan berbahaya yang berhasil ditaklukkan pada siklus rilis 1.7.6.4.x. Hal ini harus diingat secara permanen agar tidak terulang kembali di masa depan saat mengembangkan fitur baru.

## 1. Tragedi "Jam 4 Lewat 0 Menit" (Bug RAM Cache pada Voice Pack)
**Gejala:** Saat jam 04:30, pengguna melaporkan bahwa add-on menyebutkan "Jam 4 lewat 0 menit". 
**Akar Masalah:**
- Pada versi 1.7.6.4, kita mengimplementasikan optimasi C-Level `audioop` untuk performa volume tinggi dan menyematkan sistem `_audio_cache` (caching di RAM) agar NVDA tidak tersendat (lag) saat memutar suara berulang. Cache ini dikunci (*keyed*) menggunakan nama/lokasi file (`filepath`) dan persentase volume.
- Untuk fitur *Voice Pack* gabungan (sekuensial kalimat), sistem mengekstrak dan menggabungkan banyak kata dari file zip ke satu file *sementara* yang **namanya selalu tetap sama** (yakni `jadwalku_vp_seq.wav`).
- Akibatnya, pada jam 04:00, suara "jam 4 lewat 0 menit" disimpan dalam *cache* berdasarkan *key* `jadwalku_vp_seq.wav`. 
- Pada jam 04:30, meskipun file `.wav` tersebut di-generate ulang isinya dengan "jam 4 lewat 30 menit", mesin membaca nama filenya yang masih sama (`jadwalku_vp_seq.wav`) dan dengan cepat mengambil audio basi "jam 4 lewat 0 menit" dari dalam memori RAM, mengabaikan file yang sebenarnya.
**Solusi Permanen (v1.7.6.4.2):**
- Menambahkan parameter / variabel *bypass_cache* di dalam fungsi pemutaran WinMM, agar setiap `filepath` yang bernama `jadwalku_vp_seq.wav` dipaksa untuk membaca langsung dari *disk* tanpa membaca maupun menulis ke `_audio_cache`.

## 2. Kesalahan Fatal Skup Kelas "Gagal Memeriksa Pembaruan" (Auto-Updater Crash)
**Gejala:** Setelah pengguna menekan tombol periksa pembaruan, *log* NVDA berteriak `"UpdateChecker object has no attribute '_show_update_prompt'"` dan UI menampilkan *"Gagal memeriksa pembaruan. Periksa koneksi internet..."*
**Akar Masalah:**
- Kesalahan ini sangat merusak karena membuat semua pengguna terjebak di versi usang dan tidak bisa memperbarui secara otomatis.
- Terjadi ketika agen menggunakan tool penyuntingan kode secara mentah untuk menyisipkan *class* `UpdatePromptDialog` *tepat di tengah-tengah* metode milik `UpdateChecker` di `updateChecker.py`.
- Karena Python sangat bergantung pada lekukan (*indentation*), menyisipkan deklarasi kelas dengan `0 tab` (indentasi awal) memutus kelas sebelumnya (`UpdateChecker`). Segala metode (seperti `_show_update_prompt`) yang berada di bawah penyisipan tersebut malah menjadi bagian dari kelas *UpdatePromptDialog*, merusak arsitektur `UpdateChecker` dan melenyapkan berbagai fungsi pentingnya.
**Solusi Permanen (v1.7.6.4.3):**
- Kelas `UpdatePromptDialog` harus diinspeksi posisi hirarkinya. Memindahkannya ke luar (di atas `UpdateChecker`) menggunakan utilitas pemrograman (*script* parsial) untuk menjamin AST (Abstract Syntax Tree) Python tetap murni dan tidak ada metode yang "terculik" oleh kelas lain.
- Sangat dilarang untuk menyisipkan deklarasi *class* di tengah metode yang sedang berjalan. Wajib selalu membaca file utuh dan mengetahui kapan *class* berakhir.
