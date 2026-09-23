path = r'C:\Users\Raju Laini\Documents\Project_Jadwalku\PengembanganAplikasi\AIVoiceStudio\main.py'
content = open(path, 'r', encoding='utf-8').read()

# Add import re at the top of the file
if 'import re\n' not in content:
    content = content.replace('import os\nimport json', 'import os\nimport json\nimport re')
    
# Or specifically inside extract_task where it was missing
content = content.replace('import wave, array, math, hashlib\n            import zipfile', 'import wave, array, math, hashlib\n            import zipfile\n            import re')

open(path, 'w', encoding='utf-8').write(content)
