import re
import os

filepath = r"C:\Users\Raju Laini\Documents\Project_Jadwalku\JadwalKu\globalPlugins\jadwalku\guiDialogs.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Inject panel_events right after panel_tab1
panel_events_code = """
		# --- Tab Acara & Kalender ---
		self.panel_events = wx.Panel(self.notebook)
		sizer_events = wx.BoxSizer(wx.VERTICAL)
		
		# Briefing Config
		box_briefing = wx.StaticBox(self.panel_events, label="Pengaturan Briefing Pagi (Sapaan TTS)")
		sizer_briefing = wx.StaticBoxSizer(box_briefing, wx.VERTICAL)
		
		self.chk_briefing = wx.CheckBox(self.panel_events, label="Aktifkan Briefing Acara Harian")
		sizer_briefing.Add(self.chk_briefing, 0, wx.ALL, 5)
		
		hz_brief_time = wx.BoxSizer(wx.HORIZONTAL)
		hz_brief_time.Add(wx.StaticText(self.panel_events, label="Jam Briefing Pagi:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
		self.sp_briefing = wx.SpinCtrl(self.panel_events, min=0, max=23, initial=7)
		hz_brief_time.Add(self.sp_briefing, 0, wx.ALL, 5)
		sizer_briefing.Add(hz_brief_time, 0, wx.ALL, 5)
		
		btn_save_briefing = wx.Button(self.panel_events, label="Simpan Pengaturan Briefing")
		btn_save_briefing.Bind(wx.EVT_BUTTON, self.onSaveBriefing)
		sizer_briefing.Add(btn_save_briefing, 0, wx.ALL, 5)
		
		sizer_events.Add(sizer_briefing, 0, wx.EXPAND | wx.ALL, 5)
		
		# Events List
		box_list = wx.StaticBox(self.panel_events, label="Daftar Acara & Peringatan")
		sizer_list = wx.StaticBoxSizer(box_list, wx.VERTICAL)
		
		self.listEvents = wx.ListCtrl(self.panel_events, style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.BORDER_SUNKEN)
		self.listEvents.InsertColumn(0, "Nama Acara", width=150)
		self.listEvents.InsertColumn(1, "Tanggal", width=100)
		self.listEvents.InsertColumn(2, "Tipe", width=100)
		self.listEvents.InsertColumn(3, "Jam", width=60)
		self.listEvents.InsertColumn(4, "Peringatan Dini", width=100)
		sizer_list.Add(self.listEvents, 1, wx.EXPAND | wx.ALL, 5)
		
		hz_evt_btn = wx.BoxSizer(wx.HORIZONTAL)
		btn_add_evt = wx.Button(self.panel_events, label="&Tambah Acara Baru")
		btn_add_evt.Bind(wx.EVT_BUTTON, self.onAddEvent)
		hz_evt_btn.Add(btn_add_evt, 0, wx.ALL, 5)
		
		btn_edit_evt = wx.Button(self.panel_events, label="&Edit Acara")
		btn_edit_evt.Bind(wx.EVT_BUTTON, self.onEditEvent)
		hz_evt_btn.Add(btn_edit_evt, 0, wx.ALL, 5)
		
		btn_del_evt = wx.Button(self.panel_events, label="&Hapus Acara")
		btn_del_evt.Bind(wx.EVT_BUTTON, self.onDeleteEvent)
		hz_evt_btn.Add(btn_del_evt, 0, wx.ALL, 5)
		
		sizer_list.Add(hz_evt_btn, 0, wx.ALL, 5)
		sizer_events.Add(sizer_list, 1, wx.EXPAND | wx.ALL, 5)
		
		self.panel_events.SetSizer(sizer_events)
"""
content = content.replace(
    'self.notebook.AddPage(self.panel_tab1, "1. Manajemen Agenda & Jadwal")',
    panel_events_code + '\n\t\tself.notebook.AddPage(self.panel_tab1, "1. Manajemen Agenda & Jadwal")\n\t\tself.notebook.AddPage(self.panel_events, "2. Kalender & Acara (Events)")'
)
content = content.replace('"2. Pengaturan Waktu & Kalender JadwalKu"', '"3. Pengaturan Waktu"')
content = content.replace('"3. Voice Pack & Studio Suara"', '"4. Voice Pack & Studio Suara"')
content = content.replace('"4. Perintah Suara (Voice Command)"', '"5. Perintah Suara (Voice Command)"')

