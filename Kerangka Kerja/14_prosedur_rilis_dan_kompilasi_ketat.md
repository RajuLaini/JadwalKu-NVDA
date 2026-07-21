# Dokumen Referensi 14: Prosedur Rilis & Kompilasi Ketat (Pencegahan Bug OTA/Over-The-Air)

## Latar Belakang Masalah
Pada siklus pembaruan versi 1.6.5, terjadi sebuah insiden di mana penambahan file master example Voice Pack (direktori `voice_master/`) berhasil masuk ke repositori Git (`JadwalKu/`), namun **pengguna tidak menerima** pembaruan tersebut ketika Auto-Updater mengunduh paket add-on. 

Penyebab utamanya adalah agen mengembangkan fitur dan mem-push *source code* ke branch `main`, namun **lupa membangun ulang (rebuild)** paket `.nvda-addon` dan mem-push file `.nvda-addon` hasil kompilasi tersebut ke GitHub. Auto-updater bekerja dengan mengunduh langsung file `JadwalKu-vX.X.X.nvda-addon` dari tautan yang ada di `version.json`. Jika arsip zip `.nvda-addon` tersebut tidak diperbarui secara sinkron dengan *source code*, maka pengguna akan mengunduh versi usang.

## Standar Operasional Prosedur (SOP) Rilis Pembaruan
Untuk mencegah kesalahan serupa, setiap agen **WAJIB** mematuhi tata urutan kompilasi rilis berikut secara kaku:

1. **Uji Fungsional & Penyelesaian Kode**
   Pastikan seluruh modifikasi pada folder `JadwalKu/globalPlugins/jadwalku/` berjalan sempurna tanpa *SyntaxError* atau *IndentationError*.
2. **Sinkronisasi Versi**
   Jika merilis perbaikan atau fitur, selalu selaraskan versi pada 3 file utama:
   * `build_and_install.py` (`ADDON_VERSION`)
   * `version.json` (termasuk deskripsi `changelog` dan *update link url* dengan nomor versi terbaru)
   * `JadwalKu/manifest.ini` (`version`)
3. **Pencatatan Riwayat (Changelog UI)**
   Perbarui variabel `changelog_text` di dalam `guiDialogs.py` agar pengguna dapat membaca langsung dari shortcut `NVDA + /` lalu `V`.
4. **Kompilasi & Pemasangan**
   Jalankan perintah absolut:
   `python build_and_install.py`
   Perintah ini akan secara otomatis menyedot seluruh konten dari `JadwalKu/` dan membungkusnya menjadi `JadwalKu-vX.X.X.nvda-addon` di root proyek.
5. **Git Add File Add-On**
   **KRITIKAL:** Anda TIDAK BOLEH hanya melakukan `git add JadwalKu/` dan melupakan file add-on. Anda **WAJIB** menyertakan file hasil kompilasi:
   `git add JadwalKu-vX.X.X.nvda-addon` (Sesuaikan versi).
   (Contoh eksekusi nyata: `git add version.json build_and_install.py JadwalKu/manifest.ini JadwalKu/globalPlugins/jadwalku/guiDialogs.py JadwalKu-vX.X.X.nvda-addon`)
6. **Commit & Push**
   Lakukan `git commit` dan `git push origin main`.

Hanya dengan menyertakan *file bundle* instalernya (file berakhiran `.nvda-addon`) ke repositori awan, pembaruan Over-The-Air dapat tiba dengan selamat di komputer seluruh pengguna.
