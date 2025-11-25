/**
 * App Navigator
 * 
 * Manages app navigation structure with authentication flow.
 */
import React from 'react';
import { createStackNavigator } from '@react-navigation/stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Home, Search, Camera, Map, User } from 'lucide-react-native';
import { useAuth } from '../contexts/AuthContext';

// Auth Screens
import LoginScreen from '../screens/LoginScreen';

// Main Screens
import HomeScreen from '../screens/HomeScreen';
import SearchScreen from '../screens/SearchScreen';
import ItemDetailScreen from '../screens/ItemDetailScreen';
import ClaimVerificationScreen from '../screens/ClaimVerificationScreen';
import CameraScreen from '../screens/CameraScreen';
import MapScreen from '../screens/MapScreen';
import ProfileScreen from '../screens/ProfileScreen';

const Stack = createStackNavigator();
const Tab = createBottomTabNavigator();

function MainTabs() {
    return (
        <Tab.Navigator
            screenOptions={{
                tabBarActiveTintColor: '#3b82f6',
                tabBarInactiveTintColor: '#6b7280',
                headerShown: false,
            }}
        >
            <Tab.Screen
                name="Home"
                component={HomeScreen}
                options={{
                    tabBarIcon: ({ color, size }) => <Home color={color} size={size} />,
                }}
            />
            <Tab.Screen
                name="Search"
                component={SearchScreen}
                options={{
                    tabBarIcon: ({ color, size }) => <Search color={color} size={size} />,
                }}
            />
            <Tab.Screen
                name="Camera"
                component={CameraScreen}
                options={{
                    tabBarIcon: ({ color, size }) => <Camera color={color} size={size} />,
                }}
            />
            <Tab.Screen
                name="Map"
                component={MapScreen}
                options={{
                    tabBarIcon: ({ color, size }) => <Map color={color} size={size} />,
                }}
            />
            <Tab.Screen
                name="Profile"
                component={ProfileScreen}
                options={{
                    tabBarIcon: ({ color, size }) => <User color={color} size={size} />,
                }}
            />
        </Tab.Navigator>
    );
}

export default function AppNavigator() {
    const { isAuthenticated, isLoading } = useAuth();

    if (isLoading) {
        return null; // Could add a loading screen here
    }

    return (
        <Stack.Navigator screenOptions={{ headerShown: false }}>
            {!isAuthenticated ? (
                <Stack.Screen name="Login" component={LoginScreen} />
            ) : (
                <>
                    <Stack.Screen name="MainTabs" component={MainTabs} />
                    <Stack.Screen
                        name="ItemDetail"
                        component={ItemDetailScreen}
                        options={{ headerShown: true, title: 'Item Details' }}
                    />
                    <Stack.Screen
                        name="ClaimVerification"
                        component={ClaimVerificationScreen}
                        options={{ headerShown: true, title: 'Verify Claim' }}
                    />
                </>
            )}
        </Stack.Navigator>
    );
}
