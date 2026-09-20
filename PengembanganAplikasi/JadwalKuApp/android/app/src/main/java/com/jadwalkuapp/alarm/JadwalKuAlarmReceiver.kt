package com.jadwalkuapp.alarm

import android.app.AlarmManager
import android.app.PendingIntent
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.os.Build
import java.util.Calendar

class JadwalKuAlarmReceiver : BroadcastReceiver() {

    private fun isQuietHour(hour: Int, minute: Int, startStr: String, endStr: String): Boolean {
        val startParts = startStr.split(":")
        val endParts = endStr.split(":")
        if (startParts.size < 2 || endParts.size < 2) return false
        
        val startH = startParts[0].toIntOrNull() ?: 22
        val startM = startParts[1].toIntOrNull() ?: 0
        val endH = endParts[0].toIntOrNull() ?: 6
        val endM = endParts[1].toIntOrNull() ?: 0
        
        val currentMins = hour * 60 + minute
        val startMins = startH * 60 + startM
        val endMins = endH * 60 + endM
        
        if (startMins < endMins) {
            return currentMins in startMins..endMins
        } else {
            return currentMins >= startMins || currentMins <= endMins
        }
    }

    override fun onReceive(context: Context, intent: Intent) {
        val alarmType = intent.getStringExtra("ALARM_TYPE") ?: "lonceng"
        val payload = intent.getStringExtra("PAYLOAD") ?: ""
        
        val prefs = context.getSharedPreferences("JadwalKuPrefs", Context.MODE_PRIVATE)
        val masterSwitch = prefs.getBoolean("master_switch", true)
        
        JadwalKuLogger.log(context, "Menerima Alarm: $alarmType - Payload: $payload - Master: $masterSwitch")
        
        val now = Calendar.getInstance()
        
        // Kompensasi jika alarm memicu lebih awal (misal detik 58 atau 59)
        if (now.get(Calendar.SECOND) >= 45) {
            now.add(Calendar.MINUTE, 1)
            JadwalKuLogger.log(context, "Alarm memicu lebih awal, dikompensasi +1 menit.")
        }
        
        val hour = now.get(Calendar.HOUR_OF_DAY)
        val minute = now.get(Calendar.MINUTE)
        
        val quietStart = prefs.getString("lonceng_quiet_start", "22:00") ?: "22:00"
        val quietEnd = prefs.getString("lonceng_quiet_end", "06:00") ?: "06:00"
        
        var quiet = isQuietHour(hour, minute, quietStart, quietEnd)
        if (!masterSwitch) {
            quiet = true // Jika master switch OFF, paksa diam
            JadwalKuLogger.log(context, "Master Switch OFF, suara diabaikan.")
        } else if (quiet) {
            JadwalKuLogger.log(context, "Masuk waktu Jam Tenang ($quietStart - $quietEnd), suara diabaikan.")
        }
        
        if (alarmType == "time_reminder") {
            val interval = prefs.getInt("interval_minutes", 60)
            
            if (!quiet) {
                val use24h = prefs.getBoolean("lonceng_24h", false)
                val engine = prefs.getString("voice_engine", "voice_packs")
                
                var hValue = hour
                if (!use24h) {
                    hValue = hour % 12
                    if (hValue == 0) hValue = 12
                }
                
                if (engine == "tts") {
                    val mText = if (minute == 0) "tepat" else "lewat $minute menit"
                    val timeStr = "Sekarang jam $hValue $mText"
                    
                    val serviceIntent = Intent(context, AudioService::class.java).apply {
                        putExtra("ALARM_TYPE", "tts")
                        putExtra("PAYLOAD", timeStr)
                    }
                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                        context.startForegroundService(serviceIntent)
                    } else {
                        context.startService(serviceIntent)
                    }
                } else {
                    val fileList = mutableListOf<String>()
                    fileList.add("sounds/chime.wav")
                    fileList.add("voice_master/sekarang.wav")
                    fileList.add("voice_master/jam.wav")
                    fileList.add("voice_master/${hValue}.wav")
                    
                    if (minute == 0) {
                        fileList.add("voice_master/tepat.wav")
                    } else {
                        fileList.add("voice_master/lewat.wav")
                        fileList.add("voice_master/${minute}.wav")
                        fileList.add("voice_master/menit.wav")
                    }

                    val finalPayload = fileList.joinToString(",")
                    val serviceIntent = Intent(context, AudioService::class.java).apply {
                        putExtra("ALARM_TYPE", "time_reminder")
                        putExtra("PAYLOAD", finalPayload)
                    }
                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                        context.startForegroundService(serviceIntent)
                    } else {
                        context.startService(serviceIntent)
                    }
                }
            }
            scheduleNextTimeReminder(context, interval)
            
        } else if (alarmType == "classic_lonceng") {
            val hasQuarters = prefs.getBoolean("lonceng_quarters", false)
            
            if (!quiet) {
                var finalPayload = ""
                
                if (minute == 0) {
                    var h12 = hour % 12
                    if (h12 == 0) h12 = 12
                    finalPayload = "lonceng_jam_$h12"
                } else if (hasQuarters) {
                    if (minute == 15 || minute == 30 || minute == 45) {
                        finalPayload = "lonceng_quarter_$minute"
                    }
                }
                
                if (finalPayload.isNotEmpty()) {
                    JadwalKuLogger.log(context, "Memutar Classic Lonceng: $finalPayload")
                    val serviceIntent = Intent(context, AudioService::class.java).apply {
                        putExtra("ALARM_TYPE", "classic_lonceng")
                        putExtra("PAYLOAD", finalPayload)
                    }
                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                        context.startForegroundService(serviceIntent)
                    } else {
                        context.startService(serviceIntent)
                    }
                } else {
                    JadwalKuLogger.log(context, "Classic Lonceng terpicu di menit $minute, tidak ada payload yang valid.")
                }
            }
            scheduleNextLonceng(context, hasQuarters)
            
        } else {
            if (!quiet || alarmType == "timer") {
                val serviceIntent = Intent(context, AudioService::class.java).apply {
                    putExtra("ALARM_TYPE", alarmType)
                    putExtra("PAYLOAD", payload)
                }
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                    context.startForegroundService(serviceIntent)
                } else {
                    context.startService(serviceIntent)
                }
            }
        }
    }

    private fun scheduleNextLonceng(context: Context, hasQuarters: Boolean) {
        val prefs = context.getSharedPreferences("JadwalKuPrefs", Context.MODE_PRIVATE)
        val isEnabled = prefs.getBoolean("lonceng_enabled", false)
        if (!isEnabled) {
            JadwalKuLogger.log(context, "Lonceng dinonaktifkan, tidak menjadwalkan ulang.")
            return
        }
        
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
            target.add(Calendar.MINUTE, if (hasQuarters) 15 else 60)
        }

        val intent = Intent(context, JadwalKuAlarmReceiver::class.java).apply {
            putExtra("ALARM_TYPE", "classic_lonceng")
        }
        val pendingIntent = PendingIntent.getBroadcast(
            context,
            1004,
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        val alarmManager = context.getSystemService(Context.ALARM_SERVICE) as AlarmManager
        try {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                alarmManager.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, target.timeInMillis, pendingIntent)
            } else {
                alarmManager.setExact(AlarmManager.RTC_WAKEUP, target.timeInMillis, pendingIntent)
            }
            JadwalKuLogger.log(context, "Lonceng dijadwalkan ulang pada: ${target.time}")
        } catch (e: Exception) {
            JadwalKuLogger.log(context, "Gagal jadwalkan ulang lonceng: ${e.message}")
        }
    }

    private fun scheduleNextTimeReminder(context: Context, interval: Int) {
        val prefs = context.getSharedPreferences("JadwalKuPrefs", Context.MODE_PRIVATE)
        val isEnabled = prefs.getBoolean("interval_enabled", false)
        if (!isEnabled) {
            JadwalKuLogger.log(context, "Time Reminder dinonaktifkan, tidak menjadwalkan ulang.")
            return
        }

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

        val intent = Intent(context, JadwalKuAlarmReceiver::class.java).apply {
            putExtra("ALARM_TYPE", "time_reminder")
        }
        val pendingIntent = PendingIntent.getBroadcast(
            context,
            1003,
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        val alarmManager = context.getSystemService(Context.ALARM_SERVICE) as AlarmManager
        try {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                alarmManager.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, target.timeInMillis, pendingIntent)
            } else {
                alarmManager.setExact(AlarmManager.RTC_WAKEUP, target.timeInMillis, pendingIntent)
            }
            JadwalKuLogger.log(context, "Time Reminder dijadwalkan ulang pada: ${target.time}")
        } catch (e: Exception) {
            JadwalKuLogger.log(context, "Gagal jadwalkan ulang time reminder: ${e.message}")
        }
    }
}
