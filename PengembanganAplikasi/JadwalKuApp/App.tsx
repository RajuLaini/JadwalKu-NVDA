import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { SafeAreaView, View, Text, Switch, StyleSheet, ScrollView, TouchableOpacity, Button } from 'react-native';

const Tab = createBottomTabNavigator();

// --- Tab 1: Agenda & Habit ---
function AgendaScreen() {
  return (
    <SafeAreaView style={styles.container}>
      <Text style={styles.headerTitle} accessibilityRole="header">Agenda & Habit</Text>
      <ScrollView style={styles.content}>
        <View style={styles.card} accessible={true} accessibilityRole="button" accessibilityLabel="Rutinitas Pagi, Aktif, Setiap Hari jam 08:00. Ketuk dua kali untuk mengedit.">
          <Text style={styles.cardTitle}>Rutinitas Pagi</Text>
          <Text style={styles.cardDesc}>Setiap Hari - 08:00</Text>
          <Switch value={true} onValueChange={() => {}} accessibilityLabel="Aktifkan Rutinitas Pagi" />
        </View>
        <View style={styles.card} accessible={true} accessibilityRole="button" accessibilityLabel="Minum Air, Aktif, Setiap 2 Jam. Ketuk dua kali untuk mengedit.">
          <Text style={styles.cardTitle}>Minum Air</Text>
          <Text style={styles.cardDesc}>Setiap 2 Jam (Interval)</Text>
          <Switch value={true} onValueChange={() => {}} accessibilityLabel="Aktifkan Minum Air" />
        </View>
      </ScrollView>
      <TouchableOpacity style={styles.fab} accessibilityRole="button" accessibilityLabel="Tambah Agenda Baru">
        <Text style={styles.fabText}>+ Tambah</Text>
      </TouchableOpacity>
    </SafeAreaView>
  );
}

// --- Tab 2: Lonceng & Waktu ---
function LoncengScreen() {
  return (
    <SafeAreaView style={styles.container}>
      <Text style={styles.headerTitle} accessibilityRole="header">Lonceng Klasik & Waktu</Text>
      <ScrollView style={styles.content}>
        <View style={styles.settingRow}>
          <Text style={styles.settingText}>Bunyikan Lonceng Setiap Jam</Text>
          <Switch value={true} onValueChange={() => {}} accessibilityLabel="Bunyikan Lonceng Setiap Jam" />
        </View>
        <View style={styles.settingRow}>
          <Text style={styles.settingText}>Suara Detak Jam (Ticking)</Text>
          <Switch value={false} onValueChange={() => {}} accessibilityLabel="Suara Detak Jam" />
        </View>
        <View style={styles.settingRow}>
          <Text style={styles.settingText}>Pengingat Waktu Berkala (Time Reminder)</Text>
          <Switch value={true} onValueChange={() => {}} accessibilityLabel="Pengingat Waktu Berkala" />
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

// --- Tab 3: Timer & Alarm ---
function TimerScreen() {
  return (
    <SafeAreaView style={styles.container}>
      <Text style={styles.headerTitle} accessibilityRole="header">Timer Cepat & Alarm</Text>
      <View style={styles.content}>
        <Text style={styles.settingText}>Set Timer: 10 Menit</Text>
        <View style={styles.timerControls}>
          <Button title="Kurangi 1 Menit" onPress={() => {}} accessibilityLabel="Kurangi satu menit" />
          <Button title="Tambah 1 Menit" onPress={() => {}} accessibilityLabel="Tambah satu menit" />
        </View>
        <Button title="Mulai Timer" onPress={() => {}} accessibilityLabel="Mulai Timer sekarang" color="#28a745" />
      </View>
    </SafeAreaView>
  );
}

// --- Tab 4: Pengaturan ---
function SettingsScreen() {
  return (
    <SafeAreaView style={styles.container}>
      <Text style={styles.headerTitle} accessibilityRole="header">Pengaturan & Mesin Suara</Text>
      <ScrollView style={styles.content}>
        <TouchableOpacity style={styles.settingRow} accessibilityRole="button" accessibilityLabel="Pengaturan Voice Pack">
          <Text style={styles.settingText}>Voice Pack Studio</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.settingRow} accessibilityRole="button" accessibilityLabel="Pengaturan Volume Ekstrem 1200 persen">
          <Text style={styles.settingText}>Penguat Volume Audio (1200%)</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.settingRow} accessibilityRole="button" accessibilityLabel="Pengaturan Mesin TTS">
          <Text style={styles.settingText}>Mesin Pembaca Teks (TTS)</Text>
        </TouchableOpacity>
      </ScrollView>
    </SafeAreaView>
  );
}

import { SafeAreaProvider } from 'react-native-safe-area-context';

export default function App() {
  return (
    <SafeAreaProvider>
      <NavigationContainer>
        <Tab.Navigator screenOptions={{ 
            headerShown: false, 
            tabBarActiveTintColor: '#007AFF',
            tabBarLabelStyle: { fontSize: 14, fontWeight: 'bold' } 
          }}>
          <Tab.Screen name="Agenda" component={AgendaScreen} options={{ tabBarAccessibilityLabel: 'Tab Agenda dan Rutinitas' }} />
          <Tab.Screen name="Lonceng" component={LoncengScreen} options={{ tabBarAccessibilityLabel: 'Tab Lonceng dan Waktu' }} />
          <Tab.Screen name="Timer" component={TimerScreen} options={{ tabBarAccessibilityLabel: 'Tab Timer Cepat' }} />
          <Tab.Screen name="Pengaturan" component={SettingsScreen} options={{ tabBarAccessibilityLabel: 'Tab Pengaturan Sistem' }} />
        </Tab.Navigator>
      </NavigationContainer>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F5F5F5' },
  headerTitle: { fontSize: 24, fontWeight: 'bold', margin: 16, color: '#333' },
  content: { flex: 1, paddingHorizontal: 16 },
  card: { backgroundColor: '#FFF', padding: 16, marginBottom: 12, borderRadius: 8, flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', elevation: 2 },
  cardTitle: { fontSize: 18, fontWeight: 'bold', color: '#000' },
  cardDesc: { fontSize: 14, color: '#666', marginTop: 4 },
  settingRow: { backgroundColor: '#FFF', padding: 16, marginBottom: 12, borderRadius: 8, flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  settingText: { fontSize: 16, color: '#333' },
  timerControls: { flexDirection: 'row', justifyContent: 'space-between', marginVertical: 20 },
  fab: { position: 'absolute', bottom: 24, right: 24, backgroundColor: '#007AFF', padding: 16, borderRadius: 30, elevation: 4 },
  fabText: { color: '#FFF', fontWeight: 'bold', fontSize: 16 }
});
