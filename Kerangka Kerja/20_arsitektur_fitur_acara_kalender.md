# Arsitektur & Alur Kerja Fitur Acara (Calendar Events)

**Status:** Perencanaan (Draft)
**Tanggal:** 4 Oktober 2026

## 1. Latar Belakang
JadwalKu saat ini sangat kuat dalam menangani pengingat berbasis **waktu** (jam, menit, rutinitas harian/mingguan). Namun, JadwalKu belum memiliki sistem untuk menangani pengingat berbasis **tanggal khusus** di masa depan (seperti ulang tahun, janji temu dokter, atau tenggat waktu proyek). Fitur "Acara" (Events) akan mengubah JadwalKu menjadi asisten pribadi seutuhnya.

## 2. Klasifikasi Tipe Acara
Sistem akan membagi acara menjadi 2 tipe utama agar penanganannya lebih efisien:

### A. Acara Sekali Jalan (One-Time Event)
- **Karakteristik:** Hanya terjadi satu kali pada tanggal dan tahun tertentu (Misal: 10 Desember 2026).
- **Siklus Hidup:** Setelah tanggal tersebut lewat, sistem akan otomatis menandainya sebagai "Selesai" (Arsip) atau langsung menghapusnya agar file konfigurasi tidak membengkak.
- **Penggunaan:** Rapat, jadwal penerbangan, janji temu, tenggat waktu (*deadline*).

### B. Acara Tahunan (Yearly / Recurring Event)
- **Karakteristik:** Terjadi pada tanggal dan bulan yang sama setiap tahunnya (Misal: Setiap 17 Agustus).
- **Siklus Hidup:** Permanen. Tahun tidak dijadikan patokan batas akhir, melainkan bisa digunakan sebagai patokan hitungan (umur/peringatan ke-X).
- **Penggunaan:** Ulang tahun, hari jadi (anniversary), perpanjangan pajak tahunan.

## 3. Alur Kerja (Workflow) & Mekanisme Pengingat
Fitur ini tidak akan menggunakan alarm konstan yang berbunyi terus-menerus, melainkan menggunakan sistem **Pemberitahuan Proaktif (Briefing)** dan alarm spesifik.

1. **Pemeriksaan Tengah Malam (Midnight Check):**
   Pada saat jam komputer menyentuh `00:00` (atau saat NVDA/JadwalKu pertama kali dihidupkan di hari yang baru), mesin `scheduler.py` akan memeriksa apakah ada "Acara" yang jatuh pada tanggal hari ini. Atau, pada tanggal yang sama pada bulan depan untuk diingatkan hari ini.
   
2. **Briefing Pagi (Morning Greeting):**
   Alih-alih langsung membunyikan alarm di tengah malam saat tanggal berganti, JadwalKu akan menunggu waktu ideal (misalnya saat pengguna baru menghidupkan komputer di pagi hari, atau dijadwalkan pukul `07:00`). peringatan ini pun akan berbunyi dan menyesuaikan, jika menemukan tanggal yang sama pada hari ini.
   *Contoh output TTS:* "Selamat pagi. Hari ini tanggal 10 Desember. Anda memiliki 1 acara: Janji temu dokter gigi jam 3 sore." atau, "Selamat pagi. Hari ini tanggal 10 Deptember. Anda memiliki 1 acara: Janji temu dokter gigi jam 3 sore bulan depan di tanggal yang sama."

3. **Pemicu Jam (Time-Specific Trigger):**
   Pengguna dapat menetapkan jam spesifik untuk suatu acara. (Misal: Acara ulang tahun diingatkan jam 08:00 pagi, Rapat diingatkan jam 14:00). Pada jam tersebut, JadwalKu akan membunyikan alarm khusus atau membacakan TTS.

## 4. Struktur Data Konfigurasi (`config.json`)
Akan ada entri baru di dalam `config.json` bernama `"events"` yang berupa daftar (array).
Contoh struktur:
```json
"events": [
    {
        "id": "evt-12345",
        "title": "Rapat Proyek",
        "type": "one-time",
        "date": "2026-12-10",
        "time": "09:00",
        "remind_before_minutes": 30,
        "is_completed": false
    },
    {
        "id": "evt-67890",
        "title": "Ulang Tahun Atikah",
        "type": "yearly",
        "date": "08-17", // Tanpa tahun
        "birth_year": 1995, // Opsional untuk menghitung umur
        "time": "07:00",
        "is_completed": false
    }
]
```

## 5. Rencana Desain Antarmuka (GUI)
Akan ditambahkan Tab baru di jendela pengaturan JadwalKu, tepat di samping tab agenda (`guiDialogs.py`):
1. **Daftar Acara (ListCtrl):** Menampilkan semua acara mendatang, diurutkan dari yang paling dekat dengan hari ini.
2. **Tombol "Tambah Acara":** Membuka dialog kecil yang berisi:
   - Nama Acara (Teks)
   - Tipe Acara (Radio Button: Sekali Jalan / Tahunan)
   - Tanggal (Date Picker Control)
   - Jam Pengingat (Spin Control)
3. **Pengaturan Briefing Pagi:** Sebuah *checkbox* global untuk mengaktifkan/mematikan fitur TTS sapaan pagi (Briefing) beserta pilihan jam berapa sapaan itu diucapkan.

---
**Catatan Diskusi:**
File ini dibuat sebagai ruang diskusi. Silakan edit file ini secara langsung jika ada logika yang ingin diubah, ditambah, atau disederhanakan sebelum kita mulai merombak kode Python-nya.
