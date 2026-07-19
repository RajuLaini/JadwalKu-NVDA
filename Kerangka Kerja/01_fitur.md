# Daftar Fitur Lengkap Add-on JadwalKu v1.6.2

Add-on **JadwalKu** didesain khusus sebagai manajer waktu dan pengingat agenda yang 100% ramah aksesibilitas screen reader NVDA.

## 1. Manajemen Agenda Rutin (Harian / Mingguan)
- **Daftar Agenda Aktif**: Menampilkan semua jadwal dalam `ListBox` yang mudah dinavigasi menggunakan panah atas/bawah.
- **Input Berbasis Combo Box**: Saat menambah atau mengedit jadwal, pengguna tidak perlu mengetik format waktu manual. Cukup pilih **Jam (00 - 23)**, **Menit (00 - 59)**, dan **Frekuensi (Setiap Hari / Hari tertentu)** melalui dropdown/combo box.
- **Pengingat Berulang dengan Pembatas Jam Selesai (*Interval & End Hour*)**: Opsi 'Ulangi Setiap (Interval Jam Sekali)' untuk mengatur pengingat berkala dalam hari tersebut (misal setiap 1, 2, 3 jam sekali untuk minum atau istirahat kerja), dilengkapi kolom **Waktu Selesai Interval (Jam Selesai Perulangan)** sehingga pengingat berhenti otomatis setelah jam yang ditentukan baik di hari yang sama maupun lintas malam (*overnight shift*).
- **Mode Pemberitahuan (Chime vs Alarm Weker)**: Memungkinkan agenda diputar sekali bunyi (*chime*) atau berdering terus-menerus tanpa henti (*Alarm Jam Weker*) dengan fitur Tunda/Snooze 10 menit (`Z` / `Alt+T`).
- **Tombol Tes Suara (`Alt + T`)**: Di dalam formulir tambah/edit agenda (`AgendaDialog`), pengguna dapat menekan tombol `[ &Tes Suara ]` untuk langsung mendengarkan sampel suara dari opsi yang dipilih di Combo Box sebelum menyimpan.
- **Status Check/Uncheck Cepat**: Pengguna dapat mengaktifkan atau menonaktifkan suatu agenda dengan cepat melalui tombol `[ Check / Uncheck Status ]` atau langsung menekan Spasi di daftar agenda.

## 2. Pengingat Waktu Berkala (*Time Reminder / Hourly Chime*)
- **Interval Waktu Fleksibel**: Dapat diatur untuk mengingatkan setiap **5 menit**, **10 menit**, **15 menit**, **30 menit**, hingga **1 jam sekali (Setiap Jam)**.
- **Mode Notifikasi Pilihan**:
  - *Bicara Waktu via NVDA & Putar Chime* (Mode Lengkap)
  - *Hanya Bicara Waktu* (Tanpa Chime)
  - *Hanya Putar Chime* (Tanpa Bicara)
- **Format & Gaya Pengucapan Waktu Pengingat (*Time Reminder Format & Speech Style*)**: Pengguna dapat memilih format jam (24 Jam, 12 Jam AM/PM, atau mengikuti pengaturan NVDA+F12) serta memilih gaya kalimat yang dibacakan saat pengingat berbunyi (misal: "Sekarang jam 09:00 tepat", "Mengikuti gaya & format pengucapan NVDA+F12", "09:00 waktu sekarang", "Hanya 09:00", atau "Waktu sekarang pukul 09:00").
- **Rentang Jam Aktif Akurat Menit (*Quiet Hours*)**: Pengguna dapat mengatur Jam Mulai (misal jam `06:00`) dan Jam Selesai (misal jam `23:00`). Pengecekan dilakukan secara akurat hingga tingkat menit, sehingga jika Jam Selesai diatur ke `23:00`, pengingat terakhir berbunyi tepat pukul `23:00` dan diam setelahnya (`23:30` tidak berbunyi). Tersedia juga opsi khusus `23:59 (Sepanjang Hari / 24 Jam)` jika ingin pengingat aktif non-stop sepanjang hari.
- **JadwalKu Voice Pack Studio (Pengingat Tanpa TTS)**: Sebuah fasilitas mandiri bawaan yang memandu pengguna merekam 70 kata waktu menggunakan mikrofon mereka secara langsung. Rekaman akan otomatis dipotong jeda heningnya (*auto-trim*) dan dikompres menjadi file `.jvp` (*JadwalKu Voice Pack*). Paket ini kemudian dapat dibagikan atau digunakan sebagai pengganti suara TTS robotik untuk melaporkan waktu dengan suara manusia asli yang mengalir natural secara beruntun (*Concatenative Synthesis*).

