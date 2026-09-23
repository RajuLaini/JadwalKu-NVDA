import os
import re

path = r'C:\Users\Raju Laini\Documents\Project_Jadwalku\PengembanganAplikasi\AIVoiceStudio\main.py'
content = open(path, 'r', encoding='utf-8').read()

# 1. Update Buttons Sizer
old_btns = '''        btn_sizer.Add(self.btn_extract, 0, wx.ALL, 5)
        
        self.sizer.Add(btn_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 10)'''
        
new_btns = '''        btn_sizer.Add(self.btn_extract, 0, wx.ALL, 5)
        
        self.btn_pack_folder = wx.Button(self.panel, label="3. Bungkus Folder (Auto-Trim)")
        self.btn_pack_folder.Bind(wx.EVT_BUTTON, self.on_pack_folder)
        self.btn_pack_folder.SetToolTip("Memangkas keheningan dari 70 file WAV terpisah dalam 1 folder lalu menjahitnya.")
        btn_sizer.Add(self.btn_pack_folder, 0, wx.ALL, 5)
        
        self.sizer.Add(btn_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 10)'''

content = content.replace(old_btns, new_btns)

# 2. Add logic for on_pack_folder and pack_folder_task
pack_folder_logic = '''    def on_pack_folder(self, event):
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
            
            safe_pack_name = re.sub(r'[\\\\/*?:\"<>|]', '', pack_name).replace(' ', '_')
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
                threshold = 300
                
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
                
                margin = int(framerate * nchannels * 0.02) # 20ms margin
                start_idx = max(0, start_idx - margin)
                end_idx = min(len(samples), end_idx + margin)
                
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

'''

content = content.replace('    def on_extract(self, event):', pack_folder_logic + '\n    def on_extract(self, event):')

# Ensure we re-enable the new button in extract_task and generate_task
content = content.replace('wx.CallAfter(self.btn_extract.Enable)', 'wx.CallAfter(self.btn_extract.Enable)\n            wx.CallAfter(self.btn_pack_folder.Enable)')

open(path, 'w', encoding='utf-8').write(content)
