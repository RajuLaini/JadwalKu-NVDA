# -*- coding: UTF-8 -*-
import os
import wave
import threading
import time
import ctypes
import wx
from .logger import jk_log
import nvwave
import ui
import tempfile

SOUNDS_DIR = os.path.join(os.path.dirname(__file__), "sounds")

class WAVEFORMATEX(ctypes.Structure):
	_fields_ = [
		("wFormatTag", ctypes.c_ushort),
		("nChannels", ctypes.c_ushort),
		("nSamplesPerSec", ctypes.c_ulong),
		("nAvgBytesPerSec", ctypes.c_ulong),
		("nBlockAlign", ctypes.c_ushort),
		("wBitsPerSample", ctypes.c_ushort),
		("cbSize", ctypes.c_ushort)
	]

class WAVEHDR(ctypes.Structure):
	_fields_ = [
		("lpData", ctypes.c_char_p),
		("dwBufferLength", ctypes.c_ulong),
		("dwBytesRecorded", ctypes.c_ulong),
		("dwUser", ctypes.c_ulong),
		("dwFlags", ctypes.c_ulong),
		("dwLoops", ctypes.c_ulong),
		("lpNext", ctypes.c_void_p),
		("reserved", ctypes.c_ulong)
	]

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
	def __init__(self, config_manager=None, tts_manager=None):
		self.config = config_manager
		self.tts_manager = tts_manager
		self.last_played_file = None
		self._mp3_alias = "jadwalku_alarm_mp3"
		self._active_wave_outs = set()
		self._active_mp3_aliases = set()
		self._lock = threading.Lock()
		self._is_playing = False
		self.is_alarm_ringing = False
		self.active_alarm_info = None
		self.snoozed_alarms = []
		self._audio_cache = {}

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
			jk_log.error(f"JadwalKu: Gagal mengambil daftar audio device WinMM: {e}")
			
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
			jk_log.warning(f"JadwalKu: Gagal mendapatkan ID perangkat audio ({device_name}): {e}")
		return getattr(nvwave, "outputDeviceID", -1)

	def _boost_pcm_16bit(self, frames, factor):
		if factor == 1.0 or not frames:
			return frames
		
		# Optimasi C-Level (Bebas GIL Bottleneck) menggunakan audioop
		try:
			import audioop
			return audioop.mul(frames, 2, factor)
		except ImportError:
			pass
		except Exception as e:
			from .logger import jk_log
			jk_log.error(f"JadwalKu: audioop gagal: {e}")
			
		# Fallback lambat jika audioop tidak tersedia (misal di Python masa depan)
		try:
			import array
			arr = array.array('h')
			arr.frombytes(frames)
			num_samples = len(arr)
			f_int = int(factor * 256)
			for i in range(num_samples):
				val = (arr[i] * f_int) >> 8
				if val > 32767:
					arr[i] = 32767
				elif val < -32768:
					arr[i] = -32768
				else:
					arr[i] = val
			return arr.tobytes()
		except Exception as e:
			from .logger import jk_log
			jk_log.error(f"JadwalKu: Gagal boost volume audio PCM: {e}")
			return frames

	def _play_wav_winmm(self, filepath, device_id, allow_overlap=True, stop_alarm=False, loop=False, volume_override=None):
		if not allow_overlap:
			self.stop_sound(stop_alarm=stop_alarm)
			
		vol = volume_override
		if vol is None:
			vol = self.config.get_audio_volume() if hasattr(self, 'config') and self.config else 100
			
		cache_key = (filepath, vol)
		
		# Jangan gunakan cache untuk file dinamis (Voice Pack & TTS Mandiri) karena isinya selalu berubah
		import os
		bypass_cache = os.path.basename(filepath) in ("jadwalku_vp_seq.wav", "jadwalku_tts.wav")
		
		if not bypass_cache and hasattr(self, '_audio_cache') and cache_key in self._audio_cache:
			cached_data = self._audio_cache[cache_key]
			frames = cached_data['frames']
			wfx = cached_data['wfx']
			duration_sec = cached_data['duration_sec']
		else:
			try:
				wf = wave.open(filepath, 'rb')
				duration_sec = float(wf.getnframes()) / float(wf.getframerate())
				channels = wf.getnchannels()
				framerate = wf.getframerate()
				bitsPerSample = wf.getsampwidth() * 8
				frames = wf.readframes(wf.getnframes())
				wf.close()
			except Exception:
				duration_sec = 2.5
				channels = 2
				framerate = 44100
				bitsPerSample = 16
				frames = b""

			if not frames:
				return False

			wfx = WAVEFORMATEX()
			wfx.wFormatTag = 1 # WAVE_FORMAT_PCM
			wfx.nChannels = channels
			wfx.nSamplesPerSec = framerate
			wfx.wBitsPerSample = bitsPerSample
			wfx.nBlockAlign = (channels * bitsPerSample) // 8
			wfx.nAvgBytesPerSec = framerate * wfx.nBlockAlign
			wfx.cbSize = 0

			try:
				if bitsPerSample == 16 and vol != 100:
					factor = float(vol) / 100.0
					frames = self._boost_pcm_16bit(frames, factor)
			except Exception:
				pass
				
			if not bypass_cache and hasattr(self, '_audio_cache'):
				self._audio_cache[cache_key] = {
					'frames': frames,
					'wfx': wfx,
					'duration_sec': duration_sec
				}

		self._is_playing = True
		self.last_played_file = filepath

		from .logger import jk_log
		jk_log.warning(f"JadwalKu DEBUG: Memutar file: {filepath}")

		def worker():
			hWaveOut = ctypes.c_void_p()
			handle_val = None
			try:
				open_attempts = 0
				res = -1
				while open_attempts < 20:
					res = ctypes.windll.winmm.waveOutOpen(ctypes.byref(hWaveOut), device_id, ctypes.byref(wfx), 0, 0, 0)
					if res == 0:
						break
					if res == 4: # MMSYSERR_ALLOCATED
						time.sleep(0.05)
						open_attempts += 1
					else:
						break

				if res != 0:
					jk_log.error(f"JadwalKu: waveOutOpen gagal (kode {res}) pada device ID {device_id}")
					return

				handle_val = hWaveOut.value or ctypes.addressof(hWaveOut)
				with self._lock:
					self._active_wave_outs.add(handle_val)

				while True:
					with self._lock:
						if not self._is_playing:
							break

					buf = ctypes.create_string_buffer(frames)
					hdr = WAVEHDR()
					hdr.lpData = ctypes.cast(buf, ctypes.c_char_p)
					hdr.dwBufferLength = len(frames)
					hdr.dwFlags = 0
					hdr.dwLoops = 0

					res_prep = ctypes.windll.winmm.waveOutPrepareHeader(hWaveOut, ctypes.byref(hdr), ctypes.sizeof(hdr))
					if res_prep != 0:
						jk_log.error(f"JadwalKu: waveOutPrepareHeader gagal (kode {res_prep})")
						break

					res_write = ctypes.windll.winmm.waveOutWrite(hWaveOut, ctypes.byref(hdr), ctypes.sizeof(hdr))
					if res_write != 0:
						jk_log.error(f"JadwalKu: waveOutWrite gagal (kode {res_write})")
						try:
							ctypes.windll.winmm.waveOutUnprepareHeader(hWaveOut, ctypes.byref(hdr), ctypes.sizeof(hdr))
						except Exception:
							pass
						break

					start_t = time.time()
					while time.time() - start_t < duration_sec:
						with self._lock:
							if not self._is_playing:
								break
						time.sleep(0.05)

					# Tunggu sampai buffer selesai (WHDR_DONE / WAVERR_STILLPLAYING bersih) sebelum unprepare agar suara utuh 100%
					unprep_attempts = 0
					while True:
						with self._lock:
							if not self._is_playing:
								try:
									ctypes.windll.winmm.waveOutReset(hWaveOut)
								except Exception:
									pass
						res_unprep = ctypes.windll.winmm.waveOutUnprepareHeader(hWaveOut, ctypes.byref(hdr), ctypes.sizeof(hdr))
						if res_unprep == 0:
							break
						if res_unprep == 33: # WAVERR_STILLPLAYING
							time.sleep(0.02)
							unprep_attempts += 1
							if unprep_attempts > 100:
								break
						else:
							break

					with self._lock:
						if not self._is_playing:
							break

					if not loop:
						break

					# Jeda 2 detik antar putaran agar suara tidak tumpang tindih / terpotong (sesuai permintaan user)
					for _ in range(20):
						with self._lock:
							if not self._is_playing:
								break
						time.sleep(0.1)
			except Exception as e:
				jk_log.error(f"JadwalKu: Error saat pemutaran audio di thread: {e}")
			finally:
				if handle_val is not None:
					try:
						ctypes.windll.winmm.waveOutReset(hWaveOut)
					except Exception:
						pass
					try:
						ctypes.windll.winmm.waveOutClose(hWaveOut)
					except Exception:
						pass
					with self._lock:
						self._active_wave_outs.discard(handle_val)

		threading.Thread(target=worker, daemon=True).start()
		return True

	def play_sound(self, filename, allow_overlap=True, stop_alarm=False, loop=False, is_tts=False):
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
							jk_log.warning(f"JadwalKu: Gagal konversi MP3 ke WAV on the fly: {ex}")
					if os.path.exists(wav_equiv):
						path = wav_equiv
						self.last_played_file = path
						return self._play_wav_winmm(path, dev_id, allow_overlap=allow_overlap, stop_alarm=stop_alarm, loop=loop)
					else:
						if not allow_overlap:
							self.stop_sound(stop_alarm=stop_alarm)
						import random
						alias = f"jk_mp3_{int(time.time()*1000)}_{random.randint(100,999)}"
						cmd_open = f'open "{path}" type mpegvideo alias {alias}'
						res = ctypes.windll.winmm.mciSendStringW(cmd_open, None, 0, None)
						if res == 0:
							vol = getattr(self, "_override_volume", None)
							if vol is None:
								vol = self.config.get_audio_volume() if self.config else 100
							ctypes.windll.winmm.mciSendStringW(f"setaudio {alias} volume to {min(1000, int(vol * 10))}", None, 0, None)
							play_cmd = f"play {alias} repeat" if loop else f"play {alias}"
							ctypes.windll.winmm.mciSendStringW(play_cmd, None, 0, None)
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
											if not loop:
												break
											else:
												with self._lock:
													if al not in self._active_mp3_aliases:
														break
												ctypes.windll.winmm.mciSendStringW(f"seek {al} to start", None, 0, None)
												ctypes.windll.winmm.mciSendStringW(f"play {al}", None, 0, None)
										time.sleep(0.1)
								finally:
									ctypes.windll.winmm.mciSendStringW(f"close {al}", None, 0, None)
									with self._lock:
										self._active_mp3_aliases.discard(al)

							threading.Thread(target=mp3_worker, daemon=True).start()
							return True
				elif path.lower().endswith(".wav"):
					self.last_played_file = path
					return self._play_wav_winmm(path, dev_id, allow_overlap=allow_overlap, stop_alarm=stop_alarm, loop=loop)
			except Exception as e:
				jk_log.error(f"JadwalKu: Gagal memutar file suara '{path}': {e}")
		return False
	def play_voice_pack_sequence(self, filepaths, volume_override=None):
		"""Memutar kumpulan file WAV secara berurutan dan mulus."""
		if not filepaths: return
		
		# Gabungkan semua frames menjadi satu bytearray
		combined_frames = bytearray()
		framerate = 44100
		channels = 1
		bitsPerSample = 16
		
		from .logger import jk_log
		for fp in filepaths:
			if not os.path.exists(fp): 
				jk_log.warning(f"VP: File not found {fp}")
				continue
			try:
				with wave.open(fp, 'rb') as wf:
					c = wf.getnchannels()
					f = wf.getframerate()
					b = wf.getsampwidth() * 8
					frames = wf.readframes(wf.getnframes())
					combined_frames.extend(frames)
					jk_log.info(f"VP: Parsed {fp} | {c}ch {f}Hz {b}bit | {len(frames)} bytes")
					channels = c
					framerate = f
					bitsPerSample = b
			except Exception as e:
				jk_log.error(f"VP: Error reading {fp}: {e}")
				
		if not combined_frames: 
			jk_log.error("VP: combined_frames is EMPTY! Aborting playback.")
			return
		
		temp_path = os.path.join(tempfile.gettempdir(), "jadwalku_vp_seq.wav")
		try:
			with wave.open(temp_path, 'wb') as wf:
				wf.setnchannels(channels)
				wf.setsampwidth(bitsPerSample // 8)
				wf.setframerate(framerate)
				wf.writeframes(combined_frames)
			
			jk_log.info(f"VP: Playing combined WAV {temp_path} | {channels}ch {framerate}Hz {bitsPerSample}bit | Total {len(combined_frames)} bytes")
			# Mainkan file gabungan tersebut menggunakan WinMM
			# allow_overlap=True agar tidak menghentikan lonceng (mulaiLonceng)
			device_id = self.get_output_device_id()
			t = threading.Thread(target=self._play_wav_winmm, args=(temp_path, device_id, True, False, False, volume_override))
			t.daemon = True
			t.start()
		except Exception as e:
			jk_log.error(f"JadwalKu VoicePack: Gagal memutar sequence: {e}")
	def stop_sound(self, stop_alarm=True):
		try:
			if stop_alarm:
				self.is_alarm_ringing = False
			self._is_playing = False
			with self._lock:
				wave_handles = list(self._active_wave_outs)
				mp3_aliases = list(self._active_mp3_aliases)
				nv_players = list(getattr(self, "_active_nvwave_players", []))
				self._active_wave_outs.clear()
				self._active_mp3_aliases.clear()
				if hasattr(self, "_active_nvwave_players"):
					self._active_nvwave_players.clear()

			for p in nv_players:
				try:
					p.stop()
				except Exception:
					pass
				try:
					p.close()
				except Exception:
					pass

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
			jk_log.info("JadwalKu: Audio dihentikan.")
			return True
		except Exception as e:
			jk_log.error(f"JadwalKu: Gagal stop audio: {e}")
			return False

	def start_alarm_loop(self, audio_file, title, message):
		self.stop_sound(stop_alarm=False)
		self.is_alarm_ringing = True
		self.active_alarm_info = (audio_file, title, message)
		self.play_sound(audio_file, allow_overlap=True, stop_alarm=False, loop=True)
		
		def _show_dlg():
			try:
				import gui
				gui.mainFrame.prePopup()
				dlg = AlarmNotificationDialog(gui.mainFrame, title, message, self)
				dlg.ShowModal()
			except Exception as e:
				jk_log.error(f"JadwalKu: Gagal menampilkan AlarmNotificationDialog: {e}")
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
		self.stop_sound(stop_alarm=True)
		ui.message("Alarm dimatikan.")

	def snooze_alarm(self, minutes=10):
		if not self.active_alarm_info:
			self.stop_alarm()
			return
		audio_file, title, message = self.active_alarm_info
		self.is_alarm_ringing = False
		self.active_alarm_info = None
		self.stop_sound(stop_alarm=True)
		
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
			if hasattr(self, "tts_manager") and self.tts_manager and self.tts_manager.is_enabled():
				self.tts_manager.speak(full_msg)
			else:
				ui.message(full_msg)

		if audio_enabled and audio_file and audio_file != "Tanpa Suara Audio":
			if is_alarm:
				self.start_alarm_loop(audio_file, title, message)
			else:
				self.play_sound(audio_file)


	def _mci_cmd(self, cmd):
		import ctypes
		ctypes.windll.winmm.mciSendStringW(cmd, None, 0, None)

	def play_tick(self, volume):
		import os
		tick_path = os.path.join(os.path.dirname(__file__), "sounds", "WaitingClock", "WatingClock.wav")
		if not os.path.exists(tick_path):
			return
		
		dev_id = self.get_output_device_id()
		self._play_wav_winmm(tick_path, dev_id, allow_overlap=True, volume_override=volume)

	def play_quarter_lonceng(self, volume, minute):
		import os
		import threading
		from .logger import jk_log
		jk_log.warning(f"JadwalKu DEBUG: play_quarter_lonceng dipanggil untuk menit {minute} dengan volume {volume}")
		
		base_dir = os.path.join(os.path.dirname(__file__), "sounds", "Lonceng")
		
		if minute == 15:
			wav_file = "SeperempatJam.wav"
		elif minute == 30:
			wav_file = "SetengahJam.wav"
		elif minute == 45:
			wav_file = "TigaQua.wav"
		else:
			return
			
		wav_path = os.path.join(base_dir, wav_file)
		if not os.path.exists(wav_path):
			from .logger import jk_log
			jk_log.warning(f"JadwalKu: File lonceng perempat {wav_file} tidak ditemukan!")
			return
			
		dev_id = self.get_output_device_id()
		
		def quarter_thread():
			self._is_playing = True
			self._play_wav_winmm(wav_path, dev_id, allow_overlap=True, volume_override=volume)
			
			import time
			dur = 35.0
			if minute == 15: dur = 34.0
			elif minute == 30: dur = 33.0
			elif minute == 45: dur = 38.0
			
			elapsed = 0.0
			while elapsed < dur:
				if not self._is_playing: return
				time.sleep(0.1)
				elapsed += 0.1

		threading.Thread(target=quarter_thread, daemon=True).start()

	def play_lonceng_sequence(self, volume, hour, test_mode=False):
		import threading
		from .logger import jk_log
		jk_log.warning(f"JadwalKu DEBUG: play_lonceng_sequence dipanggil untuk jam {hour} dengan volume {volume}")
		def lonceng_thread():
			import os
			import time
			
			base_dir = os.path.join(os.path.dirname(__file__), "sounds", "Lonceng")
			mulai_path = os.path.join(base_dir, "mulaiLonceng.wav")
			ketuk_path = os.path.join(base_dir, "ketukanLonceng.wav")
			
			if not os.path.exists(mulai_path) or not os.path.exists(ketuk_path):
				from .logger import jk_log
				jk_log.warning("JadwalKu: File lonceng tidak ditemukan!")
				return
				
			dev_id = self.get_output_device_id()
			
			self._is_playing = True
			self._play_wav_winmm(mulai_path, dev_id, allow_overlap=True, volume_override=volume)
			
			# Selalu tunggu 16.5 detik (Sengaja dibuat tumpang tindih agar suaranya menyambung mulus tanpa putus)
			target_time = time.time() + 16.5
			while time.time() < target_time:
				if not self._is_playing: return
				time.sleep(0.05)
			
			strike_count = hour % 12
			if strike_count == 0:
				strike_count = 12
				
			for i in range(strike_count):
				if not self._is_playing: return
				self._play_wav_winmm(ketuk_path, dev_id, allow_overlap=True, volume_override=volume)
				
				# Jeda alami 1.8 detik antar ketukan (menggantikan jeda lag komputasi yang hilang karena optimasi)
				target2 = time.time() + 1.8
				while time.time() < target2:
					if not self._is_playing: return
					time.sleep(0.05)
				
		threading.Thread(target=lonceng_thread, daemon=True).start()