## 3. Shortcut & Mode Perintah (*Command Layer*) Bergaya IslamicPedia
- **`NVDA + /`**: Pintu gerbang tunggal untuk masuk ke **Mode Perintah JadwalKu** (ditandai suara nada naik dan ucapan NVDA). Dalam mode ini:
  - **`L` / `Enter`**: Buka Dialog Layout Utama (Multi-Tab: Manajemen Agenda & Pengaturan Waktu/Kalender).
  - **`1`**: Buka Dialog Pasang Timer Mundur Cepat (Quick Timer) dengan satuan Detik, Menit (default), atau Jam. Dilengkapi input **Detik Persiapan Sebelum Mulai** yang menghitung mundur terlebih dahulu (dengan detak jam dan ucapan angka di 5 detik terakhir), memicu bunyi **Ding (`chime.wav`)** saat mencapai angka nol sebagai tanda dimulainya hitung mundur utama, serta memicu detak acak (*WaitingClock random ticking sounds*) pada 10 detik terakhir sebelum timer sesungguhnya habis dan membunyikan alarm.
  - **`2`**: Buka Dialog Pasang Alarm Sekali Pakai (One-Time Alarm) dengan presisi Jam, Menit, dan Detik.
  - **`W` / `T`**: Bacakan informasi jam sekarang dan status pengingat waktu berkala (*Current Time & Status*).
  - **`K`**: Buka Dialog **Kalender Bulanan & Daftar Tanggal Merah Indonesia**.
  - **`D`**: Buka Dialog **Jam Dunia & Kalkulator Konversi Waktu Antar Negara**.
  - **`M` / `P`**: Buka Dialog **Pengaturan Suara & Mesin TTS Mandiri SAPI 5**.
  - **`J`**: Bacakan jadwal agenda terdekat berikutnya beserta sisa waktu menuju agenda tersebut.
  - **`H`**: Bacakan seluruh daftar agenda aktif hari ini.
  - **`A`**: Check / Uncheck cepat status Aktifkan Pengingat Waktu Berkala.
  - **`S`**: Buka **JadwalKu Audio Manager** (Pengaturan Speaker & Suara).
  - **`V`**: Buka Dialog **Riwayat Pembaruan JadwalKu (Changelog Read-Only)**.
  - **`Spasi`**: Hentikan suara audio/chime/alarm yang sedang berbunyi.
  - **`B` / `F1`**: Buka **Dialog Panduan Bantuan Read-Only (`HelpDialog`)**.
  - **`Escape`**: Keluar dari mode JadwalKu.

## 4. Dialog Bantuan Read-Only Aksesibel (`HelpDialog`)
- **Navigasi Panah Atas/Bawah & Eja Karakter**: Saat tombol `Bantuan...` (`Alt + B`) di dialog utama atau tombol `B`/`F1` di mode perintah ditekan, akan muncul dialog dengan multiline read-only text control (`wx.TE_MULTILINE | wx.TE_READONLY`).
- Pengguna dapat membaca panduan secara nyaman per baris menggunakan panah atas/bawah, atau mengeja huruf dengan panah kiri/kanan tepat seperti *read-only mode* standar NVDA.

