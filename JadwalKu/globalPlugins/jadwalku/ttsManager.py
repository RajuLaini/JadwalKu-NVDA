# -*- coding: UTF-8 -*-
import os
import tempfile
import threading
import logHandler
import ui

try:
	import comtypes.client
	COMTYPES_AVAILABLE = True
except Exception:
	COMTYPES_AVAILABLE = False


class TTSManager:
	def __init__(self, config_manager, audio_manager):
		self.config = config_manager
		self.audio = audio_manager
		self.lock = threading.Lock()
		self.temp_wav = os.path.join(tempfile.gettempdir(), "jadwalku_tts.wav")

	def is_enabled(self):
		cfg = self.config.get_tts_config()
		return cfg.get("enabled", False) and COMTYPES_AVAILABLE

	def get_available_voices(self):
		if not COMTYPES_AVAILABLE:
			return []
		voices_list = []
		try:
			voice = comtypes.client.CreateObject("SAPI.SpVoice")
			voices = voice.GetVoices()
			for i in range(voices.Count):
				try:
					item = voices.Item(i)
					desc = item.GetDescription()
					voices_list.append({"id": i, "name": desc})
				except Exception as e:
					continue
		except Exception as e:
			logHandler.log.error(f"JadwalKu TTSManager: Gagal memuat daftar suara SAPI: {e}")
		return voices_list

	def speak(self, text, volume_override=None):
		if not self.is_enabled():
			ui.message(text)
			return

		threading.Thread(target=self._worker_speak, args=(text, volume_override), daemon=True).start()

	def _worker_speak(self, text, volume_override=None):
		with self.lock:
			try:
				cfg = self.config.get_tts_config()
				voice_id = int(cfg.get("voice_id", 0))
				rate = int(cfg.get("rate", 0))
				volume = int(cfg.get("volume", 100))
				if volume_override is not None:
					volume = int(volume_override)
					# SAPI 5 Volume ranges from 0 to 100 natively.
					volume = max(0, min(100, volume))

				voice = comtypes.client.CreateObject("SAPI.SpVoice")
				voices = voice.GetVoices()
				if voice_id >= 0 and voice_id < voices.Count:
					voice.Voice = voices.Item(voice_id)

				voice.Rate = max(-10, min(10, rate))
				voice.Volume = max(0, min(100, volume))

				stream = comtypes.client.CreateObject("SAPI.SpFileStream")
				# 3 = SSFMCreateForWrite
				stream.Open(self.temp_wav, 3)
				voice.AudioOutputStream = stream
				voice.Speak(text, 0)
				stream.Close()

				# Putar melalui AudioManager agar tepat masuk ke speaker/kartu suara pilihan di JadwalKu
				self.audio.play_sound(self.temp_wav, is_tts=True)
			except Exception as e:
				logHandler.log.error(f"JadwalKu TTSManager: Gagal sintesis suara SAPI ({e}). Menggunakan NVDA fallback.")
				ui.message(text)

	def test_voice(self, voice_id, rate, volume):
		if not COMTYPES_AVAILABLE:
			ui.message("Sistem SAPI 5 (comtypes) tidak tersedia di sistem ini.")
			return

		test_text = "Halo, ini adalah contoh suara pengingat waktu berkala dan agenda dari JadwalKu."
		threading.Thread(
			target=self._worker_test,
			args=(voice_id, rate, volume, test_text),
			daemon=True
		).start()

	def _worker_test(self, voice_id, rate, volume, text):
		with self.lock:
			try:
				voice = comtypes.client.CreateObject("SAPI.SpVoice")
				voices = voice.GetVoices()
				if voice_id >= 0 and voice_id < voices.Count:
					voice.Voice = voices.Item(voice_id)

				voice.Rate = max(-10, min(10, int(rate)))
				voice.Volume = max(0, min(100, int(volume)))

				stream = comtypes.client.CreateObject("SAPI.SpFileStream")
				stream.Open(self.temp_wav, 3)
				voice.AudioOutputStream = stream
				voice.Speak(text, 0)
				stream.Close()

				ui.message("Memutar contoh suara TTS Mandiri...")
				self.audio.play_sound(self.temp_wav, is_tts=True)
			except Exception as e:
				logHandler.log.error(f"JadwalKu TTSManager: Gagal tes suara SAPI: {e}")
				ui.message(f"Gagal memutar suara tes SAPI: {e}")

	def stop(self):
		if self.audio:
			self.audio.stop_sound()
