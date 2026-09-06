# Catatan Kesalahan Umum UI wxPython di JadwalKu

Dokumen ini mencatat kesalahan-kesalahan kritis yang pernah terjadi dalam pengembangan antarmuka JadwalKu menggunakan wxPython, agar tidak terulang di masa depan. Agen AI diwajibkan untuk memperhatikan catatan ini sebelum memodifikasi logika GUI.

## 1. Kesalahan Fatal: wx.YES vs wx.ID_YES (Dialog Pembaruan)
**Gejala Bug (v1.7.6.4.3 dan sebelumnya):**
Saat pengguna menekan tombol 'Ya' pada dialog pembaruan otomatis (Auto-Updater), pengunduhan tidak pernah terjadi, dan sistem malah menampilkan pesan: *'Pemeriksaan pembaruan otomatis dihentikan sampai NVDA dimuat ulang.'*

**Akar Masalah:**
Di dalam skrip wxPython, sering kali kita menggunakan \wx.MessageBox\ yang mengembalikan \wx.YES\. Namun, jika kita membuat jendela dialog kustom yang diturunkan dari \wx.Dialog\ dan memanggil \dlg.ShowModal()\, nilai kembalian saat pengguna menekan tombol Ya bukanlah \wx.YES\, melainkan **\wx.ID_YES\**.

\wx.YES\ bernilai konstanta \2\ (hanya digunakan untuk pengaturan *style*).
\wx.ID_YES\ bernilai konstanta \5103\ (digunakan sebagai ID pengenal event/tombol).

Karena evaluasi \if res == wx.YES:\ membandingkan \5103 == 2\, hasilnya selalu \False\, sehingga sistem akan melempar alur ke blok \else\ dan membatalkan pembaruan seolah-olah pengguna menekan 'Tidak'.

**Prosedur Pencegahan:**
Setiap kali memeriksa kembalian dari \ShowModal()\ untuk tombol standar wx, **SELALU** gunakan konstanta ID-nya:
- Gunakan \wx.ID_YES\ bukan \wx.YES\
- Gunakan \wx.ID_NO\ bukan \wx.NO\
- Gunakan \wx.ID_OK\ bukan \wx.OK\
- Gunakan \wx.ID_CANCEL\ bukan \wx.CANCEL\

**Penyelesaian di JadwalKu:**
Bug ini diperbaiki pada versi 1.7.6.5 di modul \updateChecker.py\ dengan mengubah \if res == wx.YES:\ menjadi \if res == wx.ID_YES:\.
