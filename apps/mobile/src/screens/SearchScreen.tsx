import React, { useState } from 'react';
import { View, Text, TextInput, FlatList, StyleSheet, TouchableOpacity } from 'react-native';
import { useQuery } from '@tanstack/react-query';
import { Search as SearchIcon, Filter } from 'lucide-react-native';
import { api } from '../services/api';

export default function SearchScreen() {
    const [query, setQuery] = useState('');
    const [statusFilter, setStatusFilter] = useState<string>('all');

    const { data, isLoading } = useQuery({
        queryKey: ['search', query, statusFilter],
        queryFn: () => api.getItems({
            search: query,
            status: statusFilter !== 'all' ? statusFilter : undefined
        }),
        enabled: query.length > 0,
    });

    return (
        <View style={styles.container}>
            <View style={styles.header}>
                <View style={styles.searchBar}>
                    <SearchIcon size={20} color="#6b7280" />
                    <TextInput
                        style={styles.searchInput}
                        placeholder="Search crisis items..."
                        value={query}
                        onChangeText={setQuery}
                        autoCapitalize="none"
                    />
                </View>
            </View>

            {query.length > 0 && (
                <FlatList
                    data={data?.items || []}
                    renderItem={({ item }) => (
                        <TouchableOpacity style={styles.resultItem}>
                            <Text style={styles.resultTitle}>{item.title}</Text>
                            <Text style={styles.resultMeta}>{item.status}</Text>
                        </TouchableOpacity>
                    )}
                    keyExtractor={(item) => item.id}
                    ListEmptyComponent={
                        !isLoading && <Text style={styles.emptyText}>No results found</Text>
                    }
                />
            )}
        </View>
    );
}

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: '#f9fafb' },
    header: { backgroundColor: '#fff', padding: 16, borderBottomWidth: 1, borderBottomColor: '#e5e7eb' },
    searchBar: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#f9fafb', borderRadius: 8, padding: 12 },
    searchInput: { flex: 1, marginLeft: 8, fontSize: 16 },
    resultItem: { backgroundColor: '#fff', padding: 16, marginHorizontal: 16, marginTop: 8, borderRadius: 8 },
    resultTitle: { fontSize: 16, fontWeight: '600', color: '#1f2937' },
    resultMeta: { fontSize: 12, color: '#6b7280', marginTop: 4 },
    emptyText: { textAlign: 'center', marginTop: 32, color: '#6b7280' },
});
