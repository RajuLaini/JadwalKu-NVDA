import re
import os

filepath = r"C:\Users\Raju Laini\Documents\Project_Jadwalku\JadwalKu\globalPlugins\jadwalku\__init__.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Add kb:e
content = content.replace('"kb:enter": "openLayout",', '"kb:enter": "openLayout",\n\t\t\t"kb:e": "reportEvents",')

# Add script_reportEvents
script_code = """
	def script_reportEvents(self, gesture):
		self.closeCommandsLayer(speak=False)
		
		now = __import__('datetime').datetime.now()
		events = self.config.get_events()
		today_str = now.strftime("%Y-%m-%d")
		
		events_today = []
		for evt in events:
			if evt.get("is_completed", False): continue
			evt_type = evt.get("type", "one-time")
			evt_date = evt.get("date", "")
			
			if evt_type == "one-time" and evt_date == today_str:
				events_today.append(evt.get("title", ""))
			elif evt_type == "yearly" and evt_date == now.strftime("%m-%d"):
				events_today.append(evt.get("title", ""))
				
		if events_today:
			msg = f"Hari ini Anda memiliki {len(events_today)} acara: " + ", ".join(events_today)
		else:
			msg = "Tidak ada acara untuk hari ini."
			
		self.tts.queue_speech(msg)
"""
content += "\n" + script_code

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("init patched!")
