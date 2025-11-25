import { registerRootComponent } from 'expo';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './src/contexts/AuthContext';
import { NavigationContainer } from '@react-navigation/native';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import AppNavigator from './src/navigation/AppNavigator';
import { initNotifications } from './src/services/NotificationService';
import { useEffect } from 'react';

// Create React Query client
const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            retry: 2,
            staleTime: 5 * 60 * 1000, // 5 minutes
        },
    },
});

function App() {
    useEffect(() => {
        // Initialize notifications on app start
        initNotifications();
    }, []);

    return (
        <SafeAreaProvider>
            <QueryClientProvider client={queryClient}>
                <AuthProvider>
                    <NavigationContainer>
                        <StatusBar style="auto" />
                        <AppNavigator />
                    </NavigationContainer>
                </AuthProvider>
            </QueryClientProvider>
        </SafeAreaProvider>
    );
}

registerRootComponent(App);
