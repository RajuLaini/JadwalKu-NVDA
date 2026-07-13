# -*- coding: UTF-8 -*-
import os
import wave
import threading
import time
import ctypes
import wx
import logHandler
import nvwave
import ui

SOUNDS_DIR = os.path.join(os.path.dirname(__file__), "sounds")

class AlarmNotificationDialog(wx.Dialog):
	def __init__(self, parent, title, message, audio_manager):
		super().__init__(parent, title=title, size=(460, 250), style=wx.DEFAULT_DIALOG_STYLE | wx.STAY_ON_TOP)
		self.audio_manager = audio_manager
		
		sizer = wx.BoxSizer(wx.VERTICAL)
		
		lbl_header = wx.StaticText(self, label="ALARM JADWALKU BERBUNYI!")
		font = lbl_header.GetFont()
		font.SetPointSize(12)
		font.SetWeight(wx.FONTWEIGHT_BOLD)
		lbl_header.SetFont(font)
		sizer.Add(lbl_header, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 15)
		
		lbl_msg = wx.StaticText(self, label=message)
		sizer.Add(lbl_msg, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 10)
		
		btnSizer = wx.BoxSizer(wx.HORIZONTAL)
		self.btnStop = wx.Button(self, label="&Matikan Alarm (Spasi / Enter)")
		self.btnSnooze = wx.Button(self, label="&Tunda / Snooze 10 Menit (Alt+T)")
		
		self.btnStop.Bind(wx.EVT_BUTTON, self.onStop)
		self.btnSnooze.Bind(wx.EVT_BUTTON, self.onSnooze)
		
		btnSizer.Add(self.btnStop, 1, wx.EXPAND | wx.RIGHT, 5)
		btnSizer.Add(self.btnSnooze, 1, wx.EXPAND | wx.LEFT, 5)
		
		sizer.Add(btnSizer, 0, wx.EXPAND | wx.ALL, 15)
		
		self.SetSizer(sizer)
		self.Centre()
		self.btnStop.SetFocus()
		
		self.Bind(wx.EVT_CLOSE, self.onClose)

	def onStop(self, event):
		self.audio_manager.stop_alarm()
		self.Destroy()

	def onSnooze(self, event):
		self.audio_manager.snooze_alarm()
		self.Destroy()

	def onClose(self, event):
		self.audio_manager.stop_alarm()
		self.Destroy()

