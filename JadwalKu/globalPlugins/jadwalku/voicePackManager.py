import os
import ctypes
import wave
import struct
import math
import zipfile
import json
import tempfile
import shutil

class VoiceRecorder:
	"""Memanfaatkan Windows winmm.dll (waveIn/waveOut) untuk merekam & memutar audio."""
	def __init__(self):
		import ctypes
		from ctypes import wintypes
		self.winmm = ctypes.windll.winmm
		
		# Constants
		self.WAVE_MAPPER = -1
		self.WAVE_FORMAT_PCM = 1
		self.CALLBACK_NULL = 0

		# Structures
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

		class WAVEOUTCAPSW(ctypes.Structure):
			_fields_ = [
				("wMid", wintypes.WORD),
				("wPid", wintypes.WORD),
				("vDriverVersion", ctypes.c_uint),
				("szPname", ctypes.c_wchar * 32),
				("dwFormats", wintypes.DWORD),
				("wChannels", wintypes.WORD),
				("wReserved1", wintypes.WORD),
				("dwSupport", wintypes.DWORD),
			]

		self.WAVEFORMATEX = WAVEFORMATEX
		self.WAVEHDR = WAVEHDR
		self.WAVEINCAPSW = WAVEINCAPSW
		self.WAVEOUTCAPSW = WAVEOUTCAPSW

		self._is_recording = False
		self.hWaveIn = None
		self.hdr = None
		self.buffer = None
		self.fmt = None
		self.device_index = self.WAVE_MAPPER
		self.out_device_index = self.WAVE_MAPPER

	def set_input_device(self, idx):
		self.device_index = idx

	def set_output_device(self, idx):
		self.out_device_index = idx

	def get_input_devices(self):
		import ctypes
		count = self.winmm.waveInGetNumDevs()
		devices = [(-1, "Bawaan Windows (Default Mapper)")]
		caps = self.WAVEINCAPSW()
		for i in range(count):
			if self.winmm.waveInGetDevCapsW(i, ctypes.byref(caps), ctypes.sizeof(caps)) == 0:
				devices.append((i, caps.szPname))
		return devices

	def get_output_devices(self):
		import ctypes
		count = self.winmm.waveOutGetNumDevs()
		devices = [(-1, "Bawaan Windows (Default Mapper)")]
		caps = self.WAVEOUTCAPSW()
		for i in range(count):
			if self.winmm.waveOutGetDevCapsW(i, ctypes.byref(caps), ctypes.sizeof(caps)) == 0:
				devices.append((i, caps.szPname))
		return devices

	def start_recording(self):
		if self._is_recording: return False
		
		import ctypes
		from ctypes import wintypes
		self.hWaveIn = wintypes.HANDLE()
		self.fmt = self.WAVEFORMATEX()
		self.fmt.wFormatTag = self.WAVE_FORMAT_PCM
		self.fmt.nChannels = 1
		self.fmt.nSamplesPerSec = 44100
		self.fmt.wBitsPerSample = 16
		self.fmt.nBlockAlign = (self.fmt.nChannels * self.fmt.wBitsPerSample) // 8
		self.fmt.nAvgBytesPerSec = self.fmt.nSamplesPerSec * self.fmt.nBlockAlign
		self.fmt.cbSize = 0

		res = self.winmm.waveInOpen(ctypes.byref(self.hWaveIn), self.device_index, ctypes.byref(self.fmt), 0, 0, self.CALLBACK_NULL)
		if res != 0: return False

		buffer_size = self.fmt.nAvgBytesPerSec * 60
		self.buffer = ctypes.create_string_buffer(buffer_size)

		self.hdr = self.WAVEHDR()
		self.hdr.lpData = ctypes.cast(self.buffer, ctypes.POINTER(ctypes.c_char))
		self.hdr.dwBufferLength = buffer_size
		self.hdr.dwBytesRecorded = 0
		self.hdr.dwUser = None
		self.hdr.dwFlags = 0
		self.hdr.dwLoops = 0
		self.hdr.lpNext = ctypes.cast(None, ctypes.POINTER(self.WAVEHDR))
		self.hdr.reserved = None

		res = self.winmm.waveInPrepareHeader(self.hWaveIn, ctypes.byref(self.hdr), ctypes.sizeof(self.WAVEHDR))
		if res != 0:
			self.winmm.waveInClose(self.hWaveIn)
			return False

		res = self.winmm.waveInAddBuffer(self.hWaveIn, ctypes.byref(self.hdr), ctypes.sizeof(self.WAVEHDR))
		if res != 0:
			self.winmm.waveInUnprepareHeader(self.hWaveIn, ctypes.byref(self.hdr), ctypes.sizeof(self.WAVEHDR))
			self.winmm.waveInClose(self.hWaveIn)
			return False

		res = self.winmm.waveInStart(self.hWaveIn)
		if res == 0:
			self._is_recording = True
			return True
		return False

	def stop_and_save(self, filepath):
		if not self._is_recording: return False
		
		import ctypes
		import time
		import wave
		self.winmm.waveInStop(self.hWaveIn)
		self.winmm.waveInReset(self.hWaveIn)

		for _ in range(10):
			if self.hdr.dwFlags & 1:
				break
			time.sleep(0.05)

		self.winmm.waveInUnprepareHeader(self.hWaveIn, ctypes.byref(self.hdr), ctypes.sizeof(self.WAVEHDR))
		self.winmm.waveInClose(self.hWaveIn)
		self._is_recording = False
		
		recorded = self.hdr.dwBytesRecorded
		if recorded > 0:
			try:
				with wave.open(filepath, 'wb') as wf:
					wf.setnchannels(self.fmt.nChannels)
					wf.setsampwidth(self.fmt.wBitsPerSample // 8)
					wf.setframerate(self.fmt.nSamplesPerSec)
					wf.writeframes(self.buffer.raw[:recorded])
				return True
			except Exception as e:
				pass
		return False

	def is_recording(self):
		return self._is_recording

	def play_audio(self, filepath):
		import threading
		def worker():
			import ctypes
			from ctypes import wintypes
			import wave
			import time
			try:
				with wave.open(filepath, 'rb') as wf:
					nChannels = wf.getnchannels()
					wBitsPerSample = wf.getsampwidth() * 8
					nSamplesPerSec = wf.getframerate()
					data = wf.readframes(wf.getnframes())

				hWaveOut = wintypes.HANDLE()
				fmt = self.WAVEFORMATEX()
				fmt.wFormatTag = self.WAVE_FORMAT_PCM
				fmt.nChannels = nChannels
				fmt.nSamplesPerSec = nSamplesPerSec
				fmt.wBitsPerSample = wBitsPerSample
				fmt.nBlockAlign = (fmt.nChannels * fmt.wBitsPerSample) // 8
				fmt.nAvgBytesPerSec = fmt.nSamplesPerSec * fmt.nBlockAlign
				fmt.cbSize = 0

				res = self.winmm.waveOutOpen(ctypes.byref(hWaveOut), self.out_device_index, ctypes.byref(fmt), 0, 0, self.CALLBACK_NULL)
				if res != 0: return

				buffer = ctypes.create_string_buffer(data)
				hdr = self.WAVEHDR()
				hdr.lpData = ctypes.cast(buffer, ctypes.POINTER(ctypes.c_char))
				hdr.dwBufferLength = len(data)
				hdr.dwFlags = 0
				hdr.dwLoops = 0

				self.winmm.waveOutPrepareHeader(hWaveOut, ctypes.byref(hdr), ctypes.sizeof(self.WAVEHDR))
				self.winmm.waveOutWrite(hWaveOut, ctypes.byref(hdr), ctypes.sizeof(self.WAVEHDR))

				while not (hdr.dwFlags & 1):
					time.sleep(0.05)

				self.winmm.waveOutUnprepareHeader(hWaveOut, ctypes.byref(hdr), ctypes.sizeof(self.WAVEHDR))
				self.winmm.waveOutClose(hWaveOut)
			except Exception as e:
				pass
		
		t = threading.Thread(target=worker)
		t.daemon = True
		t.start()

def trim_silence(input_wav, output_wav, threshold=300, chunk_ms=10):
	"""Membuang bagian hening (silence) di awal dan akhir rekaman."""
	try:
		with wave.open(input_wav, 'rb') as w_in:
			n_channels = w_in.getnchannels()
			sampwidth = w_in.getsampwidth()
			framerate = w_in.getframerate()
			n_frames = w_in.getnframes()
			
			if sampwidth != 2:
				# Jika bukan 16-bit, langsung copy saja untuk amannya
				shutil.copy(input_wav, output_wav)
				return
				
			audio_data = w_in.readframes(n_frames)
			
		samples = struct.unpack(f"<{n_frames * n_channels}h", audio_data)
		chunk_samples = int(framerate * chunk_ms / 1000) * n_channels
		
		start_idx = 0
		end_idx = len(samples)
		
		# Cari batas awal (suara mulai masuk)
		for i in range(0, len(samples), chunk_samples):
			chunk = samples[i:i+chunk_samples]
			if not chunk: break
			rms = math.sqrt(sum(s*s for s in chunk) / len(chunk))
			if rms > threshold:
				start_idx = max(0, i - (chunk_samples * 5)) # Sisakan margin 50ms (5 chunks)
				break
				
		# Cari batas akhir (suara mulai hilang)
		for i in range(len(samples) - chunk_samples, 0, -chunk_samples):
			chunk = samples[i:i+chunk_samples]
			if not chunk: break
			rms = math.sqrt(sum(s*s for s in chunk) / len(chunk))
			if rms > threshold:
				end_idx = min(len(samples), i + (chunk_samples * 5)) # Sisakan margin 50ms
				break
				
		if start_idx >= end_idx:
			start_idx = 0
			end_idx = len(samples)
			
		trimmed_samples = samples[start_idx:end_idx]
		trimmed_data = struct.pack(f"<{len(trimmed_samples)}h", *trimmed_samples)
		
		with wave.open(output_wav, 'wb') as w_out:
			w_out.setnchannels(n_channels)
			w_out.setsampwidth(sampwidth)
			w_out.setframerate(framerate)
			w_out.writeframes(trimmed_data)
			
	except Exception as e:
		import traceback
		traceback.print_exc()
		# Fallback: copy file
		shutil.copy(input_wav, output_wav)


class VoicePackManager:
	"""Mengelola pembuatan, ekstraksi, dan pembacaan paket suara kustom (.jvp)."""
	def __init__(self, add_on_dir):
		# Lokasi penyimpanan permanen
		self.add_on_dir = add_on_dir
		try:
			import globalVars
			config_path = globalVars.appArgs.configPath if hasattr(globalVars, 'appArgs') and globalVars.appArgs.configPath else os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "nvda")
		except Exception:
			config_path = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "nvda")
		
		self.pack_dir = os.path.join(config_path, "jadwalku_voice_packs")
		os.makedirs(self.pack_dir, exist_ok=True)
		
		# Migrasi otomatis: pindahkan paket suara lama jika ada, agar tidak terhapus saat update add-on
		old_pack_dir = os.path.join(self.add_on_dir, "voice_packs")
		if os.path.exists(old_pack_dir):
			try:
				import shutil
				for item in os.listdir(old_pack_dir):
					old_item = os.path.join(old_pack_dir, item)
					new_item = os.path.join(self.pack_dir, item)
					if not os.path.exists(new_item):
						shutil.move(old_item, new_item)
			except Exception as e:
				from .logger import jk_log
				jk_log.error(f"JadwalKu: Gagal memigrasi voice packs lama: {e}")
				
		# Folder sementara untuk sesi perekaman berjalan
		self.temp_session_dir = os.path.join(tempfile.gettempdir(), "jadwalku_voice_session")
		
	def init_recording_session(self):
		if os.path.exists(self.temp_session_dir):
			shutil.rmtree(self.temp_session_dir, ignore_errors=True)
		os.makedirs(self.temp_session_dir, exist_ok=True)
		return self.temp_session_dir
		
	def get_session_wav_path(self, item_name):
		return os.path.join(self.temp_session_dir, f"{item_name}.wav")
		
	def export_pack(self, metadata, output_filename="MyVoice.jvp", is_draft=False, password_hash="", is_permanent=False):
		"""Membungkus sesi rekaman saat ini menjadi file ZIP (.jvp) beserta manifest."""
		metadata["is_draft"] = is_draft
		if password_hash:
			metadata["password_hash"] = password_hash
		else:
			# preserve existing password_hash if updating without changing it? Usually we just pass it from existing metadata.
			if "password_hash" not in metadata:
				metadata["password_hash"] = ""
		metadata["is_permanent"] = is_permanent
		out_path = os.path.join(self.pack_dir, output_filename)
		
		with zipfile.ZipFile(out_path, 'w', zipfile.ZIP_DEFLATED) as zf:
			zf.writestr("manifest.json", json.dumps(metadata, indent=4))
			
			for f in os.listdir(self.temp_session_dir):
				if f.endswith(".wav"):
					file_path = os.path.join(self.temp_session_dir, f)
					zf.write(file_path, f)
					
		return out_path
		
	def get_available_packs(self):
		"""Mengembalikan daftar nama paket yang tersedia (.jvp) beserta metadatanya."""
		packs = []
		if not os.path.exists(self.pack_dir):
			return packs
			
		for f in os.listdir(self.pack_dir):
			if f.endswith(".jvp"):
				pack_path = os.path.join(self.pack_dir, f)
				try:
					import zipfile
					import json
					with zipfile.ZipFile(pack_path, 'r') as zf:
						if "manifest.json" in zf.namelist():
							meta_str = zf.read("manifest.json").decode("utf-8")
							meta = json.loads(meta_str)
							
							wav_count = sum(1 for item in zf.namelist() if item.endswith(".wav"))
							
							packs.append({
								"id": f,
								"filepath": pack_path,
								"name": meta.get("name", "Tanpa Nama"),
								"author": meta.get("author", "Anonim"),
								"description": meta.get("description", ""),
								"is_draft": meta.get("is_draft", False),
								"password_hash": meta.get("password_hash", ""),
								"is_permanent": meta.get("is_permanent", False),
								"recorded_words": wav_count,
								"total_words": 70
							})
				except Exception:
					pass
		return packs
		
	def extract_for_edit(self, pack_filepath):
		if not os.path.exists(pack_filepath): return None
		if os.path.exists(self.temp_session_dir):
			import shutil
			shutil.rmtree(self.temp_session_dir, ignore_errors=True)
		os.makedirs(self.temp_session_dir, exist_ok=True)
		
		import zipfile
		import json
		try:
			with zipfile.ZipFile(pack_filepath, 'r') as zf:
				zf.extractall(self.temp_session_dir)
			
			manifest_path = os.path.join(self.temp_session_dir, "manifest.json")
			if os.path.exists(manifest_path):
				with open(manifest_path, "r", encoding="utf-8") as f:
					meta = json.load(f)
				return meta
		except Exception as e:
			from .logger import jk_log
			jk_log.error(f"JadwalKu: Gagal ekstrak voice pack untuk diedit: {e}")
		return None

	def extract_pack_to_temp(self, pack_filepath):
		"""Mengekstrak paket (.jvp) untuk digunakan secara langsung ke folder temporary."""
		# Ekstrak ke folder spesifik untuk playback
		playback_dir = os.path.join(tempfile.gettempdir(), "jadwalku_voice_playback")
		if os.path.exists(playback_dir):
			shutil.rmtree(playback_dir, ignore_errors=True)
		os.makedirs(playback_dir, exist_ok=True)
		
		try:
			with zipfile.ZipFile(pack_filepath, 'r') as zf:
				zf.extractall(playback_dir)
			return playback_dir
		except Exception:
			return None

	def install_pack(self, temp_path):
		"""Memasang paket suara dari lokasi sementara ke direktori lokal JadwalKu."""
		if not os.path.exists(temp_path):
			return False
		try:
			import shutil
			import zipfile
			# Verifikasi integritas zip
			with zipfile.ZipFile(temp_path, 'r') as zf:
				if "manifest.json" not in zf.namelist():
					return False
			
			dest_path = os.path.join(self.pack_dir, os.path.basename(temp_path))
			shutil.copy2(temp_path, dest_path)
			return True
		except Exception:
			return False
