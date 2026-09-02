import os
import shutil
import zipfile

ADDON_NAME = "JadwalKu"
ADDON_VERSION = "1.7.6.4"
BASE_DIR = os.path.join(os.path.dirname(__file__), ADDON_NAME)
ADDON_PATH = os.path.join(os.path.dirname(__file__), f"{ADDON_NAME}-v{ADDON_VERSION}.nvda-addon")
NVDA_ADDON_DIR = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "nvda", "addons", ADDON_NAME)

# 1. Buat file zip .nvda-addon
with zipfile.ZipFile(ADDON_PATH, 'w', zipfile.ZIP_DEFLATED) as zf:
	for root, dirs, files in os.walk(BASE_DIR):
		if '__pycache__' in dirs:
			dirs.remove('__pycache__')
		for file in files:
			if file.endswith('.pyc'):
				continue
			file_path = os.path.join(root, file)
			arcname = os.path.relpath(file_path, BASE_DIR)
			zf.write(file_path, arcname)

print(f"Berhasil membuat paket add-on: {ADDON_PATH}")

# 2. Instalasi Otomatis ke AppData NVDA
if os.path.exists(NVDA_ADDON_DIR):
	print(f"Menghapus add-on lama di: {NVDA_ADDON_DIR}")
	shutil.rmtree(NVDA_ADDON_DIR, ignore_errors=True)
print(f"Menyalin file baru ke: {NVDA_ADDON_DIR}")
try:
	shutil.copytree(BASE_DIR, NVDA_ADDON_DIR, dirs_exist_ok=True)
except Exception as e:
	print(f"Peringatan saat menyalin file: {e}")
print("Berhasil! Silakan RESTART NVDA Anda untuk melihat perubahan.")
