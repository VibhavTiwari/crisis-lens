import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, Switch } from 'react-native';
import { User, Bell, Lock, LogOut } from 'lucide-react-native';
import { useAuth } from '../contexts/AuthContext';
import { offlineManager } from '../services/OfflineManager';

export default function ProfileScreen() {
    const { user, logout } = useAuth();
    const [notificationsEnabled, setNotificationsEnabled] = React.useState(true);

    const handleLogout = async () => {
        await logout();
    };

    const queueLength = offlineManager.getQueueLength();
    const isOnline = offlineManager.isNetworkOnline();

    return (
        <ScrollView style={styles.container}>
            <View style={styles.header}>
                <View style={styles.avatar}>
                    <User size={48} color="#fff" />
                </View>
                <Text style={styles.name}>{user?.name || 'User'}</Text>
                <Text style={styles.email}>{user?.email}</Text>
            </View>

            <View style={styles.section}>
                <Text style={styles.sectionTitle}>Settings</Text>

                <View style={styles.settingRow}>
                    <View style={styles.settingLeft}>
                        <Bell size={20} color="#6b7280" />
                        <Text style={styles.settingText}>Notifications</Text>
                    </View>
                    <Switch
                        value={notificationsEnabled}
                        onValueChange={setNotificationsEnabled}
                    />
                </View>

                <View style={styles.settingRow}>
                    <View style={styles.settingLeft}>
                        <Lock size={20} color="#6b7280" />
                        <Text style={styles.settingText}>Biometric Login</Text>
                    </View>
                    <Switch value={true} disabled />
                </View>
            </View>

            <View style={styles.section}>
                <Text style={styles.sectionTitle}>Status</Text>
                <View style={styles.statusRow}>
                    <Text style={styles.statusLabel}>Network:</Text>
                    <Text style={[styles.statusValue, isOnline ? styles.online : styles.offline]}>
                        {isOnline ? 'Online' : 'Offline'}
                    </Text>
                </View>
                {queueLength > 0 && (
                    <View style={styles.statusRow}>
                        <Text style={styles.statusLabel}>Pending Sync:</Text>
                        <Text style={styles.statusValue}>{queueLength} items</Text>
                    </View>
                )}
            </View>

            <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
                <LogOut size={20} color="#ef4444" />
                <Text style={styles.logoutText}>Logout</Text>
            </TouchableOpacity>

            <Text style={styles.version}>Version 1.0.0</Text>
        </ScrollView>
    );
}

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: '#f9fafb' },
    header: { backgroundColor: '#fff', alignItems: 'center', padding: 32, borderBottomWidth: 1, borderBottomColor: '#e5e7eb' },
    avatar: { width: 96, height: 96, borderRadius: 48, backgroundColor: '#3b82f6', justifyContent: 'center', alignItems: 'center', marginBottom: 16 },
    name: { fontSize: 24, fontWeight: 'bold', color: '#1f2937', marginBottom: 4 },
    email: { fontSize: 14, color: '#6b7280' },
    section: { backgroundColor: '#fff', marginTop: 16, padding: 16 },
    sectionTitle: { fontSize: 16, fontWeight: '600', color: '#1f2937', marginBottom: 16 },
    settingRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingVertical: 12 },
    settingLeft: { flexDirection: 'row', alignItems: 'center', gap: 12 },
    settingText: { fontSize: 16, color: '#374151' },
    statusRow: { flexDirection: 'row', justifyContent: 'space-between', paddingVertical: 8 },
    statusLabel: { fontSize: 14, color: '#6b7280' },
    statusValue: { fontSize: 14, fontWeight: '600', color: '#374151' },
    online: { color: '#10b981' },
    offline: { color: '#ef4444' },
    logoutButton: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', backgroundColor: '#fff', marginTop: 16, marginHorizontal: 16, padding: 16, borderRadius: 8, gap: 8 },
    logoutText: { fontSize: 16, fontWeight: '600', color: '#ef4444' },
    version: { textAlign: 'center', marginTop: 32, marginBottom: 16, fontSize: 12, color: '#9ca3af' },
});
