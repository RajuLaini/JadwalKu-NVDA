import React, { useState, useEffect } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { SafeAreaView, View, Text, Switch, StyleSheet, ScrollView, TouchableOpacity, Button, NativeModules } from 'react-native';
import { SafeAreaProvider } from 'react-native-safe-area-context';

const { JadwalKuNative } = NativeModules;
const Tab = createBottomTabNavigator();

// --- Tab 1: Agenda & Habit ---
function AgendaScreen() {
  return (
    <SafeAreaView style={styles.container}>
      <Text style={styles.headerTitle} accessibilityRole="header">Agenda & Habit</Text>
      <ScrollView style={styles.content}>
        <View style={styles.card} accessible={true} accessibilityRole="button" accessibilityLabel="Rutinitas Pagi, Aktif, Setiap Hari jam 08:00.">
          <Text style={styles.cardTitle}>Rutinitas Pagi</Text>
          <Text style={styles.cardDesc}>Setiap Hari - 08:00</Text>
          <Switch value={true} onValueChange={() => {}} />
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

// --- Tab 2: Lonceng & Waktu ---
function LoncengScreen() {
  const [intervalOn, setIntervalOn] = useState(false);
  const [intervalVal, setIntervalVal] = useState(60);
  
  const [loncengOn, setLoncengOn] = useState(false);
  const [quarterOn, setQuarterOn] = useState(false);

  const [use24Hour, setUse24Hour] = useState(false);
  const [quietStart, setQuietStart] = useState("22:00");
  const [quietEnd, setQuietEnd] = useState("06:00");

  useEffect(() => {
    if (JadwalKuNative) {
      JadwalKuNative.getPreference('interval_enabled', 'boolean', 'false').then((v: boolean) => setIntervalOn(v));
      JadwalKuNative.getPreference('interval_minutes', 'int', '60').then((v: number) => setIntervalVal(v));
      JadwalKuNative.getPreference('lonceng_enabled', 'boolean', 'false').then((v: boolean) => setLoncengOn(v));
      JadwalKuNative.getPreference('lonceng_quarters', 'boolean', 'false').then((v: boolean) => setQuarterOn(v));
      JadwalKuNative.getPreference('lonceng_24h', 'boolean', 'false').then((v: boolean) => setUse24Hour(v));
      JadwalKuNative.getPreference('lonceng_quiet_start', 'string', '22:00').then((v: string) => setQuietStart(v));
      JadwalKuNative.getPreference('lonceng_quiet_end', 'string', '06:00').then((v: string) => setQuietEnd(v));
    }
  }, []);

  const toggle24Hour = (val: boolean) => {
    setUse24Hour(val);
    if (JadwalKuNative) JadwalKuNative.savePreference('lonceng_24h', 'boolean', val.toString());
  };

  const openTimePicker = (isStart: boolean) => {
    if (!JadwalKuNative) return;
    const current = isStart ? quietStart : quietEnd;
    const [h, m] = current.split(':').map(Number);
    
    JadwalKuNative.showTimePicker(h, m)
      .then((res: any) => {
        const timeStr = `${res.hour.toString().padStart(2, '0')}:${res.minute.toString().padStart(2, '0')}`;
        if (isStart) {
          setQuietStart(timeStr);
          JadwalKuNative.savePreference('lonceng_quiet_start', 'string', timeStr);
        } else {
          setQuietEnd(timeStr);
          JadwalKuNative.savePreference('lonceng_quiet_end', 'string', timeStr);
        }
      })
      .catch((e: any) => console.log(e));
  };

  const toggleInterval = (val: boolean) => {
    setIntervalOn(val);
    if (!JadwalKuNative) return;
    
    JadwalKuNative.saveTimeReminderConfig(val, intervalVal)
      .then((msg: string) => {
        if (val) {
          alert(`Pengingat aktif! Berbunyi setiap ${intervalVal} menit.`);
        } else {
          alert("Pengingat Waktu dimatikan!");
        }
      })
      .catch((e: any) => alert("Error: " + e));
  };

  const selectInterval = (val: number) => {
    setIntervalVal(val);
    if (intervalOn && JadwalKuNative) {
      JadwalKuNative.saveTimeReminderConfig(true, val);
      alert(`Interval diubah menjadi ${val} menit.`);
    }
  };

  const toggleLonceng = (val: boolean) => {
    setLoncengOn(val);
    if (JadwalKuNative) {
      JadwalKuNative.saveLoncengConfig(val, quarterOn);
    }
  };

  const toggleQuarter = (val: boolean) => {
    setQuarterOn(val);
    if (JadwalKuNative) {
      JadwalKuNative.saveLoncengConfig(loncengOn, val);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <Text style={styles.headerTitle} accessibilityRole="header">Lonceng Klasik & Waktu</Text>
      <ScrollView style={styles.content}>
        
        {/* Kartu Lonceng Klasik */}
        <View style={styles.card}>
          <View style={{flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12}}>
            <Text style={styles.cardTitle}>Lonceng Klasik (Grandfather Clock)</Text>
            <Switch value={loncengOn} onValueChange={toggleLonceng} accessibilityLabel="Aktifkan Lonceng Klasik" />
          </View>
          <Text style={styles.cardDesc}>Berbunyi dengan dentang panjang di setiap pergantian jam tepat.</Text>
          
          <View style={{flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginTop: 16}}>
            <Text style={styles.settingText}>Bunyikan Nada Kuartal (Tiap 15 Menit)</Text>
            <Switch value={quarterOn} onValueChange={toggleQuarter} accessibilityLabel="Bunyikan Nada Kuartal Tiap 15 Menit" />
          </View>
        </View>

        {/* Kartu Pengingat Waktu Berkala */}
        <View style={styles.card}>
          <View style={{flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12}}>
            <Text style={styles.cardTitle}>Pengingat Waktu Berkala</Text>
            <Switch value={intervalOn} onValueChange={toggleInterval} accessibilityLabel="Aktifkan Pengingat Waktu Berkala" />
          </View>
          <Text style={styles.cardDesc}>Berbunyi dan membacakan jam pada kelipatan menit tertentu.</Text>
          
          <Text style={[styles.settingText, {marginTop: 16, marginBottom: 8, fontWeight: 'bold'}]}>Pilih Interval (Menit):</Text>
          <View style={{flexDirection: 'row', flexWrap: 'wrap', gap: 8}}>
            {[5, 10, 15, 30, 60].map(v => (
              <TouchableOpacity 
                key={v}
                style={{
                  backgroundColor: intervalVal === v ? '#007AFF' : '#E0E0E0',
                  paddingVertical: 8,
                  paddingHorizontal: 16,
                  borderRadius: 20,
                  marginRight: 8,
                  marginBottom: 8
                }}
                onPress={() => selectInterval(v)}
                accessibilityRole="button"
                accessibilityState={{selected: intervalVal === v}}
                accessibilityLabel={`${v} Menit Sekali`}
              >
                <Text style={{color: intervalVal === v ? '#FFF' : '#333', fontWeight: 'bold'}}>
                  {v === 60 ? '1 Jam' : `${v} Menit`}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
          
          <View style={{flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginTop: 16, borderTopWidth: 1, borderTopColor: '#EEE', paddingTop: 16}}>
            <Text style={styles.settingText}>Gunakan Format 24 Jam</Text>
            <Switch value={use24Hour} onValueChange={toggle24Hour} accessibilityLabel="Gunakan Format 24 Jam" />
          </View>
        </View>

        {/* Kartu Jam Tenang */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Jam Tenang (Quiet Hours)</Text>
          <Text style={styles.cardDesc}>Lonceng dan Pengingat Waktu tidak akan berbunyi di dalam rentang waktu ini.</Text>
          
          <View style={{flexDirection: 'row', justifyContent: 'space-between', marginTop: 16}}>
            <TouchableOpacity onPress={() => openTimePicker(true)} style={{flex: 1, backgroundColor: '#F0F0F0', padding: 12, borderRadius: 8, marginRight: 8, alignItems: 'center'}}>
              <Text style={{fontSize: 12, color: '#666'}}>Mulai</Text>
              <Text style={{fontSize: 20, fontWeight: 'bold', color: '#333'}}>{quietStart}</Text>
            </TouchableOpacity>
            <TouchableOpacity onPress={() => openTimePicker(false)} style={{flex: 1, backgroundColor: '#F0F0F0', padding: 12, borderRadius: 8, marginLeft: 8, alignItems: 'center'}}>
              <Text style={{fontSize: 12, color: '#666'}}>Berakhir</Text>
              <Text style={{fontSize: 20, fontWeight: 'bold', color: '#333'}}>{quietEnd}</Text>
            </TouchableOpacity>
          </View>
        </View>
        
      </ScrollView>
    </SafeAreaView>
  );
}

// --- Tab 3: Timer & Alarm ---
function TimerScreen() {
  const [minutes, setMinutes] = useState(1);
  const [timerRunning, setTimerRunning] = useState(false);
  const [targetTime, setTargetTime] = useState<number | null>(null);
  const [timeLeft, setTimeLeft] = useState(0);

  useEffect(() => {
    let interval: any;
    if (timerRunning && targetTime) {
      interval = setInterval(() => {
        const remaining = Math.max(0, Math.floor((targetTime - Date.now()) / 1000));
        setTimeLeft(remaining);
        if (remaining === 0) {
          setTimerRunning(false);
          setTargetTime(null);
        }
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [timerRunning, targetTime]);

  const startTimer = () => {
    if (!JadwalKuNative) {
      alert("Modul Native JadwalKu tidak ditemukan!");
      return;
    }
    
    const timeToRing = Date.now() + minutes * 60000;
    
    // Rangkai kata: chime + waktu + [angka] + menit + tepat
    const payload = `sounds/chime.wav,voice_master/waktu.wav,voice_master/${minutes}.wav,voice_master/menit.wav,voice_master/tepat.wav`;
    
    JadwalKuNative.setExactAlarm(timeToRing, "voicepack", payload)
      .then(() => {
        setTargetTime(timeToRing);
        setTimerRunning(true);
        setTimeLeft(minutes * 60);
      })
      .catch((e: any) => alert("Gagal: " + e));
  };
  
  const stopTimer = () => {
    if (JadwalKuNative) JadwalKuNative.cancelAlarm("voicepack");
    setTimerRunning(false);
    setTargetTime(null);
    setTimeLeft(0);
  };

  const formatTime = (secs: number) => {
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return `${m}:${s < 10 ? '0' : ''}${s}`;
  };

  return (
    <SafeAreaView style={styles.container}>
      <Text style={styles.headerTitle} accessibilityRole="header">Timer Cepat & Alarm</Text>
      <View style={styles.content}>
        
        {!timerRunning ? (
          <View>
            <Text style={[styles.settingText, {fontSize: 24, textAlign: 'center', marginVertical: 20}]}>Set Timer: {minutes} Menit</Text>
            <View style={styles.timerControls}>
              <Button title="- 1 Menit" onPress={() => setMinutes(Math.max(1, minutes - 1))} />
              <Button title="+ 1 Menit" onPress={() => setMinutes(minutes + 1)} />
            </View>
            <Button title="Mulai Timer Android" onPress={startTimer} color="#28a745" />
          </View>
        ) : (
          <View>
            <Text style={[styles.settingText, {fontSize: 48, textAlign: 'center', marginVertical: 40}]}>{formatTime(timeLeft)}</Text>
            <Button title="Batalkan Timer" onPress={stopTimer} color="#dc3545" />
          </View>
        )}
        
      </View>
    </SafeAreaView>
  );
}

// --- Tab 4: Pengaturan ---
function SettingsScreen() {
  const [masterSwitch, setMasterSwitch] = useState(true);
  const [voiceEngine, setVoiceEngine] = useState('voice_packs');

  useEffect(() => {
    if (JadwalKuNative) {
      JadwalKuNative.getPreference('master_switch', 'boolean', 'true')
        .then((val: boolean) => setMasterSwitch(val));
      JadwalKuNative.getPreference('voice_engine', 'string', 'voice_packs')
        .then((val: string) => setVoiceEngine(val));
    }
  }, []);

  const toggleMasterSwitch = (val: boolean) => {
    setMasterSwitch(val);
    if (JadwalKuNative) {
      JadwalKuNative.savePreference('master_switch', 'boolean', val.toString());
    }
  };

  const changeEngine = (engine: string) => {
    setVoiceEngine(engine);
    if (JadwalKuNative) {
      JadwalKuNative.savePreference('voice_engine', 'string', engine);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <Text style={styles.headerTitle} accessibilityRole="header">Pengaturan</Text>
      <ScrollView style={styles.content}>
        
        <View style={[styles.card, {backgroundColor: masterSwitch ? '#E8F5E9' : '#FFEBEE'}]}>
          <Text style={styles.cardTitle}>Status JadwalKu (Global)</Text>
          <Text style={styles.cardDesc}>
            {masterSwitch 
              ? "Aplikasi AKTIF. Lonceng dan Pengingat Waktu berjalan di latar belakang." 
              : "Aplikasi MATI. JadwalKu berhenti bersuara sepenuhnya hingga dihidupkan kembali."}
          </Text>
          <View style={{flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginTop: 16}}>
            <Text style={{fontSize: 16, fontWeight: 'bold', color: masterSwitch ? '#2E7D32' : '#C62828'}}>
              {masterSwitch ? "ON" : "OFF"}
            </Text>
            <Switch 
              value={masterSwitch} 
              onValueChange={toggleMasterSwitch} 
              accessibilityLabel="Matikan atau hidupkan seluruh JadwalKu" 
            />
          </View>
        </View>

        <View style={styles.card}>
          <Text style={styles.cardTitle}>Mesin Pembaca Waktu</Text>
          <Text style={styles.cardDesc}>Pilih suara yang digunakan untuk Pengingat Waktu Berkala dan Timer.</Text>
          
          <TouchableOpacity 
            style={{flexDirection: 'row', alignItems: 'center', marginTop: 16}}
            onPress={() => changeEngine('voice_packs')}
            accessibilityRole="radio"
            accessibilityState={{checked: voiceEngine === 'voice_packs'}}
          >
            <View style={{height: 20, width: 20, borderRadius: 10, borderWidth: 2, borderColor: '#007AFF', alignItems: 'center', justifyContent: 'center'}}>
              {voiceEngine === 'voice_packs' && <View style={{height: 10, width: 10, borderRadius: 5, backgroundColor: '#007AFF'}} />}
            </View>
            <Text style={{marginLeft: 12, fontSize: 16, color: '#333'}}>Voice Packs (Suara Manusia Asli)</Text>
          </TouchableOpacity>

          <TouchableOpacity 
            style={{flexDirection: 'row', alignItems: 'center', marginTop: 16}}
            onPress={() => changeEngine('tts')}
            accessibilityRole="radio"
            accessibilityState={{checked: voiceEngine === 'tts'}}
          >
            <View style={{height: 20, width: 20, borderRadius: 10, borderWidth: 2, borderColor: '#007AFF', alignItems: 'center', justifyContent: 'center'}}>
              {voiceEngine === 'tts' && <View style={{height: 10, width: 10, borderRadius: 5, backgroundColor: '#007AFF'}} />}
            </View>
            <Text style={{marginLeft: 12, fontSize: 16, color: '#333'}}>Text-to-Speech (Google TTS)</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

export default function App() {
  return (
    <SafeAreaProvider>
      <NavigationContainer>
        <Tab.Navigator screenOptions={{ 
            headerShown: false, 
            tabBarActiveTintColor: '#007AFF',
            tabBarLabelStyle: { fontSize: 14, fontWeight: 'bold' } 
          }}>
          <Tab.Screen name="Agenda" component={AgendaScreen} />
          <Tab.Screen name="Lonceng" component={LoncengScreen} />
          <Tab.Screen name="Timer" component={TimerScreen} />
          <Tab.Screen name="Pengaturan" component={SettingsScreen} />
        </Tab.Navigator>
      </NavigationContainer>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F5F5F5' },
  headerTitle: { fontSize: 24, fontWeight: 'bold', margin: 16, color: '#333' },
  content: { flex: 1, paddingHorizontal: 16 },
  card: { backgroundColor: '#FFF', padding: 16, marginBottom: 12, borderRadius: 8 },
  cardTitle: { fontSize: 18, fontWeight: 'bold', color: '#000' },
  cardDesc: { fontSize: 14, color: '#666', marginTop: 4 },
  settingRow: { backgroundColor: '#FFF', padding: 16, marginBottom: 12, borderRadius: 8, flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  settingText: { fontSize: 16, color: '#333' },
  timerControls: { flexDirection: 'row', justifyContent: 'space-between', marginVertical: 20 }
});
