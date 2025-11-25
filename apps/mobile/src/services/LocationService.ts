/**
 * Location Service
 * 
 * Handles GPS permissions, location tracking, and geocoding.
 */
import * as Location from 'expo-location';

export interface LocationCoords {
    latitude: number;
    longitude: number;
    accuracy?: number;
    altitude?: number | null;
}

export async function requestLocationPermissions(): Promise<boolean> {
    const { status } = await Location.requestForegroundPermissionsAsync();
    return status === 'granted';
}

export async function getCurrentLocation(): Promise<LocationCoords | null> {
    try {
        const hasPermission = await requestLocationPermissions();
        if (!hasPermission) {
            throw new Error('Location permission denied');
        }

        const location = await Location.getCurrentPositionAsync({
            accuracy: Location.Accuracy.Balanced,
        });

        return {
            latitude: location.coords.latitude,
            longitude: location.coords.longitude,
            accuracy: location.coords.accuracy || undefined,
            altitude: location.coords.altitude,
        };
    } catch (error) {
        console.error('Get location error:', error);
        return null;
    }
}

export async function reverseGeocode(
    latitude: number,
    longitude: number
): Promise<string | null> {
    try {
        const results = await Location.reverseGeocodeAsync({
            latitude,
            longitude,
        });

        if (results.length > 0) {
            const address = results[0];
            const parts = [
                address.city,
                address.region,
                address.country,
            ].filter(Boolean);

            return parts.join(', ');
        }

        return null;
    } catch (error) {
        console.error('Reverse geocode error:', error);
        return null;
    }
}

export async function getLocationWithAddress(): Promise<{
    coords: LocationCoords;
    address?: string;
} | null> {
    try {
        const coords = await getCurrentLocation();
        if (!coords) return null;

        const address = await reverseGeocode(coords.latitude, coords.longitude);

        return {
            coords,
            address: address || undefined,
        };
    } catch (error) {
        console.error('Get location with address error:', error);
        return null;
    }
}

export function formatCoordinates(coords: LocationCoords): string {
    return `${coords.latitude.toFixed(6)}, ${coords.longitude.toFixed(6)}`;
}
