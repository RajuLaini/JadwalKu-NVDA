import re
import os

filepath = r"C:\Users\Raju Laini\Documents\Project_Jadwalku\JadwalKu\globalPlugins\jadwalku\guiDialogs.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# The methods block is everything between "import api\n\n\n\tdef refreshEvents(self):" 
# and "class HelpDialog(wx.Dialog):".
start_idx = content.find("\n\tdef refreshEvents(self):")
end_idx = content.find("class HelpDialog(wx.Dialog):")

if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
    methods_code = content[start_idx:end_idx]
    # Remove from top
    content = content[:start_idx] + content[end_idx:]
    
    # Inject at the end of JadwalKuDialog
    # JadwalKuDialog ends before class CalendarDialog(wx.Dialog):
    jadwal_dialog_end = content.find("\nclass CalendarDialog(wx.Dialog):")
    if jadwal_dialog_end != -1:
        content = content[:jadwal_dialog_end] + methods_code + content[jadwal_dialog_end:]
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print("Fix applied successfully!")
    else:
        print("Could not find CalendarDialog.")
else:
    print("Could not find methods block.")
