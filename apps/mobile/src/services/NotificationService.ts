/**
 * Push Notification Service
 * 
 * Handles push notification setup, permissions, and message handling.
 */
import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import { Platform } from 'react-native';
import { api } from './api';

// Configure notification handler
Notifications.setNotificationHandler({
    handleNotification: async () => ({
        shouldShowAlert: true,
        shouldPlaySound: true,
        shouldSetBadge: true,
    }),
});

export async function initNotifications() {
    if (!Device.isDevice) {
        console.warn('Push notifications only work on physical devices');
        return null;
    }

    try {
        // Request permissions
        const { status: existingStatus } = await Notifications.getPermissionsAsync();
        let finalStatus = existingStatus;

        if (existingStatus !== 'granted') {
            const { status } = await Notifications.requestPermissionsAsync();
            finalStatus = status;
        }

        if (finalStatus !== '

') {
        console.warn('Push notification permission not granted');
        return null;
    }

    // Get push token
    const token = (await Notifications.getExpoPushTokenAsync({
        projectId: 'your-project-id', // Replace with your EAS project ID
    })).data;

    // Register token with backend
    await api.registerPushToken(token, Platform.OS as 'ios' | 'android');

    // Configure Android channel
    if (Platform.OS === 'android') {
        await Notifications.setNotificationChannelAsync('default', {
            name: 'default',
            importance: Notifications.AndroidImportance.MAX,
            vibrationPattern: [0, 250, 250, 250],
            lightColor: '#FF231F7C',
        });
    }

    return token;
} catch (error) {
    console.error('Error initializing notifications:', error);
    return null;
}
}

export function addNotificationReceivedListener(
    callback: (notification: Notifications.Notification) => void
) {
    return Notifications.addNotificationReceivedListener(callback);
}

export function addNotificationResponseListener(
    callback: (response: Notifications.NotificationResponse) => void
) {
    return Notifications.addNotificationResponseReceivedListener(callback);
}

export async function scheduleLocalNotification(
    title: string,
    body: string,
    data?: any,
    seconds: number = 0
) {
    await Notifications.scheduleNotificationAsync({
        content: {
            title,
            body,
            data,
            sound: true,
        },
        trigger: seconds > 0 ? { seconds } : null,
    });
}

export async function cancelAllNotifications() {
    await Notifications.cancelAllScheduledNotificationsAsync();
}

export async function getBadgeCount(): Promise<number> {
    return await Notifications.getBadgeCountAsync();
}

export async function setBadgeCount(count: number) {
    await Notifications.setBadgeCountAsync(count);
}
