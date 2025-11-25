import React, { useState } from 'react';
import { View, Text, ScrollView, StyleSheet, TouchableOpacity, Alert } from 'react-native';
import { useQuery, useMutation } from '@tanstack/react-query';
import { CheckCircle, XCircle, AlertTriangle } from 'lucide-react-native';
import { api } from '../services/api';

export default function ClaimVerificationScreen({ route, navigation }: any) {
    const { id } = route.params;
    const [verdict, setVerdict] = useState<string | null>(null);

    const { data: claim, isLoading } = useQuery({
        queryKey: ['claim', id],
        queryFn: () => api.getClaim(id),
    });

    const verifyMutation = useMutation({
        mutationFn: (verdict: string) => api.verifyClaim(id, verdict),
        onSuccess: () => {
            Alert.alert('Success', 'Claim verified successfully');
            navigation.goBack();
        },
        onError: () => {
            Alert.alert('Error', 'Failed to verify claim');
        },
    });

    const handleVerify = (selectedVerdict: string) => {
        setVerdict(selectedVerdict);
        Alert.alert(
            'Confirm Verification',
            `Mark this claim as "${selectedVerdict}"?`,
            [
                { text: 'Cancel', style: 'cancel' },
                { text: 'Confirm', onPress: () => verifyMutation.mutate(selectedVerdict) },
            ]
        );
    };

    if (isLoading) return <View style={styles.loading}><Text>Loading...</Text></View>;
    if (!claim) return <View style={styles.loading}><Text>Claim not found</Text></View>;

    return (
        <ScrollView style={styles.container}>
            <View style={styles.claimSection}>
                <Text style={styles.label}>Claim Statement</Text>
                <Text style={styles.claimText}>{claim.text}</Text>
            </View>

            <View style={styles.actionsSection}>
                <Text style={styles.sectionTitle}>Verification</Text>

                <TouchableOpacity
                    style={[styles.actionButton, styles.trueButton]}
                    onPress={() => handleVerify('true')}
                >
                    <CheckCircle size={24} color="#10b981" />
                    <Text style={[styles.actionText, { color: '#10b981' }]}>Verify as TRUE</Text>
                </TouchableOpacity>

                <TouchableOpacity
                    style={[styles.actionButton, styles.falseButton]}
                    onPress={() => handleVerify('false')}
                >
                    <XCircle size={24} color="#ef4444" />
                    <Text style={[styles.actionText, { color: '#ef4444' }]}>Verify as FALSE</Text>
                </TouchableOpacity>

                <TouchableOpacity
                    style={[styles.actionButton, styles.uncertainButton]}
                    onPress={() => handleVerify('uncertain')}
                >
                    <AlertTriangle size={24} color="#f59e0b" />
                    <Text style={[styles.actionText, { color: '#f59e0b' }]}>Mark as UNCERTAIN</Text>
                </TouchableOpacity>
            </View>

            {claim.evidence && (
                <View style={styles.evidenceSection}>
                    <Text style={styles.sectionTitle}>Evidence</Text>
                    {claim.evidence.map((evidence: any, index: number) => (
                        <View key={index} style={styles.evidenceCard}>
                            <Text style={styles.evidenceText}>{evidence.text}</Text>
                            <Text style={styles.evidenceSource}>Source: {evidence.source}</Text>
                        </View>
                    ))}
                </View>
            )}
        </ScrollView>
    );
}

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: '#f9fafb' },
    loading: { flex: 1, justifyContent: 'center', alignItems: 'center' },
    claimSection: { backgroundColor: '#fff', padding: 16, marginBottom: 16 },
    label: { fontSize: 12, fontWeight: '600', color: '#6b7280', marginBottom: 8, textTransform: 'uppercase' },
    claimText: { fontSize: 18, lineHeight: 26, color: '#1f2937' },
    actionsSection: { backgroundColor: '#fff', padding: 16, marginBottom: 16 },
    sectionTitle: { fontSize: 16, fontWeight: '600', marginBottom: 16, color: '#1f2937' },
    actionButton: { flexDirection: 'row', alignItems: 'center', padding: 16, borderRadius: 8, marginBottom: 12, borderWidth: 2 },
    trueButton: { borderColor: '#10b981', backgroundColor: '#d1fae5' },
    falseButton: { borderColor: '#ef4444', backgroundColor: '#fee2e2' },
    uncertainButton: { borderColor: '#f59e0b', backgroundColor: '#fef3c7' },
    actionText: { fontSize: 16, fontWeight: '600', marginLeft: 12 },
    evidenceSection: { backgroundColor: '#fff', padding: 16 },
    evidenceCard: { backgroundColor: '#f9fafb', padding: 12, borderRadius: 8, marginBottom: 8 },
    evidenceText: { fontSize: 14, color: '#374151', marginBottom: 4 },
    evidenceSource: { fontSize: 12, color: '#6b7280' },
});
