import re
filepath = r"C:\Users\Raju Laini\Documents\Project_Jadwalku\JadwalKu\globalPlugins\jadwalku\scheduler.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Replace self.tts with self.tts_manager carefully
content = content.replace("self.tts.speak", "self.tts_manager.speak")
content = content.replace("if self.tts:", "if self.tts_manager:")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Replaced self.tts with self.tts_manager.")