# 2. Add event methods in JadwalKuDialog
methods_code = """
	def refreshEvents(self):
		self.listEvents.DeleteAllItems()
		events = self.config.get_events()
		import datetime
		# Urutkan berdasarkan tanggal terdekat
		now = datetime.datetime.now()
		
		def get_next_date(evt):
			date_str = evt.get("date", "")
			if not date_str: return datetime.date.max
			try:
				if evt.get("type") == "one-time":
					return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
				else:
					dt = datetime.datetime.strptime(f"{now.year}-{date_str}", "%Y-%m-%d").date()
					if dt < now.date():
						return datetime.date(now.year + 1, dt.month, dt.day)
					return dt
			except:
				return datetime.date.max
				
		events_sorted = sorted(events, key=get_next_date)
		
		for idx, evt in enumerate(events_sorted):
			self.listEvents.InsertItem(idx, evt.get("title", ""))
			self.listEvents.SetItem(idx, 1, evt.get("date", ""))
			t_str = "Sekali" if evt.get("type") == "one-time" else "Tahunan"
			self.listEvents.SetItem(idx, 2, t_str)
			self.listEvents.SetItem(idx, 3, evt.get("time", "-"))
			
			rem = str(evt.get("reminder", "0"))
			rem_str = "Hari H"
			if rem == "1": rem_str = "H-1"
			elif rem == "7": rem_str = "H-7"
			elif rem == "30": rem_str = "1 Bulan"
			self.listEvents.SetItem(idx, 4, rem_str)
			
			self.listEvents.SetItemData(idx, int(idx))
		
		# set index map
		self.event_map = events_sorted
		
	def onSaveBriefing(self, evt):
		cfg = self.config.get_events_config()
		cfg["briefing_enabled"] = self.chk_briefing.GetValue()
		cfg["briefing_hour"] = self.sp_briefing.GetValue()
		self.config.update_events_config(cfg)
		import ui
		ui.message("Pengaturan Briefing Pagi berhasil disimpan.")
		
	def onAddEvent(self, evt):
		dlg = EventEditorDialog(self)
		if dlg.ShowModal() == wx.ID_OK:
			data = dlg.get_data()
			self.config.add_event(data)
			self.refreshEvents()
		dlg.Destroy()
		
	def onEditEvent(self, evt):
		sel = self.listEvents.GetFirstSelected()
		if sel < 0: return
		event_data = self.event_map[sel]
		dlg = EventEditorDialog(self, event_data)
		if dlg.ShowModal() == wx.ID_OK:
			data = dlg.get_data()
			self.config.update_event(event_data["id"], data)
			self.refreshEvents()
		dlg.Destroy()
		
	def onDeleteEvent(self, evt):
		sel = self.listEvents.GetFirstSelected()
		if sel < 0: return
		event_data = self.event_map[sel]
		if self.config.delete_event(event_data["id"]):
			import ui
			ui.message("Acara dihapus.")
			self.refreshEvents()
"""
# inject methods at the end of JadwalKuDialog before HelpDialog
content = content.replace("class HelpDialog(wx.Dialog):", methods_code + "\nclass HelpDialog(wx.Dialog):")

