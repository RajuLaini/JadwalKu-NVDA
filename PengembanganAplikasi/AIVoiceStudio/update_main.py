import re

path = r'C:\Users\Raju Laini\Documents\Project_Jadwalku\PengembanganAplikasi\AIVoiceStudio\main.py'
content = open(path, 'r', encoding='utf-8').read()

imports = '''import urllib.parse
from pathlib import Path
import miniaudio
import wave'''
content = content.replace('import urllib.parse\nfrom pathlib import Path', imports)

# Find the conversion part
find_str = '''                generated_files.append((word, outfile))'''
replace_str = '''                # Convert MP3 to WAV using miniaudio
                wavfile = os.path.join(temp_dir, f"{word}.wav")
                try:
                    decoded = miniaudio.decode_file(outfile, sample_format=miniaudio.SampleFormat.SIGNED_16)
                    with wave.open(wavfile, 'wb') as wav:
                        wav.setnchannels(decoded.nchannels)
                        wav.setsampwidth(2)
                        wav.setframerate(decoded.sample_rate)
                        wav.writeframes(decoded.samples)
                    os.remove(outfile)
                except Exception as e:
                    raise Exception(f"Gagal mengonversi {word} ke WAV: {e}")
                
                generated_files.append((word, wavfile))'''

content = content.replace(find_str, replace_str)

# Replace .mp3 with .wav in zip
content = content.replace('zipf.write(fp, f"{w}.mp3")', 'zipf.write(fp, f"{w}.wav")')

open(path, 'w', encoding='utf-8').write(content)
print('Updated main.py to convert mp3 to wav')
