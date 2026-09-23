path = r'C:\Users\Raju Laini\Documents\Project_Jadwalku\PengembanganAplikasi\AIVoiceStudio\main.py'
content = open(path, 'r', encoding='utf-8').read()

# Add import urllib.error at the top
content = content.replace('import urllib.request', 'import urllib.request\nimport urllib.error')

# Remove import urllib.error from inside the function
content = content.replace('                    import urllib.error\n                    max_retries = 5', '                    max_retries = 5')

open(path, 'w', encoding='utf-8').write(content)
