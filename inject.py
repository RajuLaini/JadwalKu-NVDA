import json
import re

with open('all_versions.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

def version_key(v):
    base = v.split('&')[0].strip()
    parts = base.split('.')
    return [int(x) if x.isdigit() else 0 for x in parts]

sorted_keys = sorted(data.keys(), key=version_key, reverse=True)

py_list = []
for k in sorted_keys:
    text = data[k].replace('\\n\"\"', '').replace('\"\"', '').strip()
    # Also fix any weird literal \n to real newlines
    text = text.replace('\\n', '\n')
    if text:
        py_list.append(f'\t\t\t("Versi {k}", """{text}"""),')

py_code = "[\n" + "\n".join(py_list) + "\n\t\t]"

with open(r'JadwalKu\globalPlugins\jadwalku\guiDialogs.py', 'r', encoding='utf-8') as f:
    content = f.read()

pattern = r'self\.versions\s*=\s*\[.*?\]'
content = re.sub(pattern, 'self.versions = ' + py_code, content, flags=re.DOTALL)

with open(r'JadwalKu\globalPlugins\jadwalku\guiDialogs.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Injected all versions into guiDialogs.py!")
