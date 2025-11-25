/**
 * Authentication Context
 * 
 * Manages user authentication state and provides auth methods.
 */
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import * as SecureStore from 'expo-secure-store';
import * as LocalAuthentication from 'expo-local-authentication';
import { api } from '../services/api';

interface User {
    id: string;
    email: string;
    name: string;
    avatar?: string;
}

interface AuthContextType {
    user: User | null;
    isLoading: boolean;
    isAuthenticated: boolean;
    login: (email: string, password: string) => Promise<void>;
    logout: () => Promise<void>;
    authenticateWithBiometrics: () => Promise<boolean>;
    checkBiometricsAvailable: () => Promise<boolean>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        // Check for existing session on mount
        checkExistingSession();
    }, []);

    const checkExistingSession = async () => {
        try {
            const token = await SecureStore.getItemAsync('access_token');
            if (token) {
                // Verify token and get user profile
                const profile = await api.getProfile();
                setUser(profile);
            }
        } catch (error) {
            console.error('Session check failed:', error);
            await SecureStore.deleteItemAsync('access_token');
        } finally {
            setIsLoading(false);
        }
    };

    const login = async (email: string, password: string) => {
        try {
            const response = await api.login(email, password);

            // Store token securely
            await SecureStore.setItemAsync('access_token', response.access_token);

            // Store credentials for biometric auth (optional)
            await SecureStore.setItemAsync('user_email', email);

            // Get user profile
            const profile = await api.getProfile();
            setUser(profile);
        } catch (error) {
            console.error('Login failed:', error);
            throw error;
        }
    };

    const logout = async () => {
        try {
            // Clear stored data
            await SecureStore.deleteItemAsync('access_token');
            setUser(null);
        } catch (error) {
            console.error('Logout failed:', error);
        }
    };

    const checkBiometricsAvailable = async (): Promise<boolean> => {
        const hasHardware = await LocalAuthentication.hasHardwareAsync();
        if (!hasHardware) return false;

        const isEnrolled = await LocalAuthentication.isEnrolledAsync();
        return isEnrolled;
    };

    const authenticateWithBiometrics = async (): Promise<boolean> => {
        try {
            const available = await checkBiometricsAvailable();
            if (!available) {
                throw new Error('Biometric authentication not available');
            }

            const result = await LocalAuthentication.authenticateAsync({
                promptMessage: 'Authenticate to access CrisisLens',
                fallbackLabel: 'Use Password',
                disableDeviceFallback: false,
            });

            if (result.success) {
                // Check if we have a stored session
                const token = await SecureStore.getItemAsync('access_token');
                if (token) {
                    const profile = await api.getProfile();
                    setUser(profile);
                    return true;
                }
            }

            return false;
        } catch (error) {
            console.error('Biometric auth failed:', error);
            return false;
        }
    };

    const value: AuthContextType = {
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        logout,
        authenticateWithBiometrics,
        checkBiometricsAvailable,
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}
