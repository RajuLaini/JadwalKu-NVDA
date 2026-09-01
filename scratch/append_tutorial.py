import os

file_path = r'C:\Users\Raju Laini\Documents\Project_Jadwalku\JadwalKu\globalPlugins\jadwalku\simulation.py'

append_code = '''
class TutorialEntryDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="Pusat Bantuan & Tutorial JadwalKu", size=(500, 300), style=wx.DEFAULT_DIALOG_STYLE)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        lbl_info = wx.StaticText(self, label="Bagaimana Anda ingin mempelajari JadwalKu?")
        font = lbl_info.GetFont()
        font.MakeBold()
        lbl_info.SetFont(font)
        sizer.Add(lbl_info, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 15)
        
        btnSizer = wx.BoxSizer(wx.VERTICAL)
        
        self.btn_doc = wx.Button(self, label="1. Buka Panduan &Teks Biasa (Alt+T)")
        self.btn_doc.Bind(wx.EVT_BUTTON, self.onDoc)
        btnSizer.Add(self.btn_doc, 0, wx.ALL | wx.EXPAND, 8)
        
        self.btn_sim = wx.Button(self, label="2. Mulai &Simulasi Interaktif Penuh (Langkah-demi-langkah) (Alt+S)")
        self.btn_sim.Bind(wx.EVT_BUTTON, self.onSimulation)
        btnSizer.Add(self.btn_sim, 0, wx.ALL | wx.EXPAND, 8)
        
        sizer.Add(btnSizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 20)
        
        self.btnClose = wx.Button(self, wx.ID_CANCEL, label="&Tutup (Esc)")
        self.btnClose.Bind(wx.EVT_BUTTON, lambda evt: self.EndModal(wx.ID_CANCEL))
        sizer.Add(self.btnClose, 0, wx.ALL | wx.ALIGN_RIGHT, 15)
        
        self.SetSizer(sizer)
        self.Centre()
        
    def onDoc(self, evt):
        import os
        from . import utils
        doc_path = os.path.join(os.path.dirname(__file__), "..", "..", "doc", "id", "readme.html")
        if not os.path.exists(doc_path):
            doc_path = os.path.join(os.path.dirname(__file__), "..", "..", "doc", "readme.html")
        if os.path.exists(doc_path):
            utils.open_file(doc_path)
        self.EndModal(wx.ID_NO)
        
    def onSimulation(self, evt):
        self.EndModal(wx.ID_YES)

def start_tutorial(parent):
    dlg = TutorialEntryDialog(parent)
    res = dlg.ShowModal()
    dlg.Destroy()
    
    if res == wx.ID_YES:
        sim_dlg = SimulationWizardDialog(parent)
        sim_dlg.ShowModal()
        sim_dlg.Destroy()
'''

with open(file_path, 'a', encoding='utf-8') as f:
    f.write('\n' + append_code)
print('Done appending')
