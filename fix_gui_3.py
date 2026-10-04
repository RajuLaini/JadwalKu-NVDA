import re
import os

filepath = r"C:\Users\Raju Laini\Documents\Project_Jadwalku\JadwalKu\globalPlugins\jadwalku\guiDialogs.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Swap the Add calls
# Currently:
# sizer_events.Add(sizer_briefing, 0, wx.EXPAND | wx.ALL, 5)
# ...
# sizer_events.Add(sizer_list, 1, wx.EXPAND | wx.ALL, 5)
# 
# We need to change the order.
# Actually, it's easier to find the block for Briefing Config and move it after Events List.
start_briefing = content.find("\t\t# Briefing Config")
end_briefing = content.find("\t\t# Events List")

if start_briefing != -1 and end_briefing != -1:
    briefing_code = content[start_briefing:end_briefing]
    
    # Remove briefing_code from its current place
    content = content[:start_briefing] + content[end_briefing:]
    
    # Find the end of Events List (sizer_events.Add(sizer_list, 1, wx.EXPAND | wx.ALL, 5))
    end_list = content.find("sizer_events.Add(sizer_list, 1, wx.EXPAND | wx.ALL, 5)")
    if end_list != -1:
        # Move past that line
        insertion_point = content.find("\n", end_list) + 1
        content = content[:insertion_point] + "\n" + briefing_code + content[insertion_point:]

# 2. Add focus to txt_title in EventEditorDialog
focus_code = "\n\t\twx.CallAfter(self.txt_title.SetFocus)\n"
# Find self.Centre() inside EventEditorDialog
start_evt_dlg = content.find("class EventEditorDialog")
if start_evt_dlg != -1:
    end_init = content.find("self.Centre()", start_evt_dlg)
    if end_init != -1:
        insertion = end_init + len("self.Centre()")
        content = content[:insertion] + focus_code + content[insertion:]

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Fix script completed!")
