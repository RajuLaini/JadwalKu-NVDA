import re
filepath = r"C:\Users\Raju Laini\Documents\Project_Jadwalku\JadwalKu\globalPlugins\jadwalku\scheduler.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("self.tts.queue_speech(msg)", "self.tts.speak(msg)")
content = content.replace("self.tts.queue_speech(greeting)", "self.tts.speak(greeting)")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Replaced queue_speech with speak in scheduler.py")
