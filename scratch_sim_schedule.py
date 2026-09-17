import datetime

class DummyConfig:
    def __init__(self):
        self.schedules = [{
            "id": "123",
            "active": True,
            "hour": 14,
            "minute": 0,
            "interval_hour": 0,
            "interval_end_hour": 23,
            "frequency": "Setiap Hari",
            "is_habit": True,
            "last_triggered_date": ""
        }]
    def get_schedules(self):
        return self.schedules
    def update_schedule(self, sid, obj):
        for i, s in enumerate(self.schedules):
            if s["id"] == sid:
                self.schedules[i] = obj

class DummyAudio:
    def notify(self, *args, **kwargs):
        print("NOTIFY CALLED!")

class DummyScheduler:
    def __init__(self):
        self.config = DummyConfig()
        self.audio = DummyAudio()
        self.daily_overrides = {}
        self.last_day = None

    def snooze_schedule(self, sched_id, new_time):
        self.daily_overrides[sched_id] = {"hour": new_time.hour, "minute": new_time.minute}

    def check_schedules(self, now):
        schedules = self.config.get_schedules()
        today_date_str = now.strftime("%Y-%m-%d")
        weekday = now.weekday()
        days_map = {0: "Senin", 1: "Selasa", 2: "Rabu", 3: "Kamis", 4: "Jumat", 5: "Sabtu", 6: "Minggu"}

        if self.last_day is None:
            self.last_day = now.day
        if now.day != self.last_day:
            self.daily_overrides.clear()
            self.last_day = now.day

        for agenda in schedules:
            if not agenda.get("active", False):
                continue
                
            sched_id = agenda.get("id")
            eff_start_hour = int(agenda.get("hour", -1))
            eff_minute = int(agenda.get("minute", -1))
            if sched_id in self.daily_overrides:
                eff_start_hour = self.daily_overrides[sched_id]["hour"]
                eff_minute = self.daily_overrides[sched_id]["minute"]

            if eff_minute != now.minute:
                continue

            interval_hour = int(agenda.get("interval_hour", 0))
            interval_end_hour = int(agenda.get("interval_end_hour", 23))

            if interval_hour > 0:
                pass
            else:
                if eff_start_hour != now.hour:
                    continue

            freq = agenda.get("frequency", "Setiap Hari")
            match = False

            if freq == "Setiap Hari":
                match = True

            trigger_key = f"{today_date_str}_{now.hour:02d}:{now.minute:02d}" if (interval_hour > 0 or sched_id in self.daily_overrides) else today_date_str
            if match and agenda.get("last_triggered_date") != trigger_key:
                agenda["last_triggered_date"] = trigger_key
                self.config.update_schedule(agenda["id"], agenda)
                print(f"[{now.strftime('%Y-%m-%d %H:%M')}] MATCHED & TRIGGERED! trigger_key={trigger_key}")

                self.audio.notify("test", "test")

                if agenda.get("is_habit", True) and interval_hour == 0:
                    new_time = now + datetime.timedelta(hours=1)
                    self.snooze_schedule(agenda["id"], new_time)
                    print(f"  -> Snoozed to {new_time.strftime('%Y-%m-%d %H:%M')}")

def run_sim():
    sched = DummyScheduler()
    start = datetime.datetime(2026, 9, 4, 13, 50)
    for i in range(150):
        now = start + datetime.timedelta(minutes=i)
        sched.check_schedules(now)

run_sim()
