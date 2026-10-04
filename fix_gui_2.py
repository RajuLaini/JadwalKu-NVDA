import re
import os

filepath = r"C:\Users\Raju Laini\Documents\Project_Jadwalku\JadwalKu\globalPlugins\jadwalku\guiDialogs.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Extract the methods block
start_idx = content.find("\n\tdef refreshEvents(self):")
end_idx = content.find("\nclass CalendarDialog(wx.Dialog):")

if start_idx != -1 and end_idx != -1:
    methods_code = content[start_idx:end_idx]
    # Remove it from its current place
    content = content[:start_idx] + content[end_idx:]
    
    # 2. Find the end of JadwalKuDialog
    # JadwalKuDialog ends right before `def get_indonesian_holidays(year):`
    jadwal_dialog_end = content.find("\ndef get_indonesian_holidays(year):")
    if jadwal_dialog_end != -1:
        content = content[:jadwal_dialog_end] + methods_code + content[jadwal_dialog_end:]
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print("Fixed successfully!")
    else:
        print("Could not find get_indonesian_holidays")
else:
    print("Could not find methods block.")
