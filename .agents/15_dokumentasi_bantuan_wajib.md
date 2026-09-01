# Aturan Wajib Pembaruan Dokumentasi (Agent Rules)

Aturan ini dibuat secara khusus untuk memastikan bahwa panduan dan bantuan add-on JadwalKu (baik versi HTML maupun In-App) tidak pernah tertinggal dari fitur kode aslinya.

## MENGAPA INI PENTING?
Pengguna tunanetra sangat bergantung pada akurasi *Help Dialog* (`NVDA + /` lalu `B`) dan file `readme.html` yang disediakan oleh manajer Add-on NVDA. Jika fitur atau *shortcut* baru ditambahkan ke `__gestures` (atau mode lapisan perintah `commandLayerGestures`), dan tidak dicatat di dokumentasi, maka pengguna tidak akan pernah tahu fitur tersebut ada.

## PROSEDUR TETAP (SOP) AGEN:
Setiap kali Anda (Agen AI) menambahkan, mengubah, atau menghapus *shortcut* (tombol) atau fitur baru pada arsitektur JadwalKu, Anda **WAJIB** mengeksekusi tiga langkah berikut secara bersamaan sebelum mengakhiri tugas Anda:

1. **Perbarui `JadwalKu/doc/id/readme.html` dan `JadwalKu/doc/readme.html`**
   - Pastikan Anda menambahkan atau menghapus deskripsi fitur tersebut menggunakan HTML dasar (`<ul>`, `<li>`, `<b>`).
   - Ubah nomor versi di dalam tag `<h1>` jika ada kenaikan versi.

2. **Perbarui `JadwalKu/doc/en/readme.html`**
   - Lakukan hal yang sama seperti di atas, namun terjemahkan dengan akurat ke bahasa Inggris. Folder `doc/en/` didedikasikan untuk pengguna global. Jangan pernah menyalin isi bahasa Indonesia secara mentah ke dalamnya.

3. **Perbarui `guiDialogs.py` (Kelas `HelpDialog`)**
   - Cari variabel `help_text` di dalam fungsi `__init__` pada kelas `HelpDialog`.
   - Modifikasi *string* teks panjang di dalamnya agar secara akurat merepresentasikan perubahan yang Anda buat. Pastikan susunan *string*-nya tidak berantakan (hindari Syntax Error) dengan menggunakan regex atau skrip `replace_file_content` yang aman.

**Jika Anda melupakan langkah-langkah di atas, Anda telah menggagalkan aksesibilitas pengguna!**
