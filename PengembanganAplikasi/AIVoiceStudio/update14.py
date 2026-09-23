path = r'C:\Users\Raju Laini\Documents\Project_Jadwalku\PengembanganAplikasi\AIVoiceStudio\main.py'
content = open(path, 'r', encoding='utf-8').read()

import re
# Fix the unterminated f-string by replacing literal newlines inside the string with \\n
# Just search for the exact block and replace
content = content.replace('f"Voice Pack berhasil diekstrak dan dibungkus!\nDisimpan di:\n{output_file}"', 'f"Voice Pack berhasil diekstrak dan dibungkus!\\nDisimpan di:\\n{output_file}"')
content = content.replace('f"Terjadi kesalahan:\n{str(e)}"', 'f"Terjadi kesalahan:\\n{str(e)}"')

open(path, 'w', encoding='utf-8').write(content)
