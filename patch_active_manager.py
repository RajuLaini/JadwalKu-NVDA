import re
filepath = r"C:\Users\Raju Laini\Documents\Project_Jadwalku\JadwalKu\globalPlugins\jadwalku\guiDialogs.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

old_timer_init = """class ActiveTimerManagerDialog(wx.Dialog):
	def __init__(self, parent, scheduler):
		super().__init__(parent, title="Manajer Timer Aktif")
		
		mainSizer = wx.BoxSizer(wx.VERTICAL)"""

new_timer_init = """class ActiveTimerManagerDialog(wx.Dialog):
	def __init__(self, parent, scheduler):
		super().__init__(parent, title="Manajer Timer Aktif")
		self.scheduler = scheduler
		
		mainSizer = wx.BoxSizer(wx.VERTICAL)"""

content = content.replace(old_timer_init, new_timer_init)


old_alarm_init = """class ActiveAlarmManagerDialog(wx.Dialog):
	def __init__(self, parent, scheduler):
		super().__init__(parent, title="Manajer Alarm Aktif")
		
		mainSizer = wx.BoxSizer(wx.VERTICAL)"""

new_alarm_init = """class ActiveAlarmManagerDialog(wx.Dialog):
	def __init__(self, parent, scheduler):
		super().__init__(parent, title="Manajer Alarm Aktif")
		self.scheduler = scheduler
		
		mainSizer = wx.BoxSizer(wx.VERTICAL)"""

content = content.replace(old_alarm_init, new_alarm_init)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Fixed missing self.scheduler in ActiveTimerManagerDialog and ActiveAlarmManagerDialog.")
