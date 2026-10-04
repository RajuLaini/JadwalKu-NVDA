# Protokol Rilis Versi dan Push GitHub JadwalKu

Dokumen ini berisi prosedur mutlak terkait kenaikan versi (Version Bump) dan pengiriman kode ke repositori publik GitHub.

## 1. DILARANG MELAKUKAN PUSH TANPA PERINTAH EKSPLISIT
Agen dilarang keras melakukan perintah `git push` ke repositori `main` GitHub kecuali pengguna secara spesifik mengetikkan perintah/kata kunci: **"Push ke GitHub"** atau **"Silakan rilis ke publik"**.

**Alasan:** Repositori GitHub terhubung langsung dengan sistem Auto-Updater yang dipakai oleh ratusan pengguna tunanetra. Melakukan push kode yang belum stabil akan menyebabkan pembaruan massal yang merusak sistem pengguna.

## 2. Kenaikan Versi (Version Bump)
Agen boleh menaikkan versi (misal dari `1.7.6.5.7` ke `1.7.6.5.8`) secara LOKAL untuk pengujian, namun harus tetap mengikuti batasan berikut:
- **Perubahan Minor/Eksperimen**: Jangan naikkan versi mayor. Tetap di versi yang sama atau tambahkan sub-versi kecil (misal: penambahan patch lokal).
- Jika pengguna meminta "Tetap di versi yang sama", agen **DILARANG** mengubah `version.json`, `manifest.ini`, atau `build_and_install.py` untuk menaikkan versi.
- Jika ada perubahan kode yang belum di-push, agen WAJIB melakukan kompilasi lokal menggunakan `python build_and_install.py` lalu melakukan `git commit` saja (simpan di riwayat lokal).

## 3. Prosedur Saat Mendapat Izin Rilis
Jika pengguna sudah memberikan izin eksplisit (contoh: "Oke, kode sudah stabil, silakan rilis versi 1.7.6.6 dan push ke Github"):
1. Pastikan `changelog` di `guiDialogs.py` dan `version.json` sudah sinkron dan rapi.
2. Pastikan `manifest.ini` dan variabel `ADDON_VERSION` di `build_and_install.py` sudah tepat.
3. Jalankan `python build_and_install.py` untuk menghasilkan file `.nvda-addon` terbaru.
4. Lakukan komit: `git add .` dan `git commit -m "Rilis v..."`.
5. Lakukan `git push origin main`.
6. Selalu beritahu pengguna bahwa pembaruan publik sedang mengudara.

## KESIMPULAN
**LOKAL ADALAH RAJA.** Selama tidak ada kata "Push", semua pekerjaan (meskipun versi berganti) WAJIB BERHENTI pada tahap `git commit` lokal.
