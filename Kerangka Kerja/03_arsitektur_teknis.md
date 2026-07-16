# Arsitektur Teknis Add-on JadwalKu

Secara struktural, add-on `JadwalKu` mengikuti standar pengembangan add-on NVDA modern dengan arsitektur modular:

```text
Project_Jadwalku/
├── build_and_install.py        # Script otomatis pembuat paket .nvda-addon dan pemasang langsung
├── version.json                # Template spesifikasi info pembaruan untuk server/cloud
├── JadwalKu-v1.6.2.nvda-addon  # Binary/zip siap pakai dan siap dibagikan
├── Kerangka Kerja/             # Dokumentasi arsitektur, fitur, dan catatan pengerjaan
│   ├── 01_fitur.md
│   ├── 02_konsep.md
│   ├── 03_arsitektur_teknis.md
│   ├── 04_catatan_pengerjaan_dini_hari.md
│   ├── 05_rencana_pengembangan_selanjutnya.md
│   ├── 06_catatan_audio_device_routing.md
│   ├── 07_catatan_mesin_tts_mandiri.md
│   ├── 08_catatan_fitur_bagikan_direct_link.md
│   ├── 09_catatan_fitur_laporan_telegram_proxy.md
│   └── resources/
│       └── jadwalku_telegram_proxy.php # Script Web API Proxy PHP untuk pengiriman Telegram aman
├── JadwalKu/
│   ├── manifest.ini            # Metadata utama add-on NVDA (nama, versi, author, deskripsi)
│   ├── doc/                    # Dokumentasi pengguna (readme.html dalam bahasa id & en)
│   └── globalPlugins/
│       └── jadwalku/
│           ├── __init__.py     # Entry point (GlobalPlugin, Command Layer, NVDA Menu/Settings integration)
│           ├── configManager.py# Manajer persistensi JSON (%appdata%\nvda\jadwalku_data.json)
│           ├── audioManager.py # Manajer pemutaran suara non-blocking berbasis Single-Open WinMM Relooping Engine
│           ├── ttsManager.py   # Mesin sintesis suara mandiri SAPI 5 untuk notifikasi latar belakang
│           ├── scheduler.py    # Worker latar belakang (wx.Timer) pengecek waktu tiap detik
│           ├── guiDialogs.py   # Antarmuka wxPython (JadwalKuDialog, AgendaDialog, TimeReminderDialog, TTSManagerDialog, HelpDialog, FeedbackDialog)
│           ├── reportSender.py # Modul pengirim laporan asinkron via Web API Proxy & ekstraktor log NVDA
│           ├── updateChecker.py# Pemeriksa pembaruan dan Direct Background Downloader
│           └── sounds/         # Koleksi aset audio (.wav & .mp3) bawaan
```

## Penjelasan Modul Utama

### 1. `__init__.py` (`GlobalPlugin`)
- Mewarisi kelas `globalPluginHandler.GlobalPlugin`.
- Bertanggung jawab menginisialisasi `ConfigManager`, `AudioManager`, `TTSManager`, `Scheduler`, dan `UpdateChecker`.
- Mendaftarkan panel pengaturan `JadwalKuSettingsPanel` ke dalam preferensi NVDA (*NVDA Menu -> Preferences -> Settings -> JadwalKu*), dilengkapi tombol instan `Bagikan Add-on (Copy Link)` dan `Kirim Laporan & Saran`.
- Menambahkan item menu `&JadwalKu - Manajemen Agenda & Pengingat...` ke dalam *NVDA Menu -> Tools*.
- Mengelola *Layer / Mode Perintah* melalui pemicu `NVDA + /` dan pemetaan `commandLayerGestures` (termasuk memanggil `HelpDialog` saat menekan `B` / `F1`, Audio Manager saat menekan `S`, Mesin TTS saat menekan `M` / `P`, Bagikan Add-on saat menekan `G`, Laporan & Saran saat menekan `R`, serta Kalender saat menekan `K`).

