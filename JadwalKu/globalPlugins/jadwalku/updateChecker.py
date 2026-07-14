# -*- coding: UTF-8 -*-
import wx
import threading
import urllib.request
import json
import webbrowser
import logHandler
import ui
import gui
import os
import tempfile

def get_current_version():
	try:
		import addonHandler
		addon = addonHandler.getCodeAddon()
		if addon and addon.manifest:
			v = str(addon.manifest.get("version", "")).strip()
			if v:
				return v
	except Exception:
		pass
	try:
		manifest_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "manifest.ini")
		if os.path.exists(manifest_path):
			with open(manifest_path, "r", encoding="utf-8") as f:
				for line in f:
					if line.strip().startswith("version"):
						return line.split("=")[1].strip().strip('"').strip("'")
	except Exception:
		pass
	return "1.4.1"

CURRENT_VERSION = get_current_version()

class UpdateChecker:
	def __init__(self, config_manager, plugin_instance=None):
		self.config = config_manager
		self.plugin = plugin_instance
		self.update_dismissed_this_session = False
		self.timer = wx.Timer()
		self.timer.Bind(wx.EVT_TIMER, self.on_timer_tick)

	def start_auto_check(self):
		# Cek pertama 25 detik setelah NVDA dimuat agar suara boot NVDA tidak terganggu
		wx.CallLater(25000, self.check_update_silent)
		# Cek berkala setiap 3 jam (10800000 milidetik) selama sesi NVDA berjalan
		self.timer.Start(10800000)
		logHandler.log.info("JadwalKu: Fitur auto-check update dimulai.")

	def stop(self):
		if self.timer.IsRunning():
			self.timer.Stop()

	def on_timer_tick(self, event):
		self.check_update_silent()

	def check_update_silent(self):
		# Jika pengguna sudah memilih "No" / Batal, maka berhenti memeriksa sampai NVDA dimuat ulang
		if self.update_dismissed_this_session:
			return
		threading.Thread(target=self._fetch_update_info, args=(False,), daemon=True).start()

	def check_update_manual(self):
		threading.Thread(target=self._fetch_update_info, args=(True,), daemon=True).start()

	def _fetch_update_info(self, is_manual=False):
		# Ambil URL dari konfigurasi, atau gunakan URL default github/gist info
		update_url = self.config.data.get("update_url", "https://raw.githubusercontent.com/RajuLaini/JadwalKu-NVDA/main/version.json")
		
		# Jika URL masih mengandung USERNAME (belum dikonfigurasi nyata oleh user), hindari error saat silent check
		if "USERNAME" in update_url:
			if is_manual:
				wx.CallAfter(ui.message, "URL pembaruan belum dikonfigurasi. Silakan atur repositori GitHub Anda terlebih dahulu.")
			return

		try:
			headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) NVDA-JadwalKu-Addon'}
			req = urllib.request.Request(update_url, headers=headers)
			try:
				with urllib.request.urlopen(req, timeout=12) as response:
					data = json.loads(response.read().decode('utf-8'))
			except Exception as e_pub:
				token = self.config.data.get("update_token", "").strip()
				if token:
					headers['Authorization'] = f"token {token}"
					req2 = urllib.request.Request(update_url, headers=headers)
					with urllib.request.urlopen(req2, timeout=12) as response:
						data = json.loads(response.read().decode('utf-8'))
				else:
					raise e_pub
			
			remote_ver = str(data.get("version", "")).strip()
			changelog = str(data.get("changelog", "Perbaikan bug dan peningkatan performa.")).strip()
			download_url = str(data.get("download_url", "")).strip()

			if not remote_ver:
				if is_manual:
					wx.CallAfter(ui.message, "Informasi versi dari server tidak valid.")
				return

			local_ver = get_current_version()
			if self._is_newer_version(remote_ver, local_ver):
				if not self.update_dismissed_this_session:
					wx.CallAfter(self._show_update_prompt, remote_ver, changelog, download_url, local_ver)
			else:
				if is_manual:
					wx.CallAfter(ui.message, f"JadwalKu Anda sudah menggunakan versi terbaru ({local_ver}).")

		except Exception as e:
			logHandler.log.warning(f"JadwalKu: Gagal memeriksa pembaruan: {e}")
			if is_manual:
				wx.CallAfter(ui.message, "Gagal memeriksa pembaruan. Periksa koneksi internet atau tautan server.")

	def _is_newer_version(self, remote_ver, local_ver):
		try:
			r_parts = [int(p) for p in remote_ver.split(".") if p.isdigit()]
			l_parts = [int(p) for p in local_ver.split(".") if p.isdigit()]
			return r_parts > l_parts
		except Exception:
			return remote_ver != local_ver and remote_ver > local_ver

	def _show_update_prompt(self, remote_ver, changelog, download_url, local_ver=None):
		if local_ver is None:
			local_ver = get_current_version()
		if self.plugin and not self.plugin.check_dialog_open():
			return
		
		if self.plugin:
			self.plugin.is_dialog_open = True
		gui.mainFrame.prePopup()
		try:
			prompt_text = (
				f"Tersedia pembaruan baru untuk add-on JadwalKu!\n\n"
				f"Versi Terbaru: {remote_ver} (Versi saat ini: {local_ver})\n\n"
				f"Catatan Perubahan:\n{changelog}\n\n"
				f"Apakah Anda ingin mengunduh dan memperbarui sekarang?\n\n"
				f"(Catatan: Jika Anda memilih 'No / Tidak', pemeriksaan pembaruan otomatis akan dihentikan sementara hingga NVDA dimuat ulang)."
			)
			res = wx.MessageBox(prompt_text, "Pembaruan JadwalKu Tersedia", wx.YES_NO | wx.ICON_INFORMATION, gui.mainFrame)
			
			if res == wx.YES:
				if download_url:
					ui.message("Mengunduh pembaruan JadwalKu di latar belakang tanpa membuka browser... Mohon tunggu.")
					threading.Thread(target=self._download_and_install_direct, args=(download_url,), daemon=True).start()
				else:
					ui.message("Tautan unduhan tidak tersedia di server.")
			else:
				self.update_dismissed_this_session = True
				ui.message("Pemeriksaan pembaruan otomatis dihentikan sampai NVDA dimuat ulang.")
				logHandler.log.info("JadwalKu: Pengguna menekan No pada pembaruan. Auto-check dihentikan untuk sesi ini.")
		finally:
			if self.plugin:
				self.plugin.is_dialog_open = False
			gui.mainFrame.postPopup()

	def _download_and_install_direct(self, download_url):
		try:
			headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) NVDA-JadwalKu-Addon'}
			req = urllib.request.Request(download_url, headers=headers)
			try:
				with urllib.request.urlopen(req, timeout=35) as response:
					data = response.read()
			except Exception as e_pub:
				token = self.config.data.get("update_token", "").strip()
				if token:
					headers['Authorization'] = f"token {token}"
					req2 = urllib.request.Request(download_url, headers=headers)
					with urllib.request.urlopen(req2, timeout=35) as response:
						data = response.read()
				else:
					raise e_pub
			
			temp_dir = tempfile.gettempdir()
			temp_file = os.path.join(temp_dir, "JadwalKu-update.nvda-addon")
			with open(temp_file, "wb") as f:
				f.write(data)
			
			logHandler.log.info(f"JadwalKu: Pembaruan berhasil diunduh ke {temp_file}")
			wx.CallAfter(ui.message, "Unduhan selesai! Menampilkan dialog pemasangan add-on NVDA...")
			wx.CallAfter(os.startfile, temp_file)
		except Exception as e:
			logHandler.log.warning(f"JadwalKu: Unduhan langsung di latar belakang gagal ({e}). Mengalihkan ke browser...")
			wx.CallAfter(ui.message, "Mengalihkan tautan unduhan ke browser...")
			wx.CallAfter(webbrowser.open, download_url)

