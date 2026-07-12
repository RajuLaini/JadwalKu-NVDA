# Arsitektur Teknis Add-on JadwalKu

Secara struktural, add-on `JadwalKu` mengikuti standar pengembangan add-on NVDA modern dengan arsitektur modular:

```text
Project_Jadwalku/
├── build_and_install.py        # Script otomatis pembuat paket .nvda-addon dan pemasang langsung
├── version.json                # Template spesifikasi info pembaruan untuk server/cloud
├── JadwalKu-1.0.nvda-addon     # Binary/zip siap pakai dan siap dibagikan
├── Kerangka Kerja/             # Dokumentasi arsitektur, fitur, dan catatan pengerjaan
└── JadwalKu/
    ├── manifest.ini            # Metadata utama add-on NVDA (nama, versi, author, deskripsi)
    ├── doc/                    # Dokumentasi pengguna (readme.html dalam bahasa id & en)
    └── globalPlugins/
        └── jadwalku/
            ├── __init__.py     # Entry point (GlobalPlugin, Command Layer, NVDA Menu/Settings integration)
            ├── configManager.py# Manajer persistensi JSON (%appdata%\nvda\jadwalku_data.json)
            ├── audioManager.py # Manajer pemutaran suara non-blocking berbasis nvwave
            ├── scheduler.py    # Worker latar belakang (wx.Timer) pengecek waktu tiap detik
            ├── guiDialogs.py   # Antarmuka wxPython (JadwalKuDialog, AgendaDialog, TimeReminderDialog)
            ├── updateChecker.py# Pemeriksa pembaruan dan Direct Background Downloader
            └── sounds/         # Koleksi aset audio (.wav) bawaan
```

## Penjelasan Modul Utama

### 1. `__init__.py` (`GlobalPlugin`)
- Mewarisi kelas `globalPluginHandler.GlobalPlugin`.
- Bertanggung jawab menginisialisasi `ConfigManager`, `AudioManager`, `Scheduler`, dan `UpdateChecker`.
- Mendaftarkan panel pengaturan `JadwalKuSettingsPanel` ke dalam preferensi NVDA (*NVDA Menu -> Preferences -> Settings -> JadwalKu*).
- Menambahkan item menu `&JadwalKu - Manajemen Agenda & Pengingat...` ke dalam *NVDA Menu -> Tools*.
- Mengelola *Layer / Mode Perintah* melalui pemicu `NVDA + /` dan pemetaan `commandLayerGestures`.

### 2. `configManager.py` (`ConfigManager`)
- Membaca dan menulis ke `jadwalku_data.json`.
- Menyediakan metode abstrak `get_schedules()`, `add_schedule()`, `update_schedule()`, `delete_schedule()`, serta `get_time_reminder_config()` dan `update_time_reminder_config()`.
- Memastikan struktur data selalu valid menggunakan struktur `DEFAULT_DATA` sebagai *fallback*.

### 3. `audioManager.py` (`AudioManager`)
- Membungkus panggilan ke `nvwave.playWaveFile()` dalam blok *try-except* yang aman.
- Menyimpan *handle* pemutaran audio (`self._current_wave`) dan menyediakan metode `stop_sound()` untuk menghentikan suara seketika saat tombol Spasi ditekan di Mode Perintah.

### 4. `scheduler.py` (`Scheduler`)
- Menggunakan `wx.Timer` dengan interval 1000ms.
- **Logika Agenda Rutin**: Memeriksa apakah hari ini cocok dengan `frequency` (Setiap Hari, Hari Kerja, Akhir Pekan, atau nama hari tertentu) serta mencocokkan `hour` dan `minute`. Jika cocok dan belum dipicu pada menit tersebut, `ui.message()` dan/atau `audio.play_sound()` dijalankan.
- **Logika Pengingat Waktu Berkala (*Time Reminder*)**: Memeriksa apakah `time_reminder["enabled"]` bernilai `True`. Jika menit saat ini habis dibagi `interval` (misal 00, 15, 30, 45 untuk interval 15 menit), berada dalam rentang `start_hour` s/d `end_hour`, dan belum dipicu pada menit tersebut, sistem akan membacakan jam dan/atau memutar suara `chime.wav`.

### 5. `guiDialogs.py` (`wxPython UI`)
- `JadwalKuDialog`: Dialog utama dengan `ListBox` agenda dan tombol aksi (`Tambah`, `Edit`, `Hapus`, `Check/Uncheck`, `Pengingat Waktu Berkala`, dan `Cek Pembaruan`).
- `AgendaDialog`: Form input agenda menggunakan `wx.Choice` (Combo Box) untuk Jam, Menit, Frekuensi, dan Suara.
- `TimeReminderDialog`: Form pengaturan pengingat waktu berkala dengan Checkbox Aktifkan, serta Combo Box untuk Interval, Mode Notifikasi, Jam Mulai, dan Jam Selesai.

### 6. `updateChecker.py` (`UpdateChecker`)
- Mengecek info JSON melalui panggilan HTTP/HTTPS mandiri (`urllib.request`).
- Memiliki logika perbandingan angka versi `_is_newer_version()`.
- **Direct Background Downloader (`_download_and_install_direct`)**: Mengunduh file `.nvda-addon` dari remote url secara langsung ke folder `tempfile.gettempdir()`, kemudian memanggil `os.startfile(temp_path)` sehingga dialog instalasi NVDA langsung muncul secara lokal tanpa perlu membuka peramban eksternal.
