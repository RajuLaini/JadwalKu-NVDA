import wx
import os
import json
import time
import zipfile
import threading
import subprocess
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path
import miniaudio
import wave

WORDS_TO_GENERATE = [
    "sekarang", "waktu", "pukul", "jam", "tepat", "lewat", "menit", "detik", "am", "pm",
    "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
    "10", "11", "12", "13", "14", "15", "16", "17", "18", "19",
    "20", "21", "22", "23", "24", "25", "26", "27", "28", "29",
    "30", "31", "32", "33", "34", "35", "36", "37", "38", "39",
    "40", "41", "42", "43", "44", "45", "46", "47", "48", "49",
    "50", "51", "52", "53", "54", "55", "56", "57", "58", "59"
]

class VoiceStudioFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title="JadwalKu AI Voice Studio", size=(550, 600))
        self.panel = wx.Panel(self)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        
        # --- TITLE ---
        lbl_title = wx.StaticText(self.panel, label="JadwalKu AI Voice Studio")
        font = lbl_title.GetFont()
        font.PointSize += 4
        font = font.Bold()
        lbl_title.SetFont(font)
        self.sizer.Add(lbl_title, 0, wx.ALL | wx.CENTER, 10)
        
        # --- PROVIDER ---
        grid = wx.FlexGridSizer(rows=8, cols=2, vgap=10, hgap=10)
        grid.AddGrowableCol(1, 1)
        
        grid.Add(wx.StaticText(self.panel, label="Mesin AI (Provider):"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.cb_provider = wx.ComboBox(self.panel, choices=["Edge TTS (Gratis)", "Google Translate (Gratis)", "Google Cloud TTS", "Gemini API (Google AI Studio)"], style=wx.CB_READONLY)
        self.cb_provider.SetSelection(0)
        self.cb_provider.Bind(wx.EVT_COMBOBOX, self.on_provider_change)
        grid.Add(self.cb_provider, 1, wx.EXPAND)
        
        # --- VOICE ---
        grid.Add(wx.StaticText(self.panel, label="Pilihan Suara:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.cb_voice = wx.ComboBox(self.panel, choices=["id-ID-GadisNeural", "id-ID-ArdiNeural"], style=wx.CB_READONLY)
        self.cb_voice.SetSelection(0)
        self.cb_voice.Bind(wx.EVT_COMBOBOX, self.on_voice_change)
        grid.Add(self.cb_voice, 1, wx.EXPAND)
        
        # --- LOAD CONFIG ---
        self.config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
        saved_api = ""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    cfg = json.load(f)
                    saved_api = cfg.get('api_key', '')
            except: pass
            
        # --- API KEY ---
        grid.Add(wx.StaticText(self.panel, label="API Key (Kosongkan jika gratis):"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.txt_api = wx.TextCtrl(self.panel, value=saved_api)
        self.txt_api.Disable()
        grid.Add(self.txt_api, 1, wx.EXPAND)
        
        # --- PACK NAME ---
        grid.Add(wx.StaticText(self.panel, label="Nama Paket Suara:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.txt_pack_name = wx.TextCtrl(self.panel, value="Suara AI Gadis")
        grid.Add(self.txt_pack_name, 1, wx.EXPAND)
        
        # --- AUTHOR ---
        grid.Add(wx.StaticText(self.panel, label="Nama Pembuat:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.txt_author = wx.TextCtrl(self.panel, value="AI Voice Studio")
        grid.Add(self.txt_author, 1, wx.EXPAND)
        
        # --- DESCRIPTION ---
        grid.Add(wx.StaticText(self.panel, label="Deskripsi Paket:"), 0, wx.ALIGN_TOP)
        self.txt_desc = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE, size=(-1, 60))
        self.txt_desc.SetValue("Paket suara AI otomatis yang dihasilkan oleh JadwalKu Voice Studio.")
        grid.Add(self.txt_desc, 1, wx.EXPAND)
        
        # --- PASSWORD ---
        grid.Add(wx.StaticText(self.panel, label="Kata Sandi Hapus (Opsional):"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.txt_password = wx.TextCtrl(self.panel, style=wx.TE_PASSWORD)
        self.txt_password.SetToolTip("Digunakan agar Voice Pack ini tidak bisa dihapus sembarangan oleh orang lain jika Anda mengunggahnya ke server.")
        grid.Add(self.txt_password, 1, wx.EXPAND)
        
        self.sizer.Add(grid, 0, wx.ALL | wx.EXPAND, 15)
        
        # --- PROGRESS ---
        self.lbl_status = wx.StaticText(self.panel, label="Status: Siap")
        self.sizer.Add(self.lbl_status, 0, wx.ALL, 10)
        
        self.gauge = wx.Gauge(self.panel, range=len(WORDS_TO_GENERATE), size=(-1, 20))
        self.sizer.Add(self.gauge, 0, wx.ALL | wx.EXPAND, 10)
        
        # --- BUTTONS ---
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.btn_generate = wx.Button(self.panel, label="1. Otomatis via API")
        self.btn_generate.Bind(wx.EVT_BUTTON, self.on_generate)
        self.btn_generate.SetToolTip("Mendownload suara satu per satu dari internet.")
        btn_sizer.Add(self.btn_generate, 0, wx.ALL, 5)
        
        self.btn_extract = wx.Button(self.panel, label="2. Ekstrak dari WAV (Manual)")
        self.btn_extract.Bind(wx.EVT_BUTTON, self.on_extract)
        self.btn_extract.SetToolTip("Memotong 70 kata otomatis dari 1 file WAV besar (seperti hasil Google AI Studio).")
        btn_sizer.Add(self.btn_extract, 0, wx.ALL, 5)
        
        self.btn_pack_folder = wx.Button(self.panel, label="3. Bungkus Folder (Auto-Trim)")
        self.btn_pack_folder.Bind(wx.EVT_BUTTON, self.on_pack_folder)
        self.btn_pack_folder.SetToolTip("Memangkas keheningan dari 70 file WAV terpisah dalam 1 folder lalu menjahitnya.")
        btn_sizer.Add(self.btn_pack_folder, 0, wx.ALL, 5)
        
        self.sizer.Add(btn_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        
        self.panel.SetSizer(self.sizer)
        self.Layout()
        
    
    def on_voice_change(self, event):
        voice = self.cb_voice.GetValue()
        if "Gadis" in voice:
            self.txt_pack_name.SetValue("Suara AI Gadis")
        elif "Ardi" in voice:
            self.txt_pack_name.SetValue("Suara AI Ardi")
        elif "Wavenet" in voice:
            self.txt_pack_name.SetValue(f"Suara AI {voice.split(' ')[0]}")
        elif "(Gemini)" in voice:
            self.txt_pack_name.SetValue(f"Suara AI {voice.split(' ')[0]} (Gemini)")
        else:
            self.txt_pack_name.SetValue("Suara AI Custom")

    def on_provider_change(self, event):
        sel = self.cb_provider.GetValue()
        if "Edge" in sel:
            self.cb_voice.Set(["id-ID-GadisNeural", "id-ID-ArdiNeural"])
            self.cb_voice.SetSelection(0)
            self.txt_api.Disable()
            self.on_voice_change(None)
        elif "Translate" in sel:
            self.cb_voice.Set(["Google Female (id)"])
            self.cb_voice.SetSelection(0)
            self.txt_api.Disable()
            self.on_voice_change(None)
        elif "Google Cloud" in sel:
            self.cb_voice.Set(["id-ID-Wavenet-A (Wanita)", "id-ID-Wavenet-B (Pria)", "id-ID-Wavenet-C (Pria)", "id-ID-Wavenet-D (Wanita)"])
            self.cb_voice.SetSelection(0)
            self.txt_api.Enable()
            self.on_voice_change(None)
        elif "Gemini API" in sel:
            self.cb_voice.Set(["Aoede (Gemini)", "Charon (Gemini)", "Fenrir (Gemini)", "Kore (Gemini)", "Puck (Gemini)", "Zephyr (Gemini)", "Leda (Gemini)", "Orus (Gemini)", "Callirrhoe (Gemini)", "Autonoe (Gemini)", "Enceladus (Gemini)", "Iapetus (Gemini)", "Umbriel (Gemini)", "Algieba (Gemini)", "Despina (Gemini)", "Erinome (Gemini)", "Algenib (Gemini)", "Rasalgethi (Gemini)", "Laomedeia (Gemini)", "Achernar (Gemini)"])
            self.cb_voice.SetSelection(0)
            self.txt_api.Enable()
            self.on_voice_change(None)

    def set_status(self, text, progress=None):
        def update():
            self.lbl_status.SetLabel(f"Status: {text}")
            if progress is not None:
                self.gauge.SetValue(progress)
        wx.CallAfter(update)

    def on_generate(self, event):
        provider = self.cb_provider.GetValue()
        voice = self.cb_voice.GetValue()
        pack_name = self.txt_pack_name.GetValue().strip()
        author = self.txt_author.GetValue().strip()
        desc = self.txt_desc.GetValue().strip()
        api_key = self.txt_api.GetValue().strip()
        pack_password = self.txt_password.GetValue()
        
        # Save API key for next time
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump({"api_key": api_key}, f)
        except: pass
        
        if not pack_name:
            wx.MessageBox("Nama paket tidak boleh kosong!", "Error", wx.ICON_ERROR)
            return
            
        dlg = wx.DirDialog(self, "Pilih folder untuk menyimpan Voice Pack (.jvp)", style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            output_dir = dlg.GetPath()
            output_file = os.path.join(output_dir, f"{pack_name.replace(' ', '_')}.jvp")
            
            self.btn_generate.Disable()
            threading.Thread(target=self.generate_task, args=(provider, voice, pack_name, author, desc, api_key, pack_password, output_file)).start()
        dlg.Destroy()
        
    def on_pack_folder(self, event):
        pack_name = self.txt_pack_name.GetValue().strip()
        author = self.txt_author.GetValue().strip()
        desc = self.txt_desc.GetValue().strip()
        pack_password = self.txt_password.GetValue()
        
        if not pack_name:
            wx.MessageBox("Nama paket tidak boleh kosong!", "Error", wx.ICON_ERROR)
            return
            
        dlg_dir = wx.DirDialog(self, "Pilih folder yang berisi 70 file rekaman (.wav)", style=wx.DD_DEFAULT_STYLE)
        if dlg_dir.ShowModal() == wx.ID_OK:
            input_dir = dlg_dir.GetPath()
            dlg_save = wx.DirDialog(self, "Pilih folder untuk menyimpan Voice Pack (.jvp)", style=wx.DD_DEFAULT_STYLE)
            if dlg_save.ShowModal() == wx.ID_OK:
                output_dir = dlg_save.GetPath()
                output_file = os.path.join(output_dir, f"{pack_name.replace(' ', '_')}.jvp")
                self.btn_generate.Disable()
                self.btn_extract.Disable()
                self.btn_pack_folder.Disable()
                threading.Thread(target=self.pack_folder_task, args=(input_dir, pack_name, author, desc, pack_password, output_file)).start()
            dlg_save.Destroy()
        dlg_dir.Destroy()
        
    def pack_folder_task(self, input_dir, pack_name, author, desc, pack_password, output_file):
        try:
            import wave, array, math, hashlib, json, re, zipfile
            
            safe_pack_name = re.sub(r'[\\/*?:"<>|]', '', pack_name).replace(' ', '_')
            temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'TempAudio', safe_pack_name)
            if not os.path.exists(temp_dir): os.makedirs(temp_dir)
            
            generated_files = []
            missing_words = []
            
            for idx, word in enumerate(WORDS_TO_GENERATE):
                src_wav = os.path.join(input_dir, f"{word}.wav")
                if not os.path.exists(src_wav):
                    missing_words.append(word)
                    continue
                    
                self.set_status(f"Menganalisis & memotong '{word}'...", idx)
                
                with wave.open(src_wav, 'rb') as w:
                    nchannels = w.getnchannels()
                    sampwidth = w.getsampwidth()
                    framerate = w.getframerate()
                    raw_data = w.readframes(w.getnframes())
                
                samples = array.array('h', raw_data)
                threshold = 400
                
                # Gunakan sistem RMS per chunk 10ms agar kebal terhadap noise klik mic
                threshold = 1500  # Naikkan sangat tinggi untuk menembus noise napas/klik mic
                chunk_samples = int(framerate * nchannels * 10 / 1000)
                start_margin = chunk_samples * 3 # margin 30ms di awal (cepat)
                end_margin = chunk_samples * 15 # margin 150ms di akhir (lambat, untuk ekor suara)
                
                start_idx = 0
                for i in range(0, len(samples), chunk_samples):
                    chunk = samples[i:i+chunk_samples]
                    if not chunk: break
                    rms = math.sqrt(sum(s*s for s in chunk) / len(chunk))
                    if rms > threshold:
                        start_idx = max(0, i - start_margin)
                        break
                        
                end_idx = len(samples)
                for i in range(len(samples)-chunk_samples, -1, -chunk_samples):
                    chunk = samples[i:i+chunk_samples]
                    if not chunk: break
                    rms = math.sqrt(sum(s*s for s in chunk) / len(chunk))
                    if rms > threshold:
                        end_idx = min(len(samples), i + chunk_samples + end_margin)
                        break
                
                trimmed_samples = samples[start_idx:end_idx]
                
                wavfile = os.path.join(temp_dir, f"{word}.wav")
                with wave.open(wavfile, 'wb') as wav:
                    wav.setnchannels(nchannels)
                    wav.setsampwidth(sampwidth)
                    wav.setframerate(framerate)
                    wav.writeframes(trimmed_samples.tobytes())
                    
                generated_files.append((word, wavfile))
                
            if missing_words:
                wx.CallAfter(wx.MessageBox, f"Gagal! Ada {len(missing_words)} kata yang hilang di folder tersebut:\n{', '.join(missing_words[:10])}...", "Error", wx.ICON_ERROR)
                return
                
            self.set_status("Membuat Voice Pack...", len(WORDS_TO_GENERATE))
            
            password_hash = ""
            if pack_password:
                password_hash = hashlib.sha256(pack_password.encode('utf-8')).hexdigest()
                
            manifest_data = {
                "name": pack_name,
                "author": author,
                "description": desc,
                "version": "1.0",
                "words": WORDS_TO_GENERATE,
                "password_hash": password_hash,
                "is_permanent": True
            }
            
            manifest_path = os.path.join(temp_dir, "manifest.json")
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest_data, f, indent=4)
                
            with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(manifest_path, "manifest.json")
                for w, fp in generated_files:
                    if os.path.exists(fp):
                        zipf.write(fp, f"{w}.wav")
                        
            self.set_status("Selesai!", len(WORDS_TO_GENERATE))
            wx.CallAfter(wx.MessageBox, f"Folder berhasil dipangkas dan dibungkus menjadi Voice Pack!\nDisimpan di:\n{output_file}", "Sukses", wx.ICON_INFORMATION)
            
        except Exception as e:
            self.set_status("Gagal!")
            wx.CallAfter(wx.MessageBox, f"Terjadi kesalahan:\n{str(e)}", "Error", wx.ICON_ERROR)
        finally:
            wx.CallAfter(self.btn_generate.Enable)
            wx.CallAfter(self.btn_extract.Enable)
            wx.CallAfter(self.btn_pack_folder.Enable)
            wx.CallAfter(self.btn_pack_folder.Enable)


    def on_extract(self, event):
        pack_name = self.txt_pack_name.GetValue().strip()
        author = self.txt_author.GetValue().strip()
        desc = self.txt_desc.GetValue().strip()
        pack_password = self.txt_password.GetValue()
        
        if not pack_name:
            wx.MessageBox("Nama paket tidak boleh kosong!", "Error", wx.ICON_ERROR)
            return
            
        dlg_wav = wx.FileDialog(self, "Pilih file Audio WAV berisi 70 kata berurutan", wildcard="WAV files (*.wav)|*.wav", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if dlg_wav.ShowModal() == wx.ID_OK:
            input_wav = dlg_wav.GetPath()
            dlg_dir = wx.DirDialog(self, "Pilih folder untuk menyimpan Voice Pack (.jvp)", style=wx.DD_DEFAULT_STYLE)
            if dlg_dir.ShowModal() == wx.ID_OK:
                output_dir = dlg_dir.GetPath()
                output_file = os.path.join(output_dir, f"{pack_name.replace(' ', '_')}.jvp")
                self.btn_generate.Disable()
                self.btn_extract.Disable()
                threading.Thread(target=self.extract_task, args=(input_wav, pack_name, author, desc, pack_password, output_file)).start()
            dlg_dir.Destroy()
        dlg_wav.Destroy()
        
    def extract_task(self, input_wav, pack_name, author, desc, pack_password, output_file):
        try:
            import wave, array, math, hashlib
            import zipfile
            import re
            
            self.set_status("Menganalisis WAV...", 0)
            
            with wave.open(input_wav, 'rb') as w:
                nchannels = w.getnchannels()
                sampwidth = w.getsampwidth()
                framerate = w.getframerate()
                nframes = w.getnframes()
                raw_data = w.readframes(nframes)
                
            samples = array.array('h', raw_data)
            
            threshold = 300
            min_silence_frames = int(framerate * 300 / 1000) # 300ms gap
            chunk_size = int(framerate * 10 / 1000) # 10ms chunk
            
            is_silent = True
            current_silence = 0
            
            word_chunks = []
            current_word_start = 0
            
            for i in range(0, len(samples), chunk_size):
                chunk = samples[i:i+chunk_size]
                if not chunk: continue
                rms = math.sqrt(sum(s*s for s in chunk) / len(chunk))
                if rms > threshold:
                    if is_silent:
                        is_silent = False
                        current_word_start = max(0, i - int(framerate * 20 / 1000)) # 20ms margin
                    current_silence = 0
                else:
                    current_silence += len(chunk)
                    if not is_silent and current_silence >= min_silence_frames:
                        is_silent = True
                        word_end = i + len(chunk) - current_silence + int(framerate * 20 / 1000) # 20ms margin
                        word_chunks.append((current_word_start, word_end))
            
            # Jika file berakhir tanpa jeda panjang, simpan kata terakhir
            if not is_silent:
                word_chunks.append((current_word_start, len(samples)))
                
            if len(word_chunks) != len(WORDS_TO_GENERATE):
                wx.CallAfter(wx.MessageBox, f"Gagal! Ditemukan {len(word_chunks)} kata, padahal JadwalKu butuh tepat {len(WORDS_TO_GENERATE)} kata. Pastikan durasi jeda antarkata di file WAV Anda merata.", "Error Ekstrak", wx.ICON_ERROR)
                return
                
            # Buat file WAV untuk tiap kata dan Zip
            safe_pack_name = re.sub(r'[\\/*?:"<>|]', '', pack_name).replace(' ', '_')
            temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'TempAudio', safe_pack_name)
            if not os.path.exists(temp_dir): os.makedirs(temp_dir)
            
            generated_files = []
            for idx, (start_idx, end_idx) in enumerate(word_chunks):
                word = WORDS_TO_GENERATE[idx]
                self.set_status(f"Memotong '{word}'...", idx)
                word_samples = samples[start_idx:end_idx]
                
                wavfile = os.path.join(temp_dir, f"{word}.wav")
                with wave.open(wavfile, 'wb') as w:
                    w.setnchannels(nchannels)
                    w.setsampwidth(sampwidth)
                    w.setframerate(framerate)
                    w.writeframes(word_samples.tobytes())
                generated_files.append((word, wavfile))
                
            self.set_status("Membuat Voice Pack...", len(WORDS_TO_GENERATE))
            
            password_hash = ""
            if pack_password:
                password_hash = hashlib.sha256(pack_password.encode('utf-8')).hexdigest()
                
            manifest_data = {
                "name": pack_name,
                "author": author,
                "description": desc,
                "version": "1.0",
                "words": WORDS_TO_GENERATE,
                "password_hash": password_hash,
                "is_permanent": True
            }
            
            manifest_path = os.path.join(temp_dir, "manifest.json")
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest_data, f, indent=4)
                
            with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(manifest_path, "manifest.json")
                for w, fp in generated_files:
                    if os.path.exists(fp):
                        zipf.write(fp, f"{w}.wav")
                        
            self.set_status("Selesai!", len(WORDS_TO_GENERATE))
            wx.CallAfter(wx.MessageBox, f"Voice Pack berhasil diekstrak dan dibungkus!\nDisimpan di:\n{output_file}", "Sukses", wx.ICON_INFORMATION)
            
        except Exception as e:
            self.set_status("Gagal!")
            wx.CallAfter(wx.MessageBox, f"Terjadi kesalahan:\n{str(e)}", "Error", wx.ICON_ERROR)
        finally:
            wx.CallAfter(self.btn_generate.Enable)
            wx.CallAfter(self.btn_extract.Enable)
            wx.CallAfter(self.btn_pack_folder.Enable)
            wx.CallAfter(self.btn_extract.Enable)
            wx.CallAfter(self.btn_pack_folder.Enable)

    def generate_task(self, provider, voice, pack_name, author, desc, api_key, pack_password, output_file):
        import re
        safe_pack_name = re.sub(r'[\\/*?:"<>|]', '', pack_name).replace(' ', '_')
        temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'TempAudio', safe_pack_name)
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
            
        self.set_status(f"Memulai proses... (Melanjutkan cache jika ada)", 0)
        
        generated_files = []
        
        try:
            for idx, word in enumerate(WORDS_TO_GENERATE):
                wavfile = os.path.join(temp_dir, f"{word}.wav")
                outfile = os.path.join(temp_dir, f"{word}.tmp")
                
                if os.path.exists(wavfile):
                    self.set_status(f"Melewati: '{word}' (Sudah ada di cache) ({idx+1}/{len(WORDS_TO_GENERATE)})", idx)
                    generated_files.append((word, wavfile))
                    continue
                    
                self.set_status(f"Mengunduh suara untuk kata: '{word}' ({idx+1}/{len(WORDS_TO_GENERATE)})", idx)
                                # Modifikasi agar angka tidak dibaca menggantung
                speak_text = word
                if word.isdigit():
                    speak_text = f"{word}."
                elif word in ['am', 'pm']:
                    speak_text = word.upper()
                
                if "Google Cloud" in provider:
                    if not api_key:
                        raise Exception("API Key wajib diisi untuk Google Cloud / Gemini!")
                    url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={api_key}"
                    v_name = voice.split(" ")[0] # extract "id-ID-Wavenet-A"
                    payload = {
                        "input": {"text": speak_text},
                        "voice": {"languageCode": "id-ID", "name": v_name},
                        "audioConfig": {"audioEncoding": "MP3"}
                    }
                    data = json.dumps(payload).encode('utf-8')
                    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
                    with urllib.request.urlopen(req) as response:
                        resp_data = json.loads(response.read().decode('utf-8'))
                        import base64
                        with open(outfile, 'wb') as f:
                            f.write(base64.b64decode(resp_data['audioContent']))
                    time.sleep(0.1) # Fast API
                    
                elif "Gemini API" in provider:
                    if not api_key:
                        raise Exception("API Key wajib diisi untuk Gemini API!")
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-tts-preview:generateContent?key={api_key}"
                    v_name = voice.split(" ")[0]
                    # We must give it explicit instructions to ONLY output the word
                    payload = {
                        "contents": [{"role": "user", "parts": [{"text": f"Ucapkan kata ini dengan intonasi natural bahasa Indonesia, tanpa tambahan kata lain: {speak_text}"}]}],
                        "generationConfig": {
                            "responseModalities": ["AUDIO"],
                            "speechConfig": {
                                "voiceConfig": {
                                    "prebuiltVoiceConfig": {
                                        "voiceName": v_name
                                    }
                                }
                            }
                        }
                    }
                    data = json.dumps(payload).encode('utf-8')
                    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
                    
                    # Auto Retry for 429
                    max_retries = 5
                    for attempt in range(max_retries):
                        try:
                            with urllib.request.urlopen(req) as response:
                                resp_data = json.loads(response.read().decode('utf-8'))
                                break
                        except urllib.error.HTTPError as e:
                            if e.code == 429:
                                self.set_status(f"Limit Gemini (429) tercapai. Menunggu 15 detik... (Percobaan {attempt+1}/{max_retries})", idx)
                                time.sleep(15)
                            else:
                                raise e
                    else:
                        raise Exception("Gagal menghubungi Gemini karena limit 429 berulang kali.")

                    import base64
                    # Find audio part
                    audio_b64 = None
                    try:
                        parts = resp_data['candidates'][0]['content']['parts']
                        for p in parts:
                            if 'inlineData' in p and p['inlineData']['mimeType'].startswith('audio'):
                                audio_b64 = p['inlineData']['data']
                                break
                    except: pass
                    
                    if not audio_b64:
                        raise Exception("Gemini tidak mengembalikan data audio.")
                        
                    with open(outfile, 'wb') as f:
                        f.write(base64.b64decode(audio_b64))
                    time.sleep(1.0) # Rate limit Gemini API
                    
                elif "Google Translate" in provider:
                    # Google Translate TTS HTTP Request
                    url = f"http://translate.google.com/translate_tts?ie=UTF-8&total=1&idx=0&textlen={len(speak_text)}&client=tw-ob&q={urllib.parse.quote(speak_text)}&tl=id"
                    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req) as response:
                        with open(outfile, 'wb') as f:
                            f.write(response.read())
                    time.sleep(0.5) # Smart Throttle 0.5s
                    
                elif "Edge" in provider:
                    # Uses edge-tts python executable
                    cmd = f'python -m edge_tts --voice "{voice}" --text "{speak_text}" --write-media "{outfile}"'
                    result = subprocess.run(cmd, shell=True, capture_output=True)
                    if result.returncode != 0:
                        raise Exception(f"Edge-TTS Error: {result.stderr.decode('utf-8', errors='ignore')}\nPastikan Anda sudah menginstal edge-tts (pip install edge-tts)")
                    time.sleep(0.5) # Smart Throttle
                
# Convert MP3/PCM to WAV
                wavfile = os.path.join(temp_dir, f"{word}.wav")
                import array
                try:
                    if "Gemini API" in provider:
                        # Gemini mengembalikan RAW PCM (l16, 24000Hz, Mono) tanpa header
                        with open(outfile, 'rb') as f:
                            raw_pcm = f.read()
                        samples = array.array('h', raw_pcm)
                        sample_rate = 24000
                        nchannels = 1
                    else:
                        # Layanan lain (Edge, Translate, Cloud) mengembalikan MP3
                        decoded = miniaudio.mp3_read_file_s16(outfile)
                        samples = array.array('h', decoded.samples)
                        sample_rate = decoded.sample_rate
                        nchannels = decoded.nchannels
                    
                    # Auto Trim Silence
                    threshold = 400
                    start_idx = 0
                    for i in range(len(samples)):
                        if abs(samples[i]) > threshold:
                            start_idx = i
                            break
                    
                    end_idx = len(samples) - 1
                    for i in range(len(samples)-1, -1, -1):
                        if abs(samples[i]) > threshold:
                            end_idx = i
                            break
                    
                    margin = int(sample_rate * nchannels * 0.02) # 20ms margin
                    start_idx = max(0, start_idx - margin)
                    end_idx = min(len(samples), end_idx + margin)
                    
                    trimmed_samples = samples[start_idx:end_idx]
                    
                    with wave.open(wavfile, 'wb') as wav:
                        wav.setnchannels(nchannels)
                        wav.setsampwidth(2)
                        wav.setframerate(sample_rate)
                        wav.writeframes(trimmed_samples.tobytes())
                    os.remove(outfile)
                except Exception as e:
                    raise Exception(f"Gagal mengonversi {word} ke WAV: {e}")
                
                generated_files.append((word, wavfile))
                
            self.set_status("Merakit file JVP...", len(WORDS_TO_GENERATE))
            
            # Buat manifest.json
            import hashlib
            password_hash = ""
            if pack_password:
                password_hash = hashlib.sha256(pack_password.encode('utf-8')).hexdigest()
                
            manifest_data = {
                "name": pack_name,
                "author": author,
                "description": desc,
                "version": "1.0",
                "words": WORDS_TO_GENERATE,
                "password_hash": password_hash,
                "is_permanent": True
            }
            manifest_path = os.path.join(temp_dir, "manifest.json")
            with open(manifest_path, 'w', encoding='utf-8') as mf:
                json.dump(manifest_data, mf, indent=4)
                
            # Zipping
            with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(manifest_path, "manifest.json")
                for w, fp in generated_files:
                    if os.path.exists(fp):
                        zipf.write(fp, f"{w}.wav")
                        
            self.set_status("Selesai!", len(WORDS_TO_GENERATE))
            wx.CallAfter(wx.MessageBox, f"Voice Pack berhasil dibuat!\nDisimpan di:\n{output_file}", "Sukses", wx.ICON_INFORMATION)
            
        except Exception as e:
            self.set_status("Gagal!")
            wx.CallAfter(wx.MessageBox, f"Terjadi kesalahan:\n{str(e)}", "Error", wx.ICON_ERROR)
            
        finally:
            if 'manifest_path' in locals() and os.path.exists(manifest_path):
                try:
                    os.remove(manifest_path)
                except: pass
            wx.CallAfter(self.btn_generate.Enable)
            wx.CallAfter(self.btn_extract.Enable)
            wx.CallAfter(self.btn_pack_folder.Enable)
if __name__ == '__main__':
    app = wx.App(False)
    frame = VoiceStudioFrame()
    frame.Show()
    app.MainLoop()
