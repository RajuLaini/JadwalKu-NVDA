# -*- coding: UTF-8 -*-
import datetime

def get_active_status(scheduler, pomodoro_manager):
    """
    Mengembalikan daftar string status dari semua pewaktu yang sedang aktif.
    Jika tidak ada yang aktif, mengembalikan list kosong.
    """
    statuses = []
    now = datetime.datetime.now()

    # Cek Pomodoro
    if pomodoro_manager and pomodoro_manager.is_active:
        statuses.append(pomodoro_manager.get_status_str())

    # Cek Timer Rutin (Quick Timers)
    if scheduler and hasattr(scheduler, "quick_timers") and scheduler.quick_timers:
        for item in scheduler.quick_timers:
            if item.get("state") == "prep":
                diff = (item["prep_trigger_time"] - now).total_seconds()
                if diff > 0:
                    statuses.append(f"Persiapan Timer {item['duration']} {item['unit']}, sisa {int(diff)} detik.")
            else:
                diff = (item["trigger_time"] - now).total_seconds()
                if diff > 0:
                    mins, secs = divmod(int(diff), 60)
                    hrs, mins = divmod(mins, 60)
                    
                    time_str = ""
                    if hrs > 0:
                        time_str += f"{hrs} jam "
                    if mins > 0:
                        time_str += f"{mins} menit "
                    time_str += f"{secs} detik"
                    
                    statuses.append(f"Timer {item['duration']} {item['unit']}, sisa {time_str.strip()}.")

    # Cek Alarm Sekali Pakai
    if scheduler and hasattr(scheduler, "one_time_alarms") and scheduler.one_time_alarms:
        for item in scheduler.one_time_alarms:
            diff = (item["trigger_time"] - now).total_seconds()
            if diff > 0:
                mins, secs = divmod(int(diff), 60)
                hrs, mins = divmod(mins, 60)
                
                time_str = ""
                if hrs > 0:
                    time_str += f"{hrs} jam "
                if mins > 0:
                    time_str += f"{mins} menit "
                time_str += f"{secs} detik"
                
                statuses.append(f"Alarm pukul {item['time_str']}, tersisa {time_str.strip()}.")

    return statuses
