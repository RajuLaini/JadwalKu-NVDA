# -*- coding: UTF-8 -*-
import os
import json
import uuid
import logHandler

try:
	import globalVars
	CONFIG_DIR = globalVars.appArgs.configPath if hasattr(globalVars, 'appArgs') and globalVars.appArgs.configPath else os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "nvda")
except Exception:
	CONFIG_DIR = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "nvda")

DATA_FILE = os.path.join(CONFIG_DIR, "jadwalku_data.json")

DEFAULT_DATA = {
	"update_url": "https://raw.githubusercontent.com/RajuLaini/JadwalKu-NVDA/main/version.json",
	"update_token": "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",
	"audio_device": "Default (Microsoft Sound Mapper)",
	"time_reminder": {
		"enabled": False,
		"interval": 60,         # Pilihan: 5, 10, 15, 30, 60 (menit)
		"mode": "both",         # Pilihan: "both" (Bicara + Chime), "speech" (Hanya Bicara), "audio" (Hanya Chime)
		"start_hour": 0,        # 00:00
		"end_hour": 23,         # 23:59
		"last_triggered_minute": "" # Caching agar tidak bunyi 2x di menit yang sama
	},
	"schedules": [
		{
			"id": str(uuid.uuid4()),
			"name": "Minum Air & Istirahat Mata",
			"frequency": "Setiap Hari",
			"hour": 10,
			"minute": 0,
			"speech_enabled": True,
			"audio_enabled": True,
			"audio_file": "chime.wav",
			"active": True,
			"last_triggered_date": ""
		},
		{
			"id": str(uuid.uuid4()),
			"name": "Olahraga & Stretching Pagi",
			"frequency": "Setiap Hari",
			"hour": 6,
			"minute": 30,
			"speech_enabled": True,
			"audio_enabled": True,
			"audio_file": "bell.wav",
			"active": False,
			"last_triggered_date": ""
		}
	]
}


class ConfigManager:
	def __init__(self):
		self.data = {}
		self.load_data()

	def load_data(self):
		if not os.path.exists(DATA_FILE):
			self.data = DEFAULT_DATA.copy()
			self.save_data()
		else:
			try:
				with open(DATA_FILE, "r", encoding="utf-8") as f:
					self.data = json.load(f)
				# Pastikan struktur kunci lengkap jika dari versi lama
				if "time_reminder" not in self.data:
					self.data["time_reminder"] = DEFAULT_DATA["time_reminder"].copy()
				if "schedules" not in self.data:
					self.data["schedules"] = DEFAULT_DATA["schedules"].copy()
				if "update_token" not in self.data:
					self.data["update_token"] = DEFAULT_DATA["update_token"]
				if "audio_device" not in self.data:
					self.data["audio_device"] = DEFAULT_DATA["audio_device"]
				self.save_data()
			except Exception as e:
				logHandler.log.error(f"JadwalKu: Gagal memuat jadwalku_data.json: {e}")
				self.data = DEFAULT_DATA.copy()
				self.save_data()

	def save_data(self):
		try:
			# Pastikan direktori ada
			os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
			with open(DATA_FILE, "w", encoding="utf-8") as f:
				json.dump(self.data, f, indent=4, ensure_ascii=False)
		except Exception as e:
			logHandler.log.error(f"JadwalKu: Gagal menyimpan jadwalku_data.json: {e}")

	def get_schedules(self):
		return self.data.get("schedules", [])

	def get_schedule_by_id(self, schedule_id):
		for item in self.get_schedules():
			if item.get("id") == schedule_id:
				return item
		return None

	def add_schedule(self, schedule_dict):
		if "id" not in schedule_dict or not schedule_dict["id"]:
			schedule_dict["id"] = str(uuid.uuid4())
		if "last_triggered_date" not in schedule_dict:
			schedule_dict["last_triggered_date"] = ""
		self.data.setdefault("schedules", []).append(schedule_dict)
		self.save_data()
		return schedule_dict["id"]

	def update_schedule(self, schedule_id, updated_dict):
		schedules = self.get_schedules()
		for i, item in enumerate(schedules):
			if item.get("id") == schedule_id:
				updated_dict["id"] = schedule_id
				if "last_triggered_date" not in updated_dict:
					updated_dict["last_triggered_date"] = item.get("last_triggered_date", "")
				schedules[i] = updated_dict
				self.save_data()
				return True
		return False

	def delete_schedule(self, schedule_id):
		schedules = self.get_schedules()
		initial_len = len(schedules)
		self.data["schedules"] = [item for item in schedules if item.get("id") != schedule_id]
		if len(self.data["schedules"]) < initial_len:
			self.save_data()
			return True
		return False

	def toggle_schedule_active(self, schedule_id):
		for item in self.get_schedules():
			if item.get("id") == schedule_id:
				item["active"] = not item.get("active", False)
				self.save_data()
				return item["active"]
		return None

	def get_time_reminder_config(self):
		return self.data.get("time_reminder", DEFAULT_DATA["time_reminder"].copy())

	def update_time_reminder_config(self, updated_dict):
		if "time_reminder" not in self.data:
			self.data["time_reminder"] = {}
		self.data["time_reminder"].update(updated_dict)
		self.save_data()

	def get_audio_device(self):
		return self.data.get("audio_device", "Default (Microsoft Sound Mapper)")

	def set_audio_device(self, device_name):
		self.data["audio_device"] = device_name
		self.save_data()
