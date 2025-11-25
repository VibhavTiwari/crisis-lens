/**
 * Remaining App Screens (Condensed Implementation)
 * Combined file for faster development - split these in production
 */

// SearchScreen.tsx
import React, { useState } from 'react';
import { View, Text, TextInput, FlatList, StyleSheet } from 'react-native';

export function SearchScreen() {
    const [query, setQuery] = useState('');
    return (
        <View style={styles.container}>
            <TextInput
                style={styles.searchInput}
                placeholder="Search crisis items..."
                value={query}
                onChangeText={setQuery}
            />
        </View>
    );
}

// ItemDetailScreen.tsx
export function ItemDetailScreen({ route }: any) {
    const { id } = route.params;
    return (
        <View style={styles.container}>
            <Text style={styles.title}>Item Detail: {id}</Text>
        </View>
    );
}

// ClaimVerificationScreen.tsx
export function ClaimVerificationScreen({ route }: any) {
    return (
        <View style={styles.container}>
            <Text style={styles.title}>Claim Verification</Text>
        </View>
    );
}

// CameraScreen.tsx
import { capturePhoto, pickImageFromLibrary } from '../services/CameraService';

export function CameraScreen() {
    const handleCapture = async () => {
        const uri = await capturePhoto();
        if (uri) {
            // Handle captured photo
        }
    };

    return (
        <View style={styles.container}>
            <Text style={styles.title}>Camera</Text>
        </View>
    );
}

// MapScreen.tsx
export function MapScreen() {
    return (
        <View style={styles.container}>
            <Text style={styles.title}>Map View</Text>
        </View>
    );
}

// ProfileScreen.tsx
import { useAuth } from '../contexts/AuthContext';

export function ProfileScreen() {
    const { user, logout } = useAuth();

    return (
        <View style={styles.container}>
            <Text style={styles.title}>Profile</Text>
            <Text>{user?.email}</Text>
        </View>
    );
}

const styles = StyleSheet.create({
    container: { flex: 1, padding: 16, backgroundColor: '#fff' },
    title: { fontSize: 24, fontWeight: 'bold', marginBottom: 16 },
    searchInput: {
        backgroundColor: '#f9fafb',
        borderWidth: 1,
        borderColor: '#e5e7eb',
        borderRadius: 8,
        padding: 12,
        fontSize: 16,
    },
});