### 2. `configManager.py` (`ConfigManager`)
- Membaca dan menulis ke `jadwalku_data.json`.
- Menyediakan metode abstrak `get_schedules()`, `add_schedule()`, `update_schedule()`, `delete_schedule()`, `get_time_reminder_config()`, `update_time_reminder_config()`, `get_time_settings()`, `update_time_settings()`, `get_tts_config()`, serta `get_feedback_config()` dan `get_last_report_date()` (v1.6.2).
- Memastikan struktur data selalu valid menggunakan struktur `DEFAULT_DATA` sebagai *fallback*.

### 3. `audioManager.py` (`AudioManager` & `Single-Open WinMM Relooping Engine`)
- Mengolah pemutaran file `.wav` dan `.mp3` di latar belakang (`worker` thread) tanpa memblokir pembaca layar NVDA.
- **Single-Open WinMM Relooping Engine**: Membuka *handle* hardware kartu suara (`ctypes.windll.winmm.waveOutOpen`) **tepat 1 kali** di awal thread dengan parameter numeric `uDeviceID` pilihan pengguna (`Dynamic Device Routing`).
- **Penyuapan Ulang Tanpa Tutup-Buka (`Seamless Re-Feeding`)**: Selama alarm berulang (`loop=True`), data audio disuapkan ke *handle* tunggal tersebut tanpa pernah melakukan `waveOutClose` di tengah jalan. Hal ini menjamin suara berdering utuh tanpa potongan, tidak mengunci driver (*error 4*), dan mengulang tanpa batas dengan jeda 2 detik.
- **Dukungan Routing TTS Mandiri (`is_tts` flag)**: Memiliki flag khusus `is_tts=True` pada `play_sound` dan `notify` yang memungkinkan suara hasil render SAPI 5 diputar secara mulus di perangkat audio yang sama dengan audio JadwalKu lainnya.

### 4. `ttsManager.py` (`TTSManager` - Mesin Sintesis Suara Mandiri SAPI 5)
- **Sintesis Mandiri Terpisah dari NVDA**: Menggunakan API `comtypes.client.CreateObject("SAPI.SpVoice")` untuk melakukan render ucapan teks ke file audio sementara (`jadwalku_tts.wav`) di folder temporary sistem.
- **Asinkron & Non-Blocking**: Seluruh proses sintesis (`SpFileStream` + `Speak`) dijalankan pada thread terpisah (`threading.Thread`) dan diputar melalui `audioManager.play_sound(..., is_tts=True)`, sehingga pembaca layar NVDA tidak pernah terblokir dan suara notifikasi latar belakang tidak menabrak atau terpotong oleh ucapan NVDA.
- **Dynamic Voice & Parameter Override**: Memuat daftar seluruh suara SAPI 5 yang terinstal di sistem (`voice.GetTokens()`) serta mendukung penyesuaian kecepatan (`Rate` dari `-10` sampai `+10`) dan volume (`Volume` dari `0` sampai `100`).

### 5. `scheduler.py` (`Scheduler`)
- Menggunakan `wx.Timer` dengan interval 1000ms.
- **Logika Agenda Rutin & Quick Timer/Alarm**: Memeriksa agenda harian/mingguan, hitung mundur persiapan timer, dan satu kali alarm. Jika pemicu tercapai, sistem akan mengecek apakah `tts_manager` aktif untuk membacakan pesan suara mandiri, atau menggunakan `ui.message()` jika TTS mandiri dimatikan.
- **Logika Pengingat Waktu Berkala (*Time Reminder*)**: Memeriksa apakah `time_reminder["enabled"]` bernilai `True`. Jika menit saat ini habis dibagi `interval`, berada dalam rentang `start_hour` s/d `end_hour`, dan belum dipicu pada menit tersebut, sistem memanggil `tts_manager.speak(msg)` untuk pengucapan mandiri, atau `ui.message()` sebagai fallback.

