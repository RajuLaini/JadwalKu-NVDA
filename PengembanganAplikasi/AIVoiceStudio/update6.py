import os
path = r'C:\Users\Raju Laini\Documents\Project_Jadwalku\PengembanganAplikasi\AIVoiceStudio\main.py'
content = open(path, 'r', encoding='utf-8').read()

load_logic = '''        # --- LOAD CONFIG ---
        self.config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
        saved_api = ""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    cfg = json.load(f)
                    saved_api = cfg.get('api_key', '')
            except: pass
            
        # --- API KEY ---
        grid.Add(wx.StaticText(self.panel, label="API Key (Kosongkan jika gratis):"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.txt_api = wx.TextCtrl(self.panel, value=saved_api)'''

content = content.replace(
'''        # --- API KEY ---
        grid.Add(wx.StaticText(self.panel, label="API Key (Kosongkan jika gratis):"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.txt_api = wx.TextCtrl(self.panel)''', load_logic)

save_logic = '''        desc = self.txt_desc.GetValue().strip()
        api_key = self.txt_api.GetValue().strip()
        
        # Save API key for next time
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump({"api_key": api_key}, f)
        except: pass'''

content = content.replace(
'''        desc = self.txt_desc.GetValue().strip()
        api_key = self.txt_api.GetValue().strip()''', save_logic)

open(path, 'w', encoding='utf-8').write(content)
print("Added API Key saving logic!")
