# Arsitektur Teknis Add-on JadwalKu

Secara struktural, add-on `JadwalKu` mengikuti standar pengembangan add-on NVDA modern dengan arsitektur modular:

```text
Project_Jadwalku/
├── build_and_install.py        # Script otomatis pembuat paket .nvda-addon dan pemasang langsung
├── version.json                # Template spesifikasi info pembaruan untuk server/cloud
├── JadwalKu-v1.4.2.nvda-addon  # Binary/zip siap pakai dan siap dibagikan
├── Kerangka Kerja/             # Dokumentasi arsitektur, fitur, dan catatan pengerjaan
│   ├── 01_fitur.md
│   ├── 02_konsep.md
│   ├── 03_arsitektur_teknis.md
│   ├── 04_catatan_pengerjaan_dini_hari.md
│   ├── 05_rencana_pengembangan_selanjutnya.md
│   └── 06_catatan_revolusi_audio_winmm.md # Catatan revolusi Single-Open WinMM Relooping Engine & Device Routing
└── JadwalKu/
    ├── manifest.ini            # Metadata utama add-on NVDA (nama, versi, author, deskripsi)
    ├── doc/                    # Dokumentasi pengguna (readme.html dalam bahasa id & en)
    └── globalPlugins/
        └── jadwalku/
            ├── __init__.py     # Entry point (GlobalPlugin, Command Layer, NVDA Menu/Settings integration)
            ├── configManager.py# Manajer persistensi JSON (%appdata%\nvda\jadwalku_data.json)
            ├── audioManager.py # Manajer pemutaran suara non-blocking berbasis Single-Open WinMM Relooping Engine
            ├── scheduler.py    # Worker latar belakang (wx.Timer) pengecek waktu tiap detik
            ├── guiDialogs.py   # Antarmuka wxPython (JadwalKuDialog, AgendaDialog, TimeReminderDialog, HelpDialog)
            ├── updateChecker.py# Pemeriksa pembaruan dan Direct Background Downloader
            └── sounds/         # Koleksi aset audio (.wav & .mp3) bawaan
```

## Penjelasan Modul Utama

### 1. `__init__.py` (`GlobalPlugin`)
- Mewarisi kelas `globalPluginHandler.GlobalPlugin`.
- Bertanggung jawab menginisialisasi `ConfigManager`, `AudioManager`, `Scheduler`, dan `UpdateChecker`.
- Mendaftarkan panel pengaturan `JadwalKuSettingsPanel` ke dalam preferensi NVDA (*NVDA Menu -> Preferences -> Settings -> JadwalKu*).
- Menambahkan item menu `&JadwalKu - Manajemen Agenda & Pengingat...` ke dalam *NVDA Menu -> Tools*.
- Mengelola *Layer / Mode Perintah* melalui pemicu `NVDA + /` dan pemetaan `commandLayerGestures` (termasuk memanggil `HelpDialog` saat menekan `B` / `F1`, dan Audio Manager saat menekan `S`).

### 2. `configManager.py` (`ConfigManager`)
- Membaca dan menulis ke `jadwalku_data.json`.
- Menyediakan metode abstrak `get_schedules()`, `add_schedule()`, `update_schedule()`, `delete_schedule()`, `get_time_reminder_config()`, `update_time_reminder_config()`, serta `get_time_settings()` dan `update_time_settings()` (v1.5.0).
- Memastikan struktur data selalu valid menggunakan struktur `DEFAULT_DATA` sebagai *fallback*.

### 3. `audioManager.py` (`AudioManager` & `Single-Open WinMM Relooping Engine`)
- Mengolah pemutaran file `.wav` dan `.mp3` di latar belakang (`worker` thread) tanpa memblokir pembaca layar NVDA.
- **Single-Open WinMM Relooping Engine**: Membuka *handle* hardware kartu suara (`ctypes.windll.winmm.waveOutOpen`) **tepat 1 kali** di awal thread dengan parameter numeric `uDeviceID` pilihan pengguna (`Dynamic Device Routing`).
- **Penyuapan Ulang Tanpa Tutup-Buka (`Seamless Re-Feeding`)**: Selama alarm berulang (`loop=True`), data audio disuapkan ke *handle* tunggal tersebut tanpa pernah melakukan `waveOutClose` di tengah jalan. Hal ini menjamin suara berdering utuh tanpa potongan, tidak mengunci driver (*error 4*), dan mengulang tanpa batas dengan jeda 2 detik.
- **Penghentian Seketika (`Instant Reset`)**: Menyediakan metode `stop_sound()` dan `stop_alarm()` yang mengirim `ctypes.windll.winmm.waveOutReset(hWaveOut)` saat pengguna menekan tombol Spasi di Mode Perintah atau tombol dialog, mematikan alarm dalam waktu < 50 milidetik.

