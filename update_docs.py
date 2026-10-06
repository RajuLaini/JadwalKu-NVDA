import json
import re

# Update version.json
with open('version.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

new_bullet = "- Restorasi Sejarah & Desain Ulang Changelog: Mengubah tampilan kotak teks raksasa pada jendela Riwayat Pembaruan menjadi daftar ListBox yang 100% ramah aksesibilitas Screen Reader. Selain itu, berhasil menyelamatkan dan merestorasi puluhan catatan versi lawas yang sempat hilang dari peradaban."

# Find the end of 1.7.6.5.7 block in version.json
changelog = data['changelog']
parts = changelog.split('\n\nPembaruan v1.7.6.5.6:')
parts[0] = parts[0] + '\n' + new_bullet
data['changelog'] = '\n\nPembaruan v1.7.6.5.6:'.join(parts)

with open('version.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

# Update guiDialogs.py
with open(r'JadwalKu\globalPlugins\jadwalku\guiDialogs.py', 'r', encoding='utf-8') as f:
    content = f.read()

# We need to find the text for 1.7.6.5.7 and append the new bullet.
# ("Versi 1.7.6.5.7", """...""")
match = re.search(r'\(\"Versi 1\.7\.6\.5\.7\",\s*\"\"\"(.*?)\"\"\"\)', content, re.DOTALL)
if match:
    old_text = match.group(1)
    new_text = old_text + '\n  ' + new_bullet
    content = content.replace(f'("Versi 1.7.6.5.7", """{old_text}""")', f'("Versi 1.7.6.5.7", """{new_text}""")')
    with open(r'JadwalKu\globalPlugins\jadwalku\guiDialogs.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("guiDialogs.py updated!")
else:
    print("Could not find 1.7.6.5.7 in guiDialogs.py")

