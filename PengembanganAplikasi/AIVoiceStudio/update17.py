path = r'C:\Users\Raju Laini\Documents\Project_Jadwalku\PengembanganAplikasi\AIVoiceStudio\main.py'
content = open(path, 'r', encoding='utf-8').read()

content = content.replace('f"Gagal! Ada {len(missing_words)} kata yang hilang di folder tersebut:\n{', 'f"Gagal! Ada {len(missing_words)} kata yang hilang di folder tersebut:\\n{')
content = content.replace('f"Folder berhasil dipangkas dan dibungkus menjadi Voice Pack!\nDisimpan di:\n{output_file}"', 'f"Folder berhasil dipangkas dan dibungkus menjadi Voice Pack!\\nDisimpan di:\\n{output_file}"')

open(path, 'w', encoding='utf-8').write(content)