## 5. Sistem Audio Manager & Pengaturan Perangkat Speaker Khusus (`audioManager.py` & `AudioManagerDialog`)
- **Pemutaran Mandiri di Speaker Berbeda (`Dynamic Device Routing`)**: Menggunakan mesin **Single-Open WinMM Relooping Engine** berbasis API kernel Windows yang menjamin suara 100% dipancarkan melalui perangkat output audio pilihan pengguna (*kartu suara terpisah, headphone USB, atau speaker eksternal*) tanpa pernah mandek di speaker default NVDA.
- **Perulangan Alarm Tanpa Batas & Anti-Potong (`Infinite Looping & Full Completion`)**: *Handle* audio dibuka 1 kali saja di awal perulangan sehingga alarm mampu berdering ribuan kali tanpa mengalami *error 4 (driver mengunci)* setelah putaran kedua. Suara berbunyi padat 100% dari dentaman pertama hingga akhir tanpa potongan dengan jeda konsisten 2 detik sekali.
- **Dukungan Alarm Jam Weker MP3 & WAV (`mciSendStringW` & `winmm`)**: Memungkinkan pemutaran file `.wav` berkualitas tinggi serta file `.mp3` seperti `wind-up-clock-alarm-bell.mp3` secara native.
- **Daftar Suara Dinamis**: Memuat otomatis seluruh file suara (`.wav` dan `.mp3`) yang ada di dalam folder `sounds/` add-on.

## 6. Penjadwalan Gabungan Hari Kustom (`Sesuaikan Hari`)
- Menggunakan dialog khusus dengan 7 Checkbox (`Senin` - `Minggu`) yang memungkinkan pengguna menggabungkan hari tertentu (misal: Senin, Rabu, Jumat saja) sesuai kebutuhan jadwal secara akurat dan fleksibel.

## 7. Pemeriksa Pembaruan Otomatis dengan Unduh Langsung (*Direct Background Downloader*)
- **Pemeriksaan Latar Belakang**: Secara otomatis mengecek file `version.json` dari repositori GitHub Private tanpa mengganggu performa NVDA.
- **Pemasangan Langsung Tanpa Browser**: Jika pengguna menekan `Yes / Ya` saat ada pembaruan baru, add-on akan mengunduh file `.nvda-addon` di latar belakang (*background thread*) lalu memicu dialog resmi pemasangan add-on NVDA secara langsung (`os.startfile`).

## 8. Pengaturan Waktu & Kalender Aksesibel (v1.5.0)
- **Antarmuka Dialog Multi-Tab (`wx.Notebook`)**: Dialog Utama JadwalKu dibagi menjadi Tab 1 (`Manajemen Agenda & Jadwal`) dan Tab 2 (`Pengaturan Waktu & Kalender JadwalKu`) yang mudah dinavigasikan dengan `Ctrl+Tab` atau `Shift+Tab`.
- **Penggantian Pelaporan Waktu NVDA (`NVDA + F12 Override`)**: Memungkinkan penggantian fungsi pelaporan standar `NVDA + F12` secara kustom dengan format jam (24 Jam / 12 Jam AM/PM) serta berbagai pilihan gaya pengucapan (misal: `09:00 waktu sekarang`, `Waktu sekarang pukul 09:00`, `Pukul 09:00 lewat 30 detik`, dsb.).
- **Pelaporan Bertingkat `NVDA + F12`**:
  - **Tekan 1x**: Membacakan jam dan menit sekarang sesuai format yang dipilih.
  - **Tekan 2x**: Membacakan tanggal hari ini dengan gaya pengucapan yang dapat dipilih (misal: `Kamis, 16 Juli 2026` atau `Hari Kamis, tanggal 16 bulan Juli tahun 2026`).
  - **Tekan 3x**: Membacakan ringkasan lengkap tanggal & waktu serta hitung mundur akurat menuju akhir tahun (sisa hari & jam menuju 1 Januari tahun berikutnya).
- **Kalender Bulanan & Daftar Tanggal Merah (`NVDA + / lalu K`)**: Dialog khusus untuk memilih bulan dan tahun, melihat daftar hari dengan penandaan akhir pekan (Sabtu/Minggu) serta libur nasional Indonesia yang akurat.
- **Jam Dunia & Kalkulator Konversi Waktu (`NVDA + / lalu D`)**: Menampilkan daftar jam waktu aktual di berbagai kota/negara dunia dan selisih waktunya dengan WIB, serta kalkulator konversi waktu interaktif untuk menghitung waktu antar negara.

