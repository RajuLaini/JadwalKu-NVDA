# -*- coding: UTF-8 -*-
import os
import json
import urllib.request
import urllib.error
import threading
import datetime
import platform
import logHandler
import wx
import api

def get_username():
	try:
		return os.getlogin()
	except Exception:
		try:
			import getpass
			return getpass.getuser()
		except Exception:
			return os.environ.get("USERNAME", "Pengguna NVDA")

def get_machine_name():
	try:
		return platform.node() or os.environ.get("COMPUTERNAME", "PC-Windows")
	except Exception:
		return "PC-Windows"

def get_addon_version():
	try:
		import addonHandler
		addon = addonHandler.getCodeAddon()
		if addon: return addon.manifest['version']
	except Exception:
		pass
	return "Unknown"

def get_nvda_version():
	try:
		import versionInfo
		return str(getattr(versionInfo, "version", "NVDA"))
	except Exception:
		return "NVDA Modern"

def extract_recent_logs(max_lines=100):
	try:
		import globalVars
		log_path = getattr(globalVars.appArgs, 'logFileName', None)
		if not log_path and hasattr(logHandler, 'getLogFileName'):
			log_path = logHandler.getLogFileName()
		if not log_path or not os.path.exists(log_path):
			return "File log NVDA tidak ditemukan."
		
		import collections
		with open(log_path, "r", encoding="utf-8", errors="replace") as f:
			lines = list(collections.deque(f, maxlen=3000))
		
		# Ambil baris-baris yang relevan dengan JadwalKu atau Error
		relevant = []
		keywords = ["jadwalku", "exception", "traceback", "error", "audiomanager", "ttsmanager", "scheduler", "guidialogs", "voicecommand", "vosk", "vp:"]
		
		include_next = False
		for line in lines[-1000:]: # periksa 1000 baris terakhir
			lower_line = line.lower()
			
			if any(k in lower_line for k in keywords):
				relevant.append(line.strip('\r\n'))
				include_next = True if "traceback" in lower_line or "exception" in lower_line else False
			elif include_next and line.startswith((' ', '\t')):
				relevant.append(line.strip('\r\n'))
			else:
				include_next = False
		
		if not relevant:
			relevant = [l.strip('\r\n') for l in lines[-20:] if l.strip('\r\n')]
			
		# Ambil maksimal max_lines terakhir
		return "\n".join(relevant[-max_lines:])
	except Exception as e:
		return f"Gagal mengekstrak log NVDA: {e}"

def check_can_send_report(config_manager):
	"""
	Memeriksa apakah pengguna atau server masih mengizinkan pengiriman laporan hari ini.
	Mengembalikan tuple: (allowed: bool, reason_message: str)
	"""
	try:
		today_str = datetime.date.today().strftime("%Y-%m-%d")
		if config_manager.get_last_report_date() == today_str:
			return (False, "Mohon maaf, Anda sudah mengirimkan satu laporan atau saran hari ini. Setiap pengguna dibatasi maksimal 1 kali request per hari demi menjaga kenyamanan bersama.")
		
		cfg = config_manager.get_feedback_config()
		proxy_url = cfg.get("proxy_url", "https://butterflywings.my.id/api/jadwalku/proxy")
		
		check_url = f"{proxy_url}?action=check_limit&date={today_str}"
		req = urllib.request.Request(
			check_url,
			headers={
				"Content-Type": "application/json; charset=utf-8",
				"User-Agent": f"JadwalKu-NVDA-Addon/{get_addon_version()}"
			}
		)
		
		with urllib.request.urlopen(req, timeout=15.0) as resp:
			data = json.loads(resp.read().decode("utf-8", errors="replace"))
			if data.get("allowed") is False:
				msg = data.get("message", "Mohon maaf, kuota penerimaan laporan JadwalKu untuk hari ini telah penuh. Silakan coba kembali besok pagi!")
				return (False, msg)
	except urllib.error.HTTPError as e:
		if e.code == 429:
			try:
				data = json.loads(e.read().decode("utf-8", errors="replace"))
				return (False, data.get("message", "Mohon maaf, kuota penerimaan laporan JadwalKu untuk hari ini telah penuh. Silakan coba kembali besok pagi!"))
			except Exception:
				return (False, "Mohon maaf, kuota penerimaan laporan JadwalKu untuk hari ini telah penuh. Silakan coba kembali besok pagi!")
	except Exception as e:
		logHandler.log.debug(f"JadwalKu: Cek limit laporan server offline/timeout ({e}), mengizinkan dialog dibuka.")
	
	return (True, "")

