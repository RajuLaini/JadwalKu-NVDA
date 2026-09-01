import os
import json
import time
from datetime import datetime, timedelta

class HabitManager:
	def __init__(self, data_dir):
		self.stats_file = os.path.join(data_dir, "habit_stats.json")
		self.stats = self._load_stats()
		
		# Define badge tiers
		self.badge_tiers = [
			{"id": "bronze", "name": "Lencana Perunggu", "days": 7},
			{"id": "silver", "name": "Lencana Perak", "days": 21},
			{"id": "gold", "name": "Lencana Emas", "days": 66},
			{"id": "platinum", "name": "Lencana Platinum", "days": 90},
			{"id": "diamond", "name": "Lencana Berlian", "days": 180},
			{"id": "legend", "name": "Lencana Legenda", "days": 365}
		]

	def _load_stats(self):
		if os.path.exists(self.stats_file):
			try:
				with open(self.stats_file, 'r', encoding='utf-8') as f:
					return json.load(f)
			except Exception:
				pass
		return {}

	def _save_stats(self):
		try:
			with open(self.stats_file, 'w', encoding='utf-8') as f:
				json.dump(self.stats, f, indent=4)
		except Exception:
			pass

	def get_today_str(self):
		return datetime.now().strftime("%Y-%m-%d")

	def check_and_reset_streaks(self):
		"""Reset streaks if yesterday was missed."""
		today = datetime.now()
		today_str = today.strftime("%Y-%m-%d")
		yesterday_str = (today - timedelta(days=1)).strftime("%Y-%m-%d")
		
		changed = False
		for sched_id, data in self.stats.items():
			last_date = data.get("last_daily_date", "")
			# If the last activity wasn't today and wasn't yesterday, the streak is broken
			if last_date and last_date != today_str and last_date != yesterday_str:
				if data.get("current_streak", 0) > 0:
					data["current_streak"] = 0
					changed = True
					
		if changed:
			self._save_stats()

	def ensure_schedule_exists(self, schedule_id, name):
		if schedule_id not in self.stats:
			self.stats[schedule_id] = {
				"name": name,
				"current_streak": 0,
				"longest_streak": 0,
				"total_completed": 0,
				"badges": {}, # e.g. {"bronze": "2026-08-10"}
				"last_daily_date": "",
				"daily_count": 0,
				"creation_date": self.get_today_str()
			}
			self._save_stats()

	def record_completion(self, schedule_id, name):
		self.ensure_schedule_exists(schedule_id, name)
		
		today_str = self.get_today_str()
		data = self.stats[schedule_id]
		
		# Always increment total completed
		data["total_completed"] = data.get("total_completed", 0) + 1
		
		new_badge_unlocked = None
		
		if data.get("last_daily_date") != today_str:
			# First completion of the day
			data["last_daily_date"] = today_str
			data["daily_count"] = 1
			data["current_streak"] = data.get("current_streak", 0) + 1
			
			if data["current_streak"] > data.get("longest_streak", 0):
				data["longest_streak"] = data["current_streak"]
				
			# Check for badges
			streak = data["current_streak"]
			for tier in self.badge_tiers:
				if streak >= tier["days"]:
					b_id = tier["id"]
					if b_id not in data["badges"]:
						data["badges"][b_id] = today_str
						new_badge_unlocked = tier["name"]
		else:
			# Already completed at least once today, just increment daily count
			data["daily_count"] = data.get("daily_count", 0) + 1
			
		self._save_stats()
		return new_badge_unlocked

	def get_highest_badge(self, schedule_id):
		data = self.stats.get(schedule_id, {})
		badges = data.get("badges", {})
		if not badges:
			return "Belum Ada Lencana"
		
		# Traverse backwards to find the highest unlocked
		for tier in reversed(self.badge_tiers):
			if tier["id"] in badges:
				return tier["name"]
		return "Belum Ada Lencana"

	def get_badge_history_text(self, schedule_id):
		data = self.stats.get(schedule_id, {})
		if not data:
			return "Riwayat kebiasaan tidak ditemukan."
			
		lines = []
		lines.append(f"Riwayat Ketekunan: {data.get('name', 'Jadwal')}")
		lines.append(f"Rentetan Aktif Saat Ini: {data.get('current_streak', 0)} Hari tanpa putus!")
		
		# Calculate next badge
		streak = data.get("current_streak", 0)
		next_badge = None
		for tier in self.badge_tiers:
			if streak < tier["days"]:
				next_badge = tier
				break
				
		if next_badge:
			rem = next_badge["days"] - streak
			lines.append(f"Sisa waktu menuju {next_badge['name']}: {rem} Hari lagi.")
		else:
			lines.append("Anda telah mencapai Lencana Tertinggi (Legenda)!")
			
		lines.append("")
		lines.append("Jejak Lencana:")
		badges = data.get("badges", {})
		for tier in self.badge_tiers:
			b_id = tier["id"]
			if b_id in badges:
				date_str = badges[b_id]
				lines.append(f"- {tier['name']} ({tier['days']} Hari): Diraih pada {date_str}.")
			else:
				lines.append(f"- {tier['name']} ({tier['days']} Hari): Terkunci 🔒")
				
		lines.append("")
		lines.append(f"Total Keseluruhan: Anda telah menyelesaikan jadwal ini sebanyak {data.get('total_completed', 0)} kali semenjak jadwal ini dibuat.")
		lines.append("")
		lines.append("Catatan Aturan Ketekunan: Untuk jadwal berulang dalam sehari (misal tiap 2 jam), Anda hanya perlu menandainya 'Selesai' minimal 1 kali saja dalam sehari untuk mengamankan dan memajukan rentetan hari (streak) Anda menuju Lencana berikutnya.")
		lines.append("")
		lines.append("Pesan Pengingat: Lencana ini dibuat jujur untuk membangun ketekunan bagi Kita. Jadi apa pun yang Anda lakukan untuk mengubah data, itu hak pribadi Anda sebagai pembangun diri. Marilah Kita belajar jujur, mari Kita capai kesuksesan bersama!")
		
		return "\n".join(lines)
		
	def get_daily_count(self, schedule_id):
		today_str = self.get_today_str()
		data = self.stats.get(schedule_id, {})
		if data.get("last_daily_date") == today_str:
			return data.get("daily_count", 0)
		return 0

	def get_all_habits_summary(self):
		"""Returns a list of dicts suitable for the Badge Showcase dialog"""
		results = []
		for sched_id, data in self.stats.items():
			highest = self.get_highest_badge(sched_id)
			results.append({
				"id": sched_id,
				"name": data.get("name", "Jadwal"),
				"highest_badge": highest
			})
		return results
