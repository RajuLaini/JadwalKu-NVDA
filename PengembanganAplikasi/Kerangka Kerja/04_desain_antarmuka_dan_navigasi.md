# Desain Antarmuka dan Navigasi (Mobile UX)

## Konsep Utama: Bottom Tab Navigation (Bilah Tab Bawah)
Karena kita tidak lagi menggunakan pintasan *keyboard* (`NVDA + /`), interaksi utama akan menggunakan **Bilah Tab di bawah layar**. Komponen ini sangat ramah *TalkBack/VoiceOver* karena mudah ditemukan dengan meraba bagian bawah layar. Semua tombol akan diberikan `accessibilityLabel` dan `accessibilityRole="button"`.

## Struktur Tab

### Tab 1: Agenda & Habit (Manajemen Rutinitas)
*Fokus: Menggantikan ListBox di Tab 1 JadwalKu Desktop.*
- **Header**: Tampilan informasi Lencana Ketekunan (Gamifikasi).
- **Konten Utama**: Daftar gulir (FlatList) yang berisi kartu-kartu agenda rutin.
  - Setiap kartu membacakan status: *"Minum Air, Aktif, Setiap Hari jam 09:00"*.
  - Ketuk dua kali (*Double tap*) untuk mengedit atau mengaktifkan/mematikan (*Check/Uncheck*).
- **Aksi Cepat**: Tombol mengambang (FAB) berlabel *"Tambah Agenda Baru"*.

### Tab 2: Lonceng & Waktu (Grandfather Clock & Time Reminder)
*Fokus: Menggabungkan Pengingat Waktu Berkala dan Jam Lonceng.*
- **Bagian Pengingat Berkala**:
  - Sakelar (Switch) untuk menyalakan pengingat per-X-menit/jam.
  - Opsi format 12/24 jam dan gaya ucapan (waktu sekarang, pukul tepat, dll).
- **Bagian Jam Lonceng Klasik**:
  - Sakelar untuk dentang Westminster setiap pergantian jam.
  - Sakelar untuk detak latar belakang (*ticking*).
- **Bagian Informasi**: Menampilkan kalender libur nasional dan Jam Dunia (yang sebelumnya ada di pintasan `K` dan `D`).

### Tab 3: Alat Cepat (Timer & Alarm Sekali Pakai)
*Fokus: Menggantikan pintasan `1` (Timer) dan `2` (Alarm).*
- Antarmuka khusus dengan tombol besar untuk menambah (+) atau mengurangi (-) Jam, Menit, dan Detik. (Jauh lebih aksesibel dibandingkan menggeser roda/slider di layar sentuh).
- Fitur **Waktu Persiapan Sebelum Mulai** (Detik hitung mundur dengan suara *chime*) dipertahankan sepenuhnya.
- Fitur penundaan (*Snooze*) bisa dilakukan dengan menekan tombol Volume perangkat fisik.

### Tab 4: Pengaturan & Mesin Suara (Voice Studio & System)
*Fokus: Sentralisasi pengaturan mendalam JadwalKu.*
- **Manajer TTS Mandiri**: Memilih mesin suara bawahan Android/iOS, mengatur kecepatan (*Rate*) dan volume.
- **Voice Pack Studio**: Manajemen rekaman kata, pengunduhan `.jvp`, dan pengali volume PCM ekstrem (1200%).
- **Perintah Suara (Vosk)**: Pengaturan sensitivitas mikrofon dan pemrosesan *offline*.

## Panduan Aksesibilitas UI
1. **Hindari Slider Sebisa Mungkin**: Untuk pengguna tunanetra, *slider* di layar sentuh seringkali sulit diatur presisinya. Kita akan menggunakan tombol **Kurangi** dan **Tambah** (misal untuk Volume 1200%).
2. **Label yang Deskriptif**: Semua komponen *Switch* akan membaca *"Aktifkan Lonceng, mati, tombol alih"*.
3. **Konfirmasi Aksi**: Setiap aksi menyimpan jadwal akan memicu getaran (*haptic feedback*) pendek dan pengumuman *Toast* dari *TalkBack*.
