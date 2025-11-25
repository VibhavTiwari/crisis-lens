'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { AlertCircle, TrendingUp, Clock, MapPin } from 'lucide-react'
import { ItemCard } from '@/components/ItemCard'
import { StatsCard } from '@/components/StatsCard'
import { api } from '@/lib/api'

export default function DashboardPage() {
    const [filter, setFilter] = useState<'all' | 'pending' | 'high-risk'>('all')

    const { data: items, isLoading } = useQuery({
        query Key: ['items', filter],
        queryFn: () => api.getItems({ status: filter === 'pending' ? 'pending_review' : undefined }),
    })

    const { data: stats } = useQuery({
        queryKey: ['stats'],
        queryFn: () => api.getStats(),
    })

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <header className="bg-white border-b border-gray-200">
                <div className="container mx-auto px-4 py-4">
                    <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
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
