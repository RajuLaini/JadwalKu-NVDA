# -*- coding: UTF-8 -*-
import wx
import datetime
import logHandler
import ui
import os
import random

class Scheduler:
	def __init__(self, config_manager, audio_manager, tts_manager=None):
		self.config = config_manager
		self.audio = audio_manager
		self.tts_manager = tts_manager
		self.timer = wx.Timer()
		self.timer.Bind(wx.EVT_TIMER, self.on_tick)
		self.last_check_minute = -1
		self.quick_timers = []
		self.one_time_alarms = []

	def start(self):
		self.timer.Start(1000)
		logHandler.log.info("JadwalKu: Scheduler background timer dimulai (tiap 1 detik).")

	def stop(self):
		if self.timer.IsRunning():
			self.timer.Stop()
		logHandler.log.info("JadwalKu: Scheduler berhenti.")

	def add_quick_timer(self, duration, unit, audio_file, prep_seconds=0):
		now = datetime.datetime.now()
		if unit == "Detik":
			dur_sec = duration
		elif unit == "Jam":
			dur_sec = duration * 3600
		else:  # "Menit" (default)
			dur_sec = duration * 60

		if prep_seconds > 0:
			prep_trigger_time = now + datetime.timedelta(seconds=prep_seconds)
			item = {
				"state": "prep",
				"prep_trigger_time": prep_trigger_time,
				"dur_sec": dur_sec,
				"duration": duration,
				"unit": unit,
				"audio_file": audio_file,
				"last_prep_announced": -1
			}
			self.quick_timers.append(item)
			ui.message(f"Hitung mundur persiapan {prep_seconds} detik dimulai sebelum Timer {duration} {unit} berjalan.")
		else:
			trigger_time = now + datetime.timedelta(seconds=dur_sec)
			item = {
				"state": "running",
				"trigger_time": trigger_time,
				"duration": duration,
				"unit": unit,
				"audio_file": audio_file
			}
			self.quick_timers.append(item)
			ui.message(f"Timer {duration} {unit} dimulai. Akan berbunyi pada {trigger_time.strftime('%H:%M:%S')}.")
		return item

	def check_quick_timers(self, now):
		if not self.quick_timers:
			return
		remaining = []
		for item in self.quick_timers:
			if item.get("state", "running") == "prep":
				diff_prep = (item["prep_trigger_time"] - now).total_seconds()
				if diff_prep <= 0:
					try:
						if hasattr(self.audio, "play_sound"):
							self.audio.play_sound("chime.wav", allow_overlap=True)
					except Exception:
						pass
					item["state"] = "running"
					item["trigger_time"] = now + datetime.timedelta(seconds=item["dur_sec"])
					ui.message(f"Ding! Timer {item['duration']} {item['unit']} sesungguhnya dimulai!")
					remaining.append(item)
				else:
					sec_left = int(diff_prep) + 1
					if sec_left != item.get("last_prep_announced", -1):
						item["last_prep_announced"] = sec_left
						if 1 <= sec_left <= 10:
							self.play_random_clock_tick()
							if sec_left <= 5:
								ui.message(str(sec_left))
						elif sec_left % 10 == 0:
							ui.message(f"{sec_left} detik lagi sebelum mulai")
					remaining.append(item)
			else:
				diff_sec = (item["trigger_time"] - now).total_seconds()
				if diff_sec <= 0:
					title = "Timer JadwalKu Habis!"
					msg = f"Timer {item['duration']} {item['unit']} telah selesai."
					self.audio.notify(title, msg, speech_enabled=True, audio_enabled=True, audio_file=item["audio_file"], is_alarm=True)
				else:
					sec_left = int(diff_sec) + 1
					if 1 <= sec_left <= 10 and sec_left != item.get("last_ticked_sec", -1):
						item["last_ticked_sec"] = sec_left
						self.play_random_clock_tick()
					remaining.append(item)
		self.quick_timers = remaining

	def play_random_clock_tick(self):
		try:
			if not hasattr(self.audio, "play_sound"):
				return
			s_dir = os.path.join(os.path.dirname(__file__), "sounds", "WaitingClock")
			if os.path.exists(s_dir):
				files = [f for f in sorted(os.listdir(s_dir)) if f.lower().endswith((".mp3", ".wav"))]
				if files:
					chosen = random.choice(files)
					rel_path = os.path.join("WaitingClock", chosen)
					self.audio.play_sound(rel_path)
		except Exception as e:
			logHandler.log.error(f"JadwalKu: Error memutar suara hitung mundur WaitingClock: {e}")

	def add_one_time_alarm(self, hour, minute, second, audio_file, is_alarm=True):
		now = datetime.datetime.now()
		target = now.replace(hour=hour, minute=minute, second=second, microsecond=0)
		if target <= now:
			target += datetime.timedelta(days=1)
		item = {
			"trigger_time": target,
			"audio_file": audio_file,
			"is_alarm": is_alarm,
			"time_str": f"{hour:02d}:{minute:02d}:{second:02d}"
		}
		self.one_time_alarms.append(item)
		ui.message(f"Alarm sekali pakai dipasang untuk pukul {item['time_str']} ({target.strftime('%d-%m-%Y')}).")
		return item

	def check_one_time_alarms(self, now):
		if not self.one_time_alarms:
			return
		remaining = []
		for item in self.one_time_alarms:
			if now >= item["trigger_time"]:
				title = "Alarm Sekali Pakai JadwalKu!"
				msg = f"Waktu alarm pukul {item['time_str']} telah tiba."
				self.audio.notify(title, msg, speech_enabled=True, audio_enabled=True, audio_file=item["audio_file"], is_alarm=item.get("is_alarm", True))
			else:
				remaining.append(item)
		self.one_time_alarms = remaining

	def on_tick(self, event):
		try:
			now = datetime.datetime.now()
			self.check_quick_timers(now)
			self.check_one_time_alarms(now)
			if hasattr(self.audio, "check_snoozed_alarms"):
				self.audio.check_snoozed_alarms(now)

			# Pengecekan hanya dilakukan tepat satu kali saat menit berganti untuk agenda rutin & time reminder
			if now.minute == self.last_check_minute:
				return
			self.last_check_minute = now.minute

			self.check_time_reminder(now)
			self.check_schedules(now)
		except Exception as e:
			logHandler.log.error(f"JadwalKu: Error di dalam scheduler on_tick: {e}")

	def check_time_reminder(self, now):
		try:
			time_cfg = self.config.get_time_reminder_config()
			if not time_cfg.get("enabled", False):
				return

			# Cek rentang jam aktif
			start_h = int(time_cfg.get("start_hour", 0))
			end_h = int(time_cfg.get("end_hour", 23))
			if start_h <= end_h:
				if not (start_h <= now.hour <= end_h):
					return
			else:
				# Melewati tengah malam (misal 21:00 sampai 06:00)
				if not (now.hour >= start_h or now.hour <= end_h):
					return

			interval = int(time_cfg.get("interval", 60))
			if interval <= 0:
				interval = 60

			# Cek apakah menit saat ini merupakan kelipatan interval
			is_trigger_time = False
			if interval == 60:
				if now.minute == 0:
					is_trigger_time = True
			else:
				if now.minute % interval == 0:
					is_trigger_time = True

			if not is_trigger_time:
				return

			# Cek deduplikasi (agar tidak memicu ulang pada menit yang sama)
			current_trigger_key = now.strftime("%Y-%m-%d %H:%M")
			if time_cfg.get("last_triggered_minute") == current_trigger_key:
				return

			# Update record agar tidak trigger berulang
			time_cfg["last_triggered_minute"] = current_trigger_key
			self.config.update_time_reminder_config(time_cfg)

			mode = time_cfg.get("mode", "both")
			if mode in ("both", "audio"):
				self.audio.play_sound("chime.wav")

			if mode in ("both", "speech"):
				# Siapkan kalimat waktu berdasarkan gaya pengucapan yang dipilih
				speech_style = time_cfg.get("speech_style", "default")
				if speech_style == "follow_f12":
					# Ikuti persis format dari NVDA+F12 (time_settings)
					t_set = self.config.get_time_settings() if self.config else {}
					is_24 = t_set.get("time_format", "24") == "24"
					f12_style = t_set.get("time_speech_style", "default")
					inc_sec = t_set.get("include_seconds", False) or f12_style in ("full_seconds", "with_seconds")
					
					if is_24:
						h_str = f"{now.hour:02d}"
						ampm = ""
					else:
						h_12 = now.hour % 12 or 12
						ampm = " AM" if now.hour < 12 else " PM"
						h_str = f"{h_12:02d}"
					m_str = f"{now.minute:02d}"
					s_str = f"{now.second:02d}"
					
					if f12_style == "only_time":
						time_str = f"{h_str}:{m_str}:{s_str}{ampm}" if inc_sec else f"{h_str}:{m_str}{ampm}"
					elif f12_style == "prefix_pukul":
						time_str = f"Waktu sekarang pukul {h_str}:{m_str}:{s_str}{ampm}" if inc_sec else f"Waktu sekarang pukul {h_str}:{m_str}{ampm}"
					elif f12_style == "with_seconds":
						time_str = f"Pukul {h_str}:{m_str}{ampm} lewat {now.second} detik"
					elif f12_style == "full_seconds":
						time_str = f"Waktu sekarang pukul {h_str}:{m_str}:{s_str}{ampm}"
					else:
						time_str = f"{h_str}:{m_str}:{s_str}{ampm} waktu sekarang" if inc_sec else f"{h_str}:{m_str}{ampm} waktu sekarang"
				elif speech_style == "only_time":
					t_set = self.config.get_time_settings() if self.config else {}
					is_24 = t_set.get("time_format", "24") == "24"
					if is_24:
						time_str = f"{now.hour:02d}:{now.minute:02d}"
					else:
						h_12 = now.hour % 12 or 12
						ampm = " AM" if now.hour < 12 else " PM"
						time_str = f"{h_12:02d}:{now.minute:02d}{ampm}"
				elif speech_style == "waktu_sekarang":
					time_str = f"{now.hour:02d}:{now.minute:02d} waktu sekarang"
				elif speech_style == "prefix_pukul":
					time_str = f"Waktu sekarang pukul {now.hour:02d}:{now.minute:02d}"
				elif speech_style == "pukul_tepat":
					if now.minute == 0:
						time_str = f"Pukul {now.hour:02d}:00 tepat"
					else:
						time_str = f"Pukul {now.hour:02d}:{now.minute:02d}"
				else:
					# default
					if now.minute == 0:
						time_str = f"Sekarang jam {now.strftime('%H:00')} tepat"
					else:
						time_str = f"Sekarang jam {now.strftime('%H:%M')}"
				
				def speak_reminder():
					if hasattr(self, "tts_manager") and self.tts_manager and self.tts_manager.is_enabled():
						self.tts_manager.speak(time_str)
					else:
						ui.message(time_str)

				# Jika audio dan bicara menyala, beri sedikit jeda agar tidak bertabrakan dengan chime
				if mode == "both":
					wx.CallLater(350, speak_reminder)
				else:
					speak_reminder()

		except Exception as e:
			logHandler.log.error(f"JadwalKu: Error saat cek time reminder: {e}")

	def check_schedules(self, now):
		try:
			schedules = self.config.get_schedules()
			today_date_str = now.strftime("%Y-%m-%d")
			weekday = now.weekday() # 0 = Senin, ..., 6 = Minggu
			days_map = {0: "Senin", 1: "Selasa", 2: "Rabu", 3: "Kamis", 4: "Jumat", 5: "Sabtu", 6: "Minggu"}

			for agenda in schedules:
				if not agenda.get("active", False):
					continue

				if int(agenda.get("minute", -1)) != now.minute:
					continue

				start_hour = int(agenda.get("hour", -1))
				interval_hour = int(agenda.get("interval_hour", 0))
				interval_end_hour = int(agenda.get("interval_end_hour", 23))

				if interval_hour > 0:
					if start_hour <= interval_end_hour:
						if now.hour < start_hour or now.hour > interval_end_hour or (now.hour - start_hour) % interval_hour != 0:
							continue
					else:  # Lintas malam / overnight (misal start_hour=20, interval_end_hour=04)
						if now.hour >= start_hour:
							if (now.hour - start_hour) % interval_hour != 0:
								continue
						elif now.hour <= interval_end_hour:
							if ((now.hour + 24) - start_hour) % interval_hour != 0:
								continue
						else:
							continue
				else:
					if start_hour != now.hour:
						continue

				freq = agenda.get("frequency", "Setiap Hari")
				match = False

				if freq == "Setiap Hari":
					match = True
				elif freq == days_map.get(weekday):
					match = True
				elif freq == "Hari Kerja (Senin - Jumat)" and 0 <= weekday <= 4:
					match = True
				elif freq == "Akhir Pekan (Sabtu - Minggu)" and weekday in (5, 6):
					match = True
				elif freq.startswith("Sesuaikan Hari") or agenda.get("custom_days"):
					custom_days = agenda.get("custom_days", [])
					if days_map.get(weekday) in custom_days:
						match = True
				elif freq == "Sekali Waktu (Tanggal Spesifik)":
					target_date = agenda.get("date", "")
					if target_date == today_date_str:
						match = True

				trigger_key = f"{today_date_str}_{now.hour:02d}:{now.minute:02d}" if interval_hour > 0 else today_date_str
				if match and agenda.get("last_triggered_date") != trigger_key:
					agenda["last_triggered_date"] = trigger_key
					self.config.update_schedule(agenda["id"], agenda)

					title = "Pengingat JadwalKu"
					msg = agenda.get("name", "Agenda Waktunya Tiba")
					speech = agenda.get("speech_enabled", True)
					audio = agenda.get("audio_enabled", True)
					a_file = agenda.get("audio_file", "chime.wav")
					is_alarm = agenda.get("is_alarm", False)

					self.audio.notify(title, msg, speech_enabled=speech, audio_enabled=audio, audio_file=a_file, is_alarm=is_alarm)

		except Exception as e:
			logHandler.log.error(f"JadwalKu: Error saat cek schedule agenda: {e}")
