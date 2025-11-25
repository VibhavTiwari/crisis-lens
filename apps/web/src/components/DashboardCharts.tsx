'use client'

import { useQuery } from '@tanstack/react-query'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts'
import { api } from '@/lib/api'

const COLORS = ['#3b82f6', '#ef4444', '#eab308', '#22c55e', '#8b5cf6']

export function DashboardCharts() {
    const { data: stats } = useQuery({
        queryKey: ['dashboard-charts'],
        queryFn: async () => {
            // Mock data - replace with real API call
            return {
                riskDistribution: [
                    { range: '0-0.2', count: 45 },
                    { range: '0.2-0.4', count: 78 },
                    { range: '0.4-0.6', count: 120 },
                    { range: '0.6-0.8', count: 65 },
                    { range: '0.8-1.0', count: 32 },
                ],
                itemsOverTime: [
                    { date: 'Mon', items: 245 },
                    { date: 'Tue', items: 287 },
                    { date: 'Wed', items: 312 },
                    { date: 'Thu', items: 298 },
                    { date: 'Fri', items: 334 },
                    { date: 'Sat', items: 278 },
                    { date: 'Sun', items: 256 },
                ],
                sourceBreakdown: [
                    { name: 'Twitter', value: 45 },
                    { name: 'Reddit', value: 25 },
                    { name: 'YouTube', value: 15 },
                    { name: 'News', value: 10 },
                    { name: 'Other', value: 5 },
                ],
            }
        },
    })

    if (!stats) return null

    return (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-8">
            {/* Risk Distribution */}
            <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Risk Score Distribution</h3>
                <ResponsiveContainer width="100%" height={250}>
                    <BarChart data={stats.riskDistribution}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="range" />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="count" fill="#3b82f6" />
                    </BarChart>
                </ResponsiveContainer>
            </div>

            {/* Items Over Time */}
            <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Items Processed (7 Days)</h3>
                <ResponsiveContainer width="100%" height={250}>
                    <LineChart data={stats.itemsOverTime}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis />
                        <Tooltip />
                        <Line type="monotone" dataKey="items" stroke="#3b82f6" strokeWidth={2} />
                    </LineChart>
                </ResponsiveContainer>
            </div>

            {/* Source Breakdown */}
            <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Source Distribution</h3>
                <ResponsiveContainer width="100%" height={250}>
                    <PieChart>
                        <Pie
                            data={stats.sourceBreakdown}
                            cx="50%"
                            cy="50%"
                            labelLine={false}
                            label={(entry) => `${entry.name}: ${entry.value}%`}
                            outerRadius={80}
                            fill="#8884d8"
                            dataKey="value"
                        >
                            {stats.sourceBreakdown.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                            ))}
                        </Pie>
                        <Tooltip />
                    </PieChart>
                </ResponsiveContainer>
            </div>

            {/* Top Topics */}
            <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Top Topics</h3>
                <div className="space-y-3">
                    {[
                        { topic: 'Flooding', count: 156 },
                        { topic: 'Fire', count: 98 },
                        { topic: 'Accident', count: 67 },
                        { topic: 'Weather', count: 54 },
                        { topic: 'Infrastructure', count: 45 },
                    ].map((item, index) => (
                        <div key={index} className="flex items-center justify-between">
                            <span className="text-gray-700">{item.topic}</span>
                            <div className="flex items-center gap-2">
                                <div className="w-32 h-2 bg-gray-200 rounded-full overflow-hidden">
                                    <div
                                        className="h-full bg-blue-600 rounded-full"
                                        style={{ width: `${(item.count / 156) * 100}%` }}
                                    ></div>
                                </div>
                                <span className="text-sm font-semibold text-gray-900 w-12 text-right">
                                    {item.count}
                                </span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    )
}
