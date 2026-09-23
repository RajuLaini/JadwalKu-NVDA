path = r'C:\Users\Raju Laini\Documents\Project_Jadwalku\PengembanganAplikasi\AIVoiceStudio\main.py'
content = open(path, 'r', encoding='utf-8').read()

import re
# Cari fungsi pack_folder_task dan ganti thresholdnya
# We will use regex to only replace threshold = 300 inside pack_folder_task
def replacer(match):
    return match.group(0).replace('threshold = 300', 'threshold = 400')

content = re.sub(r'def pack_folder_task\(.*?(?=def |$)', replacer, content, flags=re.DOTALL)

open(path, 'w', encoding='utf-8').write(content)