### 6. `guiDialogs.py` (`wxPython UI` & `wx.Notebook`)
- `JadwalKuDialog`: Dialog utama berbasis multi-tab (`wx.Notebook`). Tab 1 (`Manajemen Agenda & Jadwal`) memuat `ListBox` agenda dan tombol aksi (`Tambah`, `Edit`, `Hapus`, `Check/Uncheck`, `Pengingat Waktu Berkala`, `Bantuan`, dan `Cek Pembaruan`). Tab 2 (`Pengaturan Waktu & Kalender JadwalKu`) memuat kontrol opsi pelaporan waktu `NVDA + F12`, format 12/24 jam, opsi detik, serta tombol untuk membuka Kalender (`NVDA + /, K`), Jam Dunia (`NVDA + /, D`), dan Pengaturan TTS Mandiri (`NVDA + /, M`).
- `TTSManagerDialog`: Dialog pengaturan khusus untuk memilih suara SAPI 5, mengatur slider kecepatan (`Rate`) dan volume (`Volume`), checkbox Aktifkan TTS Mandiri, serta tombol `[ &Tes Suara ]` untuk langsung mendengarkan pratinjau konfigurasi.
- `CalendarDialog`: Dialog interaktif penghitung hari bulan aktif dan pemetakan hari libur nasional Indonesia (`get_indonesian_holidays`).
- `WorldClockDialog`: Dialog interaktif yang memuat tabel offset zona waktu 20+ kota dunia (`WORLD_CLOCKS_DATA`) dan kalkulator perbedaan waktu modular dengan perhitungan pergeseran hari (*Day Shift Calculation*).
- `AgendaDialog`: Form input agenda menggunakan `wx.Choice`/`ComboBox` untuk Jam, Menit, Frekuensi, dan Suara. Dilengkapi tombol `[ &Tes Suara ]` yang memanggil `audio_manager.play_sound()`.
- `TimeReminderDialog`: Form pengaturan pengingat waktu berkala dengan Checkbox Aktifkan, Combo Box untuk Interval, Mode Notifikasi, Jam Mulai, dan Jam Selesai, serta tombol pintas `[ &Pengaturan Suara TTS Mandiri... ]`.
- `HelpDialog`: Dialog bantuan aksesibel dengan kontrol `wx.TextCtrl(style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2 | wx.HSCROLL)` sehingga ramah navigasi panah atas/bawah dan eja karakter NVDA.

### 7. `updateChecker.py` (`UpdateChecker`)
- Mengecek info JSON melalui panggilan HTTP/HTTPS mandiri (`urllib.request`).
- Memiliki logika perbandingan angka versi `_is_newer_version()`.
- **Direct Background Downloader (`_download_and_install_direct`)**: Mengunduh file `.nvda-addon` dari remote url secara langsung ke folder `tempfile.gettempdir()`, kemudian memanggil `os.startfile(temp_path)` sehingga dialog instalasi NVDA langsung muncul secara lokal tanpa perlu membuka peramban eksternal.

### 8. Integrasi Global Plugin & Override `NVDA + F12` (`__init__.py`)
- Mencegat tombol `NVDA + F12` melalui decorator `@scriptHandler.script(gesture="kb:NVDA+F12")` dan deklarasi kelas `__gestures`.
- Mengecek `time_settings["override_nvda_f12"]`. Jika nonaktif, penanganan dikembalikan ke `globalCommands.commands.script_dateTime` atau `gesture.send()`.
- Jika aktif, memeriksa `scriptHandler.getLastScriptRepeatCount()`:
  - **Repeat 0 (1x tekan)**: Memanggil `format_time_str(now, time_settings)` sesuai format 12/24 jam & gaya pilihan.
  - **Repeat 1 (2x tekan)**: Memanggil `format_date_str(now, time_settings)` sesuai gaya pengucapan tanggal.
  - **Repeat >1 (3x tekan)**: Memanggil `format_full_year_countdown(now, time_settings)` yang mengalkulasi sisa waktu (`datetime.timedelta`) menuju `1 Januari` tahun berikutnya secara realtime.
  - **Pengecualian TTS Mandiri**: Pembacaan manual `NVDA + F12` sengaja tetap diarahkan ke `ui.message()` (suara NVDA utama), tidak menggunakan `tts_manager`, sesuai prinsip pemisahan fungsi notifikasi latar belakang dengan pelaporan aktif manual oleh pengguna.

