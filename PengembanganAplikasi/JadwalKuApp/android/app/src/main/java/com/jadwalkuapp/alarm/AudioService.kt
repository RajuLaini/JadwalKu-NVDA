package com.jadwalkuapp.alarm

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Context
import android.content.Intent
import android.os.Build
import android.os.IBinder
import androidx.core.app.NotificationCompat
import android.util.Log
import android.speech.tts.TextToSpeech
import android.speech.tts.UtteranceProgressListener
import java.util.Locale

class AudioService : Service() {
    private val CHANNEL_ID = "JadwalKuAudioChannel"
    private var tts: TextToSpeech? = null
    private var ttsTextToSpeak: String? = null

    override fun onCreate() {
        super.onCreate()
        createNotificationChannel()
        
        tts = TextToSpeech(this) { status ->
            if (status == TextToSpeech.SUCCESS) {
                tts?.language = Locale("id", "ID")
                tts?.setOnUtteranceProgressListener(object : UtteranceProgressListener() {
                    override fun onStart(utteranceId: String?) {}
                    override fun onDone(utteranceId: String?) {
                        stopSelf()
                    }
                    override fun onError(utteranceId: String?) {
                        stopSelf()
                    }
                })
                
                ttsTextToSpeak?.let {
                    val params = android.os.Bundle()
                    tts?.speak(it, TextToSpeech.QUEUE_FLUSH, params, "tts_alarm")
                    ttsTextToSpeak = null
                }
            } else {
                stopSelf()
            }
        }
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val alarmType = intent?.getStringExtra("ALARM_TYPE") ?: "lonceng"
        val payload = intent?.getStringExtra("PAYLOAD") ?: ""

        val notification = createNotification("JadwalKu Berjalan", "Memutar suara $alarmType...")
        startForeground(1, notification)

        Log.d("JadwalKuAudio", "Memutar: $alarmType - $payload")
        
        if (alarmType == "tts") {
            if (ttsTextToSpeak == null && tts != null && tts?.isLanguageAvailable(Locale("id", "ID")) != TextToSpeech.LANG_NOT_SUPPORTED) {
                val params = android.os.Bundle()
                tts?.speak(payload, TextToSpeech.QUEUE_FLUSH, params, "tts_alarm")
            } else {
                ttsTextToSpeak = payload
            }
            return START_NOT_STICKY
        }
        
        Thread {
            if (alarmType == "classic_lonceng") {
                if (payload.startsWith("lonceng_jam_")) {
                    val h = payload.replace("lonceng_jam_", "").toIntOrNull() ?: 12
                    playLoncengJam(h)
                } else if (payload.startsWith("lonceng_quarter_")) {
                    val m = payload.replace("lonceng_quarter_", "").toIntOrNull() ?: 15
                    playLoncengQuarter(m)
                }
            } else {
                val player = GaplessAudioPlayer(this)
                val files = payload.split(",").map { it.trim() }.filter { it.isNotEmpty() }
                if (files.isNotEmpty()) {
                    player.playSequence(files)
                }
                Thread.sleep((files.size * 1200L).coerceAtLeast(3000L))
            }
            stopSelf()
        }.start()

        return START_NOT_STICKY
    }
    
    override fun onDestroy() {
        tts?.stop()
        tts?.shutdown()
        super.onDestroy()
    }

    private fun playLoncengJam(hour: Int) {
        try {
            val afdMulai = assets.openFd("sounds/Lonceng/mulaiLonceng.wav")
            val mpMulai = android.media.MediaPlayer()
            mpMulai.setAudioAttributes(
                android.media.AudioAttributes.Builder()
                    .setUsage(android.media.AudioAttributes.USAGE_ALARM)
                    .setContentType(android.media.AudioAttributes.CONTENT_TYPE_SPEECH)
                    .build()
            )
            mpMulai.setDataSource(afdMulai.fileDescriptor, afdMulai.startOffset, afdMulai.length)
            mpMulai.prepare()
            mpMulai.start()
            
            Thread.sleep(16500)
            
            val afdKetuk = assets.openFd("sounds/Lonceng/ketukanLonceng.wav")
            for (i in 0 until hour) {
                val mpKetuk = android.media.MediaPlayer()
                mpKetuk.setAudioAttributes(
                    android.media.AudioAttributes.Builder()
                        .setUsage(android.media.AudioAttributes.USAGE_ALARM)
                        .setContentType(android.media.AudioAttributes.CONTENT_TYPE_SPEECH)
                        .build()
                )
                mpKetuk.setDataSource(afdKetuk.fileDescriptor, afdKetuk.startOffset, afdKetuk.length)
                mpKetuk.prepare()
                mpKetuk.start()
                mpKetuk.setOnCompletionListener { it.release() }
                
                Thread.sleep(1800)
            }
            
            Thread.sleep(3000)
            mpMulai.release()
            afdMulai.close()
            afdKetuk.close()
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    private fun playLoncengQuarter(minute: Int) {
        try {
            val file = when (minute) {
                15 -> "sounds/Lonceng/SeperempatJam.wav"
                30 -> "sounds/Lonceng/SetengahJam.wav"
                45 -> "sounds/Lonceng/TigaQua.wav"
                else -> return
            }
            val afd = assets.openFd(file)
            val mp = android.media.MediaPlayer()
            mp.setAudioAttributes(
                android.media.AudioAttributes.Builder()
                    .setUsage(android.media.AudioAttributes.USAGE_ALARM)
                    .setContentType(android.media.AudioAttributes.CONTENT_TYPE_SPEECH)
                    .build()
            )
            mp.setDataSource(afd.fileDescriptor, afd.startOffset, afd.length)
            mp.prepare()
            mp.start()
            
            Thread.sleep(mp.duration.toLong() + 2000L)
            mp.release()
            afd.close()
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    override fun onBind(intent: Intent?): IBinder? { return null }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(CHANNEL_ID, "JadwalKu Audio Service", NotificationManager.IMPORTANCE_LOW)
            val manager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            manager.createNotificationChannel(channel)
        }
    }

    private fun createNotification(title: String, content: String): Notification {
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle(title)
            .setContentText(content)
            .setSmallIcon(android.R.drawable.ic_media_play)
            .build()
    }
}