def send_report_async(config_manager, report_data, on_complete_callback):
	"""
	Mengirim laporan secara asinkron di thread terpisah.
	on_complete_callback menerima argumen: (success: bool, message: str)
	"""
	def worker():
		try:
			cfg = config_manager.get_feedback_config()
			proxy_url = cfg.get("proxy_url", "https://butterflywings.my.id/api/jadwalku/proxy")
			
			os_ver_str = f"{platform.system()} {platform.release()} ({platform.version()})"
			payload = {
				"username": report_data.get("username", get_username()),
				"machine_name": report_data.get("machine_name", get_machine_name()),
				"nvda_version": report_data.get("nvda_version", get_nvda_version()),
				"os_version": os_ver_str,
				"category": report_data.get("category", "Bug"),
				"sub_feature": report_data.get("sub_feature", ""),
				"title": report_data.get("title", "Laporan JadwalKu"),
				"description": report_data.get("description", ""),
				"logs": report_data.get("logs", ""),
				"client_time": datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
			}
			
			json_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")
			req = urllib.request.Request(
				proxy_url,
				data=json_bytes,
				headers={
					"Content-Type": "application/json; charset=utf-8",
					"User-Agent": f"JadwalKu-NVDA-Addon/{get_addon_version()}"
				},
				method="POST"
			)
			
			try:
				with urllib.request.urlopen(req, timeout=15.0) as resp:
					status = resp.getcode()
					resp_body = json.loads(resp.read().decode("utf-8", errors="replace"))
					if status in (200, 201) and resp_body.get("success", True):
						today_str = datetime.date.today().strftime("%Y-%m-%d")
						config_manager.set_last_report_date(today_str)
						msg = resp_body.get("message", "Laporan Anda berhasil dikirim ke Bot Telegram pengembang (Aileen Bot). Terima kasih banyak atas kontribusi Anda!")
						wx.CallAfter(on_complete_callback, True, msg)
						return
					elif resp_body.get("allowed") is False or status == 429:
						msg = resp_body.get("message", "Mohon maaf, kuota penerimaan laporan JadwalKu untuk hari ini telah penuh. Silakan coba kembali besok!")
						wx.CallAfter(on_complete_callback, False, msg)
						return
					else:
						raise Exception(resp_body.get("message", f"HTTP {status}"))
			except urllib.error.HTTPError as e:
				if e.code in (400, 429):
					try:
						resp_body = json.loads(e.read().decode("utf-8", errors="replace"))
						msg = resp_body.get("message", "Mohon maaf, permintaan tidak dapat diproses atau kuota laporan telah habis.")
					except Exception:
						msg = "Mohon maaf, kuota harian telah penuh atau deskripsi laporan kurang lengkap."
					wx.CallAfter(on_complete_callback, False, msg)
					return
				else:
					raise
					
		except Exception as e:
			logHandler.log.error(f"JadwalKu: Gagal mengirim laporan ke server proxy: {e}")
			
			backup_text = (
				f"=== LAPORAN & SARAN JADWALKU (v1.6.2) ===\n"
				f"Kategori: {report_data.get('category', 'Laporan')}\n"
				f"Fitur/Sub-Kategori: {report_data.get('sub_feature', '-')}\n"
				f"Judul: {report_data.get('title', '-')}\n"
				f"Pengguna / Machine: {report_data.get('username', get_username())} ({report_data.get('machine_name', get_machine_name())})\n"
				f"Versi NVDA & OS: {get_nvda_version()} / {platform.platform()}\n"
				f"Waktu: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n"
				f"--- DESKRIPSI LAPORAN ---\n"
				f"{report_data.get('description', '')}\n\n"
				f"--- LOG DIAGNOSTIK OTOMATIS ---\n"
				f"{report_data.get('logs', 'Tidak ada log terlampir')}\n"
			)
			try:
				api.copyToClip(backup_text)
				msg = "Gagal terhubung ke server proxy Cloudflare (koneksi offline atau timeout). Jangan khawatir, seluruh isi laporan beserta log diagnostik Anda telah otomatis disalin ke clipboard! Anda dapat menempelkannya (Paste) langsung ke chat bot Telegram Aileen atau pengembang."
			except Exception:
				msg = f"Gagal mengirim laporan: {e}"
			
			wx.CallAfter(on_complete_callback, False, msg)

	t = threading.Thread(target=worker, daemon=True)
	t.start()
