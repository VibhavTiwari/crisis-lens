'use client'

import { useState, useRef, useCallback } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Search, SlidersHorizontal } from 'lucide-react'
import { ItemCard } from '@/components/ItemCard'
import { api } from '@/lib/api'
import { ProtectedRoute } from '@/components/ProtectedRoute'

export default function ItemsPage() {
    return (
        <ProtectedRoute>
            <ItemsContent />
        </ProtectedRoute>
    )
}

function ItemsContent() {
    const [searchQuery, setSearchQuery] = useState('')
    const [statusFilter, setStatusFilter] = useState<string>('all')
    const [riskFilter, setRiskFilter] = useState<[number, number]>([0, 1])
    const [showFilters, setShowFilters] = useState(false)
    const [page, setPage] = useState(1)
    const observerTarget = useRef(null)

    const { data, isLoading, isFetchingNextPage } = useQuery({
        queryKey: ['items', searchQuery, statusFilter, riskFilter, page],
        queryFn: () => api.getItems({
            status: statusFilter !== 'all' ? statusFilter : undefined,
            search: searchQuery || undefined,
            limit: 20,
            offset: (page - 1) * 20,
        }),
    })

    // Infinite scroll observer
    const handleObserver = useCallback((entries: IntersectionObserverEntry[]) => {
        const [target] = entries
        if (target.isIntersecting && !isLoading && !isFetchingNextPage) {
            setPage(prev => prev + 1)
        }
    }, [isLoading, isFetchingNextPage])

    // Set up intersection observer
    useState(() => {
        const element = observerTarget.current
        if (!element) return

        const observer = new IntersectionObserver(handleObserver, {
            threshold: 0.5,
        })

        observer.observe(element)
        return () => observer.disconnect()
    })

    const filteredItems = data?.items?.filter((item: any) => {
        return item.risk_score >= riskFilter[0] && item.risk_score <= riskFilter[1]
    }) || []

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
                <div className="container mx-auto px-4 py-4">
                    <h1 className="text-2xl font-bold text-gray-900">Item Explorer</h1>
                </div>
            </header>

            <main className="container mx-auto px-4 py-8">
                {/* Search & Filters */}
                <div className="bg-white rounded-lg shadow p-6 mb-6">
                    <div className="flex gap-4 mb-4">
                        {/* Search */}
                        <div className="flex-1 relative">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                            <input
                                type="text"
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                placeholder="Search items..."
                                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            />
                        </div>

                        {/* Filter Toggle */}
                        <button
                            onClick={() => setShowFilters(!showFilters)}
                            className={`px-4 py-2 rounded-lg font-medium transition flex items-center gap-2 ${showFilters ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                                }`}
                        >
                            <SlidersHorizontal className="w-5 h-5" />
                            Filters
                        </button>
                    </div>

                    {/* Advanced Filters */}
                    {showFilters && (
                        <div className="grid md:grid-cols-3 gap-4 pt-4 border-t border-gray-200">
                            {/* Status Filter */}
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Status
                                </label>
                                <select
                                    value={statusFilter}
                                    onChange={(e) => setStatusFilter(e.target.value)}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                >
                                    <option value="all">All Status</option>
                                    <option value="pending_review">Pending Review</option>
                                    <option value="verified_true">Verified True</option>
                                    <option value="verified_false">Verified False</option>
                                </select>
                            </div>

                            {/* Risk Range */}
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Risk Score Range
                                </label>
                                <div className="flex items-center gap-2">
                                    <input
                                        type="number"
                                        min="0"
                                        max="1"
                                        step="0.1"
                                        value={riskFilter[0]}
                                        onChange={(e) => setRiskFilter([parseFloat(e.target.value), riskFilter[1]])}
                                        className="w-20 px-2 py-1 border border-gray-300 rounded"
                                    />
                                    <span>to</span>
                                    <input
                                        type="number"
                                        min="0"
                                        max="1"
                                        step="0.1"
                                        value={riskFilter[1]}
                                        onChange={(e) => setRiskFilter([riskFilter[0], parseFloat(e.target.value)])}
                                        className="w-20 px-2 py-1 border border-gray-300 rounded"
                                    />
                                </div>
                            </div>

                            {/* Sort */}
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Sort By
                                </label>
                                <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                                    <option>Risk Score (High to Low)</option>
                                    <option>Date (Newest First)</option>
                                    <option>Date (Oldest First)</option>
                                </select>
                            </div>
                        </div>
                    )}
                </div>

                {/* Results */}
                <div className="mb-4 text-sm text-gray-600">
                    Showing {filteredItems.length} items
                </div>

                {/* Items List */}
                {isLoading && page === 1 ? (
                    <div className="text-center py-12">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                    </div>
                ) : (
                    <div className="space-y-4">
                        {filteredItems.map((item: any) => (
                            <ItemCard key={item.id} item={item} />
                        ))}
                        {filteredItems.length === 0 && (
                            <div className="text-center py-12 bg-white rounded-lg shadow">
                                <p className="text-gray-500">No items found matching your criteria</p>
                            </div>
                        )}

                        {/* Infinite Scroll Target */}
                        {filteredItems.length > 0 && (
                            <div ref={observerTarget} className="py-8 text-center">
                                {isFetchingNextPage && (
                                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                                )}
                            </div>
                        )}
                    </div>
                )}
            </main>
        </div>
    )
}