## 9. Mesin Suara TTS Mandiri untuk Notifikasi Latar Belakang (v1.6.0)
- **Sintesis Suara Mandiri Latar Belakang (`comtypes` SAPI 5 + `WinMM`)**: Seluruh pemberitahuan latar belakang (pengingat waktu berkala setiap jam/menit, alarm agenda, quick timer, dan satu kali alarm) dibacakan menggunakan mesin suara SAPI 5 terpisah yang mandiri dan tidak menumpuk dengan suara pembacaan layar NVDA yang sedang aktif!
- **Pengaturan Suara, Kecepatan & Volume TTS SAPI 5**: Pilih suara SAPI 5 yang diinginkan (misal suara Indonesia atau Inggris di sistem), sesuaikan kecepatan (Rate -10 s/d +10) dan volume (0% - 100%) dengan pratinjau tes suara langsung (`[ &Tes Suara ]`).
- **Routing Audio Penuh (`Audio Device Independent`)**: Suara TTS Mandiri sepenuhnya mengikuti rute perangkat audio (Speaker/Headphone/Virtual Audio Cable) yang dipilih pada Audio Manager JadwalKu, sehingga suara notifikasi tidak bocor ke speaker utama jika diatur ke perangkat lain.
- **Pengecualian Pintar NVDA + F12**: Pengucapan waktu/tanggal manual via `NVDA + F12` tetap dibacakan oleh pembaca layar NVDA utama sesuai preferensi pengguna, menjaga pemisahan fungsi yang sempurna.

## 10. Fitur Bagikan Add-on Instan (`NVDA + / lalu G`) (v1.6.1)
- **Salin Tautan Unduhan Langsung (*Direct Download Link*)**: Memungkinkan pengguna dengan 1x tekan tombol (`NVDA + /` lalu `G`) atau melalui tombol `Bagikan Add-on` di Panel Pengaturan NVDA menyalin tautan unduhan `.nvda-addon` terbaru secara otomatis ke clipboard (`api.copyToClip`).
- **Berbagi Tanpa Browser**: Teman pengguna dapat langsung menempel (*paste*) tautan ke browser atau download manager dan mengunduh file `.nvda-addon` terbaru tanpa perlu membuka dan menavigasi halaman repositori GitHub yang kompleks.

## 11. Fitur Kirim Laporan, Kritik, Saran & Bug Fix (`NVDA + / lalu R`) (v1.6.2)
- **Terhubung ke Bot Telegram Aileen via Web API Proxy Aman**: Memungkinkan pengguna dengan 1x tekan tombol (`NVDA + /` lalu `R`) atau melalui tombol `Kirim Laporan & Saran` di Panel Pengaturan NVDA mengirimkan permintaan fitur baru, kritik saran, atau melaporkan bug langsung ke Telegram pengembang (`Aileen Bot`). Seluruh komunikasi melewati Web API Proxy (`jadwalku_telegram_proxy.php`) untuk menjaga keamanan mutlak dan mencegah kebocoran token Bot Telegram.
- **Kategori & Sub-Kategori Bug Spesifik**: Pengguna dapat memilih kategori (`Minta Fitur Baru`, `Laporkan Kesalahan`, atau `Kritik Saran`). Saat memilih `Laporkan Kesalahan`, dropdown sub-fitur (10 modul utama JadwalKu) ditampilkan untuk memudahkan diagnosis cepat.
- **Pratinjau Log Transparan & Bisa Diedit**: Sistem mengekstrak baris log diagnostik NVDA/JadwalKu terkini dan menampilkannya pada kotak edit transparan yang dapat dibaca dan diedit pengguna sebelum dikirimkan.
- **Pembatasan Pintar & Salin Clipboard Otomatis**: Dilengkapi pembatasan 1 laporan per pengguna per hari (maksimal 10 laporan/hari dari seluruh pengguna). Jika koneksi internet offline atau server proxy gagal, seluruh laporan beserta log diagnostik otomatis disalin ke clipboard (`api.copyToClip`) agar tidak ada pesan atau kontribusi pengguna yang hilang!




