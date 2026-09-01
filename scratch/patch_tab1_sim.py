import re
import os

target_file = r'C:\Users\Raju Laini\Documents\Project_Jadwalku\JadwalKu\globalPlugins\jadwalku\simulation.py'

with open(target_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Tambahkan onTimeReminderPressed dan onAudioPressed
handler_code = """
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
                {"instruction": "Di sini Anda bisa mengubah mode suara notifikasi. Sekarang tekan Shift+Tab berulang kali ke tombol 'Batal', lalu tekan Spasi.", "bind_target": remind_dlg.btnCancel, "bind_event": wx.EVT_SET_FOCUS},
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
                {"instruction": "Sekarang tekan Shift+Tab berulang kali ke tombol 'Batal', lalu tekan Spasi.", "bind_target": audio_dlg.btnCancel, "bind_event": wx.EVT_SET_FOCUS},
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
"""

content = content.replace("def onClosePressed(evt):", handler_code.strip('\n') + "\n\n        def onClosePressed(evt):")

# Ganti list steps lama dengan yang baru
old_steps = '''            {
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
            },'''

new_steps = '''            {
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
            },'''

if old_steps in content:
    content = content.replace(old_steps, new_steps)
    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Berhasil!")
else:
    print("Gagal menemukan steps lama!")
