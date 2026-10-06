import re

filepath = r"C:\Users\Raju Laini\Documents\Project_Jadwalku\JadwalKu\globalPlugins\jadwalku\scheduler.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# We want to extract the briefing logic into a new method `get_todays_events(self, now)`
# Let's see the current check_events code.
start_str = "events_today = []\n\t\t\t\t\tfor evt in events:"
end_str = "if events_today:\n\t\t\t\t\t\tgreeting = f\"Selamat pagi."

if start_str in content and end_str in content:
    # We will inject the new method `get_todays_events` before `check_events`
    new_method = """	def get_todays_events(self, now):
		import datetime
		events = self.config.data.get("events", [])
		events_today = []
		for evt in events:
			if evt.get("is_completed", False): continue
			evt_type = evt.get("type", "one-time")
			evt_date = evt.get("date", "")
			reminder = int(evt.get("reminder", 0))
			
			try:
				evt_title = evt.get('title', '')
				parts = evt_date.split("-")
				base_year = None
				
				if evt_type == "one-time":
					evt_dt_obj = datetime.datetime.strptime(evt_date, "%Y-%m-%d").date()
				else:
					if len(parts) == 3:
						base_year = int(parts[0])
						m, d = int(parts[1]), int(parts[2])
					elif len(parts) == 2:
						m, d = int(parts[0]), int(parts[1])
					else:
						continue
						
					dt_obj = datetime.date(now.year, m, d)
					if dt_obj < now.date():
						evt_dt_obj = datetime.date(now.year + 1, m, d)
					else:
						evt_dt_obj = dt_obj
						
					if base_year is not None:
						ke = evt_dt_obj.year - base_year
						if ke > 0:
							evt_title += f" yang ke-{ke}"
						
				diff_days = (evt_dt_obj - now.date()).days
				if diff_days < 0:
					continue
					
				should_brief = False
				brief_msg = ""
				
				if reminder == 0:
					if diff_days == 0:
						should_brief = True
						brief_msg = f"hari ini, {evt_title}"
				elif reminder == 1:
					if diff_days >= 0:
						should_brief = True
						if diff_days == 0:
							brief_msg = f"hari ini, {evt_title}"
						elif diff_days == 1:
							brief_msg = f"besok, {evt_title}"
						else:
							brief_msg = f"{diff_days} hari lagi, {evt_title}"
				elif reminder == 7:
					if diff_days >= 0 and diff_days % 7 == 0:
						should_brief = True
						if diff_days == 0:
							brief_msg = f"hari ini, {evt_title}"
						elif diff_days == 7:
							brief_msg = f"minggu depan, {evt_title}"
						else:
							weeks = diff_days // 7
							brief_msg = f"{weeks} minggu lagi, {evt_title}"
				elif reminder == 30:
					if diff_days >= 0 and now.day == evt_dt_obj.day:
						should_brief = True
						if diff_days == 0:
							brief_msg = f"hari ini, {evt_title}"
						else:
							m_diff = (evt_dt_obj.year - now.year) * 12 + (evt_dt_obj.month - now.month)
							if m_diff == 1:
								brief_msg = f"bulan depan, {evt_title}"
							else:
								brief_msg = f"{m_diff} bulan lagi, {evt_title}"
								
				if should_brief:
					events_today.append(brief_msg)
			except Exception:
				continue
		return events_today

"""
    # Let's replace the logic inside check_events
    replacement_str = "events_today = self.get_todays_events(now)\n\t\t\t\t\t" + end_str
    
    # We need to extract the exact block to replace
    idx_start = content.find(start_str)
    idx_end = content.find(end_str)
    
    if idx_start != -1 and idx_end != -1:
        block_to_replace = content[idx_start:idx_end+len(end_str)]
        new_content = content.replace(block_to_replace, replacement_str)
        
        # Inject new_method before check_events
        idx_check_events = new_content.find("\tdef check_events(self, now):")
        new_content = new_content[:idx_check_events] + new_method + new_content[idx_check_events:]
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("Updated scheduler.py to extract get_todays_events.")
    else:
        print("Could not find the block to replace.")
