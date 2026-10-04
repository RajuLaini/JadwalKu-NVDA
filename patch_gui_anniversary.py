import re

filepath = r"C:\Users\Raju Laini\Documents\Project_Jadwalku\JadwalKu\globalPlugins\jadwalku\guiDialogs.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

old_get_next_date = """
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
				return datetime.date.max"""

new_get_next_date = """
		def get_next_date(evt):
			date_str = evt.get("date", "")
			if not date_str: return datetime.date.max
			try:
				if evt.get("type") == "one-time":
					return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
				else:
					parts = date_str.split("-")
					if len(parts) == 3:
						m, d = int(parts[1]), int(parts[2])
					elif len(parts) == 2:
						m, d = int(parts[0]), int(parts[1])
					else:
						return datetime.date.max
					
					dt = datetime.date(now.year, m, d)
					if dt < now.date():
						return datetime.date(now.year + 1, m, d)
					return dt
			except:
				return datetime.date.max"""

content = content.replace(old_get_next_date.strip("\n"), new_get_next_date.strip("\n"))
with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated guiDialogs.py get_next_date.")
