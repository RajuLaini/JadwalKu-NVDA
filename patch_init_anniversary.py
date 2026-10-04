import re

filepath = r"C:\Users\Raju Laini\Documents\Project_Jadwalku\JadwalKu\globalPlugins\jadwalku\__init__.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

old_report = """
		events_today = []
		for evt in events:
			if evt.get("is_completed", False): continue
			evt_type = evt.get("type", "one-time")
			evt_date = evt.get("date", "")
			
			if evt_type == "one-time" and evt_date == today_str:
				events_today.append(evt.get("title", ""))
			elif evt_type == "yearly" and evt_date == now.strftime("%m-%d"):
				events_today.append(evt.get("title", ""))"""

new_report = """
		events_today = []
		for evt in events:
			if evt.get("is_completed", False): continue
			evt_type = evt.get("type", "one-time")
			evt_date = evt.get("date", "")
			evt_title = evt.get("title", "")
			
			try:
				if evt_type == "one-time":
					if evt_date == today_str:
						events_today.append(evt_title)
				else:
					parts = evt_date.split("-")
					if len(parts) == 3:
						base_year = int(parts[0])
						m, d = int(parts[1]), int(parts[2])
					elif len(parts) == 2:
						base_year = None
						m, d = int(parts[0]), int(parts[1])
					else:
						continue
					
					if m == now.month and d == now.day:
						if base_year is not None:
							ke = now.year - base_year
							if ke > 0:
								evt_title += f" yang ke-{ke}"
						events_today.append(evt_title)
			except Exception:
				continue"""

content = content.replace(old_report.strip("\n"), new_report.strip("\n"))
with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated __init__.py with anniversary calculation.")
