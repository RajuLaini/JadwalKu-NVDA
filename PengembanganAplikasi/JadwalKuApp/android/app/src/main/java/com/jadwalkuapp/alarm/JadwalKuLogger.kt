package com.jadwalkuapp.alarm

import android.content.Context
import android.util.Log
import java.io.File
import java.io.FileWriter
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

object JadwalKuLogger {
    fun log(context: Context, message: String) {
        Log.d("JadwalKu", message)
        try {
            val dir = context.getExternalFilesDir(null)
            if (dir != null) {
                val file = File(dir, "jadwalku_android.log")
                val writer = FileWriter(file, true)
                val sdf = SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault())
                val time = sdf.format(Date())
                writer.append("[$time] $message\n")
                writer.flush()
                writer.close()
            }
        } catch (e: Exception) {
            Log.e("JadwalKuLogger", "Gagal menulis log", e)
        }
    }
}
