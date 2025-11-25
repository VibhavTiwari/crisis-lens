'use client'

import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { AlertCircle, TrendingUp, Clock, MapPin } from 'lucide-react'
import { ItemCard } from '@/components/ItemCard'
import { StatsCard } from '@/components/StatsCard'
import { DashboardCharts } from '@/components/DashboardCharts'
import { ProtectedRoute } from '@/components/ProtectedRoute'
import { NotificationCenter } from '@/components/NotificationCenter'
import { useGlobalWebSocket } from '@/hooks/useWebSocket'
import { api } from '@/lib/api'

export default function DashboardPage() {
    return (
        <ProtectedRoute>
            <DashboardContent />
        </ProtectedRoute>
    )
}

function DashboardContent() {
    const [filter, setFilter] = useState<'all' | 'pending' | 'high-risk'>('all')
    const [realtimeItems, setRealtimeItems] = useState<any[]>([])

    // Get token from localStorage
    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null

    // WebSocket connection for real-time updates
    const { isConnected, newItems, alerts } = useGlobalWebSocket(token || undefined)

    // Fetch items
    const { data: items, isLoading, refetch } = useQuery({
        queryKey: ['items', filter],
        queryFn: () => api.getItems({ status: filter === 'pending' ? 'pending_review' : undefined }),
    })

    // Fetch stats
    const { data: stats, refetch: refetchStats } = useQuery({
        queryKey: ['stats'],
        queryFn: () => api.getStats(),
    })

    // Update when new items arrive via WebSocket
    useEffect(() => {
        if (newItems.length > 0) {
            setRealtimeItems(newItems)
            // Refetch to update stats
            refetchStats()
        }
    }, [newItems, refetchStats])

    // Show alerts as notifications
    useEffect(() => {
        if (alerts.length > 0) {
            // Alerts are already handled by NotificationCenter
            console.log('New alerts:', alerts)
        }
    }, [alerts])

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <header className="bg-white border-b border-gray-200">
                <div className="container mx-auto px-4 py-4 flex items-center justify-between">
                    <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>

                    <div className="flex items-center gap-4">
                        {/* WebSocket Status */}
                        <div className="flex items-center gap-2">
                            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
                            <span className="text-sm text-gray-600">
                                {isConnected ? 'Live' : 'Offline'}
                            </span>
                        </div>

                        {/* Notification Center */}
                        <NotificationCenter />
                    </div>
                </div>
            </header>

            <main className="container mx-auto px-4 py-8">
                {/* Stats Grid */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                    <StatsCard
                        title="Pending Review"
                        value={stats?.pending || 45}
                        icon={<Clock className="w-6 h-6" />}
                        color="blue"
                    />
                    <StatsCard
                        title="High Risk"
                        value={stats?.highRisk || 12}
                        icon={<AlertCircle className="w-6 h-6" />}
                        color="red"
                    />
                    <StatsCard
                        title="Avg Risk Score"
                        value={(stats?.avgRisk || 0.42).toFixed(2)}
                        icon={<TrendingUp className="w-6 h-6" />}
                        color="yellow"
                    />
                    <StatsCard
                        title="Active Locations"
                        value={stats?.locations || 8}
                        icon={<MapPin className="w-6 h-6" />}
                        color="green"
                    />
                </div>

                {/* Charts Section */}
                <DashboardCharts />

                {/* Real-time New Items */}
                {realtimeItems.length > 0 && (
                    <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                        <div className="flex items-center justify-between mb-3">
                            <h3 className="font-semibold text-blue-900">
                                🔴 {realtimeItems.length} New Item{realtimeItems.length !== 1 ? 's' : ''}
                            </h3>
                            <button
                                onClick={() => {
                                    setRealtimeItems([])
                                    refetch()
                                }}
                                className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                            >
                                Load new items
                            </button>
                        </div>
                    </div>
                )}

                {/* Filters */}
                <div className="flex space-x-4 mb-6">
                    {(['all', 'pending', 'high-risk'] as const).map((f) => (
                        <button
                            key={f}
                            onClick={() => setFilter(f)}
                            className={`px-4 py-2 rounded-lg font-medium transition ${filter === f
                                    ? 'bg-blue-600 text-white'
                                    : 'bg-white text-gray-700 hover:bg-gray-100'
                                }`}
                        >
                            {f === 'all' ? 'All Items' : f === 'pending' ? 'Pending Review' : 'High Risk'}
                        </button>
                    ))}
                </div>

                {/* Items List */}
                {isLoading ? (
                    <div className="text-center py-12">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                    </div>
                ) : (
                    <div className="space-y-4">
                        {items?.items?.map((item: any) => (
                            <ItemCard key={item.id} item={item} />
                        ))}
                    </div>
                )}
            </main>
        </div>
    )
}
