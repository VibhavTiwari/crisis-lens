import React, { useState, useEffect } from 'react';
import { View, StyleSheet, Text } from 'react-native';
import MapView, { Marker } from 'react-native-maps';
import { getCurrentLocation, LocationCoords } from '../services/LocationService';
import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';

export default function MapScreen() {
    const [userLocation, setUserLocation] = useState<LocationCoords | null>(null);

    const { data: items } = useQuery({
        queryKey: ['items-map'],
        queryFn: () => api.getItems({ limit: 100 }),
    });

    useEffect(() => {
        loadUserLocation();
    }, []);

    const loadUserLocation = async () => {
        const location = await getCurrentLocation();
        if (location) {
            setUserLocation(location);
        }
    };

    const initialRegion = userLocation ? {
        latitude: userLocation.latitude,
        longitude: userLocation.longitude,
        latitudeDelta: 0.5,
        longitudeDelta: 0.5,
    } : {
        latitude: 0,
        longitude: 0,
        latitudeDelta: 100,
        longitudeDelta: 100,
    };

    return (
        <View style={styles.container}>
            <MapView
                style={styles.map}
                initialRegion={initialRegion}
                showsUserLocation
                showsMyLocationButton
            >
                {items?.items?.map((item: any) => {
                    if (!item.latitude || !item.longitude) return null;
                    return (
                        <Marker
                            key={item.id}
                            coordinate={{
                                latitude: item.latitude,
                                longitude: item.longitude,
                            }}
                            title={item.title}
                            description={`Risk: ${(item.risk_score * 100).toFixed(0)}%`}
                            pinColor={item.risk_score > 0.7 ? 'red' : item.risk_score > 0.4 ? 'orange' : 'green'}
                        />
                    );
                })}
            </MapView>
        </View>
    );
}

const styles = StyleSheet.create({
    container: { flex: 1 },
    map: { flex: 1 },
});
