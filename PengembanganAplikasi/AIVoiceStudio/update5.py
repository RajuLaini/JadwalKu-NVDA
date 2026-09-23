path = r'C:\Users\Raju Laini\Documents\Project_Jadwalku\PengembanganAplikasi\AIVoiceStudio\main.py'
content = open(path, 'r', encoding='utf-8').read()

gemini_logic = '''
                    data = json.dumps(payload).encode('utf-8')
                    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
                    
                    # Retry logic for Rate Limit (HTTP 429)
                    max_retries = 5
                    for attempt in range(max_retries):
                        try:
                            with urllib.request.urlopen(req) as response:
                                resp_data = json.loads(response.read().decode('utf-8'))
                                break
                        except urllib.error.HTTPError as e:
                            if e.code == 429: # Too Many Requests
                                self.set_status(f"Limit Gemini (429) tercapai. Menunggu 15 detik... (Percobaan {attempt+1}/{max_retries})", idx)
                                time.sleep(15)
                            else:
                                raise e
                    else:
                        raise Exception("Gagal menghubungi Gemini setelah beberapa kali mencoba karena Rate Limit (429).")
                        
                    import base64
'''

# Find the exact string to replace in main.py
find_str = '''                    data = json.dumps(payload).encode('utf-8')
                    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
                    with urllib.request.urlopen(req) as response:
                        resp_data = json.loads(response.read().decode('utf-8'))
                        import base64'''

content = content.replace(find_str, gemini_logic.strip())
open(path, 'w', encoding='utf-8').write(content)
print("Added HTTP 429 Auto-Retry for Gemini!")
