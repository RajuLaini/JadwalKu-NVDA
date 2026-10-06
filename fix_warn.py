with open(r'JadwalKu\globalPlugins\jadwalku\guiDialogs.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('\- Perbaikan Interaksi', '- Perbaikan Interaksi')

with open(r'JadwalKu\globalPlugins\jadwalku\guiDialogs.py', 'w', encoding='utf-8') as f:
    f.write(content)
