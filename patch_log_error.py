import re
filepath = r"C:\Users\Raju Laini\Documents\Project_Jadwalku\JadwalKu\globalPlugins\jadwalku\scheduler.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

old_except = """
								evt["last_triggered_date"] = today_str
								# Jika one-time, tandai selesai
								if evt_type == "one-time":
									evt["is_completed"] = True
								self.config.save_data()
					except Exception:
						pass"""

new_except = """
								evt["last_triggered_date"] = today_str
								# Jika one-time, tandai selesai
								if evt_type == "one-time":
									evt["is_completed"] = True
								self.config.save_data()
					except Exception as e:
						from .logger import jk_log
						jk_log.error(f"Error in time trigger: {e}")"""

if old_except in content:
    content = content.replace(old_except, new_except)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print("Injected logging into time trigger block.")
else:
    print("Could not find the except block.")
