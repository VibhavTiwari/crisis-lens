/**
 * Login Screen
 * 
 * Handles user authentication with email/password and biometrics.
 */
import React, { useState, useEffect } from 'react';
import {
    View,
    Text,
    TextInput,
    TouchableOpacity,
    StyleSheet,
    KeyboardAvoidingView,
    Platform,
    Alert,
} from 'react-native';
import { Fingerprint } from 'lucide-react-native';
import { useAuth } from '../contexts/AuthContext';

export default function LoginScreen() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [biometricsAvailable, setBiometricsAvailable] = useState(false);

    const { login, authenticateWithBiometrics, checkBiometricsAvailable } = useAuth();

    useEffect(() => {
        checkBiometrics();
    }, []);

    const checkBiometrics = async () => {
        const available = await checkBiometricsAvailable();
        setBiometricsAvailable(available);
    };

    const handleLogin = async () => {
        if (!email || !password) {
            Alert.alert('Error', 'Please enter email and password');
            return;
        }

        setIsLoading(true);
        try {
            await login(email, password);
        } catch (error: any) {
            Alert.alert('Login Failed', error.message || 'Invalid credentials');
        } finally {
            setIsLoading(false);
        }
    };

    const handleBiometricLogin = async () => {
        try {
            const success = await authenticateWithBiometrics();
            if (!success) {
                Alert.alert('Authentication Failed', 'Please try again or use password');
            }
        } catch (error: any) {
            Alert.alert('Error', error.message);
        }
    };

    return (
        <KeyboardAvoidingView
            style={styles.container}
            behavior={Platform.OS === 'ios' ? 'padding' : undefined}
        >
            <View style={styles.content}>
                <Text style={styles.title}>CrisisLens</Text>
                <Text style={styles.subtitle}>Real-time Crisis Intelligence</Text>

                <View style={styles.form}>
                    <TextInput
                        style={styles.input}
                        placeholder="Email"
                        value={email}
                        onChangeText={setEmail}
                        keyboardType="email-address"
                        autoCapitalize="none"
                        editable={!isLoading}
                    />

                    <TextInput
                        style={styles.input}
                        placeholder="Password"
                        value={password}
                        onChangeText={setPassword}
                        secureTextEntry
                        editable={!isLoading}
                    />

                    <TouchableOpacity
                        style={[styles.button, isLoading && styles.buttonDisabled]}
                        onPress={handleLogin}
                        disabled={isLoading}
                    >
                        <Text style={styles.buttonText}>
                            {isLoading ? 'Logging in...' : 'Login'}
                        </Text>
                    </TouchableOpacity>

                    {biometricsAvailable && (
                        <TouchableOpacity
                            style={styles.biometricButton}
                            onPress={handleBiometricLogin}
                        >
                            <Fingerprint color="#3b82f6" size={32} />
                            <Text style={styles.biometricText}>Use Biometrics</Text>
                        </TouchableOpacity>
                    )}
                </View>
            </View>
        </KeyboardAvoidingView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#fff',
    },
    content: {
        flex: 1,
        justifyContent: 'center',
        padding: 24,
    },
    title: {
        fontSize: 32,
        fontWeight: 'bold',
        color: '#1f2937',
        textAlign: 'center',
        marginBottom: 8,
    },
    subtitle: {
        fontSize: 16,
        color: '#6b7280',
        textAlign: 'center',
        marginBottom: 48,
    },
    form: {
        width: '100%',
    },
    input: {
        backgroundColor: '#f9fafb',
        borderWidth: 1,
        borderColor: '#e5e7eb',
        borderRadius: 8,
        padding: 16,
        fontSize: 16,
        marginBottom: 16,
    },
    button: {
        backgroundColor: '#3b82f6',
        borderRadius: 8,
        padding: 16,
        alignItems: 'center',
        marginTop: 8,
    },
    buttonDisabled: {
        opacity: 0.6,
    },
    buttonText: {
        color: '#fff',
        fontSize: 16,
        fontWeight: '600',
    },
    biometricButton: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        marginTop: 24,
        padding: 16,
    },
    biometricText: {
        color: '#3b82f6',
        fontSize: 16,
        fontWeight: '600',
        marginLeft: 8,
    },
});
