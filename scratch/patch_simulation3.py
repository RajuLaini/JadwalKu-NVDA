import os
import re

file_path = r"C:\Users\Raju Laini\Documents\Project_Jadwalku\JadwalKu\globalPlugins\jadwalku\simulation.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update SimulationGuide.__init__
content = content.replace(
    "def __init__(self, dialog, steps, interval=5, on_complete=None):",
    "def __init__(self, dialog, steps, interval=5, on_complete=None, on_close=None, start_step=0):"
)
content = content.replace(
    "self.current_step = 0\n        self.on_complete = on_complete",
    "self.current_step = start_step\n        self.on_complete = on_complete\n        self.on_close = on_close"
)

# 2. Update setup_current_step to handle pre_action
setup_current_step_code = """        step = self.steps[self.current_step]
        self.spoken = False
        self.ticks = 0
        
        if "pre_action" in step and step["pre_action"]:
            try:
                step["pre_action"]()
            except Exception:
                pass

        self.timer.Start(100) # 100ms per tick"""
content = content.replace(
    """        step = self.steps[self.current_step]
        self.spoken = False
        self.ticks = 0
        self.timer.Start(100) # 100ms per tick""",
    setup_current_step_code
)

# 3. Update onClose to call on_close
onClose_code = """    def onClose(self, evt):
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
            self.ticks = 0"""
content = re.sub(r'    def onClose\(self, evt\):.*?(?=\n    def |$)', onClose_code + "\n\n", content, flags=re.DOTALL)

# 4. Update SimulationWizardDialog stages
old_stages = """        self.stages = [
            {
                "title": "Tahap 1: Manajemen Agenda Dasar",
                "desc": "Mari kita mulai dengan membuat jadwal/alarm pertama Anda. Sistem akan memandu Anda dari Jendela Utama hingga selesai membuat jadwal.",
                "action": self.run_stage_1
            },
            {
                "title": "Tahap 2: Tur Eksplorasi 4 Tab Pengaturan (Masterclass Jendela Utama)",
                "desc": "Tahap ini akan memandu Anda menelusuri seluruh fitur hebat di 4 Tab Jendela Utama JadwalKu, termasuk Pengaturan Waktu, Kalender, Voice Pack, dan Voice Command.",
                "action": self.run_stage_2
            },
            {
                "title": "Tahap 3: Simulasi Fitur Ekstra (Quick Timer & Jam Dunia)",
                "desc": "Mari pelajari cara menyalakan Quick Timer untuk memasak, serta melihat selisih waktu atau tanggal merah dengan fitur Jam Dunia.",
                "action": self.run_stage_3
            }
        ]"""
new_stages = """        self.stages = [
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
        ]"""
content = content.replace(old_stages, new_stages)

# 5. Merge run_stage_1 and run_stage_2
# I'll just replace the entire run_stage_1, run_stage_2, and run_stage_3 body!
# run_stage_3 becomes run_stage_2!

new_stages_methods = """    def run_stage_1(self):
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
                "instruction": "Sekarang tekan Tab lagi ke tombol 'Pengaturan Audio Manager (Speaker)'.",
                "bind_target": dlg.btnAudio,
                "bind_event": wx.EVT_SET_FOCUS,
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
                "instruction": "Selamat datang di Tab 2 (Pengaturan Waktu & Kalender). Tekan Tab hingga Anda menemukan pilihan 'Format Jam'.",
                "bind_target": dlg.cb_time_format,
                "bind_event": wx.EVT_SET_FOCUS,
                "pre_action": lambda: dlg.notebook.SetSelection(1)
            },
            {
                "instruction": "Bagus, di sini Anda bisa memilih format 12 atau 24 jam. Sekarang tekan Tab hingga tombol 'Simpan Pengaturan Waktu'.",
                "bind_target": dlg.btnSaveTimeCfg,
                "bind_event": wx.EVT_SET_FOCUS,
                "pre_action": lambda: dlg.notebook.SetSelection(1)
            },
            {
                "instruction": "Tepat sekali! Sekarang mari kita ke Tab 3. Tekan 'Ctrl+Tab' lagi.",
                "bind_target": dlg.notebook,
                "bind_event": wx.EVT_NOTEBOOK_PAGE_CHANGED,
                "bind_handler": onPageChange,
                "pre_action": lambda: dlg.notebook.SetSelection(1)
            },
            {
                "instruction": "Anda berada di Tab 3 (Voice Pack & Studio). Tekan Tab untuk menemukan Slider 'Volume Voice Pack Kustom'.",
                "bind_target": dlg.sld_vp_vol,
                "bind_event": wx.EVT_SET_FOCUS,
                "pre_action": lambda: dlg.notebook.SetSelection(2)
            },
            {
                "instruction": "Baik. Jika sudah, silakan pindah ke Tab 4 dengan 'Ctrl+Tab'.",
                "bind_target": dlg.notebook,
                "bind_event": wx.EVT_NOTEBOOK_PAGE_CHANGED,
                "bind_handler": onPageChange,
                "pre_action": lambda: dlg.notebook.SetSelection(2)
            },
            {
                "instruction": "Selamat datang di Tab terakhir, Tab 4 (Voice Command). Tekan Tab untuk fokus pada pilihan 'Sistem Pemrosesan'.",
                "bind_target": dlg.cb_vc_engine,
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
            
            # Buka Jam Dunia
            dlg2 = WorldClockDialog(self)
            
            def onCloseWorldClock(e):
                guide2.timer.Stop()
                dlg2.EndModal(wx.ID_OK)
                
            guide2 = SimulationGuide(dlg2, [
                {
                    "instruction": "Sekarang Anda berada di Jam Dunia. Tekan Tab untuk menelusuri daftar zona waktu dan tanggal merah. Jika sudah, tekan Tutup Dialog.",
                    "bind_target": dlg2.btnClose,
                    "bind_event": wx.EVT_BUTTON,
                    "bind_handler": onCloseWorldClock
                }
            ], on_complete=self.onStageComplete, on_close=save_prog, start_step=0 if start_step < 3 else start_step - 3)
            
            dlg2.ShowModal()
            dlg2.Destroy()

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
            onCloseQuickTimer(None)"""

content = re.sub(r'    def run_stage_1\(self\):.*', new_stages_methods, content, flags=re.DOTALL)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Berhasil memperbarui simulation.py")
