import os
import re

path = r'C:\Users\Raju Laini\Documents\Project_Jadwalku\JadwalKu\globalPlugins\jadwalku\scheduler.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace self.daily_overrides = {} with persistent logic
target1 = r"self\.daily_overrides = \{\}"
replacement1 = """if "daily_overrides" not in self.config.data:
			self.config.data["daily_overrides"] = {}
		self.daily_overrides = self.config.data["daily_overrides"]"""
content = re.sub(target1, replacement1, content)

# Fix snooze_schedule to save config
target2 = r"def snooze_schedule\(self, sched_id, new_time\):\n\s*self\.daily_overrides\[sched_id\] = \{\"hour\": new_time\.hour, \"minute\": new_time\.minute\}"
replacement2 = """def snooze_schedule(self, sched_id, new_time):
		self.daily_overrides[sched_id] = {"hour": new_time.hour, "minute": new_time.minute}
		self.config.data["daily_overrides"] = self.daily_overrides
		self.config.save_data()"""
content = re.sub(target2, replacement2, content)

# Also fix the timer drift issue by checking a range of 2 minutes instead of exact match
target_drift1 = r"if eff_minute != now\.minute:\n\s*continue"
replacement_drift1 = """diff_minutes = (now.hour * 60 + now.minute) - (eff_start_hour * 60 + eff_minute)
				if diff_minutes < 0 or diff_minutes > 1: # Toleransi keterlambatan 1 menit (anti-drift)
					continue"""
content = re.sub(target_drift1, replacement_drift1, content)

# Wait, if I replace that, I also need to remove the exact hour check!
target_drift2 = r"if eff_start_hour != now\.hour:\n\s*continue"
replacement_drift2 = """pass # Hour is already checked by diff_minutes above"""
content = re.sub(target_drift2, replacement_drift2, content)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("scheduler.py patched!")
