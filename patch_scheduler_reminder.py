import re

filepath = r"C:\Users\Raju Laini\Documents\Project_Jadwalku\JadwalKu\globalPlugins\jadwalku\scheduler.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Replace the briefing logic
old_logic = """
						try:
							if evt_type == "one-time":
								evt_dt = datetime.datetime.strptime(evt_date, "%Y-%m-%d")
							else:
								evt_dt = datetime.datetime.strptime(f"{now.year}-{evt_date}", "%Y-%m-%d")
							
							diff_days = (evt_dt.date() - now.date()).days
							
							if diff_days == 0 and reminder == 0:
								events_today.append(f"hari ini, {evt.get('title')}")
							elif diff_days == 1 and reminder == 1:
								events_today.append(f"besok, {evt.get('title')}")
							elif diff_days == 7 and reminder == 7:
								events_today.append(f"minggu depan, {evt.get('title')}")
							elif reminder == 30:
								next_m = now.month % 12 + 1
								next_y = now.year + (now.month // 12)
								try:
									target_date = datetime.date(next_y, next_m, now.day)
									if evt_dt.date() == target_date:
										events_today.append(f"bulan depan di tanggal yang sama, {evt.get('title')}")
								except ValueError:
									pass
						except Exception:
							continue"""

new_logic = """
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

content = content.replace(old_logic.strip("\n"), new_logic.strip("\n"))
with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated scheduler.py")
