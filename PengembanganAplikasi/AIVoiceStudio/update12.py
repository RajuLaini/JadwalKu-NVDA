path = r'C:\Users\Raju Laini\Documents\Project_Jadwalku\PengembanganAplikasi\AIVoiceStudio\main.py'
content = open(path, 'r', encoding='utf-8').read()

# Fix the sanitization of temp_dir
old_temp_dir = "        temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'TempAudio', pack_name.replace(' ', '_').replace('/', '_'))"
new_temp_dir = "        import re\n        safe_pack_name = re.sub(r'[\\\\/*?:\"<>|]', '', pack_name).replace(' ', '_')\n        temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'TempAudio', safe_pack_name)"

content = content.replace(old_temp_dir, new_temp_dir)

open(path, 'w', encoding='utf-8').write(content)
