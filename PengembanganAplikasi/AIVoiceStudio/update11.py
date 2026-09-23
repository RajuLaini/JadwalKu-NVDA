path = r'C:\Users\Raju Laini\Documents\Project_Jadwalku\PengembanganAplikasi\AIVoiceStudio\main.py'
content = open(path, 'r', encoding='utf-8').read()

# Fix the indentation of the block right after def generate_task
content = content.replace(
'''    def generate_task(self, provider, voice, pack_name, author, desc, api_key, pack_password, output_file):
temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'TempAudio', pack_name.replace(' ', '_').replace('/', '_'))''',
'''    def generate_task(self, provider, voice, pack_name, author, desc, api_key, pack_password, output_file):
        temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'TempAudio', pack_name.replace(' ', '_').replace('/', '_'))'''
)

open(path, 'w', encoding='utf-8').write(content)