# 3. Add EventEditorDialog at the end of file
dialog_code = """
class EventEditorDialog(wx.Dialog):
	def __init__(self, parent, event_data=None):
		super().__init__(parent, title="Edit Acara" if event_data else "Tambah Acara Baru", size=(400, 350))
		self.event_data = event_data or {}
		
		sizer = wx.BoxSizer(wx.VERTICAL)
		
		hz1 = wx.BoxSizer(wx.HORIZONTAL)
		hz1.Add(wx.StaticText(self, label="Nama Acara:"), 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
		self.txt_title = wx.TextCtrl(self, value=self.event_data.get("title", ""))
		hz1.Add(self.txt_title, 1, wx.ALL, 5)
		sizer.Add(hz1, 0, wx.EXPAND)
		
		hz2 = wx.BoxSizer(wx.HORIZONTAL)
		hz2.Add(wx.StaticText(self, label="Tipe Acara:"), 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
		self.rb_onetime = wx.RadioButton(self, label="Sekali Jalan", style=wx.RB_GROUP)
		self.rb_yearly = wx.RadioButton(self, label="Tahunan (Setiap Tahun)")
		
		if self.event_data.get("type") == "yearly":
			self.rb_yearly.SetValue(True)
		else:
			self.rb_onetime.SetValue(True)
			
		hz2.Add(self.rb_onetime, 0, wx.ALL, 5)
		hz2.Add(self.rb_yearly, 0, wx.ALL, 5)
		sizer.Add(hz2, 0, wx.EXPAND)
		
		hz3 = wx.BoxSizer(wx.HORIZONTAL)
		hz3.Add(wx.StaticText(self, label="Tanggal (YYYY-MM-DD atau MM-DD):"), 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
		import datetime
		default_date = self.event_data.get("date", datetime.datetime.now().strftime("%Y-%m-%d"))
		self.txt_date = wx.TextCtrl(self, value=default_date)
		hz3.Add(self.txt_date, 1, wx.ALL, 5)
		sizer.Add(hz3, 0, wx.EXPAND)
		
		hz4 = wx.BoxSizer(wx.HORIZONTAL)
		hz4.Add(wx.StaticText(self, label="Jam Pengingat (HH:MM):"), 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
		self.txt_time = wx.TextCtrl(self, value=self.event_data.get("time", "09:00"))
		hz4.Add(self.txt_time, 1, wx.ALL, 5)
		sizer.Add(hz4, 0, wx.EXPAND)
		
		hz5 = wx.BoxSizer(wx.HORIZONTAL)
		hz5.Add(wx.StaticText(self, label="Peringatan Dini (Briefing):"), 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
		self.cb_reminder = wx.ComboBox(self, choices=["Hanya Hari H", "H-1 (Besok)", "H-7 (Minggu Depan)", "1 Bulan Sebelumnya"], style=wx.CB_READONLY)
		
		rem = str(self.event_data.get("reminder", "0"))
		if rem == "1": self.cb_reminder.SetSelection(1)
		elif rem == "7": self.cb_reminder.SetSelection(2)
		elif rem == "30": self.cb_reminder.SetSelection(3)
		else: self.cb_reminder.SetSelection(0)
		hz5.Add(self.cb_reminder, 1, wx.ALL, 5)
		sizer.Add(hz5, 0, wx.EXPAND)
		
		btnSizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
		sizer.Add(btnSizer, 0, wx.EXPAND | wx.ALL, 10)
		
		self.SetSizer(sizer)
		self.Centre()
		
	def get_data(self):
		sel = self.cb_reminder.GetSelection()
		rem_val = 0
		if sel == 1: rem_val = 1
		elif sel == 2: rem_val = 7
		elif sel == 3: rem_val = 30
		
		return {
			"title": self.txt_title.GetValue().strip(),
			"type": "yearly" if self.rb_yearly.GetValue() else "one-time",
			"date": self.txt_date.GetValue().strip(),
			"time": self.txt_time.GetValue().strip(),
			"reminder": rem_val,
			"is_completed": False
		}
"""
content += "\n" + dialog_code

# Add refreshEvents and load config in JadwalKuDialog.__init__
content = content.replace("self.refreshList()", "self.refreshList()\n\t\tself.refreshEvents()\n\t\tevt_cfg = self.config.get_events_config()\n\t\tself.chk_briefing.SetValue(evt_cfg.get('briefing_enabled', True))\n\t\tself.sp_briefing.SetValue(int(evt_cfg.get('briefing_hour', 7)))")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Patched!")
