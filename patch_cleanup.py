import re
filepath = r"C:\Users\Raju Laini\Documents\Project_Jadwalku\JadwalKu\globalPlugins\jadwalku\scheduler.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# First, modify get_todays_events to append time
old_get_todays = """				if base_year is not None:
						ke = evt_dt_obj.year - base_year
						if ke > 0:
							evt_title += f" yang ke-{ke}"
						
				diff_days = (evt_dt_obj - now.date()).days"""

new_get_todays = """				if base_year is not None:
						ke = evt_dt_obj.year - base_year
						if ke > 0:
							evt_title += f" yang ke-{ke}"
							
				evt_time = evt.get("time", "")
				if evt_time and evt_time != "00:00":
					evt_title += f", pada jam {evt_time}"
						
				diff_days = (evt_dt_obj - now.date()).days"""

content = content.replace(old_get_todays, new_get_todays)

# Now, modify check_events to collect events to remove
# We will inject `events_to_remove = []`
# and modify the trigger block.

old_loop_start = """			import datetime
			# 1. Pemicu spesifik waktu
			for evt in events:
				if evt.get("is_completed", False): continue
				evt_time = evt.get("time", "")"""

new_loop_start = """			import datetime
			# 1. Pemicu spesifik waktu
			events_to_remove = []
			for evt in events:
				if evt.get("type", "one-time") == "one-time" and evt.get("date", "") < today_str:
					events_to_remove.append(evt)
					continue
					
				if evt.get("is_completed", False): continue
				evt_time = evt.get("time", "")"""

content = content.replace(old_loop_start, new_loop_start)


old_trigger_block = """							last_triggered = evt.get("last_triggered_date", "")
							if should_trigger and last_triggered != today_str:
								msg = f"Pengingat Acara: {evt.get('title', '')}"
								if self.tts_manager:
									self.tts_manager.speak(msg)
								elif self.audio:
									import ui
									ui.message(msg)
								
								evt["last_triggered_date"] = today_str
								# Jika one-time, tandai selesai
								if evt_type == "one-time":
									evt["is_completed"] = True
								self.config.save_data()
					except Exception as e:
						from .logger import jk_log
						jk_log.error(f"Error in time trigger: {e}")"""

new_trigger_block = """							last_triggered = evt.get("last_triggered_date", "")
							if should_trigger and last_triggered != today_str:
								msg = f"Pengingat Acara: {evt.get('title', '')}"
								if self.tts_manager:
									self.tts_manager.speak(msg)
								elif self.audio:
									import ui
									ui.message(msg)
								
								if evt_type == "one-time":
									events_to_remove.append(evt)
								else:
									evt["last_triggered_date"] = today_str
									self.config.save_data()
					except Exception as e:
						from .logger import jk_log
						jk_log.error(f"Error in time trigger: {e}")
			
			if events_to_remove:
				for e in events_to_remove:
					if e in events:
						events.remove(e)
				self.config.save_data()"""

content = content.replace(old_trigger_block, new_trigger_block)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated scheduler.py for time announcement and event cleanup.")
