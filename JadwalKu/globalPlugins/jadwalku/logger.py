import logging
import os
import globalVars

_logger = None

def get_jadwalku_logger():
    global _logger
    if _logger is not None:
        return _logger
        
    _logger = logging.getLogger("JadwalKu")
    
    # Hanya inisialisasi jika belum memiliki handler
    if not _logger.handlers:
        _logger.setLevel(logging.DEBUG)
        
        # Lokasi file jadwalku.log (sejajar dengan config NVDA)
        log_path = os.path.join(globalVars.appArgs.configPath, "jadwalku.log")
        
        # Mode 'w' akan mereset (menghapus) isi file setiap kali NVDA / JadwalKu restart
        handler = logging.FileHandler(log_path, mode='w', encoding='utf-8')
        
        # Format log: Waktu - Level - Pesan
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')
        handler.setFormatter(formatter)
        
        _logger.addHandler(handler)
        
        # Cegah teks bocor ke NVDA log (nvda.log)
        _logger.propagate = False 
        
    return _logger

jk_log = get_jadwalku_logger()
