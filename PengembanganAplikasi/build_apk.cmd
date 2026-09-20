@echo off
set JAVA_HOME=D:\AI\jdk-17
set ANDROID_HOME=D:\AI\androit
set PATH=D:\AI\jdk-17\bin;D:\AI\androit\platform-tools;D:\AI\androit\cmdline-tools\latest\bin;%PATH%
X:
cd \JadwalKuApp\android
call gradlew assembleDebug

