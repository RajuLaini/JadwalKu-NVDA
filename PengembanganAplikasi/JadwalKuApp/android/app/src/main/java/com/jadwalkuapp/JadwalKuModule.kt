package com.jadwalkuapp

import android.app.AlarmManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.content.SharedPreferences
import android.os.Build
import android.util.Log
import com.facebook.react.bridge.ReactApplicationContext
import com.facebook.react.bridge.ReactContextBaseJavaModule
import com.facebook.react.bridge.ReactMethod
import com.facebook.react.bridge.Promise
import com.jadwalkuapp.alarm.JadwalKuAlarmReceiver
import java.util.Calendar

class JadwalKuModule(reactContext: ReactApplicationContext) : ReactContextBaseJavaModule(reactContext) {

    override fun getName(): String {
        return "JadwalKuNative"
    }

    private fun getPrefs(): SharedPreferences {
        return reactApplicationContext.getSharedPreferences("JadwalKuPrefs", Context.MODE_PRIVATE)
    }

    @ReactMethod
    fun saveTimeReminderConfig(enabled: Boolean, interval: Int, promise: Promise) {
        try {
            val editor = getPrefs().edit()
            editor.putBoolean("interval_enabled", enabled)
            editor.putInt("interval_minutes", interval)
            editor.apply()
            
            if (enabled) {
                scheduleNextTimeReminder()
                promise.resolve("Time Reminder Enabled with interval: $interval")
            } else {
                cancelAlarm("time_reminder", promise)
            }
        } catch (e: Exception) {
            promise.reject("CONFIG_ERROR", e)
        }
    }

    @ReactMethod
    fun saveLoncengConfig(enabled: Boolean, quartersEnabled: Boolean, promise: Promise) {
        try {
            val editor = getPrefs().edit()
            editor.putBoolean("lonceng_enabled", enabled)
            editor.putBoolean("lonceng_quarters", quartersEnabled)
            editor.apply()
            
            if (enabled || quartersEnabled) {
                scheduleNextLonceng()
                promise.resolve("Lonceng Config Saved")
            } else {
                cancelAlarm("classic_lonceng", promise)
            }
        } catch (e: Exception) {
            promise.reject("CONFIG_ERROR", e)
        }
    }

