# Aturan Wajib Bantuan Dinamis / Kontekstual JadwalKu (Agent Rule)

Setiap kali Anda (Agen AI) ditugaskan untuk:
1. **Membuat dialog pengaturan (GUI) baru** (seperti membuat dialog untuk fitur yang baru dibuat).
2. **Menambahkan Tab (Page) baru** ke dalam dialog utama (`JadwalKuDialog` di `guiDialogs.py`).
3. **Memodifikasi fitur** sehingga mengubah cara kerja pengaturan yang ada.

Anda **WAJIB** mematuhi prosedur Bantuan Dinamis berikut:

## Aturan Utama (Contextual Help Button)
- **Tombol Bantuan Wajib Hadir**: Setiap dialog dalam JadwalKu yang memiliki tombol "Tutup", "Simpan", atau "Batal" (biasanya dengan `wx.StdDialogButtonSizer`), **WAJIB** menyertakan tombol `self.btnHelp = wx.Button(self, label="&Bantuan... (Alt+B)")` di sampingnya.
- **Shortcut & Binding**: Tombol ini harus di-*bind* ke `self.onContextualHelp` dan dapat diakses pengguna melalui kombinasi tombol `Alt+B`.

## Struktur `onContextualHelp(self, evt)`
- Dalam method `onContextualHelp`, Anda harus mendeklarasikan variabel `text` yang berisi panduan terperinci, mudah dipahami, dan relevan khusus untuk dialog tersebut.
- Panduan tersebut harus menjelaskan cara kerja fitur dan pintasan papan tik (keyboard shortcut) yang relevan (contoh: cara menjeda timer, atau arti status centang pada agenda).
- Untuk dialog utama dengan *Tab/Notebook*, metode ini harus memeriksa tab yang sedang aktif menggunakan `tab = self.notebook.GetSelection()` lalu menampilkan teks bantuan yang berbeda (dinamis) sesuai dengan tab tersebut (contoh: bantuan untuk Manajemen Agenda vs Pengaturan Waktu).

## Menggunakan `ContextualHelpDialog`
- Panggil `ContextualHelpDialog` dari `guiDialogs.py` untuk menampilkan teks panduan.
- Contoh implementasi:
  ```python
  def onContextualHelp(self, evt):
      from .guiDialogs import ContextualHelpDialog # (Hanya jika Anda berada di file lain seperti pomodoro.py)
      text = "BANTUAN FITUR XYZ:\n\n- Fitur ini digunakan untuk..."
      dlg = ContextualHelpDialog(self, "Bantuan: Fitur XYZ", text)
      dlg.ShowModal()
      dlg.Destroy()
  ```

Patuhi aturan ini tanpa pengecualian demi memastikan JadwalKu tetap ramah bagi pengguna tunanetra dan pembaca layar. Jangan membiarkan fitur baru dirilis tanpa melengkapinya dengan tombol Bantuan Dinamis!