## Update v1.6.4: NativeAudioIO & Pemilih Perangkat
- **Pemilih Mikrofon & Speaker Bebas**: Pengguna dapat memilih mikrofon mana yang akan dipakai merekam, dan speaker mana untuk memutar hasil tes. Menuntaskan masalah Virtual Audio Cable.
- **NativeAudioIO**: Menggantikan MCI usang dengan akses langsung ke winmm (waveIn/waveOut) menggunakan ctypes, menghasilkan arsitektur audio sinkron yang stabil tanpa library eksternal (PyAudio/sounddevice).
- **3-Step Wizard**: Tampilan Voice Studio dipisah menjadi 3 halaman agar instruksinya fokus dan logis.


## Update v1.6.5: Aksesibilitas Voice Pack Studio
- **Fokus Teks Langsung**: Mengubah gaya teks kotak Penampil Kata di Studio dari `wx.TE_READONLY` menjadi mode biasa (tapi ditahan inputannya), agar pengguna NVDA bisa langsung mencapai kotak tersebut menggunakan tombol Tab dan bisa mengeja hurufnya dengan mudah.


## Update v1.6.6: Peningkatan Algoritma Penggabungan Kata
- **Translasi Angka ke Suara**: Memperbaiki kelemahan pada *Concatenative Synthesis* yang mana angka murni seperti '13' (tiga belas) dan '56' (lima puluh enam) gagal dibaca karena mencari file '13.wav' atau '56.wav'. Sistem kini cerdas merombak angka tersebut ke struktur ejaan bahasa Indonesia yang sesuai dengan potongan kata yang tersedia.


## Update v1.6.7: Perbaikan Total Voice Pack Pagi/Malam
- **Solusi Bug Penggantian AM/PM**: Memperbaiki fungsi internal yang sebelumnya menimpa huruf 'am' secara serampangan sehingga merusak kata 'jam' menjadi 'j am'. Ini yang membuat Voice Pack sebelumnya gagal mencari file suara 'j' dan terus-menerus jatuh ke fallback TTS standar.


## Update v1.6.8: Uji Cepat Voice Pack via Pintasan W
- **Simulasi Pengingat via Pintasan**: Pintasan utama pemeriksa waktu (NVDA + / lalu W) kini telah terintegrasi dengan mesin *Voice Pack* dan *Chime* (nada dering). Jika pengguna memilih paket suara kustom, menekan pintasan ini akan langsung menyimulasikan pengalaman pengingat waktu asli: membunyikan nada dering diikuti pembacaan waktu dengan suara manusia, sementara TTS hanya membacakan sisa pesan status saja.


## Update v1.6.9: Perbaikan Playback Voice Pack
- **Perbaikan Atribut AudioManager**: Mengatasi kegagalan diam-diam (*silent failure*) pada fungsi pemutar antrean paket suara yang selama ini mencari fungsi `get_active_audio_device_id` yang sudah diganti menjadi `get_output_device_id` sejak refaktor *WinMM*. Perbaikan ini memastikan fitur simulasi `NVDA + / lalu W` dan pengingat waktu otomatis berjalan mulus tanpa macet.


## Update v1.6.11: Toleransi Missing Word Voice Pack
- **Ketahanan Perakitan Suara**: Jika pengguna tidak merekam salah satu kata dalam Voice Pack (misalnya lupa merekam 'waktu' atau 'sekarang'), sistem tidak akan lagi menggagalkan perakitan suara dan kembali ke TTS. Sistem akan mentoleransi kata yang hilang tersebut dan merangkai kata-kata lain yang tersedia (misal hanya bunyi '15' dan '24'). Hal ini menghilangkan ilusi bahwa pintasan 'W' rusak jika pengguna menggunakan Voice Pack yang tidak lengkap.