class AudioManager:
	def __init__(self, config_manager=None):
		self.config = config_manager
		self.last_played_file = None
		self._mp3_alias = "jadwalku_alarm_mp3"
		self._active_wave_outs = set()
		self._active_mp3_aliases = set()
		self._lock = threading.Lock()
		self._is_playing = False
		self.is_alarm_ringing = False
		self.active_alarm_info = None
		self.snoozed_alarms = []

	def has_active_playback(self):
		with self._lock:
			return len(self._active_wave_outs) > 0 or len(self._active_mp3_aliases) > 0

	def has_active_sounds(self):
		with self._lock:
			return len(self._active_wave_outs) > 0 or len(self._active_mp3_aliases) > 0 or self.is_alarm_ringing

	def get_sound_path(self, filename):
		if not filename:
			return None
		path = os.path.join(SOUNDS_DIR, filename)
		if os.path.exists(path):
			return path
		return None

	def get_available_output_devices(self):
		devices = ["Default (Microsoft Sound Mapper)"]
		# Coba dari nvwave terlebih dahulu
		try:
			if hasattr(nvwave, "getOutputDeviceNames"):
				names = nvwave.getOutputDeviceNames()
				if names and len(names) > 1:
					return [str(n) for n in names if n]
		except Exception:
			pass
		
		# Gunakan WinMM API untuk mengambil seluruh speaker aktif pada Windows
		try:
			import ctypes
			class WAVEOUTCAPSW(ctypes.Structure):
				_fields_ = [
					('wMid', ctypes.c_ushort),
					('wPid', ctypes.c_ushort),
					('vDriverVersion', ctypes.c_uint),
					('szPname', ctypes.c_wchar * 32),
					('dwFormats', ctypes.c_ulong),
					('wChannels', ctypes.c_ushort),
					('wReserved1', ctypes.c_ushort),
					('dwSupport', ctypes.c_ulong)
				]
			num = ctypes.windll.winmm.waveOutGetNumDevs()
			for i in range(num):
				caps = WAVEOUTCAPSW()
				res = ctypes.windll.winmm.waveOutGetDevCapsW(i, ctypes.byref(caps), ctypes.sizeof(caps))
				if res == 0:
					name = caps.szPname.strip()
					if name:
						devices.append(f"{i}: {name}")
		except Exception as e:
			logHandler.log.error(f"JadwalKu: Gagal mengambil daftar audio device WinMM: {e}")
			
		return devices

	def get_output_device_id(self):
		if not self.config:
			return getattr(nvwave, "outputDeviceID", -1)
		device_name = self.config.get_audio_device()
		if not device_name or device_name.startswith("Default") or device_name == "Default (Microsoft Sound Mapper)":
			return getattr(nvwave, "outputDeviceID", -1)
		
		# Jika formatnya "0: Speakers (F999X)", ambil angka di depannya
		if ":" in device_name:
			try:
				prefix = device_name.split(":", 1)[0].strip()
				if prefix.lstrip("-").isdigit():
					return int(prefix)
			except Exception:
				pass
		
		try:
			if hasattr(nvwave, "outputDeviceNameToID"):
				return nvwave.outputDeviceNameToID(device_name, True)
			if hasattr(nvwave, "getOutputDeviceNames"):
				names = nvwave.getOutputDeviceNames()
				if device_name in names:
					idx = names.index(device_name)
					return idx - 1 if idx > 0 else -1
		except Exception as e:
			logHandler.log.warning(f"JadwalKu: Gagal mendapatkan ID perangkat audio ({device_name}): {e}")
		return getattr(nvwave, "outputDeviceID", -1)

	def _play_wav_winmm(self, filepath, device_id):
		self.stop_sound()
		try:
			wf = wave.open(filepath, 'rb')
			nchannels = wf.getnchannels()
			framerate = wf.getframerate()
			sampwidth = wf.getsampwidth()
			frames = wf.readframes(wf.getnframes())
			wf.close()
		except Exception as e:
			logHandler.log.error(f"JadwalKu: Gagal membaca file wave '{filepath}': {e}")
			return False

		winmm = ctypes.windll.winmm
		class WAVEFORMATEX(ctypes.Structure):
			_fields_ = [
				('wFormatTag', ctypes.c_ushort),
				('nChannels', ctypes.c_ushort),
				('nSamplesPerSec', ctypes.c_ulong),
				('nAvgBytesPerSec', ctypes.c_ulong),
				('nBlockAlign', ctypes.c_ushort),
				('wBitsPerSample', ctypes.c_ushort),
				('cbSize', ctypes.c_ushort)
			]

		class WAVEHDR(ctypes.Structure):
			_fields_ = [
				('lpData', ctypes.c_char_p),
				('dwBufferLength', ctypes.c_ulong),
				('dwBytesRecorded', ctypes.c_ulong),
				('dwUser', ctypes.c_ulong),
				('dwFlags', ctypes.c_ulong),
				('dwLoops', ctypes.c_ulong),
				('lpNext', ctypes.c_void_p),
				('reserved', ctypes.c_ulong)
			]

		wfx = WAVEFORMATEX()
		wfx.wFormatTag = 1 # PCM
		wfx.nChannels = nchannels
		wfx.nSamplesPerSec = framerate
		wfx.wBitsPerSample = sampwidth * 8
		wfx.nBlockAlign = wfx.nChannels * sampwidth
		wfx.nAvgBytesPerSec = wfx.nSamplesPerSec * wfx.nBlockAlign
		wfx.cbSize = 0

		hWaveOut = ctypes.c_void_p()
		res = winmm.waveOutOpen(ctypes.byref(hWaveOut), device_id, ctypes.byref(wfx), 0, 0, 0)
		if res != 0:
			logHandler.log.warning(f"JadwalKu: waveOutOpen gagal (kode {res}) untuk device {device_id}")
			return False

		with self._lock:
			self._active_wave_outs.add(hWaveOut.value or ctypes.addressof(hWaveOut))
		self._is_playing = True

		def worker(hw=hWaveOut):
			try:
				hdr = WAVEHDR()
				hdr.lpData = frames
				hdr.dwBufferLength = len(frames)
				hdr.dwFlags = 0

				winmm.waveOutPrepareHeader(hw, ctypes.byref(hdr), ctypes.sizeof(hdr))
				winmm.waveOutWrite(hw, ctypes.byref(hdr), ctypes.sizeof(hdr))

				handle_val = hw.value or ctypes.addressof(hw)
				while True:
					with self._lock:
						if handle_val not in self._active_wave_outs:
							break
					if (hdr.dwFlags & 1): # WHDR_DONE
						break
					time.sleep(0.05)

				winmm.waveOutReset(hw)
				winmm.waveOutUnprepareHeader(hw, ctypes.byref(hdr), ctypes.sizeof(hdr))
				winmm.waveOutClose(hw)
			except Exception as e:
				logHandler.log.error(f"JadwalKu: Error saat pemutaran audio di thread: {e}")
			finally:
				handle_val = hw.value or ctypes.addressof(hw)
				with self._lock:
					self._active_wave_outs.discard(handle_val)
					if len(self._active_wave_outs) == 0 and len(self._active_mp3_aliases) == 0:
						self._is_playing = False

		threading.Thread(target=worker, daemon=True).start()
		return True

	def play_sound(self, filename):
		if not filename or filename == "Tanpa Suara Audio":
			return False
		path = self.get_sound_path(filename)
		if not path and os.path.exists(filename):
			path = filename
		
		if path and os.path.exists(path):
			dev_id = self.get_output_device_id()
			try:
				if path.lower().endswith(".mp3"):
					wav_equiv = os.path.splitext(path)[0] + ".wav"
					if not os.path.exists(wav_equiv):
						try:
							import pygame, wave
							if not pygame.mixer.get_init():
								pygame.mixer.init()
							s = pygame.mixer.Sound(path)
							w = wave.open(wav_equiv, 'wb')
							w.setnchannels(2)
							w.setsampwidth(2)
							w.setframerate(44100)
							w.writeframes(s.get_raw())
							w.close()
						except Exception as ex:
							logHandler.log.warning(f"JadwalKu: Gagal konversi MP3 ke WAV on the fly: {ex}")
					if os.path.exists(wav_equiv):
						path = wav_equiv
						self.last_played_file = path
						return self._play_wav_winmm(path, dev_id)
					else:
						import random
						alias = f"jk_mp3_{int(time.time()*1000)}_{random.randint(100,999)}"
						cmd_open = f'open "{path}" type mpegvideo alias {alias}'
						res = ctypes.windll.winmm.mciSendStringW(cmd_open, None, 0, None)
						if res == 0:
							ctypes.windll.winmm.mciSendStringW(f"play {alias}", None, 0, None)
							with self._lock:
								self._active_mp3_aliases.add(alias)
							self._is_playing = True
							self.last_played_file = path

							def mp3_worker(al=alias):
								try:
									buf = ctypes.create_unicode_buffer(128)
									while True:
										with self._lock:
											if al not in self._active_mp3_aliases:
												break
										ctypes.windll.winmm.mciSendStringW(f"status {al} mode", buf, 128, None)
										mode = buf.value.lower()
										if mode in ["stopped", "not ready", ""]:
											break
										time.sleep(0.1)
								finally:
									ctypes.windll.winmm.mciSendStringW(f"close {al}", None, 0, None)
									with self._lock:
										self._active_mp3_aliases.discard(al)
										if len(self._active_wave_outs) == 0 and len(self._active_mp3_aliases) == 0:
											self._is_playing = False

							threading.Thread(target=mp3_worker, daemon=True).start()
							return True
				elif path.lower().endswith(".wav"):
					self.last_played_file = path
					return self._play_wav_winmm(path, dev_id)
			except Exception as e:
				logHandler.log.error(f"JadwalKu: Gagal memutar file suara '{path}': {e}")
		return False

	def stop_sound(self):
		try:
			self.is_alarm_ringing = False
			self._is_playing = False
			with self._lock:
				wave_handles = list(self._active_wave_outs)
				mp3_aliases = list(self._active_mp3_aliases)
				self._active_wave_outs.clear()
				self._active_mp3_aliases.clear()

			for hw in wave_handles:
				try:
					ctypes.windll.winmm.waveOutReset(ctypes.c_void_p(hw))
				except Exception:
					pass
			for al in mp3_aliases:
				try:
					ctypes.windll.winmm.mciSendStringW(f"close {al}", None, 0, None)
				except Exception:
					pass
			try:
				ctypes.windll.winmm.mciSendStringW(f"close {self._mp3_alias}", None, 0, None)
			except Exception:
				pass
			try:
				nvwave.playWaveFile("")
			except Exception:
				pass
			logHandler.log.info("JadwalKu: Audio dihentikan.")
			return True
		except Exception as e:
			logHandler.log.error(f"JadwalKu: Gagal stop audio: {e}")
			return False

	def start_alarm_loop(self, audio_file, title, message):
		self.is_alarm_ringing = True
		self.active_alarm_info = (audio_file, title, message)
		
		def _looper():
			while self.is_alarm_ringing:
				if not self.has_active_playback():
					self.play_sound(audio_file)
				time.sleep(0.5)
		
		threading.Thread(target=_looper, daemon=True).start()
		
		def _show_dlg():
			try:
				import gui
				gui.mainFrame.prePopup()
				dlg = AlarmNotificationDialog(gui.mainFrame, title, message, self)
				dlg.ShowModal()
			except Exception as e:
				logHandler.log.error(f"JadwalKu: Gagal menampilkan AlarmNotificationDialog: {e}")
			finally:
				try:
					import gui
					gui.mainFrame.postPopup()
				except Exception:
					pass
		wx.CallAfter(_show_dlg)

	def stop_alarm(self):
		self.is_alarm_ringing = False
		self.active_alarm_info = None
		self.stop_sound()
		ui.message("Alarm dimatikan.")

	def snooze_alarm(self, minutes=10):
		if not self.active_alarm_info:
			self.stop_alarm()
			return
		audio_file, title, message = self.active_alarm_info
		self.is_alarm_ringing = False
		self.active_alarm_info = None
		self.stop_sound()
		
		import datetime
		trigger_time = datetime.datetime.now() + datetime.timedelta(minutes=minutes)
		self.snoozed_alarms.append({
			"trigger_time": trigger_time,
			"audio_file": audio_file,
			"title": title,
			"message": f"[Snooze {minutes}m] {message}"
		})
		ui.message(f"Alarm ditunda {minutes} menit.")

	def check_snoozed_alarms(self, now):
		if not self.snoozed_alarms:
			return
		remaining = []
		for s in self.snoozed_alarms:
			if now >= s["trigger_time"]:
				self.notify(s["title"], s["message"], speech_enabled=True, audio_enabled=True, audio_file=s["audio_file"], is_alarm=True)
			else:
				remaining.append(s)
		self.snoozed_alarms = remaining

	def notify(self, title, message, speech_enabled=True, audio_enabled=True, audio_file="chime.wav", is_alarm=False):
		if speech_enabled:
			full_msg = f"{title}: {message}" if title else message
			ui.message(full_msg)

		if audio_enabled and audio_file and audio_file != "Tanpa Suara Audio":
			if is_alarm:
				self.start_alarm_loop(audio_file, title, message)
			else:
				self.play_sound(audio_file)


