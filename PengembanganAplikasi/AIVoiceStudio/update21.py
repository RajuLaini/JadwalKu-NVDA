import re

path = r'C:\Users\Raju Laini\Documents\Project_Jadwalku\PengembanganAplikasi\AIVoiceStudio\main.py'
content = open(path, 'r', encoding='utf-8').read()

old_trim = '''                # Gunakan sistem RMS per chunk 10ms agar kebal terhadap noise klik mic
                chunk_samples = int(framerate * nchannels * 10 / 1000)
                margin_samples = chunk_samples * 5 # margin 50ms
                
                start_idx = 0
                for i in range(0, len(samples), chunk_samples):
                    chunk = samples[i:i+chunk_samples]
                    if not chunk: break
                    rms = math.sqrt(sum(s*s for s in chunk) / len(chunk))
                    if rms > threshold:
                        start_idx = max(0, i - margin_samples)
                        break
                        
                end_idx = len(samples)
                for i in range(len(samples)-chunk_samples, -1, -chunk_samples):
                    chunk = samples[i:i+chunk_samples]
                    if not chunk: break
                    rms = math.sqrt(sum(s*s for s in chunk) / len(chunk))
                    if rms > threshold:
                        end_idx = min(len(samples), i + chunk_samples + margin_samples)
                        break'''

new_trim = '''                # Gunakan sistem RMS per chunk 10ms agar kebal terhadap noise klik mic
                threshold = 1500  # Naikkan sangat tinggi untuk menembus noise napas/klik mic
                chunk_samples = int(framerate * nchannels * 10 / 1000)
                margin_samples = chunk_samples * 3 # margin 30ms (sangat ketat)
                
                start_idx = 0
                for i in range(0, len(samples), chunk_samples):
                    chunk = samples[i:i+chunk_samples]
                    if not chunk: break
                    rms = math.sqrt(sum(s*s for s in chunk) / len(chunk))
                    if rms > threshold:
                        start_idx = max(0, i - margin_samples)
                        break
                        
                end_idx = len(samples)
                for i in range(len(samples)-chunk_samples, -1, -chunk_samples):
                    chunk = samples[i:i+chunk_samples]
                    if not chunk: break
                    rms = math.sqrt(sum(s*s for s in chunk) / len(chunk))
                    if rms > threshold:
                        end_idx = min(len(samples), i + chunk_samples + margin_samples)
                        break'''

content = content.replace(old_trim, new_trim)
open(path, 'w', encoding='utf-8').write(content)