## Update v1.6.12: Perbaikan Race Condition Antrian Audio
- **Masalah**: Sebelumnya, saat pengguna menekan `NVDA + /, W`, JadwalKu akan memutar suara bel (`chime.wav`), lalu dengan sangat cepat sistem mencoba menghentikan bel tersebut untuk langsung memutar antrian Voice Pack gabungan (`jadwalku_vp_seq.wav`). Sayangnya, terdapat *Race Condition* di mana sistem lama (bel) terlambat melapor bahwa ia sudah mati, sehingga ia secara tidak sengaja memicu perintah 'Stop' (*flag* `_is_playing = False`) **setelah** sistem baru (Voice Pack) baru saja mau hidup. Hal ini membuat Voice Pack langsung terpotong seketika bahkan sebelum sempat berbunyi, sehingga yang terdengar oleh pengguna hanyalah sisa suara bel saja.
- **Solusi**: Saya telah merestrukturisasi manajemen status pemutaran (`has_active_sounds`, `has_active_playback`, dan pelepasan *handle* WinMM) agar tidak lagi memaksakan *flag* `_is_playing = False` secara buta ketika sebuah thread selesai, melainkan secara dinamis memeriksa jumlah antrian audio yang aktif (`_active_wave_outs`). Ini membebaskan Voice Pack dari pembunuhan karakter prematur!


## Update v1.6.13: Volume Kustom Voice Pack
- **Volume Voice Pack**: Menambahkan pengaturan volume khusus (hingga 300%) di Tab 3 Pengaturan Voice Pack. Nilai volume ini tidak mengganggu volume master atau volume TTS NVDA. Slider volume ini akan secara interaktif menyimpan perubahan ke `time_reminder_config` (dengan metode penundaan eksekusi *debounce 200ms* agar tidak membebani SSD saat *slider* digeser secara berkelanjutan). Hal ini menyelesaikan kendala di mana hasil rekaman Voice Pack sering kali kurang lantang dibandingkan suara bel.


## Update v1.6.14: Pratinjau Audio Otomatis (Live Preview)
- **Pratinjau Slider Voice Pack**: Menjawab kebutuhan pengguna untuk langsung merasakan perubahan volume saat menggeser *slider*, JadwalKu kini akan secara otomatis memutar sampel audio Voice Pack (berbunyi: "Waktu sekarang [Jam] [Menit]") setiap kali pengguna selesai menggeser slider volume khusus Voice Pack (dengan jeda pintar *debounce* 200 milidetik). Fitur ini mempermudah pencarian keseimbangan volume antara Voice Pack dan suara bel secara *real-time* tanpa harus menekan tombol tes terpisah.


## Update v1.6.15: Stabilisasi Pratinjau Volume Kustom
- **Hotfix Syntax Error**: Memperbaiki masalah di mana *string* tanda kutip ganda (`"`) bocor ke dalam riwayat rilis `guiDialogs.py` (yang menyebabkan seluruh *addon* mati dan pintasan utama `NVDA + /` tidak berfungsi).
- **Pembuktian Volume 300%**: Fitur *Live Preview* Slider kini berjalan sempurna, memastikan bahwa volume audio benar-benar didongkrak secara matematis (`(arr[i] * factor) >> 8`) hingga 3 kali lipat (batas aman 16-bit PCM), dan dapat didengarkan secara instan oleh pengguna tanpa harus menekan `NVDA + /, W`.


## Update v1.6.16: Peningkatan Batas Volume Voice Pack
- **Penyetaraan Batas Volume Voice Pack (600%)**: Merespon masukan pengguna di mana slider maksimal 300% pada Voice Pack dirasa masih kurang keras (dibandingkan slider Ringtone yang bisa mencapai 600%), batas maksimal Slider Volume Voice Pack kini telah dinaikkan menjadi 600%. Algoritma pengganda PCM 16-bit JadwalKu mampu mengatasi amplitudo ini secara konsisten tanpa *error* di tingkat dasar.


## Update v1.6.17: Penggandaan Ekstrem Volume 1200%
- **Peningkatan Kapasitas Slider Volume (1200%)**: Untuk menjawab skenario langka di mana peralatan mikrofon pengguna (atau sampel audio bel) terekam dalam *gain* yang terlampau senyap, kedua Slider Volume (baik untuk Audio Ringtone di Tab 2 maupun Voice Pack Kustom di Tab 3) kini telah digandakan batas maksimalnya dari 600% menjadi **1200% (penggalian 12 kali lipat amplitudo dasar)**.
