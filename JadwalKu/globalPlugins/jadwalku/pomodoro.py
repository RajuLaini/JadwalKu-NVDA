# -*- coding: UTF-8 -*-
import wx
import ui
from .guiDialogs import ContextualHelpDialog
import gui
import time
import datetime
import os
import core

class PomodoroManager:
	def __init__(self, audio_manager, plugin=None):
		self.audio = audio_manager
		self.plugin = plugin
		
		self.is_active = False
		self.state = ""
		self.work_seconds = 0
		self.short_break_seconds = 0
		self.long_break_seconds = 0
		self.cycles = 0
		self.current_cycle = 0
		self.remaining_seconds = 0
		
		self.timer = wx.Timer()
		self.timer.Bind(wx.EVT_TIMER, self.on_tick)

	def start(self, work_min, short_break_min, long_break_min, cycles):
		self.stop(manual=False) # Ensure any previous timer is fully stopped
		self.work_seconds = work_min * 60
		self.short_break_seconds = short_break_min * 60
		self.long_break_seconds = long_break_min * 60
		self.cycles = cycles
		self.current_cycle = 1
		self.state = "Fokus"
		self.remaining_seconds = self.work_seconds
		self.is_active = True
		self.timer.Start(1000)
		ui.message(f"Pomodoro dimulai. Saat ini: Waktu {self.state} selama {work_min} menit.")

	def stop(self, manual=True):
		if self.timer.IsRunning():
			self.timer.Stop()
		self.is_active = False
		if manual:
			ui.message("Pomodoro Timer dihentikan.")

	def on_tick(self, event):
		if not self.is_active:
			return
		
		self.remaining_seconds -= 1
		
		if self.remaining_seconds <= 0:
			self.remaining_seconds = 0
			# Call transition via wx.CallAfter to prevent blocking the timer thread
			# in case audio playback or speech message takes time.
			wx.CallAfter(self.transition_state)
			
	def play_alarm(self):
		if self.audio:
			if hasattr(self.audio, "play_sound"):
				try:
					self.audio.play_sound("chime.wav", allow_overlap=True)
				except Exception as e:
					import logHandler
					logHandler.log.error(f"JadwalKu Pomodoro: Error playing alarm {e}")

	def transition_state(self):
		if not self.is_active:
			return
			
		self.play_alarm()
		if self.state == "Fokus":
			if self.current_cycle >= self.cycles and self.cycles > 0:
				self.state = "Istirahat Panjang"
				self.remaining_seconds = self.long_break_seconds
				ui.message(f"Waktu fokus habis! Sekarang waktunya Istirahat Panjang selama {self.long_break_seconds // 60} menit.")
			else:
				self.state = "Istirahat Pendek"
				self.remaining_seconds = self.short_break_seconds
				ui.message(f"Waktu fokus habis! Sekarang waktunya Istirahat Pendek selama {self.short_break_seconds // 60} menit.")
		elif self.state in ("Istirahat Pendek", "Istirahat Panjang"):
			if self.state == "Istirahat Panjang" and self.cycles > 0:
				self.stop(manual=False)
				ui.message("Siklus Pomodoro telah selesai sepenuhnya. Selamat beristirahat!")
				return
				
			self.current_cycle += 1
			self.state = "Fokus"
			self.remaining_seconds = self.work_seconds
			ui.message(f"Waktu istirahat selesai! Kembali Fokus untuk siklus ke-{self.current_cycle}. Selamat bekerja selama {self.work_seconds // 60} menit!")

	def get_status_str(self):
		if not self.is_active:
			return "Pomodoro tidak aktif."
		mins, secs = divmod(self.remaining_seconds, 60)
		return f"Pomodoro: Waktu {self.state}, sisa {mins} menit {secs} detik. (Siklus {self.current_cycle}/{self.cycles})"


