# -*- coding: UTF-8 -*-
import os
import wave
import threading
import time
import ctypes
import logHandler
import nvwave
import ui

SOUNDS_DIR = os.path.join(os.path.dirname(__file__), "sounds")

class AudioManager:
	def __init__(self, config_manager=None):
		self.config = config_manager
		self.last_played_file = None
		self._mp3_alias = "jadwalku_alarm_mp3"
		self._active_wave_out = None
		self._is_playing = False

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

		self._active_wave_out = hWaveOut
		self._is_playing = True

		def worker():
			try:
				hdr = WAVEHDR()
				hdr.lpData = frames
				hdr.dwBufferLength = len(frames)
				hdr.dwFlags = 0

				winmm.waveOutPrepareHeader(hWaveOut, ctypes.byref(hdr), ctypes.sizeof(hdr))
				winmm.waveOutWrite(hWaveOut, ctypes.byref(hdr), ctypes.sizeof(hdr))

				while self._is_playing and not (hdr.dwFlags & 1): # WHDR_DONE
					time.sleep(0.05)

				winmm.waveOutReset(hWaveOut)
				winmm.waveOutUnprepareHeader(hWaveOut, ctypes.byref(hdr), ctypes.sizeof(hdr))
				winmm.waveOutClose(hWaveOut)
			except Exception as e:
				logHandler.log.error(f"JadwalKu: Error saat pemutaran audio di thread: {e}")
			finally:
				self._is_playing = False
				if self._active_wave_out == hWaveOut:
					self._active_wave_out = None

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
					if os.path.exists(wav_equiv):
						path = wav_equiv
						self.last_played_file = path
						return self._play_wav_winmm(path, dev_id)
					else:
						ctypes.windll.winmm.mciSendStringW(f"close {self._mp3_alias}", None, 0, None)
						cmd_open = f'open "{path}" type mpegvideo alias {self._mp3_alias}'
						res = ctypes.windll.winmm.mciSendStringW(cmd_open, None, 0, None)
						if res == 0:
							ctypes.windll.winmm.mciSendStringW(f"play {self._mp3_alias}", None, 0, None)
							self.last_played_file = path
							return True
				elif path.lower().endswith(".wav"):
					self.last_played_file = path
					return self._play_wav_winmm(path, dev_id)
			except Exception as e:
				logHandler.log.error(f"JadwalKu: Gagal memutar file suara '{path}': {e}")
		return False

	def stop_sound(self):
		try:
			self._is_playing = False
			if self._active_wave_out:
				try:
					ctypes.windll.winmm.waveOutReset(self._active_wave_out)
				except Exception:
					pass
			try:
				nvwave.playWaveFile("")
			except Exception:
				pass
			try:
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

