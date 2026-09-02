import os
import sys
import threading
import ctypes
from ctypes import wintypes
import time
import json
import logging

try:
	import globalVars
except ImportError:
	pass

class VoiceCommandManager:
	def __init__(self, callback):
		self.callback = callback
		self.is_listening = False
		self.thread = None
		self.winmm = ctypes.windll.winmm
		self.device_index = -1
		self.mic_boost = 100
		
		# Locate module path
		appdata = os.getenv("APPDATA")
		self.module_path = os.path.join(appdata, "nvda", "jadwalku_voice_module")
		self.model_path = os.path.join(self.module_path, "vosk-model-small-id")
		
		self.recognizer = None
		self._stop_event = threading.Event()
		self.device_index = -1
		
		class WAVEINCAPSW(ctypes.Structure):
			_fields_ = [
				("wMid", wintypes.WORD),
				("wPid", wintypes.WORD),
				("vDriverVersion", ctypes.c_uint),
				("szPname", ctypes.c_wchar * 32),
				("dwFormats", wintypes.DWORD),
				("wChannels", wintypes.WORD),
				("wReserved1", wintypes.WORD),
			]
		self.WAVEINCAPSW = WAVEINCAPSW
		
	def set_input_device(self, idx):
		self.device_index = idx

	def get_input_devices(self):
		count = self.winmm.waveInGetNumDevs()
		devices = [(-1, "Bawaan Windows (Default Mapper)")]
		caps = self.WAVEINCAPSW()
		for i in range(count):
			if self.winmm.waveInGetDevCapsW(i, ctypes.byref(caps), ctypes.sizeof(caps)) == 0:
				devices.append((i, caps.szPname))
		return devices
		
	def is_module_installed(self):
		if not os.path.isdir(self.module_path):
			return False
		if not os.path.isdir(self.model_path):
			return False
		return True
		
	def _init_vosk(self):
		if self.module_path not in sys.path:
			sys.path.insert(0, self.module_path)
		
		try:
			import types
			for mod_name in ['srt', 'tqdm', 'requests']:
				if mod_name not in sys.modules:
					mock_mod = types.ModuleType(mod_name)
					if mod_name == 'tqdm':
						mock_mod.tqdm = lambda *args, **kwargs: None
					sys.modules[mod_name] = mock_mod
			
			import vosk
			vosk.SetLogLevel(-1) # Disable verbose logs
			model = vosk.Model(self.model_path)
			self.recognizer = vosk.KaldiRecognizer(model, 16000)
			return True
		except Exception as e:
			logging.error(f"Gagal memuat Vosk: {e}")
			return False

	def start_listening(self):
		if self.is_listening: return False
		if not self.is_module_installed(): return False
		
		if not self._init_vosk(): return False
		
		self.is_listening = True
		self._stop_event = threading.Event()
		self.thread = threading.Thread(target=self._listen_loop, args=(self._stop_event,), daemon=True)
		self.thread.start()
		return True
		
	def stop_listening(self):
		if not self.is_listening: return
		self.is_listening = False
		self._stop_event.set()
		if self.thread and self.thread.is_alive():
			self.thread.join(timeout=2)
		self.recognizer = None

	def _boost_pcm_16bit(self, frames, factor):
		if factor == 1.0 or not frames:
			return frames
		try:
			import array
			arr = array.array('h')
			arr.frombytes(frames)
			num_samples = len(arr)
			f_int = int(factor * 256)
			for i in range(num_samples):
				val = (arr[i] * f_int) >> 8
				if val > 32767:
					val = 32767
				elif val < -32768:
					val = -32768
				arr[i] = val
			return arr.tobytes()
		except Exception as e:
			from .logger import jk_log
			jk_log.error(f"JadwalKu VC: Error in mic boost: {e}")
			return frames

	def _listen_loop(self, stop_event):
		class WAVEFORMATEX(ctypes.Structure):
			_fields_ = [
				("wFormatTag", wintypes.WORD),
				("nChannels", wintypes.WORD),
				("nSamplesPerSec", wintypes.DWORD),
				("nAvgBytesPerSec", wintypes.DWORD),
				("nBlockAlign", wintypes.WORD),
				("wBitsPerSample", wintypes.WORD),
				("cbSize", wintypes.WORD)
			]

		class WAVEHDR(ctypes.Structure):
			pass
		WAVEHDR._fields_ = [
			("lpData", ctypes.POINTER(ctypes.c_char)),
			("dwBufferLength", wintypes.DWORD),
			("dwBytesRecorded", wintypes.DWORD),
			("dwUser", ctypes.c_void_p),
			("dwFlags", wintypes.DWORD),
			("dwLoops", wintypes.DWORD),
			("lpNext", ctypes.POINTER(WAVEHDR)),
			("reserved", ctypes.c_void_p)
		]
		
		hWaveIn = wintypes.HANDLE()
		fmt = WAVEFORMATEX()
		fmt.wFormatTag = 1 # PCM
		fmt.nChannels = 1
		fmt.nSamplesPerSec = 16000
		fmt.wBitsPerSample = 16
		fmt.nBlockAlign = (fmt.nChannels * fmt.wBitsPerSample) // 8
		fmt.nAvgBytesPerSec = fmt.nSamplesPerSec * fmt.nBlockAlign
		fmt.cbSize = 0

		# 0.5s chunks
		chunk_size = fmt.nAvgBytesPerSec // 2
		
		NUM_BUFFERS = 3
		buffers = []
		hdrs = []
		
		if self.winmm.waveInOpen(ctypes.byref(hWaveIn), self.device_index, ctypes.byref(fmt), 0, 0, 0) != 0:
			self.is_listening = False
			return

		for _ in range(NUM_BUFFERS):
			buf = ctypes.create_string_buffer(chunk_size)
			hdr = WAVEHDR()
			hdr.lpData = ctypes.cast(buf, ctypes.POINTER(ctypes.c_char))
			hdr.dwBufferLength = chunk_size
			hdr.dwBytesRecorded = 0
			hdr.dwUser = None
			hdr.dwFlags = 0
			hdr.dwLoops = 0
			hdr.lpNext = ctypes.cast(None, ctypes.POINTER(WAVEHDR))
			hdr.reserved = None
			
			self.winmm.waveInPrepareHeader(hWaveIn, ctypes.byref(hdr), ctypes.sizeof(WAVEHDR))
			self.winmm.waveInAddBuffer(hWaveIn, ctypes.byref(hdr), ctypes.sizeof(WAVEHDR))
			
			buffers.append(buf)
			hdrs.append(hdr)
			
		self.winmm.waveInStart(hWaveIn)
		
		buf_idx = 0
		last_trigger_time = 0
		
		while not stop_event.is_set():
			hdr = hdrs[buf_idx]
			# WHDR_DONE is 1
			if hdr.dwFlags & 1:
				if hdr.dwBytesRecorded > 0:
					data = ctypes.string_at(hdr.lpData, hdr.dwBytesRecorded)
					if self.mic_boost != 100:
						factor = float(self.mic_boost) / 100.0
						data = self._boost_pcm_16bit(data, factor)
					
					if self.recognizer.AcceptWaveform(data):
						res = json.loads(self.recognizer.Result())
						text = res.get("text", "").lower()
						if "jam berapa" in text or "sekarang jam" in text or "what time" in text or "time" in text:
							current_time = time.time()
							if current_time - last_trigger_time > 4.0:
								last_trigger_time = current_time
								self.callback()
					else:
						res = json.loads(self.recognizer.PartialResult())
						text = res.get("partial", "").lower()
						if "jam berapa" in text or "sekarang jam" in text or "what time" in text or "time" in text:
							# Restart recognizer so we don't trigger twice
							self.recognizer.Reset()
							current_time = time.time()
							if current_time - last_trigger_time > 4.0:
								last_trigger_time = current_time
								self.callback()
				
				# Re-add buffer
				self.winmm.waveInUnprepareHeader(hWaveIn, ctypes.byref(hdr), ctypes.sizeof(WAVEHDR))
				hdr.dwFlags = 0
				hdr.dwBytesRecorded = 0
				self.winmm.waveInPrepareHeader(hWaveIn, ctypes.byref(hdr), ctypes.sizeof(WAVEHDR))
				self.winmm.waveInAddBuffer(hWaveIn, ctypes.byref(hdr), ctypes.sizeof(WAVEHDR))
				
				buf_idx = (buf_idx + 1) % NUM_BUFFERS
			else:
				time.sleep(0.01)

		self.winmm.waveInStop(hWaveIn)
		self.winmm.waveInReset(hWaveIn)
		for hdr in hdrs:
			self.winmm.waveInUnprepareHeader(hWaveIn, ctypes.byref(hdr), ctypes.sizeof(WAVEHDR))
		self.winmm.waveInClose(hWaveIn)
