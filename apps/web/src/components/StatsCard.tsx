import { ReactNode } from 'react'

interface StatsCardProps {
    title: string
    value: string | number
    icon: ReactNode
    color: 'blue' | 'red' | 'yellow' | 'green'
}

export function StatsCard({ title, value, icon, color }: StatsCardProps) {
    const colorClasses = {
        blue: 'bg-blue-100 text-blue-600',
        red: 'bg-red-100 text-red-600',
        yellow: 'bg-yellow-100 text-yellow-600',
        green: 'bg-green-100 text-green-600',
    }

    return (
        <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
                <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${colorClasses[color]}`}>
                    {icon}
                </div>
            </div>
            <div className="text-3xl font-bold text-gray-900 mb-1">{value}</div>
            <div className="text-sm text-gray-600">{title}</div>
        </div>
    )
}
