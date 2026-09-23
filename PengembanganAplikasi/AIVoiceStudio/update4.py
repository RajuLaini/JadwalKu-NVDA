import re

path = r'C:\Users\Raju Laini\Documents\Project_Jadwalku\PengembanganAplikasi\AIVoiceStudio\main.py'
content = open(path, 'r', encoding='utf-8').read()

gemini_voices = [
    "Aoede", "Charon", "Fenrir", "Kore", "Puck", "Zephyr", "Leda", "Orus", 
    "Callirrhoe", "Autonoe", "Enceladus", "Iapetus", "Umbriel", "Algieba", 
    "Despina", "Erinome", "Algenib", "Rasalgethi", "Laomedeia", "Achernar"
]

gemini_list_str = "[" + ", ".join([f'"{v} (Gemini)"' for v in gemini_voices]) + "]"

content = content.replace(
    'self.cb_voice.Set(["Aoede (Wanita)", "Charon (Pria)", "Fenrir (Pria)", "Kore (Wanita)", "Puck (Pria)"])',
    f'self.cb_voice.Set({gemini_list_str})'
)

# Replace the specific name logic
name_logic = '''
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
'''

content = re.sub(r'def on_voice_change\(self, event\):.*?def on_provider_change', name_logic.strip() + '\n\n    def on_provider_change', content, flags=re.DOTALL)

open(path, 'w', encoding='utf-8').write(content)
print("Added all 20 Gemini voices!")
