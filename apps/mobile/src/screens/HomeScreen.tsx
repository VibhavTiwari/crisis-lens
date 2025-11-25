/**
 * Home Screen
 * 
 * Main feed showing crisis items with pull-to-refresh and infinite scroll.
 */
import React, { useState } from 'react';
import {
    View,
    Text,
    FlatList,
    StyleSheet,
    RefreshControl,
    TouchableOpacity,
    ActivityIndicator,
} from 'react-native';
import { useQuery } from '@tanstack/react-query';
import { useNavigation } from '@react-navigation/native';
import { AlertCircle, TrendingUp, MapPin } from 'lucide-react-native';
import { api } from '../services/api';
import { offlineManager } from '../services/OfflineManager';

export default function HomeScreen() {
    const navigation = useNavigation();
    const [refreshing, setRefreshing] = useState(false);

    const { data, isLoading, refetch, fetchNextPage, hasNextPage, isFetchingNextPage } = useQuery({
        queryKey: ['items'],
        queryFn: async () => {
            // Try to get from cache first if offline
            const isOnline = await offlineManager.checkIsOnline();
            if (!isOnline) {
                const cached = await offlineManager.getCachedData('items');
                if (cached) return cached;
            }

            const result = await api.getItems({ limit: 20 });

            // Cache the result
            await offlineManager.cacheData('items', result);

            return result;
        },
    });

    const handleRefresh = async () => {
        setRefreshing(true);
        await refetch();
        setRefreshing(false);
    };

    const handleLoadMore = () => {
        if (hasNextPage && !isFetchingNextPage) {
            fetchNextPage();
        }
    };

    const renderItem = ({ item }: { item: any }) => (
        <TouchableOpacity
            style={styles.card}
            onPress={() => navigation.navigate('ItemDetail' as never, { id: item.id } as never)}
        >
            <View style={styles.cardHeader}>
                <Text style={styles.cardTitle} numberOfLines={2}>
                    {item.title}
                </Text>
                <View style={[
                    styles.riskBadge,
                    item.risk_score > 0.7 ? styles.riskHigh : item.risk_score > 0.4 ? styles.riskMedium : styles.riskLow
                ]}>
                    <Text style={styles.riskText}>
                        {(item.risk_score * 100).toFixed(0)}%
                    </Text>
                </View>
            </View>

            <Text style={styles.cardContent} numberOfLines={3}>
                {item.content || item.summary}
            </Text>

            <View style={styles.cardFooter}>
                {item.location && (
                    <View style={styles.metaItem}>
                        <MapPin size={14} color="#6b7280" />
                        <Text style={styles.metaText}>{item.location}</Text>
                    </View>
                )}
                <View style={styles.metaItem}>
                    <AlertCircle size={14} color="#6b7280" />
                    <Text style={styles.metaText}>{item.status}</Text>
                </View>
            </View>
        </TouchableOpacity>
    );

    return (
        <View style={styles.container}>
            <View style={styles.header}>
                <Text style={styles.headerTitle}>CrisisLens</Text>
                <View style={styles.headerStats}>
                    <Text style={styles.headerStat}>
                        {data?.total || 0} Items
                    </Text>
                </View>
            </View>

            {isLoading && !refreshing ? (
                <View style={styles.loading}>
                    <ActivityIndicator size="large" color="#3b82f6" />
                </View>
            ) : (
                <FlatList
                    data={data?.items || []}
                    renderItem={renderItem}
                    keyExtractor={(item) => item.id}
                    contentContainerStyle={styles.list}
                    refreshControl={
                        <RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />
                    }
                    onEndReached={handleLoadMore}
                    onEndReachedThreshold={0.5}
                    ListFooterComponent={
                        isFetchingNextPage ? (
                            <ActivityIndicator style={styles.footerLoader} />
                        ) : null
                    }
                />
            )}
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#f9fafb',
    },
    header: {
        backgroundColor: '#fff',
        padding: 16,
        borderBottomWidth: 1,
        borderBottomColor: '#e5e7eb',
    },
    headerTitle: {
        fontSize: 24,
        fontWeight: 'bold',
        color: '#1f2937',
    },
    headerStats: {
        marginTop: 4,
    },
    headerStat: {
        fontSize: 14,
        color: '#6b7280',
    },
    loading: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
    },
    list: {
        padding: 16,
    },
    card: {
        backgroundColor: '#fff',
        borderRadius: 12,
        padding: 16,
        marginBottom: 16,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 3,
    },
    cardHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        marginBottom: 8,
    },
    cardTitle: {
        fontSize: 18,
        fontWeight: '600',
        color: '#1f2937',
        flex: 1,
        marginRight: 8,
    },
    riskBadge: {
        paddingHorizontal: 8,
        paddingVertical: 4,
        borderRadius: 12,
    },
    riskHigh: {
        backgroundColor: '#fee2e2',
    },
    riskMedium: {
        backgroundColor: '#fef3c7',
    },
    riskLow: {
        backgroundColor: '#d1fae5',
    },
    riskText: {
        fontSize: 12,
        fontWeight: '600',
    },
    cardContent: {
        fontSize: 14,
        color: '#4b5563',
        lineHeight: 20,
        marginBottom: 12,
    },
    cardFooter: {
        flexDirection: 'row',
        gap: 16,
    },
    metaItem: {
        flexDirection: 'row',
        alignItems: 'center',
        gap: 4,
    },
    metaText: {
        fontSize: 12,
        color: '#6b7280',
    },
    footerLoader: {
        paddingVertical: 20,
    },
});
