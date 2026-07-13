# -*- coding: UTF-8 -*-
import os
import logHandler
import nvwave
import ui

SOUNDS_DIR = os.path.join(os.path.dirname(__file__), "sounds")

class AudioManager:
	def __init__(self, config_manager=None):
		self.config = config_manager
		self.last_played_file = None
		self._mp3_alias = "jadwalku_alarm_mp3"

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

	def play_sound(self, filename):
		if not filename or filename == "Tanpa Suara Audio":
			return False
		path = self.get_sound_path(filename)
		if not path and os.path.exists(filename):
			path = filename
		
		if path and os.path.exists(path):
			dev_id = self.get_output_device_id()
			try:
				if path.lower().endswith(".wav"):
					try:
						# Pemutaran WAV pada speaker khusus jika didukung oleh versi NVDA
						nvwave.playWaveFile(path, outputDevice=dev_id)
					except TypeError:
						try:
							wp = nvwave.WavePlayer(channels=2, samplesPerSec=44100, bitsPerSample=16, outputDevice=dev_id)
							wp.feed(open(path, 'rb').read())
							wp.idle()
						except Exception:
							nvwave.playWaveFile(path)
					self.last_played_file = path
					return True
				elif path.lower().endswith(".mp3"):
					import ctypes
					# Hentikan/tutup pemutaran MP3 sebelumnya jika ada
					ctypes.windll.winmm.mciSendStringW(f"close {self._mp3_alias}", None, 0, None)
					cmd_open = f'open "{path}" type mpegvideo alias {self._mp3_alias}'
					res = ctypes.windll.winmm.mciSendStringW(cmd_open, None, 0, None)
					if res == 0:
						ctypes.windll.winmm.mciSendStringW(f"play {self._mp3_alias}", None, 0, None)
						self.last_played_file = path
						return True
					else:
						logHandler.log.error(f"JadwalKu: Gagal membuka MP3 via mciSendString (kode {res})")
			except Exception as e:
				logHandler.log.error(f"JadwalKu: Gagal memutar file suara '{path}': {e}")
		return False

	def stop_sound(self):
		try:
			try:
				nvwave.playWaveFile("")
			except Exception:
				pass
			try:
				import ctypes
				ctypes.windll.winmm.mciSendStringW(f"close {self._mp3_alias}", None, 0, None)
			except Exception:
				pass
			logHandler.log.info("JadwalKu: Audio dihentikan.")
			return True
		except Exception as e:
			logHandler.log.error(f"JadwalKu: Gagal stop audio: {e}")
			return False

	def notify(self, title, message, speech_enabled=True, audio_enabled=True, audio_file="chime.wav"):
		if audio_enabled and audio_file and audio_file != "Tanpa Suara Audio":
			self.play_sound(audio_file)
		
		if speech_enabled:
			full_msg = f"{title}: {message}" if title else message
			ui.message(full_msg)

