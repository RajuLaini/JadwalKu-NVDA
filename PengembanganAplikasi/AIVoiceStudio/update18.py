path = r'C:\Users\Raju Laini\Documents\Project_Jadwalku\PengembanganAplikasi\AIVoiceStudio\main.py'
content = open(path, 'r', encoding='utf-8').read()

content = content.replace('f"Terjadi kesalahan:\n{str(e)}"', 'f"Terjadi kesalahan:\\n{str(e)}"')

open(path, 'w', encoding='utf-8').write(content)
