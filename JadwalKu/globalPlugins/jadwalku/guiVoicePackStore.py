import wx
import os
import threading
import urllib.request
import urllib.error
import urllib.parse
import json
import zipfile
import shutil
import tempfile
import getpass
import platform
import subprocess

API_URL = "https://jadwalku-vp-api.onionknight610.workers.dev"

def get_hardware_id():
	# Generate unique ID based on Windows Product ID and Processor ID
	# If WMI fails, fallback to something else
	try:
		hw_id = ""
		# Simple fast fallback instead of slow WMI:
		hw_id += platform.node() + "_" + getpass.getuser()
		return hw_id
	except:
		return "unknown_device_001"

class VoicePackStoreDialog(wx.Dialog):
	def __init__(self, parent, add_on_dir, vp_manager):
		super().__init__(parent, title="JadwalKu Voice Pack Store", size=(700, 500), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
		self.add_on_dir = add_on_dir
		self.vp_manager = vp_manager
		self.hardware_id = get_hardware_id()
		
		main_sizer = wx.BoxSizer(wx.VERTICAL)
		
		info = wx.StaticText(self, label="Selamat datang di JadwalKu Voice Pack Store!\nDi sini Anda dapat mengunduh paket suara dari pengguna lain atau membagikan karya Anda sendiri.")
		main_sizer.Add(info, 0, wx.ALL, 10)
		
		# List of voice packs
		self.list_ctrl = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.BORDER_SUNKEN)
		self.list_ctrl.InsertColumn(0, "Nama Paket", width=200)
		self.list_ctrl.InsertColumn(1, "Pembuat", width=150)
		self.list_ctrl.InsertColumn(2, "Tanggal", width=150)
		self.list_ctrl.InsertColumn(3, "Unduhan", width=80)
		main_sizer.Add(self.list_ctrl, 1, wx.EXPAND | wx.ALL, 10)
		
		self.packs_data = []
		
		btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
		self.btn_download = wx.Button(self, label="&Unduh & Pasang")
		self.btn_download.Bind(wx.EVT_BUTTON, self.onDownload)
		btn_sizer.Add(self.btn_download, 0, wx.ALL, 5)
		
		self.btn_upload = wx.Button(self, label="&Unggah Paket Saya")
		self.btn_upload.Bind(wx.EVT_BUTTON, self.onUpload)
		btn_sizer.Add(self.btn_upload, 0, wx.ALL, 5)
		
		self.btn_delete = wx.Button(self, label="&Hapus Paket Saya")
		self.btn_delete.Bind(wx.EVT_BUTTON, self.onDelete)
		btn_sizer.Add(self.btn_delete, 0, wx.ALL, 5)
		
		self.btn_refresh = wx.Button(self, label="&Segarkan (Refresh)")
		self.btn_refresh.Bind(wx.EVT_BUTTON, self.onRefresh)
		btn_sizer.Add(self.btn_refresh, 0, wx.ALL, 5)
		
		self.btn_close = wx.Button(self, wx.ID_CANCEL, label="&Tutup")
		btn_sizer.Add(self.btn_close, 0, wx.ALL, 5)
		
		main_sizer.Add(btn_sizer, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)
		
		self.SetSizer(main_sizer)
		self.CenterOnParent()
		
		self.refreshList()

	def onRefresh(self, event):
		self.refreshList()

	def refreshList(self):
		self.list_ctrl.DeleteAllItems()
		self.packs_data = []
		
		def worker():
			try:
				req = urllib.request.Request(f"{API_URL}/list", headers={'User-Agent': 'JadwalKu-NVDA'})
				with urllib.request.urlopen(req, timeout=15) as resp:
					data = json.loads(resp.read().decode('utf-8'))
					if data.get('success'):
						wx.CallAfter(self.populateList, data.get('data', []))
					else:
						wx.CallAfter(self.showError, data.get('message', 'Unknown error'))
			except Exception as e:
				wx.CallAfter(self.showError, str(e))
		
		threading.Thread(target=worker).start()

	def populateList(self, data):
		for p in data:
			idx = self.list_ctrl.GetItemCount()
			filename = p.get("filename", "")
			if len(filename) > 9 and filename[8] == '_':
				disp_name = filename[9:]
			else:
				disp_name = filename
			
			if disp_name.endswith(".jvp"):
				disp_name = disp_name[:-4]
				
			self.list_ctrl.InsertItem(idx, disp_name)
			self.list_ctrl.SetItem(idx, 1, p.get("uploader", "Anonim"))
			
			raw_date = p.get("uploadDate", "")
			short_date = raw_date.split("T")[0] if "T" in raw_date else raw_date
			self.list_ctrl.SetItem(idx, 2, short_date)
			
			self.list_ctrl.SetItem(idx, 3, str(p.get("downloadCount", 0)))
			
			self.packs_data.append(p)
			
		if self.list_ctrl.GetItemCount() > 0:
			self.list_ctrl.Select(0)
			self.list_ctrl.SetFocus()

	def showError(self, msg):
		wx.MessageBox(f"Gagal mengambil daftar Store:\n{msg}", "Error Koneksi", wx.OK | wx.ICON_ERROR, self)

	def onDownload(self, event):
		sel = self.list_ctrl.GetFirstSelected()
		if sel < 0 or sel >= len(self.packs_data):
			return
		pack = self.packs_data[sel]
		
		dl_url = f"{API_URL}/download/{urllib.parse.quote(pack['hardwareId'])}"
		
		dlg = wx.ProgressDialog("Mengunduh", f"Sedang mengunduh {pack['filename']}...", maximum=100, parent=self, style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE)
		
		def worker():
			try:
				temp_path = os.path.join(tempfile.gettempdir(), pack['filename'])
				req = urllib.request.Request(dl_url, headers={'User-Agent': 'JadwalKu-NVDA'})
				
				# Download with progress
				with urllib.request.urlopen(req, timeout=30) as resp, open(temp_path, 'wb') as out_file:
					total_length = resp.headers.get('content-length')
					if total_length is None:
						out_file.write(resp.read())
					else:
						total_length = int(total_length)
						downloaded = 0
						while True:
							buffer = resp.read(8192)
							if not buffer:
								break
							downloaded += len(buffer)
							out_file.write(buffer)
							pct = int((downloaded / total_length) * 100)
							wx.CallAfter(dlg.Update, pct)
				
				# Install using VoicePackManager
				wx.CallAfter(dlg.Update, 100, "Memasang...")
				result = self.vp_manager.install_pack(temp_path)
				
				if result:
					wx.CallAfter(wx.MessageBox, "Paket suara berhasil dipasang!", "Sukses", wx.OK | wx.ICON_INFORMATION, self)
				else:
					wx.CallAfter(wx.MessageBox, "Gagal memasang paket suara.", "Error", wx.OK | wx.ICON_ERROR, self)
			except Exception as e:
				wx.CallAfter(wx.MessageBox, f"Gagal mengunduh: {str(e)}", "Error", wx.OK | wx.ICON_ERROR, self)
			finally:
				wx.CallAfter(dlg.Destroy)
		
		threading.Thread(target=worker).start()

	def onUpload(self, event):
		dlg = UploadDialog(self, self.vp_manager)
		if dlg.ShowModal() == wx.ID_OK:
			uploader_name = dlg.txt_name.GetValue().strip()
			password = dlg.txt_pwd.GetValue().strip()
			
			sel_idx = dlg.cb_pack.GetSelection()
			if sel_idx < 0 or not dlg.pack_list:
				wx.MessageBox("Silakan pilih paket suara yang valid terlebih dahulu!", "Peringatan", wx.OK | wx.ICON_WARNING, self)
				dlg.Destroy()
				return
				
			pack_meta = dlg.pack_list[sel_idx]
			pack_path = os.path.join(self.vp_manager.pack_dir, pack_meta['id'])
			pack_name = pack_meta['name']
			
			if not uploader_name or not password:
				wx.MessageBox("Semua field harus diisi!", "Peringatan", wx.OK | wx.ICON_WARNING, self)
				dlg.Destroy()
				return
				
			dlg.Destroy()
			self.doUpload(uploader_name, password, pack_path, pack_name)
		else:
			dlg.Destroy()
			
	def doUpload(self, uploader_name, password, pack_path, pack_name):
		# Upload to server
		prog_dlg = wx.ProgressDialog("Mengunggah", f"Sedang mengunggah paket {pack_name}...", maximum=100, parent=self, style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE)
		prog_dlg.Pulse("Mohon tunggu...")
		
		def worker():
			try:
				with open(pack_path, 'rb') as f:
					body_bytes = f.read()
				
				headers = {
					'Content-Type': 'application/octet-stream',
					'Content-Length': str(len(body_bytes)),
					'X-Hardware-ID': self.hardware_id,
					'X-Password': password,
					'X-Uploader-Name': urllib.parse.quote(uploader_name),
					'X-Pack-Name': urllib.parse.quote(pack_name),
					'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
				}
				
				req = urllib.request.Request(f"{API_URL}/upload", data=body_bytes, headers=headers, method='POST')
				with urllib.request.urlopen(req, timeout=60) as resp:
					resp_data = json.loads(resp.read().decode('utf-8'))
					
					def on_success():
						prog_dlg.Destroy()
						wx.MessageBox("Berhasil mengunggah paket suara!", "Sukses", wx.OK | wx.ICON_INFORMATION, self)
						self.refreshList()
						
					def on_failure(msg):
						prog_dlg.Destroy()
						wx.MessageBox(f"Gagal mengunggah:\n{msg}", "Error", wx.OK | wx.ICON_ERROR, self)
					
					if resp_data.get('success'):
						wx.CallAfter(on_success)
					else:
						wx.CallAfter(on_failure, resp_data.get('message'))
			except Exception as e:
				def on_exception(err_details):
					prog_dlg.Destroy()
					wx.MessageBox(f"Koneksi gagal: {err_details}", "Error", wx.OK | wx.ICON_ERROR, self)
				
				err_details = str(e)
				if hasattr(e, 'read'):
					try:
						err_details += "\n\n" + e.read().decode('utf-8', errors='ignore')
					except:
						pass
				wx.CallAfter(on_exception, err_details)
					
		threading.Thread(target=worker).start()

	def onDelete(self, event):
		dlg = wx.TextEntryDialog(self, "Peringatan: Paket Anda di Store akan dihapus selamanya.\nMasukkan Kata Sandi yang Anda gunakan saat mengunggah:", "Konfirmasi Hapus Paket")
		if dlg.ShowModal() == wx.ID_OK:
			password = dlg.txt_pwd = dlg.GetValue()
			if not password:
				dlg.Destroy()
				return
				
			dlg.Destroy()
			
			def worker():
				try:
					req = urllib.request.Request(f"{API_URL}/delete", headers={'X-Hardware-ID': self.hardware_id, 'X-Password': password}, method='DELETE')
					with urllib.request.urlopen(req, timeout=15) as resp:
						resp_data = json.loads(resp.read().decode('utf-8'))
						if resp_data.get('success'):
							wx.CallAfter(wx.MessageBox, "Paket berhasil dihapus dari Store!", "Sukses", wx.OK | wx.ICON_INFORMATION, self)
							wx.CallAfter(self.refreshList)
						else:
							wx.CallAfter(wx.MessageBox, f"Gagal menghapus: {resp_data.get('message')}", "Error", wx.OK | wx.ICON_ERROR, self)
				except urllib.error.HTTPError as e:
					try:
						resp_data = json.loads(e.read().decode('utf-8'))
						wx.CallAfter(wx.MessageBox, f"Gagal menghapus: {resp_data.get('message')}", "Error", wx.OK | wx.ICON_ERROR, self)
					except:
						wx.CallAfter(wx.MessageBox, f"Koneksi ditolak (HTTP {e.code})", "Error", wx.OK | wx.ICON_ERROR, self)
				except Exception as e:
					wx.CallAfter(wx.MessageBox, f"Error: {str(e)}", "Error", wx.OK | wx.ICON_ERROR, self)
			
			threading.Thread(target=worker).start()
		else:
			dlg.Destroy()

