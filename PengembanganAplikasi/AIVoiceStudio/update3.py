import re

path = r'C:\Users\Raju Laini\Documents\Project_Jadwalku\PengembanganAplikasi\AIVoiceStudio\main.py'
content = open(path, 'r', encoding='utf-8').read()

# 1. Update cb_provider choices
content = content.replace(
    'choices=["Edge TTS (Gratis)", "Google Translate (Gratis)", "Google Cloud / Gemini (Berbayar API)"]',
    'choices=["Edge TTS (Gratis)", "Google Translate (Gratis)", "Google Cloud TTS", "Gemini API (Google AI Studio)"]'
)

# 2. Update on_voice_change function for Gemini voices
voice_change_func = '''
    def on_voice_change(self, event):
        voice = self.cb_voice.GetValue()
        if "Gadis" in voice:
            self.txt_pack_name.SetValue("Suara AI Gadis")
        elif "Ardi" in voice:
            self.txt_pack_name.SetValue("Suara AI Ardi")
        elif "Wavenet-A" in voice or "Female" in voice:
            self.txt_pack_name.SetValue("Suara AI Wavenet Wanita")
        elif "Wavenet-B" in voice or "Wavenet-C" in voice or "Male" in voice:
            self.txt_pack_name.SetValue("Suara AI Wavenet Pria")
        elif "Aoede" in voice:
            self.txt_pack_name.SetValue("Suara AI Aoede (Gemini)")
        elif "Charon" in voice:
            self.txt_pack_name.SetValue("Suara AI Charon (Gemini)")
        elif "Fenrir" in voice:
            self.txt_pack_name.SetValue("Suara AI Fenrir (Gemini)")
        elif "Kore" in voice:
            self.txt_pack_name.SetValue("Suara AI Kore (Gemini)")
        elif "Puck" in voice:
            self.txt_pack_name.SetValue("Suara AI Puck (Gemini)")
        else:
            self.txt_pack_name.SetValue("Suara AI Custom")
'''
content = re.sub(r'def on_voice_change\(self, event\):.*?def on_provider_change', voice_change_func.strip() + '\n\n    def on_provider_change', content, flags=re.DOTALL)

# 3. Update on_provider_change logic
new_provider_logic = '''
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
            self.cb_voice.Set(["Aoede (Wanita)", "Charon (Pria)", "Fenrir (Pria)", "Kore (Wanita)", "Puck (Pria)"])
            self.cb_voice.SetSelection(0)
            self.txt_api.Enable()
            self.on_voice_change(None)
'''
content = re.sub(r'def on_provider_change\(self, event\):.*?def set_status', new_provider_logic.strip() + '\n\n    def set_status', content, flags=re.DOTALL)

# 4. Add Gemini API request logic
gemini_logic = '''
                elif "Gemini API" in provider:
                    if not api_key:
                        raise Exception("API Key wajib diisi untuk Gemini API!")
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
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
                    with urllib.request.urlopen(req) as response:
                        resp_data = json.loads(response.read().decode('utf-8'))
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
                            
                        # Gemini returns raw PCM or WAV, we save it as mp3 extension so our miniaudio trimmer still picks it up (miniaudio supports decoding WAV too!)
                        with open(outfile, 'wb') as f:
                            f.write(base64.b64decode(audio_b64))
                    time.sleep(1.0) # Rate limit Gemini API
'''
content = content.replace('elif "Google Translate" in provider:', gemini_logic.strip() + '\n                    \n                elif "Google Translate" in provider:')

open(path, 'w', encoding='utf-8').write(content)
print("Updated successfully for Gemini Native Speech!")
