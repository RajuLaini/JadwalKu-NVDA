import os
import shutil
import zipfile

BASE_DIR = os.path.join(os.path.dirname(__file__), "JadwalKu")
ADDON_PATH = os.path.join(os.path.dirname(__file__), "JadwalKu-1.0.nvda-addon")
NVDA_ADDON_DIR = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "nvda", "addons", "JadwalKu")

# 1. Buat file zip .nvda-addon
with zipfile.ZipFile(ADDON_PATH, 'w', zipfile.ZIP_DEFLATED) as zf:
	for root, dirs, files in os.walk(BASE_DIR):
		for file in files:
			file_path = os.path.join(root, file)
			arcname = os.path.relpath(file_path, BASE_DIR)
			zf.write(file_path, arcname)

print(f"Berhasil membuat paket add-on: {ADDON_PATH}")

# 2. Salin langsung ke %appdata%\nvda\addons\JadwalKu agar siap dicoba langsung
os.makedirs(NVDA_ADDON_DIR, exist_ok=True)
for root, dirs, files in os.walk(BASE_DIR):
	for file in files:
		src_file = os.path.join(root, file)
		rel_path = os.path.relpath(src_file, BASE_DIR)
		dst_file = os.path.join(NVDA_ADDON_DIR, rel_path)
		os.makedirs(os.path.dirname(dst_file), exist_ok=True)
		shutil.copy2(src_file, dst_file)

print(f"Berhasil memasang langsung ke folder NVDA: {NVDA_ADDON_DIR}")
print("Silakan tekan NVDA + Ctrl + F3 untuk memuat ulang add-on NVDA sekarang!")
