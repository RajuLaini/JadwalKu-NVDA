import zipfile
import glob
import os
import re
import json

addons = glob.glob('*.nvda-addon')
# sort by modification time to get chronological order
addons.sort(key=os.path.getmtime)

all_versions = {}

for addon in addons:
    try:
        with zipfile.ZipFile(addon, 'r') as z:
            names = z.namelist()
            if 'globalPlugins/jadwalku/guiDialogs.py' in names:
                content = z.read('globalPlugins/jadwalku/guiDialogs.py').decode('utf-8', errors='ignore')
                
                # Match [Versi 1.x] or --- Versi 1.x ---
                pattern = r'(?:\[(Versi [\d\.]+(?: & [\d\.]+)*)\]|--- (Versi [\d\.]+) ---)\r?\n(.*?)(?=\r?\n(?:\[Versi|--- Versi|\s*\"\s*\)|\Z))'
                matches = re.finditer(pattern, content, re.DOTALL)
                for match in matches:
                    v_name = match.group(1) if match.group(1) else match.group(2)
                    v_name = v_name.strip()
                    v_text = match.group(3).strip()
                    # Only add if not already there, or if the new one is LONGER (more details)
                    if v_name not in all_versions or len(v_text) > len(all_versions[v_name]):
                        all_versions[v_name] = v_text
    except Exception as e:
        pass

# Add the ones from the current guiDialogs.py
with open(r'JadwalKu\globalPlugins\jadwalku\guiDialogs.py', 'r', encoding='utf-8') as f:
    content = f.read()
    # In our current file, they are in a python list format: ("Versi X", "- detail")
    matches = re.finditer(r'\(\"(Versi[^\"]+)\",\s*\"([^\"]+)\"\)', content)
    for match in matches:
        all_versions[match.group(1)] = match.group(2).replace('\\n', '\n')

with open('all_versions.json', 'w', encoding='utf-8') as f:
    json.dump(all_versions, f, indent=4, ensure_ascii=False)

print(f"Extracted {len(all_versions)} versions.")