### 4. `scheduler.py` (`Scheduler`)
- Menggunakan `wx.Timer` dengan interval 1000ms.
- **Logika Agenda Rutin**: Memeriksa apakah hari ini cocok dengan `frequency` serta mencocokkan `hour` dan `minute`. Jika cocok dan belum dipicu pada menit tersebut, `ui.message()` dan/atau `audio.play_sound()` dijalankan.
- **Logika Pengingat Waktu Berkala (*Time Reminder*)**: Memeriksa apakah `time_reminder["enabled"]` bernilai `True`. Jika menit saat ini habis dibagi `interval`, berada dalam rentang `start_hour` s/d `end_hour`, dan belum dipicu pada menit tersebut, sistem akan membacakan jam dan/atau memutar suara `chime.wav`.

### 5. `guiDialogs.py` (`wxPython UI` & `wx.Notebook`)
- `JadwalKuDialog`: Dialog utama berbasis multi-tab (`wx.Notebook`). Tab 1 (`Manajemen Agenda & Jadwal`) memuat `ListBox` agenda dan tombol aksi (`Tambah`, `Edit`, `Hapus`, `Check/Uncheck`, `Pengingat Waktu Berkala`, `Bantuan`, dan `Cek Pembaruan`). Tab 2 (`Pengaturan Waktu & Kalender JadwalKu`) memuat kontrol opsi pelaporan waktu `NVDA + F12`, format 12/24 jam, opsi detik, serta tombol untuk membuka Kalender (`NVDA + /, K`) dan Jam Dunia (`NVDA + /, D`).
- `CalendarDialog`: Dialog interaktif penghitung hari bulan aktif dan pemetakan hari libur nasional Indonesia (`get_indonesian_holidays`).
- `WorldClockDialog`: Dialog interaktif yang memuat tabel offset zona waktu 20+ kota dunia (`WORLD_CLOCKS_DATA`) dan kalkulator perbedaan waktu modular dengan perhitungan pergeseran hari (*Day Shift Calculation*).
- `AgendaDialog`: Form input agenda menggunakan `wx.Choice`/`ComboBox` untuk Jam, Menit, Frekuensi, dan Suara. Dilengkapi tombol `[ &Tes Suara ]` yang memanggil `audio_manager.play_sound()`.
- `TimeReminderDialog`: Form pengaturan pengingat waktu berkala dengan Checkbox Aktifkan, serta Combo Box untuk Interval, Mode Notifikasi, Jam Mulai, dan Jam Selesai.
- `HelpDialog`: Dialog bantuan aksesibel dengan kontrol `wx.TextCtrl(style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2 | wx.HSCROLL)` sehingga ramah navigasi panah atas/bawah dan eja karakter NVDA.

### 6. `updateChecker.py` (`UpdateChecker`)
- Mengecek info JSON melalui panggilan HTTP/HTTPS mandiri (`urllib.request`).
- Memiliki logika perbandingan angka versi `_is_newer_version()`.
- **Direct Background Downloader (`_download_and_install_direct`)**: Mengunduh file `.nvda-addon` dari remote url secara langsung ke folder `tempfile.gettempdir()`, kemudian memanggil `os.startfile(temp_path)` sehingga dialog instalasi NVDA langsung muncul secara lokal tanpa perlu membuka peramban eksternal.

### 7. Integrasi Global Plugin & Override `NVDA + F12` (`__init__.py`)
- Mencegat tombol `NVDA + F12` melalui decorator `@scriptHandler.script(gesture="kb:NVDA+F12")` dan deklarasi kelas `__gestures`.
- Mengecek `time_settings["override_nvda_f12"]`. Jika nonaktif, penanganan dikembalikan ke `globalCommands.commands.script_dateTime` atau `gesture.send()`.
- Jika aktif, memeriksa `scriptHandler.getLastScriptRepeatCount()`:
  - **Repeat 0 (1x tekan)**: Memanggil `format_time_str(now, time_settings)` sesuai format 12/24 jam & gaya pilihan.
  - **Repeat 1 (2x tekan)**: Memanggil `format_date_str(now, time_settings)` sesuai gaya pengucapan tanggal.
  - **Repeat >1 (3x tekan)**: Memanggil `format_full_year_countdown(now, time_settings)` yang mengalkulasi sisa waktu (`datetime.timedelta`) menuju `1 Januari` tahun berikutnya secara realtime.

