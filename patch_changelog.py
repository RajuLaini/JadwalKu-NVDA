import re
filepath = r"C:\Users\Raju Laini\Documents\Project_Jadwalku\JadwalKu\globalPlugins\jadwalku\guiDialogs.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

old_changelog = """			"[Versi 1.7.6.5.7]\\n"
			"- Fitur Raksasa Baru (Kalender & Acara): JadwalKu kini telah berevolusi menjadi asisten pribadi! Anda dapat menjadwalkan 'Acara Sekali Jalan' (seperti Rapat atau Tenggat Waktu Proyek) atau 'Acara Tahunan' (Ulang Tahun, Anniversary). Lengkap dengan fitur *Briefing Pagi* dan *Peringatan Dini* yang mampu mengingatkan Anda sehari, seminggu, atau bahkan tepat 1 bulan sebelum acara tersebut tiba!\\n"
			"- Tab Navigasi Baru: Penambahan tab khusus 'Kalender & Acara (Events)' di pengaturan utama.\\n"
			"- Pintasan Baru: Tekan NVDA + / lalu E untuk mendengarkan TTS menyebutkan rincian acara hari ini.\\n\\n"
			"[Versi 1.7.6.5.6]\\n\""""

new_changelog = """			"[Versi 1.7.6.5.7]\\n"
			"- Fitur Raksasa Baru (Kalender & Acara): JadwalKu kini telah berevolusi menjadi asisten pribadi! Anda dapat menjadwalkan 'Acara Sekali Jalan' (seperti Rapat atau Tenggat Waktu Proyek) atau 'Acara Tahunan' (Ulang Tahun, Anniversary). Lengkap dengan fitur *Briefing Pagi* dan *Peringatan Dini* yang mampu mengingatkan Anda sehari, seminggu, atau bahkan tepat 1 bulan sebelum acara tersebut tiba!\\n"
			"- Pintar Menghitung Usia: JadwalKu kini memiliki kalkulator cerdas untuk acara tahunan. Cukup masukkan tanggal format YYYY-MM-DD (contoh: 1999-12-26), dan sistem otomatis menyebutkan 'Ulang Tahun yang ke-27' saat alarm peringatannya bergema!\\n"
			"- Sinkronisasi Laporan (E) dan Pembersihan Otomatis: Shortcut pelaporan manual acara (E) kini memuat algoritma cerdas yang sama dengan Briefing Pagi, plus tambahan sebutan jam acara. Dan untuk acara One-Time yang telah lewat atau berhasil disuarakan, sistem kini akan langsung membersihkan/menghapusnya dari daftar secara otomatis agar tidak menumpuk menjadi sampah memori.\\n"
			"- Perbaikan Bug (Silent Crash): Memperbaiki bug diam yang membuat jendela 'Manajer Timer Aktif' dan 'Manajer Alarm Aktif' gagal terbuka ketika ada alarm yang berjalan, serta menyembuhkan pemicu waktu spesifik Acara dari masalah fungsi usang.\\n"
			"- Tab Navigasi Baru: Penambahan tab khusus 'Kalender & Acara (Events)' di pengaturan utama.\\n"
			"- Pintasan Baru: Tekan NVDA + / lalu E untuk mendengarkan TTS menyebutkan rincian acara hari ini beserta jamnya.\\n\\n"
			"[Versi 1.7.6.5.6]\\n\""""

if old_changelog in content:
    content = content.replace(old_changelog, new_changelog)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print("Updated changelog in guiDialogs.py")
else:
    print("Could not find old changelog block.")
