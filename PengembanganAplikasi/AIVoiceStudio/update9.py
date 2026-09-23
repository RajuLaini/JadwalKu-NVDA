path = r'C:\Users\Raju Laini\Documents\Project_Jadwalku\PengembanganAplikasi\AIVoiceStudio\main.py'
content = open(path, 'r', encoding='utf-8').read()

convert_logic = '''                # Convert MP3/PCM to WAV
                wavfile = os.path.join(temp_dir, f"{word}.wav")
                import array
                try:
                    if "Gemini API" in provider:
                        # Gemini mengembalikan RAW PCM (l16, 24000Hz, Mono) tanpa header
                        with open(outfile, 'rb') as f:
                            raw_pcm = f.read()
                        samples = array.array('h', raw_pcm)
                        sample_rate = 24000
                        nchannels = 1
                    else:
                        # Layanan lain (Edge, Translate, Cloud) mengembalikan MP3
                        decoded = miniaudio.mp3_read_file_s16(outfile)
                        samples = array.array('h', decoded.samples)
                        sample_rate = decoded.sample_rate
                        nchannels = decoded.nchannels
                    
                    # Auto Trim Silence
                    threshold = 400
                    start_idx = 0
                    for i in range(len(samples)):
                        if abs(samples[i]) > threshold:
                            start_idx = i
                            break
                    
                    end_idx = len(samples) - 1
                    for i in range(len(samples)-1, -1, -1):
                        if abs(samples[i]) > threshold:
                            end_idx = i
                            break
                    
                    margin = int(sample_rate * nchannels * 0.02) # 20ms margin
                    start_idx = max(0, start_idx - margin)
                    end_idx = min(len(samples), end_idx + margin)
                    
                    trimmed_samples = samples[start_idx:end_idx]
                    
                    with wave.open(wavfile, 'wb') as wav:
                        wav.setnchannels(nchannels)
                        wav.setsampwidth(2)
                        wav.setframerate(sample_rate)
                        wav.writeframes(trimmed_samples.tobytes())
                    os.remove(outfile)
                except Exception as e:
                    raise Exception(f"Gagal mengonversi {word} ke WAV: {e}")'''

old_convert_logic = '''                # Convert MP3 to WAV using miniaudio
                wavfile = os.path.join(temp_dir, f"{word}.wav")
                import array
                try:
                    decoded = miniaudio.mp3_read_file_s16(outfile)
                    samples = array.array('h', decoded.samples)
                    
                    # Auto Trim Silence
                    threshold = 400
                    start_idx = 0
                    for i in range(len(samples)):
                        if abs(samples[i]) > threshold:
                            start_idx = i
                            break
                    
                    end_idx = len(samples) - 1
                    for i in range(len(samples)-1, -1, -1):
                        if abs(samples[i]) > threshold:
                            end_idx = i
                            break
                    
                    margin = int(decoded.sample_rate * decoded.nchannels * 0.02) # 20ms margin
                    start_idx = max(0, start_idx - margin)
                    end_idx = min(len(samples), end_idx + margin)
                    
                    trimmed_samples = samples[start_idx:end_idx]
                    
                    with wave.open(wavfile, 'wb') as wav:
                        wav.setnchannels(decoded.nchannels)
                        wav.setsampwidth(2)
                        wav.setframerate(decoded.sample_rate)
                        wav.writeframes(trimmed_samples.tobytes())
                    os.remove(outfile)
                except Exception as e:
                    raise Exception(f"Gagal mengonversi {word} ke WAV: {e}")'''

content = content.replace(old_convert_logic, convert_logic.strip())
open(path, 'w', encoding='utf-8').write(content)