class PomodoroTimerDialog(wx.Dialog):
	def __init__(self, parent, manager):
		super().__init__(parent, title="Mode Asisten Produktivitas (Percobaan)", size=(450, 400), style=wx.DEFAULT_DIALOG_STYLE)
		self.manager = manager
		sizer = wx.BoxSizer(wx.VERTICAL)
		
		info_label = wx.StaticText(self, label="Atur waktu untuk teknik Pomodoro Anda:")
		sizer.Add(info_label, 0, wx.ALL, 10)
		
		grid = wx.FlexGridSizer(4, 2, 10, 10)
		
		# Waktu Fokus
		lbl_work = wx.StaticText(self, label="Waktu &Fokus (Menit):")
		self.txt_work = wx.TextCtrl(self, value="25")
		grid.Add(lbl_work, 0, wx.ALIGN_CENTER_VERTICAL)
		grid.Add(self.txt_work, 1, wx.EXPAND)
		
		# Waktu Istirahat Pendek
		lbl_short = wx.StaticText(self, label="Waktu Istirahat &Pendek (Menit):")
		self.txt_short = wx.TextCtrl(self, value="5")
		grid.Add(lbl_short, 0, wx.ALIGN_CENTER_VERTICAL)
		grid.Add(self.txt_short, 1, wx.EXPAND)
		
		# Waktu Istirahat Panjang
		lbl_long = wx.StaticText(self, label="Waktu Istirahat P&anjang (Menit):")
		self.txt_long = wx.TextCtrl(self, value="15")
		grid.Add(lbl_long, 0, wx.ALIGN_CENTER_VERTICAL)
		grid.Add(self.txt_long, 1, wx.EXPAND)
		
		# Siklus
		lbl_cycles = wx.StaticText(self, label="&Siklus sebelum istirahat panjang:")
		self.txt_cycles = wx.TextCtrl(self, value="4")
		grid.Add(lbl_cycles, 0, wx.ALIGN_CENTER_VERTICAL)
		grid.Add(self.txt_cycles, 1, wx.EXPAND)
		
		sizer.Add(grid, 1, wx.ALL | wx.EXPAND, 10)
		
		if self.manager.is_active:
			stat_lbl = wx.StaticText(self, label=f"Status: {self.manager.get_status_str()}")
			sizer.Add(stat_lbl, 0, wx.ALL, 10)
		
		btn_sizer = wx.StdDialogButtonSizer()
		
		if self.manager.is_active:
			btn_stop = wx.Button(self, label="Ber&henti")
			btn_stop.Bind(wx.EVT_BUTTON, self.onStop)
			btn_sizer.AddButton(btn_stop)
		else:
			btn_start = wx.Button(self, label="Mula&i")
			btn_start.Bind(wx.EVT_BUTTON, self.onStart)
			btn_start.SetDefault()
			btn_sizer.AddButton(btn_start)
		
		btn_cancel = wx.Button(self, wx.ID_CANCEL, label="&Tutup")
		btn_help = wx.Button(self, label="&Bantuan... (Alt+B)")
		btn_help.Bind(wx.EVT_BUTTON, self.onContextualHelp)
		btn_sizer.AddButton(btn_cancel)
		btn_sizer.AddButton(btn_help)
		btn_sizer.Realize()
		
		sizer.Add(btn_sizer, 0, wx.ALL | wx.ALIGN_RIGHT, 10)
		self.SetSizer(sizer)
		
		if not self.manager.is_active:
			self.txt_work.SetFocus()
		else:
			btn_cancel.SetFocus()

	def onContextualHelp(self, event):
		try:
			from .guiDialogs import HelpDialog
			dlg = HelpDialog(self.GetParent())
			dlg.ShowModal()
			dlg.Destroy()
		except Exception as e:
			import logHandler
			logHandler.log.error(f"Error opening help from pomodoro: {e}")

	def onStart(self, event):
		try:
			work_min = int(self.txt_work.GetValue())
			short_min = int(self.txt_short.GetValue())
			long_min = int(self.txt_long.GetValue())
			cycles = int(self.txt_cycles.GetValue())
			if work_min <= 0 or short_min <= 0:
				wx.MessageBox("Waktu harus lebih dari 0 menit.", "Error", wx.OK | wx.ICON_ERROR, self)
				return
		except ValueError:
			wx.MessageBox("Harap masukkan angka yang valid.", "Error", wx.OK | wx.ICON_ERROR, self)
			return
		
		self.manager.start(work_min, short_min, long_min, cycles)
		self.Destroy()

	def onStop(self, event):
		self.manager.stop(manual=True)
		self.Destroy()
