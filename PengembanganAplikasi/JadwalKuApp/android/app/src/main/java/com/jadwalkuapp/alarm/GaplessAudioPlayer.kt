package com.jadwalkuapp.alarm

import android.content.Context
import android.media.AudioAttributes
import android.media.AudioFormat
import android.media.AudioTrack
import android.util.Log
import java.io.InputStream
import java.nio.ByteBuffer
import java.nio.ByteOrder

class GaplessAudioPlayer(private val context: Context) {

    fun playSequence(fileNames: List<String>) {
        if (fileNames.isEmpty()) return

        try {
            // Semua WAV pack JadwalKu ternyata berformat 44100Hz, 16-bit, Mono
            val sampleRate = 44100
            val channelConfig = AudioFormat.CHANNEL_OUT_MONO
            val audioFormat = AudioFormat.ENCODING_PCM_16BIT

            val minBufferSize = AudioTrack.getMinBufferSize(sampleRate, channelConfig, audioFormat)
            
            val audioTrack = AudioTrack.Builder()
                .setAudioAttributes(
                    AudioAttributes.Builder()
                        .setUsage(AudioAttributes.USAGE_ALARM)
                        .setContentType(AudioAttributes.CONTENT_TYPE_SPEECH)
                        .build()
                )
                .setAudioFormat(
                    AudioFormat.Builder()
                        .setEncoding(audioFormat)
                        .setSampleRate(sampleRate)
                        .setChannelMask(channelConfig)
                        .build()
                )
                .setBufferSizeInBytes(minBufferSize * 4)
                .setTransferMode(AudioTrack.MODE_STREAM)
                .build()

            audioTrack.play()

            for (assetPath in fileNames) {
                try {
                    val inputStream: InputStream = context.assets.open(assetPath)
                    
                    // Melewati 44 bytes header WAV standar
                    val header = ByteArray(44)
                    inputStream.read(header)

                    val buffer = ByteArray(minBufferSize)
                    var bytesRead: Int

                    while (inputStream.read(buffer).also { bytesRead = it } != -1) {
                        audioTrack.write(buffer, 0, bytesRead)
                    }
                    inputStream.close()
                } catch (e: Exception) {
                    Log.e("JadwalKuAudio", "Gagal memutar: $assetPath", e)
                }
            }
            
            // Tunggu buffer terakhir benar-benar habis dimainkan oleh hardware
            // audioTrack.stop() pada beberapa HP memotong buffer secara agresif, jadi kita sleep sebentar.
            Thread.sleep(1000) 
            
            audioTrack.stop()
            audioTrack.release()
            
        } catch (e: Exception) {
            Log.e("JadwalKuAudio", "Error in audio sequence", e)
        }
    }
}
