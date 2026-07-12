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

CURRENT_VERSION = "1.0.0"

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
			req = urllib.request.Request(update_url, headers={'User-Agent': 'NVDA-JadwalKu-Addon/1.0'})
			with urllib.request.urlopen(req, timeout=12) as response:
				data = json.loads(response.read().decode('utf-8'))
			
			remote_ver = str(data.get("version", "")).strip()
			changelog = str(data.get("changelog", "Perbaikan bug dan peningkatan performa.")).strip()
			download_url = str(data.get("download_url", "")).strip()

			if not remote_ver:
				if is_manual:
					wx.CallAfter(ui.message, "Informasi versi dari server tidak valid.")
				return

			# Perbandingan sederhana versi (misal "1.1.0" > "1.0.0")
			if self._is_newer_version(remote_ver, CURRENT_VERSION):
				if not self.update_dismissed_this_session:
					wx.CallAfter(self._show_update_prompt, remote_ver, changelog, download_url)
			else:
				if is_manual:
					wx.CallAfter(ui.message, f"JadwalKu Anda sudah menggunakan versi terbaru ({CURRENT_VERSION}).")

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

	def _show_update_prompt(self, remote_ver, changelog, download_url):
		if self.plugin and not self.plugin.check_dialog_open():
			return
		
		if self.plugin:
			self.plugin.is_dialog_open = True
		gui.mainFrame.prePopup()
		try:
			prompt_text = (
				f"Tersedia pembaruan baru untuk add-on JadwalKu!\n\n"
				f"Versi Terbaru: {remote_ver} (Versi saat ini: {CURRENT_VERSION})\n\n"
				f"Catatan Perubahan:\n{changelog}\n\n"
				f"Apakah Anda ingin mengunduh dan memperbarui sekarang?\n\n"
				f"(Catatan: Jika Anda memilih 'No / Tidak', pemeriksaan pembaruan otomatis akan dihentikan sementara hingga NVDA dimuat ulang)."
			)
			res = wx.MessageBox(prompt_text, "Pembaruan JadwalKu Tersedia", wx.YES_NO | wx.ICON_INFORMATION, gui.mainFrame)
			
			if res == wx.YES:
				if download_url:
					ui.message("Membuka tautan unduhan di browser Anda...")
					webbrowser.open(download_url)
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
