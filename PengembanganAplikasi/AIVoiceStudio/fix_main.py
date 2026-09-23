import re
path = r'C:\Users\Raju Laini\Documents\Project_Jadwalku\PengembanganAplikasi\AIVoiceStudio\main.py'
content = open(path, 'r', encoding='utf-8').read()

start_idx = content.find('    def generate_task(self')
end_idx = content.find('if __name__ ==')

new_generate_task = '''    def generate_task(self, provider, voice, pack_name, author, desc, api_key, output_file):
        temp_dir = os.path.join(os.environ.get('TEMP', ''), 'jadwalku_ai_temp')
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
            
        self.set_status("Memulai proses... (Mohon tunggu)", 0)
        
        generated_files = []
        
        try:
            for idx, word in enumerate(WORDS_TO_GENERATE):
                self.set_status(f"Mengunduh suara untuk kata: '{word}' ({idx+1}/{len(WORDS_TO_GENERATE)})", idx)
                
                outfile = os.path.join(temp_dir, f"{word}.mp3")
                
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
                    import urllib.error
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
                        raise Exception(f"Edge-TTS Error: {result.stderr.decode('utf-8', errors='ignore')}\\nPastikan Anda sudah menginstal edge-tts (pip install edge-tts)")
                    time.sleep(0.5) # Smart Throttle
                
                # Convert MP3 to WAV using miniaudio
                wavfile = os.path.join(temp_dir, f"{word}.wav")
                import array
                try:
                    decoded = miniaudio.mp3_read_file_s16(outfile)
                    samples = array.array('h', decoded.samples)
                    
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
                    
                    margin = int(decoded.sample_rate * decoded.nchannels * 0.02) # 20ms margin
                    start_idx = max(0, start_idx - margin)
                    end_idx = min(len(samples), end_idx + margin)
                    
                    trimmed_samples = samples[start_idx:end_idx]
                    
                    with wave.open(wavfile, 'wb') as wav:
                        wav.setnchannels(decoded.nchannels)
                        wav.setsampwidth(2)
                        wav.setframerate(decoded.sample_rate)
                        wav.writeframes(trimmed_samples.tobytes())
                    os.remove(outfile)
                except Exception as e:
                    raise Exception(f"Gagal mengonversi {word} ke WAV: {e}")
                
                generated_files.append((word, wavfile))
                
            self.set_status("Merakit file JVP...", len(WORDS_TO_GENERATE))
            
            # Buat manifest.json
            manifest_data = {
                "name": pack_name,
                "author": author,
                "description": desc,
                "version": "1.0",
                "words": WORDS_TO_GENERATE,
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
            wx.CallAfter(wx.MessageBox, f"Voice Pack berhasil dibuat!\\nDisimpan di:\\n{output_file}", "Sukses", wx.ICON_INFORMATION)
            
        except Exception as e:
            self.set_status("Gagal!")
            wx.CallAfter(wx.MessageBox, f"Terjadi kesalahan:\\n{str(e)}", "Error", wx.ICON_ERROR)
            
        finally:
            # Cleanup temp files
            for w, fp in generated_files:
                if os.path.exists(fp):
                    try:
                        os.remove(fp)
                    except: pass
            if os.path.exists(manifest_path):
                try:
                    os.remove(manifest_path)
                except: pass
            wx.CallAfter(self.btn_generate.Enable)

'''

open(path, 'w', encoding='utf-8').write(content[:start_idx] + new_generate_task + content[end_idx:])
print("Fixed generate_task entirely!")
