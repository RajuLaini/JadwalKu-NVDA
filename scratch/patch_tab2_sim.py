import re
import os

target_file = r'C:\Users\Raju Laini\Documents\Project_Jadwalku\JadwalKu\globalPlugins\jadwalku\simulation.py'

with open(target_file, 'r', encoding='utf-8') as f:
    content = f.read()

new_stage_2 = """
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
"""

# Replace from 'def run_stage_2(self):' up to the end of SimulationWizardDialog
content = re.sub(r'    def run_stage_2\(self\):.*?(?=\nclass TutorialEntryDialog)', new_stage_2, content, flags=re.DOTALL)

with open(target_file, 'w', encoding='utf-8') as f:
    f.write(content)
print("Berhasil!")
