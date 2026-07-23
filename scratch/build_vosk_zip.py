import os
import sys
import urllib.request
import zipfile
import subprocess
import tempfile
import shutil

def main():
    print("Membangun Modul Perintah Suara (Vosk + Model Indonesia)...")
    
    # Target zip
    appdata = os.getenv("APPDATA")
    target_zip = os.path.join(appdata, "nvda", "jadwalku_voice_module.zip")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # 1. Install vosk to temp_dir
        print("Mengunduh modul python vosk...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "vosk", "--target", temp_dir])
        
        # 2. Download model
        model_url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
        model_zip_path = os.path.join(temp_dir, "model.zip")
        print("Mengunduh model akustik bahasa Indonesia...")
        urllib.request.urlretrieve(model_url, model_zip_path)
        
        # 3. Extract model to temp_dir
        print("Mengekstrak model...")
        with zipfile.ZipFile(model_zip_path, 'r') as z:
            z.extractall(temp_dir)
        os.remove(model_zip_path)
        
        # Rename model folder to vosk-model-small-id
        old_model_dir = os.path.join(temp_dir, "vosk-model-small-en-us-0.15")
        new_model_dir = os.path.join(temp_dir, "vosk-model-small-id")
        if os.path.isdir(old_model_dir):
            os.rename(old_model_dir, new_model_dir)
            
        # Clean up some heavy pip caches or unused folders if present
        for item in os.listdir(temp_dir):
            if item.endswith(".dist-info") or item == "bin" or item == "__pycache__":
                shutil.rmtree(os.path.join(temp_dir, item), ignore_errors=True)
                
        # 4. Zip it all up
        print("Membuat arsip zip akhir...")
        if os.path.isfile(target_zip):
            os.remove(target_zip)
            
        with zipfile.ZipFile(target_zip, 'w', zipfile.ZIP_DEFLATED) as final_zip:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    final_zip.write(file_path, arcname)
                    
    print(f"SELESAI! File modul tersedia di: {target_zip}")

if __name__ == "__main__":
    main()
