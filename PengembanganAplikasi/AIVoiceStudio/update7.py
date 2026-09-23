import re

path = r'C:\Users\Raju Laini\Documents\Project_Jadwalku\PengembanganAplikasi\AIVoiceStudio\main.py'
content = open(path, 'r', encoding='utf-8').read()

# Increase row count for the grid
content = content.replace('rows=7', 'rows=8')

# Add Password Field in UI
pw_logic = '''        # --- DESCRIPTION ---
        grid.Add(wx.StaticText(self.panel, label="Deskripsi Paket:"), 0, wx.ALIGN_TOP)
        self.txt_desc = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE, size=(-1, 60))
        self.txt_desc.SetValue("Paket suara AI otomatis yang dihasilkan oleh JadwalKu Voice Studio.")
        grid.Add(self.txt_desc, 1, wx.EXPAND)
        
        # --- PASSWORD ---
        grid.Add(wx.StaticText(self.panel, label="Kata Sandi Hapus (Opsional):"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.txt_password = wx.TextCtrl(self.panel, style=wx.TE_PASSWORD)
        self.txt_password.SetToolTip("Digunakan agar Voice Pack ini tidak bisa dihapus sembarangan oleh orang lain jika Anda mengunggahnya ke server.")
        grid.Add(self.txt_password, 1, wx.EXPAND)'''

content = content.replace(
'''        # --- DESCRIPTION ---
        grid.Add(wx.StaticText(self.panel, label="Deskripsi Paket:"), 0, wx.ALIGN_TOP)
        self.txt_desc = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE, size=(-1, 60))
        self.txt_desc.SetValue("Paket suara AI otomatis yang dihasilkan oleh JadwalKu Voice Studio.")
        grid.Add(self.txt_desc, 1, wx.EXPAND)''', pw_logic)

# Retrieve Password in on_generate
ret_logic = '''        desc = self.txt_desc.GetValue().strip()
        api_key = self.txt_api.GetValue().strip()
        pack_password = self.txt_password.GetValue()'''

content = content.replace(
'''        desc = self.txt_desc.GetValue().strip()
        api_key = self.txt_api.GetValue().strip()''', ret_logic)

# Pass password to generate_task
content = content.replace(
    'args=(provider, voice, pack_name, author, desc, api_key, output_file)).start()',
    'args=(provider, voice, pack_name, author, desc, api_key, pack_password, output_file)).start()'
)

content = content.replace(
    'def generate_task(self, provider, voice, pack_name, author, desc, api_key, output_file):',
    'def generate_task(self, provider, voice, pack_name, author, desc, api_key, pack_password, output_file):'
)

# Hash password and add to manifest
manifest_logic = '''            # Buat manifest.json
            import hashlib
            password_hash = ""
            if pack_password:
                password_hash = hashlib.sha256(pack_password.encode('utf-8')).hexdigest()
                
            manifest_data = {
                "name": pack_name,
                "author": author,
                "description": desc,
                "version": "1.0",
                "words": WORDS_TO_GENERATE,
                "password_hash": password_hash,
                "is_permanent": True
            }'''
            
content = re.sub(r'# Buat manifest\.json.*?is_permanent": True\n            \}', manifest_logic.strip(), content, flags=re.DOTALL)

open(path, 'w', encoding='utf-8').write(content)
print("Added Password protection logic!")
