# Catatan Pengerjaan NativeAudioIO & Pemilih Perangkat (v1.6.4)

## Masalah Awal
Pengguna melaporkan bahwa saat mencoba Tes Mikrofon di JadwalKu Voice Pack Studio, suara tidak terekam. Masalah terjadi karena perintah lawas `mciSendString` selalu menggunakan *Default Recording Device*. Pada PC pengguna yang memiliki aplikasi Virtual Audio Cable, saluran default tersebut dibajak oleh Virtual Line yang kosong, sehingga mikrofon fisik (Headset) tidak terekam.

Selain itu, ada masalah `AttributeError: module 'wx' has no attribute 'Sound'` saat menekan Putar Hasil Tes karena dependensi `wx.Sound` sudah dihapus/dipindah di versi Phoenix terbaru NVDA.

## Solusi & Eksekusi
1. **Pembuatan NativeAudioIO**: Mengembangkan pembungkus murni C (`ctypes`) untuk fungsi-fungsi `winmm` (`waveInOpen`, dll) agar bisa menentukan `device_index` secara langsung tanpa perlu `PyAudio` atau modul luar.
2. **Pemilih Perangkat (`wx.Choice`)**: Menambahkan dropdown di GUI agar pengguna bisa melihat dan memilih daftar mikrofon dan speaker.
3. **3-Step Wizard**: Memperbaiki alur UI menjadi 3 langkah berurutan (Tes Perangkat -> Metadata -> Studio) untuk pengalaman pengguna yang lebih baik.
4. **Pembaruan Fallback Audio**: Mengganti ketergantungan `wx.Sound` dengan `winsound.PlaySound` dan pemutar `waveOutOpen` dari NativeAudioIO.
