import zipfile
import glob
import os
import re
import json
import ast

addons = glob.glob('*.nvda-addon')
addons.sort(key=os.path.getmtime)

all_versions = {}

def parse_changelog(full_text):
    # Regex to split by version headers
    # Matches: [Versi 1.x.x], --- Versi 1.x.x ---, etc.
    pattern = r'(?:\[(?:Versi )?([\d\.]+(?: & [\d\.]+)*)\]|--- (?:Versi )?([\d\.]+(?: & [\d\.]+)*) ---)'
    
    parts = re.split(pattern, full_text)
    # parts[0] is intro text before any header
    # parts[1] is group 1 (if matched)
    # parts[2] is group 2 (if matched)
    # parts[3] is the text for that version
    
    idx = 1
    while idx < len(parts) - 2:
        v1 = parts[idx]
        v2 = parts[idx+1]
        v_name = v1 if v1 else v2
        
        if v_name:
            v_name = v_name.strip()
            v_text = parts[idx+2].strip()
            if v_name not in all_versions or len(v_text) > len(all_versions[v_name]):
                all_versions[v_name] = v_text
        idx += 3

for addon in addons:
    try:
        with zipfile.ZipFile(addon, 'r') as z:
            names = z.namelist()
            if 'globalPlugins/jadwalku/guiDialogs.py' in names:
                content = z.read('globalPlugins/jadwalku/guiDialogs.py').decode('utf-8', errors='ignore')
                
                # Find changelog_text assignment
                # It usually looks like: changelog_text = (\n "..." \n "..." \n)
                match = re.search(r'changelog_text\s*=\s*(\(.*?\)|""".*?"""|\'\'.*?\'\')', content, re.DOTALL)
                if match:
                    code_block = match.group(1)
                    try:
                        # Safely evaluate the literal string
                        parsed_str = ast.literal_eval(code_block)
                        parse_changelog(parsed_str)
                    except Exception as e:
                        # Fallback to naive regex if ast fails
                        # Remove quotes and + and whitespace
                        clean_str = re.sub(r'[\r\n\t]', '', code_block)
                        parse_changelog(clean_str)
    except Exception as e:
        pass

# Also get current ones from our active guiDialogs.py
try:
    with open(r'JadwalKu\globalPlugins\jadwalku\guiDialogs.py', 'r', encoding='utf-8') as f:
        content = f.read()
        matches = re.finditer(r'\(\"(Versi [^\"]+)\",\s*\"([^\"]+)\"\)', content)
        for match in matches:
            v_name = match.group(1).replace("Versi ", "").strip()
            v_text = match.group(2).replace('\\n', '\n').strip()
            if v_name not in all_versions or len(v_text) > len(all_versions[v_name]):
                all_versions[v_name] = v_text
except:
    pass

with open('all_versions.json', 'w', encoding='utf-8') as f:
    json.dump(all_versions, f, indent=4, ensure_ascii=False)

print(f"Extracted {len(all_versions)} versions.")