    private fun scheduleNextLonceng() {
        val prefs = getPrefs()
        val isLoncengEnabled = prefs.getBoolean("lonceng_enabled", false)
        val hasQuarters = prefs.getBoolean("lonceng_quarters", false)
        
        if (!isLoncengEnabled && !hasQuarters) return

        val now = Calendar.getInstance()
        val m = now.get(Calendar.MINUTE)
        
        var nextMinute = 0
        var addHour = 0
        
        if (hasQuarters) {
            if (m < 15) nextMinute = 15
            else if (m < 30) nextMinute = 30
            else if (m < 45) nextMinute = 45
            else { nextMinute = 0; addHour = 1 }
        } else {
            nextMinute = 0
            addHour = 1
        }
        
        val target = Calendar.getInstance().apply {
            if (addHour > 0) add(Calendar.HOUR_OF_DAY, 1)
            set(Calendar.MINUTE, nextMinute)
            set(Calendar.SECOND, 0)
            set(Calendar.MILLISECOND, 0)
        }
        
        if (target.timeInMillis <= System.currentTimeMillis()) {
            // Safety fallback
            target.add(Calendar.MINUTE, if (hasQuarters) 15 else 60)
        }

        val intent = Intent(reactApplicationContext, JadwalKuAlarmReceiver::class.java).apply {
            putExtra("ALARM_TYPE", "classic_lonceng")
        }
        
        val pendingIntent = PendingIntent.getBroadcast(
            reactApplicationContext,
            1004,
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val alarmManager = reactApplicationContext.getSystemService(Context.ALARM_SERVICE) as AlarmManager
        try {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                alarmManager.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, target.timeInMillis, pendingIntent)
            } else {
                alarmManager.setExact(AlarmManager.RTC_WAKEUP, target.timeInMillis, pendingIntent)
            }
            Log.d("JadwalKuNative", "Classic Lonceng dijadwalkan pada: ${target.time}")
        } catch (e: Exception) {
            Log.e("JadwalKuNative", "Gagal set alarm lonceng", e)
        }
    }
    private fun scheduleNextTimeReminder() {
        val prefs = getPrefs()
        if (!prefs.getBoolean("interval_enabled", false)) return
        
        val interval = prefs.getInt("interval_minutes", 60)
        
        val now = Calendar.getInstance()
        val currentMinute = now.get(Calendar.MINUTE)
        
        var nextMinute = ((currentMinute / interval) + 1) * interval
        var addHour = 0
        if (nextMinute >= 60) {
            nextMinute -= 60
            addHour = 1
        }
        
        val target = Calendar.getInstance().apply {
            if (addHour > 0) add(Calendar.HOUR_OF_DAY, 1)
            set(Calendar.MINUTE, nextMinute)
            set(Calendar.SECOND, 0)
            set(Calendar.MILLISECOND, 0)
        }
        
        if (target.timeInMillis <= System.currentTimeMillis()) {
            target.add(Calendar.MINUTE, interval)
        }

        val intent = Intent(reactApplicationContext, JadwalKuAlarmReceiver::class.java).apply {
            putExtra("ALARM_TYPE", "time_reminder")
        }
        
        val pendingIntent = PendingIntent.getBroadcast(
            reactApplicationContext,
            1003,
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val alarmManager = reactApplicationContext.getSystemService(Context.ALARM_SERVICE) as AlarmManager
        try {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                alarmManager.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, target.timeInMillis, pendingIntent)
            } else {
                alarmManager.setExact(AlarmManager.RTC_WAKEUP, target.timeInMillis, pendingIntent)
            }
            Log.d("JadwalKuNative", "Time Reminder dijadwalkan pada: ${target.time}")
        } catch (e: SecurityException) {
            Log.e("JadwalKuNative", "Gagal set alarm", e)
        }
    }

    @ReactMethod
    fun setExactAlarm(timeInMillis: Double, alarmType: String, payload: String, promise: Promise) {
        try {
            val alarmManager = reactApplicationContext.getSystemService(Context.ALARM_SERVICE) as AlarmManager
            val intent = Intent(reactApplicationContext, JadwalKuAlarmReceiver::class.java).apply {
                putExtra("ALARM_TYPE", alarmType)
                putExtra("PAYLOAD", payload)
            }
            
            // Untuk hourly_chime kita pakai 1001, untuk timer kita pakai 1002, time_reminder 1003, classic_lonceng 1004
            val requestCode = if (alarmType == "hourly_chime") 1001 else if (alarmType == "time_reminder") 1003 else if (alarmType == "classic_lonceng") 1004 else 1002
            
            val pendingIntent = PendingIntent.getBroadcast(
                reactApplicationContext,
                requestCode,
                intent,
                PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
            )

            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                alarmManager.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, timeInMillis.toLong(), pendingIntent)
            } else {
                alarmManager.setExact(AlarmManager.RTC_WAKEUP, timeInMillis.toLong(), pendingIntent)
            }
            
            promise.resolve("Alarm set for $timeInMillis")
        } catch (e: Exception) {
            promise.reject("ALARM_ERROR", e)
        }
    }

    @ReactMethod
    fun showTimePicker(currentHour: Int, currentMinute: Int, promise: Promise) {
        val activity = getCurrentActivity()
        if (activity == null) {
            promise.reject("E_ACTIVITY_DOES_NOT_EXIST", "Activity is null")
            return
        }
        
        activity.runOnUiThread {
            android.app.TimePickerDialog(
                activity,
                android.app.TimePickerDialog.OnTimeSetListener { _, hourOfDay, minute ->
                    val map = com.facebook.react.bridge.Arguments.createMap()
                    map.putInt("hour", hourOfDay)
                    map.putInt("minute", minute)
                    promise.resolve(map)
                },
                currentHour,
                currentMinute,
                true // 24 hour view
            ).show()
        }
    }

    @ReactMethod
    fun savePreference(key: String, type: String, value: String, promise: Promise) {
        val editor = getPrefs().edit()
        when (type) {
            "boolean" -> editor.putBoolean(key, value.toBooleanStrictOrNull() ?: false)
            "int" -> editor.putInt(key, value.toIntOrNull() ?: 0)
            "string" -> editor.putString(key, value)
        }
        editor.apply()
        promise.resolve(true)
    }
    
    @ReactMethod
    fun getPreference(key: String, type: String, defaultValue: String, promise: Promise) {
        val prefs = getPrefs()
        when (type) {
            "boolean" -> promise.resolve(prefs.getBoolean(key, defaultValue.toBooleanStrictOrNull() ?: false))
            "int" -> promise.resolve(prefs.getInt(key, defaultValue.toIntOrNull() ?: 0))
            "string" -> promise.resolve(prefs.getString(key, defaultValue))
        }
    }

    @ReactMethod
    fun cancelAlarm(alarmType: String, promise: Promise) {
        try {
            val alarmManager = reactApplicationContext.getSystemService(Context.ALARM_SERVICE) as AlarmManager
            val intent = Intent(reactApplicationContext, JadwalKuAlarmReceiver::class.java).apply {
                putExtra("ALARM_TYPE", alarmType)
                // Payload tidak perlu cocok untuk cancel, karena filter Intent hanya berdasarkan class (dan action jika ada).
                // Namun, kita harus menggunakan requestCode yang sama persis saat kita membuat alarm.
            }
            
            // Untuk hourly_chime kita pakai 1001, untuk timer kita pakai 1002, time_reminder 1003, classic_lonceng 1004
            val requestCode = if (alarmType == "hourly_chime") 1001 else if (alarmType == "time_reminder") 1003 else if (alarmType == "classic_lonceng") 1004 else 1002
            
            val pendingIntent = PendingIntent.getBroadcast(
                reactApplicationContext,
                requestCode,
                intent,
                PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
            )

            alarmManager.cancel(pendingIntent)
            promise.resolve("Alarm $alarmType cancelled")
        } catch (e: Exception) {
            promise.reject("CANCEL_ERROR", e)
        }
    }
}
