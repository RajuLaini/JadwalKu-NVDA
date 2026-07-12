# -*- coding: UTF-8 -*-
import os
import logHandler
import nvwave
import ui

SOUNDS_DIR = os.path.join(os.path.dirname(__file__), "sounds")

class AudioManager:
	def __init__(self):
		self.last_played_file = None

	def get_sound_path(self, filename):
		if not filename:
			return None
		path = os.path.join(SOUNDS_DIR, filename)
		if os.path.exists(path):
			return path
		return None

	def play_sound(self, filename):
		path = self.get_sound_path(filename)
		if not path:
			# Coba fallback jika tidak ada eksistensi file
			if os.path.exists(filename):
				path = filename
		
		if path and os.path.exists(path):
			try:
				# nvwave.playWaveFile mendukung pemutaran file .wav secara non-blocking
				nvwave.playWaveFile(path)
				self.last_played_file = path
				return True
			except Exception as e:
				logHandler.log.error(f"JadwalKu: Gagal memutar file suara '{path}': {e}")
		return False

	def stop_sound(self):
		try:
			# Untuk menghentikan audio di nvwave, kita bisa memutar string kosong atau None bila didukung
			# Atau panggil nvwave.playWaveFile("") jika diizinkan oleh NVDA.
			try:
				nvwave.playWaveFile("")
			except Exception:
				pass
			logHandler.log.info("JadwalKu: Audio dihentikan.")
			return True
		except Exception as e:
			logHandler.log.error(f"JadwalKu: Gagal stop audio: {e}")
			return False

	def notify(self, title, message, speech_enabled=True, audio_enabled=True, audio_file="chime.wav"):
		if audio_enabled and audio_file:
			self.play_sound(audio_file)
		
		if speech_enabled:
			# Gabungkan judul dan pesan untuk dibacakan oleh NVDA
			full_msg = f"{title}: {message}" if title else message
			ui.message(full_msg)
