import re

filepath = r"C:\Users\Raju Laini\Documents\Project_Jadwalku\JadwalKu\globalPlugins\jadwalku\scheduler.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Replace the date parsing and calculation logic inside check_events
# We also need to fix exact time trigger logic.

# In exact time trigger:
# elif evt_type == "yearly" and evt_date == now.strftime("%m-%d"): -> this assumes evt_date is MM-DD.
# If evt_date is YYYY-MM-DD, it will never trigger.

# Let's fix exact time first
old_time_trigger = """
							if evt_type == "one-time" and evt_date == today_str:
								should_trigger = True
							elif evt_type == "yearly" and evt_date == now.strftime("%m-%d"):
								should_trigger = True"""

new_time_trigger = """
							if evt_type == "one-time" and evt_date == today_str:
								should_trigger = True
							elif evt_type == "yearly":
								# Handle both YYYY-MM-DD and MM-DD
								if evt_date.endswith(now.strftime("%m-%d")):
									should_trigger = True"""

content = content.replace(old_time_trigger, new_time_trigger)

# Now fix briefing logic
old_briefing = """
						try:
							if evt_type == "one-time":
								evt_dt_obj = datetime.datetime.strptime(evt_date, "%Y-%m-%d").date()
							else:
								dt_obj = datetime.datetime.strptime(f"{now.year}-{evt_date}", "%Y-%m-%d").date()
								if dt_obj < now.date():
									evt_dt_obj = datetime.date(now.year + 1, dt_obj.month, dt_obj.day)
								else:
									evt_dt_obj = dt_obj
									
							diff_days = (evt_dt_obj - now.date()).days
							if diff_days < 0:
								continue
								
							should_brief = False
							brief_msg = ""
							
							if reminder == 0:
								if diff_days == 0:
									should_brief = True
									brief_msg = f"hari ini, {evt.get('title')}"
							elif reminder == 1:
								if diff_days >= 0:
									should_brief = True
									if diff_days == 0:
										brief_msg = f"hari ini, {evt.get('title')}"
									elif diff_days == 1:
										brief_msg = f"besok, {evt.get('title')}"
									else:
										brief_msg = f"{diff_days} hari lagi, {evt.get('title')}"
							elif reminder == 7:
								if diff_days >= 0 and diff_days % 7 == 0:
									should_brief = True
									if diff_days == 0:
										brief_msg = f"hari ini, {evt.get('title')}"
									elif diff_days == 7:
										brief_msg = f"minggu depan, {evt.get('title')}"
									else:
										weeks = diff_days // 7
										brief_msg = f"{weeks} minggu lagi, {evt.get('title')}"
							elif reminder == 30:
								if diff_days >= 0 and now.day == evt_dt_obj.day:
									should_brief = True
									if diff_days == 0:
										brief_msg = f"hari ini, {evt.get('title')}"
									else:
										m_diff = (evt_dt_obj.year - now.year) * 12 + (evt_dt_obj.month - now.month)
										if m_diff == 1:
											brief_msg = f"bulan depan, {evt.get('title')}"
										else:
											brief_msg = f"{m_diff} bulan lagi, {evt.get('title')}"
											
							if should_brief:
								events_today.append(brief_msg)
						except Exception:
							continue"""

new_briefing = """
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
							continue"""

content = content.replace(old_briefing.strip("\n"), new_briefing.strip("\n"))
with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated scheduler.py with anniversary calculation.")
