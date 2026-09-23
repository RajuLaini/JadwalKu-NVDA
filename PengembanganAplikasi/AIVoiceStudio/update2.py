import re

path = r'C:\Users\Raju Laini\Documents\Project_Jadwalku\PengembanganAplikasi\AIVoiceStudio\main.py'
content = open(path, 'r', encoding='utf-8').read()

# 1. Update cb_provider choices
content = content.replace(
    'choices=["Edge TTS (Gratis)", "Google Translate (Gratis)"]',
    'choices=["Edge TTS (Gratis)", "Google Translate (Gratis)", "Google Cloud / Gemini (Berbayar API)"]'
)

# 2. Add EVT_COMBOBOX for voice
content = content.replace(
    'self.cb_voice.SetSelection(0)\n        grid.Add(self.cb_voice',
    'self.cb_voice.SetSelection(0)\n        self.cb_voice.Bind(wx.EVT_COMBOBOX, self.on_voice_change)\n        grid.Add(self.cb_voice'
)

# 3. Add on_voice_change function
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
        else:
            self.txt_pack_name.SetValue("Suara AI Custom")
'''
content = content.replace('def on_provider_change(self, event):', voice_change_func + '\n    def on_provider_change(self, event):')

# 4. Update on_provider_change logic
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
'''
content = re.sub(r'def on_provider_change\(self, event\):.*?def set_status', new_provider_logic + '\n    def set_status', content, flags=re.DOTALL)

# 5. Extract API key in on_generate
content = content.replace(
    'desc = self.txt_desc.GetValue().strip()',
    'desc = self.txt_desc.GetValue().strip()\n        api_key = self.txt_api.GetValue().strip()'
)

content = content.replace(
    'args=(provider, voice, pack_name, author, desc, output_file)).start()',
    'args=(provider, voice, pack_name, author, desc, api_key, output_file)).start()'
)

content = content.replace(
    'def generate_task(self, provider, voice, pack_name, author, desc, output_file):',
    'def generate_task(self, provider, voice, pack_name, author, desc, api_key, output_file):'
)

# 6. Add Google Cloud API request logic
google_cloud_logic = '''
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
                    
                elif "Google Translate" in provider:
'''
content = content.replace('if "Google Translate" in provider:', google_cloud_logic.strip())

open(path, 'w', encoding='utf-8').write(content)
print("Updated successfully!")
