import os
import wx
import gui
from .configManager import ConfigManager
import ui
import time
from .guiDialogs import (
    HelpDialog, QuickTimerDialog, JadwalKuDialog, WorldClockDialog, AgendaDialog
)

class DummyAudio:
    def __init__(self):
        self._override_volume = None
    def play_sound(self, *args, **kwargs):
        ui.message("Simulasi: Memutar suara.")
    def stop_sound(self):
        pass
    def get_available_output_devices(self):
        return ["Default (Microsoft Sound Mapper)"]
    def has_active_sounds(self):
        return False
    def play_voice_pack_sequence(self, *args, **kwargs):
        ui.message("Simulasi: Memutar urutan Voice Pack.")

class DummyScheduler:
    def __init__(self):
        pass
    def get_active_timers(self):
        return []
    def add_timer(self, *args, **kwargs):
        ui.message("Simulasi: Berhasil menambahkan timer!")
        return True

class DummyTTS:
    def __init__(self):
        pass
    def play_text(self, text):
        ui.message(f"Simulasi TTS: {text}")
    def get_available_voices(self):
        return []
    def test_voice(self, v_id, rate, vol):
        ui.message("Simulasi: Percobaan TTS berjalan.")

class DummyConfig:
    def __init__(self):
        self.data = {"schedules": []}
    def get_schedules(self):
        return self.data["schedules"]
    def add_schedule(self, s):
        self.data["schedules"].append(s)
        ui.message("Simulasi: Jadwal berhasil ditambahkan ke daftar.")
    def set_schedules(self, s):
        self.data["schedules"] = s
    def get_audio_device(self):
        return "Default"
    def get_audio_volume(self):
        return 100
    def get_time_settings(self):
        return {"report_24h": True, "time_format": "24", "clock_mode": 1}
    def get_time_reminder_config(self):
        return {"enabled": False, "interval": 60, "sound": "chime.wav", "active_voice_pack": ""}
    def get_tts_config(self):
        return {"enabled": False, "rate": 50, "volume": 100, "voice": ""}
    def get_voice_command(self):
        return {"enabled": False}
    def update_schedule(self, id, updated):
        ui.message("Simulasi: Jadwal berhasil diperbarui.")
    def delete_schedule(self, id):
        ui.message("Simulasi: Jadwal berhasil dihapus.")
    def toggle_schedule_active(self, id):
        ui.message("Simulasi: Status jadwal diubah.")
        return True
    def update_time_reminder_config(self, data):
        ui.message("Simulasi: Pengaturan pengingat waktu disimpan.")
    def update_tts_config(self, data):
        ui.message("Simulasi: Pengaturan TTS disimpan.")
    def set_audio_device(self, dev):
        pass
    def set_audio_volume(self, vol):
        pass
    def update_time_settings(self, data):
        ui.message("Simulasi: Pengaturan waktu disimpan.")
    def update_voice_command(self, data):
        ui.message("Simulasi: Pengaturan Voice Command disimpan.")

# ==========================================================
# INTERACTIVE GUIDE ENGINE
# ==========================================================

class SimulationGuide:
    def __init__(self, dialog, steps, interval=5, on_complete=None, on_close=None, start_step=0):
        self.dialog = dialog
        self.steps = steps
        self.interval = interval
        self.current_step = start_step
        self.on_complete = on_complete
        self.on_close = on_close
        self.timer = wx.Timer(self.dialog)
        self.dialog.Bind(wx.EVT_TIMER, self.onTimer, self.timer)
        self.dialog.Bind(wx.EVT_CLOSE, self.onClose)
        self.dialog.Bind(wx.EVT_BUTTON, self.onClose, id=wx.ID_CANCEL)
        self.ticks = 0
        self.spoken = False
        self.setup_current_step()
        
    def setup_current_step(self):
        if self.current_step >= len(self.steps):
            self.timer.Stop()
            ui.message("Bagus sekali! Anda telah menyelesaikan latihan ini dengan sempurna.")
            if self.on_complete:
                self.on_complete()
            self.dialog.EndModal(wx.ID_OK)
            return
            
        step = self.steps[self.current_step]
        self.spoken = False
        self.ticks = 0
        
        if "pre_action" in step and step["pre_action"]:
            try:
                step["pre_action"]()
            except Exception:
                pass

        self.timer.Start(100) # 100ms per tick
        
        # Override behavior if needed (Only for actions)
        if "bind_target" in step and "bind_event" in step:
            if step["bind_event"] != wx.EVT_SET_FOCUS:
                def handler(evt):
                    if "bind_handler" in step and step["bind_handler"]:
                        step["bind_handler"](evt)
                    else:
                        self.advance_step()
                
                # Note: this replaces the existing binding for this event on the target!
                step["bind_target"].Bind(step["bind_event"], handler)
            
    def advance_step(self):
        self.timer.Stop()
        self.current_step += 1
        self.setup_current_step()
        
    def is_focused(self, target):
        focus = wx.Window.FindFocus()
        while focus:
            if focus == target:
                return True
            focus = focus.GetParent()
        return False
        
    def onTimer(self, evt):
        if self.current_step >= len(self.steps):
            return
            
        self.ticks += 1
        step = self.steps[self.current_step]
        
        # Speak after 1.5 seconds (15 ticks) and repeat every 7 seconds (70 ticks)
        if not self.spoken and self.ticks >= 15:
            ui.message(step["instruction"])
            self.spoken = True
        elif self.spoken and self.ticks >= 85:
            self.spoken = False
            self.ticks = 0
        
        # Poll for focus if the event is EVT_SET_FOCUS
        if "bind_target" in step and step.get("bind_event") == wx.EVT_SET_FOCUS:
            if self.is_focused(step["bind_target"]):
                self.advance_step()
                return

    def onClose(self, evt):
        self.timer.Stop()
        res = gui.messageBox(
            "Apakah Anda yakin ingin mengakhiri sesi latihan ini sebelum selesai? Anda dapat melanjutkannya nanti.",
            "Konfirmasi Keluar Simulasi",
            wx.YES_NO | wx.ICON_QUESTION,
            self.dialog
        )
        if res == wx.YES:
            ui.message("Simulasi dihentikan. Progres disimpan.")
            if self.on_close:
                self.on_close(self.current_step)
            self.dialog.EndModal(wx.ID_CANCEL)
        else:
            self.timer.Start(100)
            self.ticks = 0

class TutorialEntryDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="Pusat Bantuan & Tutorial JadwalKu", size=(400, 200), style=wx.DEFAULT_DIALOG_STYLE)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        info_label = wx.StaticText(self, label="Bagaimana Anda ingin mempelajari JadwalKu?")
        sizer.Add(info_label, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 15)
        
        btn_help = wx.Button(self, label="&1. Buka Panduan Teks Biasa")
        btn_help.Bind(wx.EVT_BUTTON, self.onTextHelp)
        sizer.Add(btn_help, 0, wx.EXPAND | wx.ALL, 10)
        
        btn_sim = wx.Button(self, label="&2. Mulai Tutorial Simulasi Interaktif (Ditutup Sementara)")
        btn_sim.Bind(wx.EVT_BUTTON, self.onSimulation)
        sizer.Add(btn_sim, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        
        btn_cancel = wx.Button(self, wx.ID_CANCEL, label="&Tutup")
        sizer.Add(btn_cancel, 0, wx.ALIGN_RIGHT | wx.ALL, 10)
        
        self.SetSizer(sizer)
        self.Centre()
        
    def onTextHelp(self, evt):
        self.EndModal(wx.ID_NO)
        
    def onSimulation(self, evt):
        self.EndModal(wx.ID_YES)

class SimulationWizardDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="Tutorial Simulasi JadwalKu", size=(600, 450), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.config = ConfigManager()
        progress = self.config.get_simulation_progress()
        
        self.stages = [
            {
                "title": "Tahap 1: Masterclass Jendela Utama & 4 Tab (Eksplorasi Menyeluruh)",
                "desc": "Mari jelajahi fitur JadwalKu tanpa hambatan! Mulai dari membuat jadwal, mengedit, menghapus, hingga menelusuri Pengaturan Waktu, Voice Pack, dan Voice Command.",
                "action": self.run_stage_1
            },
            {
                "title": "Tahap 2: Simulasi Fitur Ekstra (Quick Timer & Jam Dunia)",
                "desc": "Mari pelajari cara menyalakan Quick Timer untuk memasak, serta melihat selisih waktu atau tanggal merah dengan fitur Jam Dunia.",
                "action": self.run_stage_2
            }
        ]
        self.current_stage = progress["stage"] - 1 if progress["stage"] <= len(self.stages) else 0
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.lbl_progress = wx.StaticText(self, label="")
        font = self.lbl_progress.GetFont()
        font.MakeBold()
        self.lbl_progress.SetFont(font)
        sizer.Add(self.lbl_progress, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 10)
        
        self.lbl_title = wx.StaticText(self, label="")
        self.lbl_title.SetFont(font)
        sizer.Add(self.lbl_title, 0, wx.LEFT | wx.RIGHT | wx.TOP, 10)
        
        self.txt_desc = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2 | wx.HSCROLL)
        sizer.Add(self.txt_desc, 1, wx.EXPAND | wx.ALL, 10)
        
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.btn_action = wx.Button(self, label="&Mulai Latihan Ini (Enter)")
        self.btn_action.Bind(wx.EVT_BUTTON, self.onAction)
        self.btn_action.SetDefault()
        btn_sizer.Add(self.btn_action, 0, wx.ALL, 5)
        
        self.btn_repeat = wx.Button(self, label="&Ulangi Tahap Ini")
        self.btn_repeat.Bind(wx.EVT_BUTTON, self.onAction)
        self.btn_repeat.Hide()
        btn_sizer.Add(self.btn_repeat, 0, wx.ALL, 5)
        
        self.btn_next = wx.Button(self, label="Lanjut ke Tahap &Berikutnya")
        self.btn_next.Bind(wx.EVT_BUTTON, self.onNext)
        self.btn_next.Hide()
        btn_sizer.Add(self.btn_next, 0, wx.ALL, 5)
        
        self.btn_close = wx.Button(self, wx.ID_CANCEL, label="&Tutup Simulasi (Esc)")
        self.btn_close.Bind(wx.EVT_BUTTON, lambda evt: self.EndModal(wx.ID_CANCEL))
        btn_sizer.Add(self.btn_close, 0, wx.ALL, 5)
        
        sizer.Add(btn_sizer, 0, wx.ALIGN_RIGHT | wx.ALL, 5)
        
        self.SetSizer(sizer)
        self.update_ui()
        self.Centre()
        
    def update_ui(self):
        percent = int(((self.current_stage) / len(self.stages)) * 100)
        if self.current_stage >= len(self.stages):
            self.lbl_progress.SetLabel(f"Progres: 100% Selesai!")
            self.lbl_title.SetLabel("Selamat! Anda telah menguasai JadwalKu!")
            self.txt_desc.SetValue("Anda sudah menyelesaikan seluruh tahapan simulasi. Sekarang Anda dapat menggunakan JadwalKu dengan percaya diri di dunia nyata!\n\nTekan Tutup Simulasi untuk kembali beraktivitas.")
            self.btn_action.Hide()
            self.btn_repeat.Hide()
            self.btn_next.Hide()
            self.btn_close.SetFocus()
        else:
            self.lbl_progress.SetLabel(f"Progres Pemahaman: {percent}%")
            stage = self.stages[self.current_stage]
            self.lbl_title.SetLabel(stage["title"])
            self.txt_desc.SetValue(stage["desc"])
            self.btn_action.Show()
            self.btn_repeat.Hide()
            self.btn_next.Hide()
            self.txt_desc.SetFocus()
            
        self.Layout()
        
    def onAction(self, evt):
        if self.current_stage < len(self.stages):
            self.Hide()
            self.stages[self.current_stage]["action"]()
            
    def onStageComplete(self):
        self.Show()
        self.Raise()
        self.btn_action.Hide()
        self.btn_repeat.Show()
        self.btn_next.Show()
        self.Layout()
        self.btn_next.SetFocus()
        ui.message("Latihan tahap ini selesai. Tekan Tab untuk memilih Ulangi atau Lanjut.")
            
    def onNext(self, evt):
        self.current_stage += 1
        
        # Save progress
        if self.current_stage >= len(self.stages):
            self.config.set_simulation_progress(self.current_stage, 0, completed=True)
        else:
            self.config.set_simulation_progress(self.current_stage + 1, 0, completed=False)
            
        self.update_ui()
        
    def run_stage_1(self):
        dlg = JadwalKuDialog(self, DummyConfig(), DummyAudio(), tts_manager=DummyTTS())
        progress = self.config.get_simulation_progress()
        start_step = progress["step"] if progress["stage"] == 1 and not progress.get("completed") else 0
        
        def save_prog(step):
            self.config.set_simulation_progress(1, step, completed=False)
            
        def onAddPressed(evt):
            guide.timer.Stop()
            ui.message("Bagus! Dialog Tambah Agenda terbuka.")
            from .guiDialogs import AgendaDialog
            agenda_dlg = AgendaDialog(dlg, {}, DummyAudio())
            def onSaveAgenda(e):
                ui.message("Agenda berhasil disimpan (Simulasi).")
                agenda_dlg.EndModal(wx.ID_OK)
            guide2 = SimulationGuide(agenda_dlg, [
                {"instruction": "Anda sedang berada di form penambahan agenda. Fokus saat ini berada di Kotak Nama. Ketikkan nama agenda, lalu tekan Tab.", "bind_target": agenda_dlg.cb_freq, "bind_event": wx.EVT_SET_FOCUS},
                {"instruction": "Di Frekuensi ini, Anda bisa memilih 'Sekali Saja', 'Setiap Hari', atau hari spesifik. Biarkan pada 'Setiap Hari', dan tekan Tab.", "bind_target": agenda_dlg.btnCustomDays, "bind_event": wx.EVT_SET_FOCUS},
                {"instruction": "Tombol ini digunakan jika Anda memilih 'Sesuaikan Hari'. Tekan Tab untuk lanjut.", "bind_target": agenda_dlg.txt_date, "bind_event": wx.EVT_SET_FOCUS},
                {"instruction": "Kotak ini digunakan untuk menentukan tanggal spesifik. Tekan Tab untuk lanjut.", "bind_target": agenda_dlg.cb_hour, "bind_event": wx.EVT_SET_FOCUS},
                {"instruction": "Pilih jam alarm berbunyi dengan panah atas/bawah. Jika sudah, tekan Tab.", "bind_target": agenda_dlg.cb_minute, "bind_event": wx.EVT_SET_FOCUS},
                {"instruction": "Atur menit alarm Anda dengan panah atas/bawah. Lalu tekan Tab.", "bind_target": agenda_dlg.cb_interval, "bind_event": wx.EVT_SET_FOCUS},
                {"instruction": "Ini adalah pengingat berulang. Biarkan pada 'Sekali Saja', dan tekan Tab.", "bind_target": agenda_dlg.cb_interval_end, "bind_event": wx.EVT_SET_FOCUS},
                {"instruction": "Jika Anda menyetel pengingat berulang, kotak ini menentukan jam berhenti. Tekan Tab.", "bind_target": agenda_dlg.cb_alarm_mode, "bind_event": wx.EVT_SET_FOCUS},
                {"instruction": "Pilih mode suara: Pemberitahuan Singkat atau Alarm Weker. Tekan Tab.", "bind_target": agenda_dlg.cb_audio, "bind_event": wx.EVT_SET_FOCUS},
                {"instruction": "Pilih jenis nada dering menggunakan panah atas dan bawah. Tekan Tab.", "bind_target": agenda_dlg.btnTestSound, "bind_event": wx.EVT_SET_FOCUS},
                {"instruction": "Tekan Spasi pada tombol ini jika Anda ingin mendengarkan contoh nada dering. Tekan Tab.", "bind_target": agenda_dlg.chk_speech, "bind_event": wx.EVT_SET_FOCUS},
                {"instruction": "Beri centang jika Anda ingin NVDA membacakan nama agenda. Tekan Tab.", "bind_target": agenda_dlg.chk_active, "bind_event": wx.EVT_SET_FOCUS},
                {"instruction": "Beri centang agar jadwal ini langsung aktif. Tekan Tab.", "bind_target": agenda_dlg.btnOk, "bind_event": wx.EVT_SET_FOCUS},
                {"instruction": "Sempurna! Anda telah mempelajari seluruh kolom. Sekarang tekan Spasi atau Enter pada tombol Simpan ini untuk menyelesaikan penambahan.", "bind_target": agenda_dlg.btnOk, "bind_event": wx.EVT_BUTTON, "bind_handler": onSaveAgenda}
            ], on_complete=None)
            res = agenda_dlg.ShowModal()
            agenda_dlg.Destroy()
            def after_close():
                dlg.Raise()
                dlg.btnAdd.SetFocus()
                if res == wx.ID_OK:
                    dlg.listBox.Append("[X] Minum Obat - Setiap Hari (12:00)")
                    dlg.listBox.SetSelection(0)
                    guide.current_step = 1
                    guide.setup_current_step()
                else:
                    guide.timer.Start(100)
                    guide.ticks = 0
            wx.CallLater(100, after_close)

        def onEditPressed(evt):
            guide.timer.Stop()
            ui.message("Bagus! Dialog Edit Agenda terbuka.")
            from .guiDialogs import AgendaDialog
            agenda_dlg = AgendaDialog(dlg, {"name": "Minum Obat", "frequency": "Setiap Hari", "hour": 12, "minute": 0}, DummyAudio())
            def onCancelEdit(e):
                ui.message("Batal edit.")
                agenda_dlg.EndModal(wx.ID_CANCEL)
            agenda_dlg.btnCancel.Bind(wx.EVT_BUTTON, onCancelEdit)
            guide3 = SimulationGuide(agenda_dlg, [
                {"instruction": "Di sini Anda bisa mengubah data jadwal yang sudah ada. Untuk latihan ini, tekan Shift+Tab berulang kali ke arah mundur hingga menemukan tombol 'Batal', lalu tekan Spasi.", "bind_target": agenda_dlg.btnCancel, "bind_event": wx.EVT_SET_FOCUS},
                {"instruction": "Hebat! Sekarang tekan Spasi untuk membatalkan perubahan.", "bind_target": agenda_dlg.btnCancel, "bind_event": wx.EVT_BUTTON, "bind_handler": onCancelEdit}
            ], on_complete=None)
            res = agenda_dlg.ShowModal()
            agenda_dlg.Destroy()
            def after_close_edit():
                dlg.Raise()
                dlg.btnEdit.SetFocus()
                guide.current_step = 2
                guide.setup_current_step()
            wx.CallLater(100, after_close_edit)

        def onDeletePressed(evt):
            guide.timer.Stop()
            msg_dlg = wx.MessageDialog(dlg, "Apakah Anda yakin ingin menghapus jadwal 'Minum Obat'?", "Konfirmasi Hapus", wx.YES_NO | wx.ICON_QUESTION)
            res = msg_dlg.ShowModal()
            msg_dlg.Destroy()
            def after_close_del():
                dlg.Raise()
                dlg.btnDel.SetFocus()
                if res == wx.ID_YES:
                    dlg.listBox.Clear()
                    ui.message("Jadwal dihapus.")
                else:
                    ui.message("Penghapusan dibatalkan.")
                guide.current_step = 3
                guide.setup_current_step()
            wx.CallLater(100, after_close_del)
            
        def onCheckUncheck(evt):
            guide.timer.Stop()
            ui.message("Status jadwal berhasil diubah (Simulasi).")
            guide.current_step += 1
            guide.setup_current_step()
            
        def onPageChange(evt):
            evt.Skip()
            guide.timer.Stop()
            wx.CallAfter(lambda: ui.message("Berhasil pindah tab."))
            guide.current_step += 1
            guide.setup_current_step()
            
        def onTimeReminderPressed(evt):
            guide.timer.Stop()
            ui.message("Bagus! Dialog Pengaturan Pengingat Waktu Berkala terbuka.")
            from .guiDialogs import TimeReminderDialog
            remind_dlg = TimeReminderDialog(dlg, {}, None, self.config)
            
            def onCancelRemind(e):
                ui.message("Batal menyimpan pengingat.")
                remind_dlg.EndModal(wx.ID_CANCEL)
                
            remind_dlg.btnCancel.Bind(wx.EVT_BUTTON, onCancelRemind)
            
            guide_rem = SimulationGuide(remind_dlg, [
                {"instruction": "Di kotak dialog ini, Anda dapat menyetel pengingat waktu (Time Reminder). Fokus Anda sekarang di Kotak Centang Aktif. Tekan Tab.", "bind_target": remind_dlg.cb_interval, "bind_event": wx.EVT_SET_FOCUS},
                {"instruction": "Pilih interval pengingat. Tekan Tab.", "bind_target": remind_dlg.cb_mode, "bind_event": wx.EVT_SET_FOCUS},
                {"instruction": "Di sini Anda bisa mengubah mode suara notifikasi. Tekan Tab.", "bind_target": remind_dlg.cb_speech_style, "bind_event": wx.EVT_SET_FOCUS},
                {"instruction": "Pilih gaya pengucapan waktu pengingat yang Anda inginkan. Tekan Tab.", "bind_target": remind_dlg.cb_time_format, "bind_event": wx.EVT_SET_FOCUS},
                {"instruction": "Pilih format jam 12 atau 24 jam. Tekan Tab.", "bind_target": remind_dlg.cb_start, "bind_event": wx.EVT_SET_FOCUS},
                {"instruction": "Tentukan mulai jam berapa pengingat ini aktif setiap harinya. Tekan Tab.", "bind_target": remind_dlg.cb_end, "bind_event": wx.EVT_SET_FOCUS},
                {"instruction": "Tentukan batas akhir jam pengingat berbunyi. Tekan Tab.", "bind_target": remind_dlg.btnOpenTTS, "bind_event": wx.EVT_SET_FOCUS},
                {"instruction": "Anda bisa menekan tombol ini nanti untuk mengatur volume dan kecepatan TTS latar belakang. Tekan Tab lagi.", "bind_target": remind_dlg.btnOk, "bind_event": wx.EVT_SET_FOCUS},
                {"instruction": "Ini adalah tombol Simpan. Tekan Tab lagi.", "bind_target": remind_dlg.btnHelp, "bind_event": wx.EVT_SET_FOCUS},
                {"instruction": "Anda bisa menekan tombol Bantuan kapan saja di setiap dialog. Sekarang, tekan Shift+Tab berulang kali ke tombol 'Batal', lalu tekan Spasi.", "bind_target": remind_dlg.btnCancel, "bind_event": wx.EVT_SET_FOCUS},
                {"instruction": "Sekarang tekan Spasi untuk membatalkan.", "bind_target": remind_dlg.btnCancel, "bind_event": wx.EVT_BUTTON, "bind_handler": onCancelRemind}
            ], on_complete=None)
            
            remind_dlg.ShowModal()
            remind_dlg.Destroy()
            
            def after_close_remind():
                dlg.Raise()
                dlg.btnTimeRemind.SetFocus()
                guide.current_step += 1
                guide.setup_current_step()
                
            wx.CallLater(100, after_close_remind)

        def onAudioPressed(evt):
            guide.timer.Stop()
            ui.message("Bagus! Dialog Audio Manager terbuka.")
            from .guiDialogs import AudioManagerDialog
            audio_dlg = AudioManagerDialog(dlg, DummyAudio(), self.config)
            
            def onCancelAudio(e):
                ui.message("Batal menyimpan pengaturan audio.")
                audio_dlg.EndModal(wx.ID_CANCEL)
                
            audio_dlg.btnCancel.Bind(wx.EVT_BUTTON, onCancelAudio)
            
            guide_aud = SimulationGuide(audio_dlg, [
                {"instruction": "Di Audio Manager ini, Anda dapat mengatur output suara JadwalKu agar terpisah dari NVDA. Tekan Tab untuk memindahkan fokus.", "bind_target": audio_dlg.btnTestDevice, "bind_event": wx.EVT_SET_FOCUS},
                {"instruction": "Di sini Anda dapat menguji speaker. Tekan Tab lagi untuk mengatur Volume.", "bind_target": audio_dlg.slider_volume, "bind_event": wx.EVT_SET_FOCUS},
                {"instruction": "Gunakan panah untuk mengatur volume. Tekan Tab ke tombol Reset.", "bind_target": audio_dlg.btnResetVolume, "bind_event": wx.EVT_SET_FOCUS},
                {"instruction": "Tombol ini mengembalikan volume ke 100%. Tekan Tab.", "bind_target": audio_dlg.lb_sounds, "bind_event": wx.EVT_SET_FOCUS},
                {"instruction": "Di sini terdapat daftar semua file suara Anda. Tekan Tab.", "bind_target": audio_dlg.btnTestFile, "bind_event": wx.EVT_SET_FOCUS},
                {"instruction": "Gunakan tombol ini untuk mengetes file suara yang dipilih. Tekan Tab.", "bind_target": audio_dlg.btnOk, "bind_event": wx.EVT_SET_FOCUS},
                {"instruction": "Tombol Simpan untuk menyimpan preferensi audio. Tekan Tab.", "bind_target": audio_dlg.btnHelp, "bind_event": wx.EVT_SET_FOCUS},
                {"instruction": "Tombol Bantuan tersedia kapan saja. Sekarang tekan Shift+Tab berulang kali ke tombol 'Batal', lalu tekan Spasi.", "bind_target": audio_dlg.btnCancel, "bind_event": wx.EVT_SET_FOCUS},
                {"instruction": "Tekan Spasi untuk membatalkan dan menutup dialog ini.", "bind_target": audio_dlg.btnCancel, "bind_event": wx.EVT_BUTTON, "bind_handler": onCancelAudio}
            ], on_complete=None)
            
            audio_dlg.ShowModal()
            audio_dlg.Destroy()
            
            def after_close_audio():
                dlg.Raise()
                dlg.btnAudio.SetFocus()
                guide.current_step += 1
                guide.setup_current_step()
                
            wx.CallLater(100, after_close_audio)

        def onClosePressed(evt):
            guide.timer.Stop()
            dlg.EndModal(wx.ID_OK)
            
        guide = SimulationGuide(dlg, [
            {
                "instruction": "Sekarang Anda berada di Jendela Utama. Tekan Tab untuk mencari dan menekan tombol 'Tambah Jadwal Baru'.",
                "bind_target": dlg.btnAdd,
                "bind_event": wx.EVT_BUTTON,
                "bind_handler": onAddPressed,
                "pre_action": lambda: dlg.notebook.SetSelection(0)
            },
            {
                "instruction": "Jadwal Anda telah ditambahkan ke daftar. Sekarang coba cari dan tekan tombol 'Edit Jadwal...'",
                "bind_target": dlg.btnEdit,
                "bind_event": wx.EVT_BUTTON,
                "bind_handler": onEditPressed,
                "pre_action": lambda: dlg.notebook.SetSelection(0)
            },
            {
                "instruction": "Sempurna. Sekarang tekan tombol 'Hapus Jadwal'. Anda akan diminta konfirmasi penghapusan, pilih Yes atau No.",
                "bind_target": dlg.btnDel,
                "bind_event": wx.EVT_BUTTON,
                "bind_handler": onDeletePressed,
                "pre_action": lambda: dlg.notebook.SetSelection(0)
            },
            {
                "instruction": "Luar biasa! Agenda dihapus. Saat ini Anda masih di Tab 1 (Manajemen Agenda). Coba cari dan tekan tombol 'Check / Uncheck Status'.",
                "bind_target": dlg.btnToggle,
                "bind_event": wx.EVT_BUTTON,
                "bind_handler": onCheckUncheck,
                "pre_action": lambda: dlg.notebook.SetSelection(0)
            },
            {
                "instruction": "Bagus. Selanjutnya, tekan Tab hingga menemukan tombol 'Pengaturan Pengingat Waktu Berkala'.",
                "bind_target": dlg.btnTimeRemind,
                "bind_event": wx.EVT_SET_FOCUS,
                "pre_action": lambda: dlg.notebook.SetSelection(0)
            },
            {
                "instruction": "Sekarang tekan Spasi pada tombol tersebut untuk membuka Pengaturan Pengingat Waktu Berkala.",
                "bind_target": dlg.btnTimeRemind,
                "bind_event": wx.EVT_BUTTON,
                "bind_handler": onTimeReminderPressed,
                "pre_action": lambda: dlg.notebook.SetSelection(0)
            },
            {
                "instruction": "Luar biasa! Sekarang tekan Tab ke tombol 'Pengaturan Audio Manager (Speaker)'.",
                "bind_target": dlg.btnAudio,
                "bind_event": wx.EVT_SET_FOCUS,
                "pre_action": lambda: dlg.notebook.SetSelection(0)
            },
            {
                "instruction": "Sekarang tekan Spasi pada tombol tersebut untuk membuka Audio Manager.",
                "bind_target": dlg.btnAudio,
                "bind_event": wx.EVT_BUTTON,
                "bind_handler": onAudioPressed,
                "pre_action": lambda: dlg.notebook.SetSelection(0)
            },
            {
                "instruction": "Ini adalah akhir dari Tab 1. Sekarang mari kita pindah ke Tab 2. Tekan tombol 'Ctrl+Tab' untuk berpindah tab.",
                "bind_target": dlg.notebook,
                "bind_event": wx.EVT_NOTEBOOK_PAGE_CHANGED,
                "bind_handler": onPageChange,
                "pre_action": lambda: dlg.notebook.SetSelection(0)
            },
            {
                "instruction": "Selamat datang di Tab 2 (Pengaturan Waktu & Kalender). Fokus Anda ada di 'Aktifkan Penggantian Pelaporan Waktu'. Tekan Tab.",
                "bind_target": dlg.cb_time_format,
                "bind_event": wx.EVT_SET_FOCUS,
                "pre_action": lambda: dlg.notebook.SetSelection(1)
            },
            {
                "instruction": "Pilih format jam 12 atau 24 jam. Tekan Tab.",
                "bind_target": dlg.cb_time_speech_style,
                "bind_event": wx.EVT_SET_FOCUS,
                "pre_action": lambda: dlg.notebook.SetSelection(1)
            },
            {
                "instruction": "Pilih gaya pengucapan waktu. Tekan Tab.",
                "bind_target": dlg.cb_date_speech_style,
                "bind_event": wx.EVT_SET_FOCUS,
                "pre_action": lambda: dlg.notebook.SetSelection(1)
            },
            {
                "instruction": "Pilih gaya pengucapan tanggal. Tekan Tab.",
                "bind_target": dlg.cb_full_speech_style,
                "bind_event": wx.EVT_SET_FOCUS,
                "pre_action": lambda: dlg.notebook.SetSelection(1)
            },
            {
                "instruction": "Pilih gaya pengucapan laporan waktu penuh. Tekan Tab hingga menemukan tombol Kalender.",
                "bind_target": getattr(dlg, 'btnOpenCal', dlg.btnClose),
                "bind_event": wx.EVT_SET_FOCUS,
                "pre_action": lambda: dlg.notebook.SetSelection(1)
            },
            {
                "instruction": "Tombol ini membuka Kalender JadwalKu. Tekan Tab lagi.",
                "bind_target": getattr(dlg, 'btnOpenWorld', dlg.btnClose),
                "bind_event": wx.EVT_SET_FOCUS,
                "pre_action": lambda: dlg.notebook.SetSelection(1)
            },
            {
                "instruction": "Tombol ini membuka Jam Dunia. Tekan Tab.",
                "bind_target": getattr(dlg, 'btnOpenTTS', dlg.btnClose),
                "bind_event": wx.EVT_SET_FOCUS,
                "pre_action": lambda: dlg.notebook.SetSelection(1)
            },
            {
                "instruction": "Tombol ini membuka Pengaturan TTS. Tekan Tab.",
                "bind_target": getattr(dlg, 'btnSaveTimeCfg', dlg.btnClose),
                "bind_event": wx.EVT_SET_FOCUS,
                "pre_action": lambda: dlg.notebook.SetSelection(1)
            },
            {
                "instruction": "Bagus. Sekarang mari kita ke Tab 3. Tekan 'Ctrl+Tab'.",
                "bind_target": dlg.notebook,
                "bind_event": wx.EVT_NOTEBOOK_PAGE_CHANGED,
                "bind_handler": onPageChange,
                "pre_action": lambda: dlg.notebook.SetSelection(1)
            },
            {
                "instruction": "Anda berada di Tab 3 (Voice Pack & Studio). Di sini Anda bisa memilih Voice Pack aktif. Tekan Tab.",
                "bind_target": getattr(dlg, 'cb_active_vp', dlg.btnClose),
                "bind_event": wx.EVT_SET_FOCUS,
                "pre_action": lambda: dlg.notebook.SetSelection(2)
            },
            {
                "instruction": "Geser untuk mengatur volume Voice Pack Kustom. Tekan Tab.",
                "bind_target": getattr(dlg, 'sld_vp_vol', dlg.btnClose),
                "bind_event": wx.EVT_SET_FOCUS,
                "pre_action": lambda: dlg.notebook.SetSelection(2)
            },
            {
                "instruction": "Anda bisa membuka Studio Rekaman Suara JadwalKu di sini. Tekan Tab.",
                "bind_target": getattr(dlg, 'btnOpenVoiceStudio', dlg.btnClose),
                "bind_event": wx.EVT_SET_FOCUS,
                "pre_action": lambda: dlg.notebook.SetSelection(2)
            },
            {
                "instruction": "Atau buka Toko Voice Pack untuk mencari suara tambahan. Tekan Tab.",
                "bind_target": getattr(dlg, 'btnOpenStore', dlg.btnClose),
                "bind_event": wx.EVT_SET_FOCUS,
                "pre_action": lambda: dlg.notebook.SetSelection(2)
            },
            {
                "instruction": "Jika sudah, silakan pindah ke Tab 4 dengan 'Ctrl+Tab'.",
                "bind_target": dlg.notebook,
                "bind_event": wx.EVT_NOTEBOOK_PAGE_CHANGED,
                "bind_handler": onPageChange,
                "pre_action": lambda: dlg.notebook.SetSelection(2)
            },
            {
                "instruction": "Selamat datang di Tab terakhir, Tab 4 (Voice Command). Tekan Tab untuk menjelajahi opsi Perintah Suara yang ada.",
                "bind_target": getattr(dlg, 'cb_vc_engine', getattr(dlg, 'btnDownloadVC', dlg.btnClose)),
                "bind_event": wx.EVT_SET_FOCUS,
                "pre_action": lambda: dlg.notebook.SetSelection(3)
            },
            {
                "instruction": "Sempurna! Anda telah menelusuri keempat tab secara komprehensif. Terakhir, tekan tombol 'Tutup Dialog' untuk menyelesaikan Masterclass ini.",
                "bind_target": dlg.btnClose,
                "bind_event": wx.EVT_BUTTON,
                "bind_handler": onClosePressed,
                "pre_action": lambda: dlg.notebook.SetSelection(3)
            }
        ], on_complete=self.onStageComplete, on_close=save_prog, start_step=start_step)
        
        dlg.ShowModal()
        dlg.Destroy()
        

    def run_stage_2(self):
        progress = self.config.get_simulation_progress()
        start_step = progress["step"] if progress["stage"] == 2 and not progress.get("completed") else 0

        def save_prog(step):
            self.config.set_simulation_progress(2, step, completed=False)

        dlg = QuickTimerDialog(self, DummyScheduler())
        
        def onStartQuickTimer(evt):
            guide.timer.Stop()
            ui.message("Timer diatur (Simulasi).")
            guide.current_step += 1
            guide.setup_current_step()
            
        def onCloseQuickTimer(evt):
            guide.timer.Stop()
            ui.message("Quick Timer tertutup (Simulasi).")
            dlg.Destroy()
            
            # 2. Alarm Sekali Pakai
            from .guiDialogs import OneTimeAlarmDialog
            dlg2 = OneTimeAlarmDialog(self, DummyAudio())
            
            def onStartAlarm(e):
                guide2.timer.Stop()
                ui.message("Alarm disetel (Simulasi).")
                guide2.current_step += 1
                guide2.setup_current_step()

            def onCloseAlarm(e):
                guide2.timer.Stop()
                ui.message("Dialog Alarm tertutup.")
                dlg2.Destroy()
                
                # 3. Pomodoro Timer
                from .pomodoro import PomodoroTimerDialog, PomodoroManager
                class DummyPomodoroManager:
                    is_active = False
                    def get_status_str(self): return "Berhenti"
                dlg3 = PomodoroTimerDialog(self, DummyPomodoroManager())
                
                def onStartPomodoro(e3):
                    guide3.timer.Stop()
                    ui.message("Pomodoro dimulai (Simulasi).")
                    guide3.current_step += 1
                    guide3.setup_current_step()
                    
                def onClosePomodoro(e3):
                    guide3.timer.Stop()
                    ui.message("Dialog Pomodoro tertutup.")
                    dlg3.Destroy()
                    
                    # 4. Kalender
                    from .guiDialogs import CalendarDialog
                    dlg4 = CalendarDialog(self)
                    
                    def onCloseCalendar(e4):
                        guide4.timer.Stop()
                        ui.message("Kalender tertutup.")
                        dlg4.Destroy()
                        
                        # 5. Jam Dunia
                        dlg5 = WorldClockDialog(self)
                        
                        def onCloseWorldClock(e5):
                            guide5.timer.Stop()
                            dlg5.EndModal(wx.ID_OK)
                            
                        guide5 = SimulationGuide(dlg5, [
                            {"instruction": "Sekarang Anda berada di Jam Dunia. Tekan Tab untuk menelusuri daftar zona waktu dan tanggal merah. Jika sudah, tekan Tutup Dialog.", "bind_target": dlg5.btnClose, "bind_event": wx.EVT_BUTTON, "bind_handler": onCloseWorldClock}
                        ], on_complete=self.onStageComplete, on_close=save_prog, start_step=max(0, start_step - 13))
                        
                        dlg5.ShowModal()
                        dlg5.Destroy()
                        
                    guide4 = SimulationGuide(dlg4, [
                        {"instruction": "Ini adalah Kalender. Anda dapat melihat hari ini dan menambah catatan. Tekan Tab hingga tombol Tutup.", "bind_target": dlg4.btnClose, "bind_event": wx.EVT_SET_FOCUS},
                        {"instruction": "Tekan Spasi pada Tutup untuk lanjut.", "bind_target": dlg4.btnClose, "bind_event": wx.EVT_BUTTON, "bind_handler": onCloseCalendar}
                    ], on_complete=None, on_close=save_prog, start_step=max(0, start_step - 11))
                    if start_step < 13:
                        dlg4.ShowModal()
                        dlg4.Destroy()
                    else:
                        dlg4.Destroy()
                        onCloseCalendar(None)

                # Bind events for Pomodoro depending on initialization
                btn_start_pom = None
                btn_cancel_pom = None
                for child in dlg3.GetChildren():
                    if isinstance(child, wx.Button):
                        if child.GetLabel() == "Mula&i":
                            btn_start_pom = child
                        elif child.GetLabel() == "&Tutup":
                            btn_cancel_pom = child
                            
                guide3 = SimulationGuide(dlg3, [
                    {"instruction": "Selamat datang di Pomodoro Timer! Fokus di Waktu Fokus. Tekan Tab.", "bind_target": dlg3.txt_work, "bind_event": wx.EVT_SET_FOCUS},
                    {"instruction": "Pindah ke tombol Mulai.", "bind_target": btn_start_pom, "bind_event": wx.EVT_SET_FOCUS},
                    {"instruction": "Tekan Spasi untuk memulai Pomodoro.", "bind_target": btn_start_pom, "bind_event": wx.EVT_BUTTON, "bind_handler": onStartPomodoro},
                    {"instruction": "Bagus, Pomodoro berjalan. Sekarang tekan tombol Tutup.", "bind_target": btn_cancel_pom, "bind_event": wx.EVT_BUTTON, "bind_handler": onClosePomodoro}
                ], on_complete=None, on_close=save_prog, start_step=max(0, start_step - 7))
                if start_step < 11:
                    dlg3.ShowModal()
                    dlg3.Destroy()
                else:
                    dlg3.Destroy()
                    onClosePomodoro(None)
                    
            btn_ok_alarm = None
            btn_cancel_alarm = None
            for child in dlg2.GetChildren():
                if isinstance(child, wx.Button):
                    if child.GetLabel() == "&Simpan":
                        btn_ok_alarm = child
                    elif child.GetLabel() == "&Batal":
                        btn_cancel_alarm = child

            guide2 = SimulationGuide(dlg2, [
                {"instruction": "Sekarang Anda berada di Alarm Sekali Pakai. Tekan Tab ke Kotak Jam.", "bind_target": dlg2.cb_hour, "bind_event": wx.EVT_SET_FOCUS},
                {"instruction": "Tekan Tab ke tombol Simpan.", "bind_target": btn_ok_alarm, "bind_event": wx.EVT_SET_FOCUS},
                {"instruction": "Tekan Spasi untuk menyetel alarm.", "bind_target": btn_ok_alarm, "bind_event": wx.EVT_BUTTON, "bind_handler": onStartAlarm},
                {"instruction": "Luar biasa. Sekarang tutup dialog Alarm ini dengan tombol Batal.", "bind_target": btn_cancel_alarm, "bind_event": wx.EVT_BUTTON, "bind_handler": onCloseAlarm}
            ], on_complete=None, on_close=save_prog, start_step=max(0, start_step - 3))
            
            if start_step < 7:
                dlg2.ShowModal()
                dlg2.Destroy()
            else:
                dlg2.Destroy()
                onCloseAlarm(None)

        guide = SimulationGuide(dlg, [
            {
                "instruction": "Selamat datang di Tahap 2! Anda berada di Quick Timer. Tekan Tab untuk memindahkan fokus ke Kotak Durasi Waktu Angka.",
                "bind_target": dlg.txt_duration,
                "bind_event": wx.EVT_SET_FOCUS
            },
            {
                "instruction": "Bagus. Sekarang tekan Tab hingga Anda menemukan tombol 'Mulai Timer'.",
                "bind_target": dlg.btnOk,
                "bind_event": wx.EVT_SET_FOCUS
            },
            {
                "instruction": "Sekarang tekan Spasi pada tombol tersebut untuk memulai timer (Simulasi).",
                "bind_target": dlg.btnOk,
                "bind_event": wx.EVT_BUTTON,
                "bind_handler": onStartQuickTimer
            },
            {
                "instruction": "Hebat. Sekarang cari tombol Batal untuk menutup Quick Timer.",
                "bind_target": dlg.btnCancel,
                "bind_event": wx.EVT_BUTTON,
                "bind_handler": onCloseQuickTimer
            }
        ], on_complete=None, on_close=save_prog, start_step=start_step if start_step < 3 else 3)
        
        if start_step < 3:
            dlg.ShowModal()
            dlg.Destroy()
        else:
            dlg.Destroy()
            onCloseQuickTimer(None)

class TutorialEntryDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="Pusat Bantuan & Tutorial JadwalKu", size=(500, 300), style=wx.DEFAULT_DIALOG_STYLE)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        lbl_info = wx.StaticText(self, label="Bagaimana Anda ingin mempelajari JadwalKu?")
        font = lbl_info.GetFont()
        font.MakeBold()
        lbl_info.SetFont(font)
        sizer.Add(lbl_info, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 15)
        
        btnSizer = wx.BoxSizer(wx.VERTICAL)
        
        self.btn_doc = wx.Button(self, label="1. Buka Panduan &Teks Biasa (Alt+T)")
        self.btn_doc.Bind(wx.EVT_BUTTON, self.onDoc)
        btnSizer.Add(self.btn_doc, 0, wx.ALL | wx.EXPAND, 8)
        
        self.btn_sim = wx.Button(self, label="2. Mulai &Simulasi Interaktif Penuh (Langkah-demi-langkah) (Alt+S)")
        self.btn_sim.Bind(wx.EVT_BUTTON, self.onSimulation)
        btnSizer.Add(self.btn_sim, 0, wx.ALL | wx.EXPAND, 8)
        
        sizer.Add(btnSizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 20)
        
        self.btnClose = wx.Button(self, wx.ID_CANCEL, label="&Tutup (Esc)")
        self.btnClose.Bind(wx.EVT_BUTTON, lambda evt: self.EndModal(wx.ID_CANCEL))
        sizer.Add(self.btnClose, 0, wx.ALL | wx.ALIGN_RIGHT, 15)
        
        self.SetSizer(sizer)
        self.Centre()
        
    def onDoc(self, evt):
        import os
        from . import utils
        doc_path = os.path.join(os.path.dirname(__file__), "..", "..", "doc", "id", "readme.html")
        if not os.path.exists(doc_path):
            doc_path = os.path.join(os.path.dirname(__file__), "..", "..", "doc", "readme.html")
        if os.path.exists(doc_path):
            utils.open_file(doc_path)
        self.EndModal(wx.ID_NO)
        
    def onSimulation(self, evt):
        self.EndModal(wx.ID_YES)

def start_tutorial(parent):
    dlg = TutorialEntryDialog(parent)
    res = dlg.ShowModal()
    dlg.Destroy()
    
    if res == wx.ID_YES:
        import ui
        ui.message("Fitur Simulasi saat ini ditutup sementara karena masih dalam tahap pengembangan. (Versi 1.7.6.2)")
    elif res == wx.ID_NO:
        from .guiDialogs import HelpDialog
        help_dlg = HelpDialog(parent)
        help_dlg.ShowModal()
        help_dlg.Destroy()