class UploadDialog(wx.Dialog):
	def __init__(self, parent, vp_manager):
		super().__init__(parent, title="Unggah Paket Suara ke Store", size=(450, 380))
		self.vp_manager = vp_manager
		sizer = wx.BoxSizer(wx.VERTICAL)
		
		info = wx.StaticText(self, label="PENTING: Satu perangkat hanya diizinkan memiliki 1 paket di Store.\nJika Anda pernah mengunggah sebelumnya, ini akan menimpa (update) paket lama Anda.")
		info.Wrap(420)
		sizer.Add(info, 0, wx.ALL, 10)
		
		grid = wx.FlexGridSizer(3, 2, 10, 10)
		grid.AddGrowableCol(1)
		
		grid.Add(wx.StaticText(self, label="Pilih Paket:"), 0, wx.ALIGN_CENTER_VERTICAL)
		self.pack_list = [p for p in self.vp_manager.get_available_packs() if not p.get("is_draft")]
		pack_names = [p['name'] for p in self.pack_list]
		if not pack_names:
			pack_names = ["(Tidak ada paket)"]
		self.cb_pack = wx.Choice(self, choices=pack_names)
		if pack_names[0] != "(Tidak ada paket)":
			self.cb_pack.SetSelection(0)
		grid.Add(self.cb_pack, 1, wx.EXPAND)
		
		grid.Add(wx.StaticText(self, label="Nama Anda (Pengunggah):"), 0, wx.ALIGN_CENTER_VERTICAL)
		self.txt_name = wx.TextCtrl(self, value=getpass.getuser())
		grid.Add(self.txt_name, 1, wx.EXPAND)
		
		grid.Add(wx.StaticText(self, label="Kata Sandi Rahasia:"), 0, wx.ALIGN_CENTER_VERTICAL)
		self.txt_pwd = wx.TextCtrl(self, style=wx.TE_PASSWORD)
		grid.Add(self.txt_pwd, 1, wx.EXPAND)
		
		sizer.Add(grid, 1, wx.EXPAND | wx.ALL, 10)
		
		pwd_warn = wx.StaticText(self, label="*Simpan kata sandi ini! Anda akan membutuhkannya jika suatu saat ingin menghapus atau memperbarui paket ini di Store.")
		pwd_warn.Wrap(380)
		sizer.Add(pwd_warn, 0, wx.ALL, 10)
		
		btn_sizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
		sizer.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 10)
		
		self.SetSizer(sizer)
		self.CenterOnParent()
		
		# Set initial focus to the dropdown instead of the OK button
		wx.CallAfter(self.cb_pack.SetFocus)
