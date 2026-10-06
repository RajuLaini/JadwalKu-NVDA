import re

with open(r'.agents\AGENTS.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Update Section 1
old_sec_1 = """## 1. Pembaruan Catatan Riwayat di Tombol V (ChangelogDialog - guiDialogs.py)
- **Wajib Memperbarui guiDialogs.py**: Setiap perubahan kode atau penambahan fitur harus langsung dicatat ke dalam variabel changelog_text di dalam kelas ChangelogDialog (di bawah heading versi terbaru yang sedang berjalan).
- **Shortcut NVDA + / lalu V**: Pastikan deskripsi pada command layer (__init__.py) selaras, sehingga saat pengguna menekan shortcut V, riwayat pembaruan terbaru langsung dapat dibaca dengan mudah menggunakan panah atas/bawah."""

new_sec_1 = """## 1. Pembaruan Catatan Riwayat di Tombol V (ChangelogDialog - guiDialogs.py)
- **Arsitektur ListBox Baru**: Mulai Oktober 2026, catatan riwayat TIDAK LAGI menggunakan variabel teks tunggal. Riwayat kini disimpan dalam variabel self.versions (sebuah List of Tuples) di dalam ChangelogDialog (file guiDialogs.py).
- **Wajib Memperbarui guiDialogs.py (Metode Sisip/Insert)**: Setiap ada rilis versi BARU (misal 1.7.6.5.8), agen JANGAN mengubah atau menghapus teks versi lama. Agen cukup **menyelipkan Tuple baru di urutan teratas (index 0)** tepat di bawah deklarasi self.versions = [.
  Contoh format: ("Versi 1.7.6.5.8", \"\"\"- Fitur baru...\"\"\"),
- Jika hanya memperbarui versi saat ini (versi belum naik), cukup tambahkan poin di Tuple versi teratas tersebut.
- **Shortcut NVDA + / lalu V**: Pastikan riwayat terbaru bisa langsung dinavigasi menggunakan panah atas/bawah lalu tekan Tab di ListBox."""

content = content.replace(old_sec_1, new_sec_1)

# Update Section 6
old_sec_6 = """## 6. Hati-Hati terhadap Pembaruan String (Gunakan Replace Secara Akurat)
- **Hindari Skrip Pengganti Teks yang Mentah (Naive String Replace)**: Saat Anda diminta memperbarui riwayat versi/Changelog (misalnya pada variabel changelog_text di guiDialogs.py), JANGAN menggunakan perintah eplace() string secara mentah (seperti skrip ump_version.py) karena dapat menyebabkan penggandaan awal *string* tak terduga (misalnya kurung buka ganda changelog_text = () jika sebagian teks sebelumnya masih ada. **SELALU gunakan perangkat khusus modifikasi file eplace_file_content** bawaan sistem agen yang menjamin penggantian kode dengan keakuratan tinggi dan memeriksa rentang baris secara tepat, guna menghindari SyntaxError."""

new_sec_6 = """## 6. Hati-Hati terhadap Pembaruan String & Changelog (Gunakan Skrip Injeksi Akurat)
- **Hindari Kerusakan Sejarah (Anti-Data Loss)**: Saat membuat versi baru, JANGAN menimpa keseluruhan blok self.versions di guiDialogs.py karena akan berisiko menghapus puluhan sejarah lawas. Selalu gunakan *Python script* yang cerdas (misal menggunakan modul e) untuk menemukan self.versions = [ lalu menginjeksi elemen tuple baru ke dalamnya, ATAU gunakan eplace_file_content secara presisi HANYA pada rentang baris versi teratas.
- **Auto-Updater (ersion.json) Berbeda dengan Arsip (guiDialogs.py)**: Ingatlah bahwa berkas ersion.json HANYA menyimpan teks changelog untuk SATU versi terbaru (untuk ditampilkan di jendela notifikasi pembaruan). Anda boleh menimpa (overwrite) field changelog di ersion.json sepenuhnya dengan teks baru. Namun untuk guiDialogs.py, Anda HARUS mempertahankan sejarah versi lama di bawahnya."""

content = content.replace(old_sec_6, new_sec_6)

with open(r'.agents\AGENTS.md', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated AGENTS.md!")
