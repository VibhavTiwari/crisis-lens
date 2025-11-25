import { AlertCircle, CheckCircle, Clock } from 'lucide-react'
import Link from 'next/link'

interface ItemCardProps {
    item: {
        id: string
        title: string
        text: string
        risk_score: number
        status: string
        topics?: string[]
        created_at: string
    }
}

export function ItemCard({ item }: ItemCardProps) {
    const riskColor =
        item.risk_score > 0.7 ? 'red' :
            item.risk_score > 0.4 ? 'yellow' : 'green'

    return (
        <Link href={`/items/${item.id}`}>
            <div className="bg-white rounded-lg shadow hover:shadow-lg transition p-6 cursor-pointer border-l-4"
                style={{ borderLeftColor: riskColor === 'red' ? '#ef4444' : riskColor === 'yellow' ? '#eab308' : '#22c55e' }}
            >
                <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">{item.title}</h3>
                        <p className="text-gray-600 line-clamp-2">{item.text}</p>
                    </div>
                    <div className="ml-4">
                        {item.status === 'pending_review' && (
                            <Clock className="w-6 h-6 text-yellow-500" />
                        )}
                        {item.status === 'verified_true' && (
                            <CheckCircle className="w-6 h-6 text-green-500" />
                        )}
                        {item.risk_score > 0.7 && (
                            <AlertCircle className="w-6 h-6 text-red-500" />
                        )}
                    </div>
                </div>

                <div className="flex items-center justify-between mt-4">
                    <div className="flex space-x-2">
                        {item.topics?.slice(0, 3).map((topic) => (
                            <span key={topic} className="px-2 py-1 bg-blue-100 text-blue-700 text-sm rounded">
                                {topic}
                            </span>
                        ))}
                    </div>
                    <div className="text-sm font-semibold">
                        Risk: <span className={`text-${riskColor}-600`}>{(item.risk_score * 100).toFixed(0)}%</span>
                    </div>
                </div>
            </div>
        </Link>
    )
}
