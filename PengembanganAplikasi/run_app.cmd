@echo off
set JAVA_HOME=D:\AI\jdk-17
set ANDROID_HOME=D:\AI\androit
set PATH=D:\AI\jdk-17\bin;D:\AI\androit\platform-tools;D:\AI\androit\cmdline-tools\latest\bin;%PATH%
cd /d "c:\Users\Raju Laini\Documents\Project_Jadwalku\PengembanganAplikasi\JadwalKuApp"
echo Memulai kompilasi Android...
npx react-native run-android
