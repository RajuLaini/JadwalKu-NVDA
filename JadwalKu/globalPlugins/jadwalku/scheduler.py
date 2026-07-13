# -*- coding: UTF-8 -*-
import wx
import datetime
import logHandler
import ui
import os
import random

class Scheduler:
	def __init__(self, config_manager, audio_manager):
		self.config = config_manager
		self.audio = audio_manager
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

	def add_quick_timer(self, duration, unit, audio_file):
		now = datetime.datetime.now()
		if unit == "Detik":
			delta = datetime.timedelta(seconds=duration)
		elif unit == "Jam":
			delta = datetime.timedelta(hours=duration)
		else:  # "Menit" (default)
			delta = datetime.timedelta(minutes=duration)
		trigger_time = now + delta
		item = {
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
				# Siapkan kalimat waktu
				if now.minute == 0:
					time_str = f"Sekarang jam {now.strftime('%H:00')} tepat"
				else:
					time_str = f"Sekarang jam {now.strftime('%H:%M')}"
				
				# Jika audio dan bicara menyala, beri sedikit jeda agar tidak bertabrakan dengan chime
				if mode == "both":
					wx.CallLater(350, ui.message, time_str)
				else:
					ui.message(time_str)

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

				if int(agenda.get("hour", -1)) != now.hour or int(agenda.get("minute", -1)) != now.minute:
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

				if match and agenda.get("last_triggered_date") != today_date_str:
					agenda["last_triggered_date"] = today_date_str
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
