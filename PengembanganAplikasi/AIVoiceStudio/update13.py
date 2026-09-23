import os
import re

path = r'C:\Users\Raju Laini\Documents\Project_Jadwalku\PengembanganAplikasi\AIVoiceStudio\main.py'
content = open(path, 'r', encoding='utf-8').read()

# 1. Ganti Tombol Tunggal menjadi Sizer 2 Tombol
old_btn = '''        # --- BUTTON ---
        self.btn_generate = wx.Button(self.panel, label="Mulai Buat Voice Pack!")
        self.btn_generate.Bind(wx.EVT_BUTTON, self.on_generate)
        self.sizer.Add(self.btn_generate, 0, wx.ALL | wx.CENTER, 15)'''
        
new_btn = '''        # --- BUTTONS ---
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.btn_generate = wx.Button(self.panel, label="1. Otomatis via API")
        self.btn_generate.Bind(wx.EVT_BUTTON, self.on_generate)
        self.btn_generate.SetToolTip("Mendownload suara satu per satu dari internet.")
        btn_sizer.Add(self.btn_generate, 0, wx.ALL, 5)
        
        self.btn_extract = wx.Button(self.panel, label="2. Ekstrak dari WAV (Manual)")
        self.btn_extract.Bind(wx.EVT_BUTTON, self.on_extract)
        self.btn_extract.SetToolTip("Memotong 70 kata otomatis dari 1 file WAV besar (seperti hasil Google AI Studio).")
        btn_sizer.Add(self.btn_extract, 0, wx.ALL, 5)
        
        self.sizer.Add(btn_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 10)'''

content = content.replace(old_btn, new_btn)

# 2. Tambahkan fungsi on_extract
on_extract_func = '''    def on_extract(self, event):
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
            safe_pack_name = re.sub(r'[\\\\/*?:\"<>|]', '', pack_name).replace(' ', '_')
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

'''

# Insert on_extract right before generate_task
content = content.replace('    def generate_task(self', on_extract_func + '    def generate_task(self')

# Enable extract button in generate_task finally block
content = content.replace('wx.CallAfter(self.btn_generate.Enable)', 'wx.CallAfter(self.btn_generate.Enable)\n            wx.CallAfter(self.btn_extract.Enable)')

open(path, 'w', encoding='utf-8').write(content)
