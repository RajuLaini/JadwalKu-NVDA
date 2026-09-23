import re

path = r'C:\Users\Raju Laini\Documents\Project_Jadwalku\PengembanganAplikasi\AIVoiceStudio\main.py'
content = open(path, 'r', encoding='utf-8').read()

new_logic = '''        temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'TempAudio', pack_name.replace(' ', '_').replace('/', '_'))
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
'''

# Find the start of try block to replace
start_idx = content.find('''        temp_dir = os.path.join(os.environ.get('TEMP', ''), 'jadwalku_ai_temp')''')
end_idx = content.find('''                # Modifikasi agar angka tidak dibaca menggantung''')

content = content[:start_idx] + new_logic.strip() + '\n                ' + content[end_idx:]

# Remove cleanup of wav files in finally block
finally_start = content.find('        finally:')
finally_logic = '''        finally:
            if 'manifest_path' in locals() and os.path.exists(manifest_path):
                try:
                    os.remove(manifest_path)
                except: pass
            wx.CallAfter(self.btn_generate.Enable)'''

content = content[:finally_start] + finally_logic

open(path, 'w', encoding='utf-8').write(content)
print("Added Resume and Caching Logic!")
