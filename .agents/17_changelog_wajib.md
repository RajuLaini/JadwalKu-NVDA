# Aturan Wajib Penulisan Riwayat Pembaruan (Changelog) JadwalKu

Setiap kali Anda (Agen AI) ditugaskan untuk melakukan:
1. Penambahan fitur baru sekecil apa pun.
2. Perbaikan bug (bugfix) atau error.
3. Modifikasi atau pembaruan kode yang mengubah perilaku sistem.

Anda **WAJIB** mencatat seluruh perubahan tersebut ke dalam riwayat pembaruan (Changelog) agar pengguna selalu mengetahui apa yang baru tanpa ada yang terlewat.

## Lokasi yang Wajib Diperbarui
Anda harus memperbarui riwayat pada DUA file berikut secara sinkron:

1. **`guiDialogs.py` (Variabel `changelog_text` di kelas `ChangelogDialog`)**
   - Cari bagian daftar riwayat di bawah label versi yang sedang dikerjakan (contoh: `--- Versi 1.7.6.1 ---`).
   - Tambahkan poin penjelasan fitur/perbaikan menggunakan simbol bintang (`*`).
   - Penjelasan harus jelas, mudah dipahami pengguna awam, dan merangkum manfaat dari perubahan tersebut.

2. **`version.json` (Properti `"changelog"`)**
   - Tambahkan poin pembaruan yang sama (bisa sedikit diringkas) ke dalam string `changelog`.
   - Gunakan format baris baru `\n` dan awalan tanda hubung (`-`) untuk poin-poinnya.

## Pengecualian
Aturan ini **wajib dilakukan** meskipun pengguna hanya mengatakan "tetap di versi yang sama". Selama ada fitur baru yang ditambahkan, laporan riwayat untuk versi berjalan harus ditambahkan sebelum tugas dinyatakan selesai!
