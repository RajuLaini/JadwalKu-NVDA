@echo off
echo Menginstal PyInstaller...
python -m pip install pyinstaller
echo.
echo Membangun AI Voice Studio menjadi .exe...
python -m PyInstaller --noconsole --onefile --name "JadwalKu AIVoiceStudio" main.py
echo.
echo Selesai! File .exe Anda ada di dalam folder 'dist'.
pause
