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

	def pause_quick_timer(self, index):
		if 0 <= index < len(self.quick_timers):
			item = self.quick_timers[index]
			if item.get("state") in ("running", "prep"):
				now = datetime.datetime.now()
				if item.get("state") == "prep":
					diff = (item["prep_trigger_time"] - now).total_seconds()
				else:
					diff = (item["trigger_time"] - now).total_seconds()
				item["paused_remaining_seconds"] = diff
				item["state"] = "paused"
				ui.message(f"Timer {item['duration']} {item['unit']} dijeda sementara.")

	def resume_quick_timer(self, index):
		if 0 <= index < len(self.quick_timers):
			item = self.quick_timers[index]
			if item.get("state") == "paused":
				now = datetime.datetime.now()
				if "paused_remaining_seconds" in item:
					# Restore as running
					item["state"] = "running"
					item["trigger_time"] = now + datetime.timedelta(seconds=item["paused_remaining_seconds"])
				ui.message(f"Timer {item['duration']} {item['unit']} dilanjutkan.")

	def stop_quick_timer(self, index):
		if 0 <= index < len(self.quick_timers):
			item = self.quick_timers.pop(index)
			ui.message(f"Timer {item['duration']} {item['unit']} dibatalkan.")

	def check_quick_timers(self, now):
		if not self.quick_timers:
			return
		remaining = []
		for item in self.quick_timers:
			if item.get("state") == "paused":
				remaining.append(item)
				continue
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

	def pause_one_time_alarm(self, index):
		if 0 <= index < len(self.one_time_alarms):
			item = self.one_time_alarms[index]
			if item.get("state") != "paused":
				item["state"] = "paused"
				ui.message(f"Alarm pukul {item['time_str']} dinonaktifkan sementara.")

	def resume_one_time_alarm(self, index):
		if 0 <= index < len(self.one_time_alarms):
			item = self.one_time_alarms[index]
			if item.get("state") == "paused":
				item["state"] = "active"
				now = datetime.datetime.now()
				# If the time has passed while it was paused, shift to tomorrow
				if item["trigger_time"] <= now:
					item["trigger_time"] += datetime.timedelta(days=1)
				ui.message(f"Alarm pukul {item['time_str']} diaktifkan kembali.")

	def stop_one_time_alarm(self, index):
		if 0 <= index < len(self.one_time_alarms):
			item = self.one_time_alarms.pop(index)
			ui.message(f"Alarm pukul {item['time_str']} dibatalkan sepenuhnya.")

	def check_one_time_alarms(self, now):
		if not self.one_time_alarms:
			return
		remaining = []
		for item in self.one_time_alarms:
			if item.get("state") == "paused":
				remaining.append(item)
				continue
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

			# Cek rentang jam aktif dalam satuan menit (agar akurat sampai menit)
			start_h = int(time_cfg.get("start_hour", 0))
			end_h = int(time_cfg.get("end_hour", 24))
			
			now_minutes = now.hour * 60 + now.minute
			start_minutes = start_h * 60
			if end_h >= 24:
				end_minutes = 24 * 60 - 1 # 23:59 (Sepanjang Hari)
			else:
				end_minutes = end_h * 60 # tepat pada HH:00
				
			if start_minutes <= end_minutes:
				if not (start_minutes <= now_minutes <= end_minutes):
					return
			else:
				# Melewati tengah malam (misal 21:00 sampai 06:00)
				if not (now_minutes >= start_minutes or now_minutes <= end_minutes):
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
				# Tentukan format 12 vs 24 jam dan gaya pengucapan
				speech_style = time_cfg.get("speech_style", "default")
				chosen_format = time_cfg.get("time_format", "24")
				t_set = self.config.get_time_settings() if self.config else {}
				
				if chosen_format == "follow_f12" or speech_style == "follow_f12":
					is_24 = t_set.get("time_format", "24") == "24"
				else:
					is_24 = chosen_format == "24"
				
				# Siapkan string jam dan AM/PM
				if is_24:
					h_str = f"{now.hour:02d}"
					ampm = ""
				else:
					h_12 = now.hour % 12 or 12
					ampm = " AM" if now.hour < 12 else " PM"
					h_str = f"{h_12:02d}"
				
				m_str = f"{now.minute:02d}"
				s_str = f"{now.second:02d}"
				
				if speech_style == "follow_f12":
					f12_style = t_set.get("time_speech_style", "default")
					inc_sec = t_set.get("include_seconds", False) or f12_style in ("full_seconds", "with_seconds")
					if f12_style == "only_time":
						time_str = f"{h_str}:{m_str}:{s_str}{ampm}" if inc_sec else f"{h_str}:{m_str}{ampm}"
					elif f12_style == "prefix_pukul":
						time_str = f"Waktu sekarang pukul {h_str}:{m_str}:{s_str}{ampm}" if inc_sec else f"Waktu sekarang pukul {h_str}:{m_str}{ampm}"
					elif f12_style == "with_seconds":
						time_str = f"Pukul {h_str}:{m_str}{ampm} lewat {now.second} detik"
					elif f12_style == "full_seconds":
						time_str = f"Waktu sekarang pukul {h_str}:{m_str}:{s_str}{ampm}"
					elif f12_style == "jam_lewat_menit":
						time_str = f"Jam {h_str} lewat {m_str} menit{ampm}"
					elif f12_style == "jam_lewat_menit_detik":
						time_str = f"Jam {h_str} lewat {m_str} menit {s_str} detik{ampm}"
					else:
						time_str = f"{h_str}:{m_str}:{s_str}{ampm} waktu sekarang" if inc_sec else f"{h_str}:{m_str}{ampm} waktu sekarang"
				elif speech_style == "only_time":
					time_str = f"{h_str}:{m_str}{ampm}"
				elif speech_style == "waktu_sekarang":
					time_str = f"{h_str}:{m_str}{ampm} waktu sekarang"
				elif speech_style == "prefix_pukul":
					time_str = f"Waktu sekarang pukul {h_str}:{m_str}{ampm}"
				elif speech_style == "pukul_tepat":
					if now.minute == 0:
						time_str = f"Pukul {h_str}:00{ampm} tepat"
					else:
						time_str = f"Pukul {h_str}:{m_str}{ampm}"
				elif speech_style == "jam_lewat_menit":
					time_str = f"Jam {h_str} lewat {m_str} menit{ampm}"
				elif speech_style == "jam_lewat_menit_detik":
					time_str = f"Jam {h_str} lewat {m_str} menit {s_str} detik{ampm}"
				else:
					# default
					if now.minute == 0:
						time_str = f"Sekarang jam {h_str}:00{ampm} tepat"
					else:
						time_str = f"Sekarang jam {h_str}:{m_str}{ampm}"
				
				def speak_reminder():
					active_vp = time_cfg.get("active_voice_pack", "")
					if active_vp:
						# Parse string ke array kata
						import os
						import re
						# Buang ":00" agar tidak dibaca "nol" pada menit pas
						# Hati-hati, JANGAN pakai .replace("am", " am") karena akan memecah kata "jam" menjadi "j am"!
						# (Variabel ampm selalu memiliki spasi sebelumnya: " AM")
						clean_str = time_str.lower().replace(":00", " ").replace(":", " ")
						words = clean_str.split()
						
						vp_files = []
						try:
							from globalPlugins.jadwalku.voicePackManager import VoicePackManager
							vp_mgr = VoicePackManager(os.path.dirname(os.path.abspath(__file__)))
							pack_path = os.path.join(vp_mgr.pack_dir, active_vp)
							if os.path.exists(pack_path):
								temp_dir = vp_mgr.extract_pack_to_temp(pack_path)
								if temp_dir:
									valid = True
									missing_words = []
									for w in words:
										if w.isdigit():
											w = str(int(w)) # hapus leading zero ("09" -> "9")
										wav_path = os.path.join(temp_dir, f"{w}.wav")
										if os.path.exists(wav_path):
											vp_files.append(wav_path)
										else:
											missing_words.append(w)
											
									if missing_words:
										import logHandler
										logHandler.log.warning(f"JadwalKu: Voice Pack kehilangan file berikut, namun tetap diputar: {missing_words}")
											
									if vp_files:
										vp_vol = time_cfg.get("voice_pack_volume", 100)
										self.audio.play_voice_pack_sequence(vp_files, volume_override=vp_vol)
										return
									else:
										import logHandler
										logHandler.log.warning("JadwalKu: Voice Pack tidak memiliki file yang dapat diputar.")
						except Exception as e:
							import logHandler
							logHandler.log.error(f"JadwalKu: Gagal memutar Voice Pack: {e}")

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
