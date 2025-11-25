import React from 'react';
import { View, Text, ScrollView, StyleSheet, Image, TouchableOpacity } from 'react-native';
import { useQuery } from '@tanstack/react-query';
import { MapPin, Clock, AlertCircle } from 'lucide-react-native';
import { api } from '../services/api';

export default function ItemDetailScreen({ route, navigation }: any) {
    const { id } = route.params;

    const { data: item, isLoading } = useQuery({
        queryKey: ['item', id],
        queryFn: () => api.getItem(id),
    });

    if (isLoading) return <View style={styles.loading}><Text>Loading...</Text></View>;
    if (!item) return <View style={styles.loading}><Text>Item not found</Text></View>;

    return (
        <ScrollView style={styles.container}>
            <View style={styles.header}>
                <Text style={styles.title}>{item.title}</Text>
                <View style={[styles.riskBadge, item.risk_score > 0.7 && styles.riskHigh]}>
                    <Text style={styles.riskText}>Risk: {(item.risk_score * 100).toFixed(0)}%</Text>
                </View>
            </View>

            <View style={styles.section}>
                <Text style={styles.content}>{item.content || item.summary}</Text>
            </View>

            <View style={styles.metadata}>
                {item.location && (
                    <View style={styles.metaRow}>
                        <MapPin size={16} color="#6b7280" />
                        <Text style={styles.metaText}>{item.location}</Text>
                    </View>
                )}
                <View style={styles.metaRow}>
                    <AlertCircle size={16} color="#6b7280" />
                    <Text style={styles.metaText}>Status: {item.status}</Text>
                </View>
                {item.created_at && (
                    <View style={styles.metaRow}>
                        <Clock size={16} color="#6b7280" />
                        <Text style={styles.metaText}>{new Date(item.created_at).toLocaleDateString()}</Text>
                    </View>
                )}
            </View>

            {item.claims && item.claims.length > 0 && (
                <View style={styles.section}>
                    <Text style={styles.sectionTitle}>Related Claims</Text>
                    {item.claims.map((claim: any) => (
                        <TouchableOpacity
                            key={claim.id}
                            style={styles.claimCard}
                            onPress={() => navigation.navigate('ClaimVerification', { id: claim.id })}
                        >
                            <Text style={styles.claimText}>{claim.text}</Text>
                        </TouchableOpacity>
                    ))}
                </View>
            )}
        </ScrollView>
    );
}

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: '#f9fafb' },
    loading: { flex: 1, justifyContent: 'center', alignItems: 'center' },
    header: { backgroundColor: '#fff', padding: 16, borderBottomWidth: 1, borderBottomColor: '#e5e7eb' },
    title: { fontSize: 24, fontWeight: 'bold', color: '#1f2937', marginBottom: 12 },
    riskBadge: { alignSelf: 'flex-start', backgroundColor: '#d1fae5', paddingHorizontal: 12, paddingVertical: 6, borderRadius: 16 },
    riskHigh: { backgroundColor: '#fee2e2' },
    riskText: { fontSize: 12, fontWeight: '600' },
    section: { backgroundColor: '#fff', padding: 16, marginTop: 8 },
    content: { fontSize: 16, lineHeight: 24, color: '#374151' },
    metadata: { backgroundColor: '#fff', padding: 16, marginTop: 8 },
    metaRow: { flexDirection: 'row', alignItems: 'center', marginBottom: 8 },
    metaText: { marginLeft: 8, fontSize: 14, color: '#6b7280' },
    sectionTitle: { fontSize: 18, fontWeight: '600', marginBottom: 12 },
    claimCard: { backgroundColor: '#f9fafb', padding: 12, borderRadius: 8, marginBottom: 8 },
    claimText: { fontSize: 14, color: '#374151' },
});
