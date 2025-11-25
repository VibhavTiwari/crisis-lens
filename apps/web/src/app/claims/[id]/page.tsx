'use client'

import { useQuery } from '@tanstack/react-query'
import { useParams } from 'next/navigation'
import { CheckCircle, XCircle, AlertCircle, ExternalLink } from 'lucide-react'
import { api } from '@/lib/api'

export default function ClaimDetailPage() {
    const params = useParams()
    const claimId = params.id as string

    const { data: claim, isLoading } = useQuery({
        queryKey: ['claim', claimId],
        queryFn: () => api.getItem(claimId), // Simplified - would be api.getClaim()
    })

    if (isLoading) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        )
    }

    const veracity = claim?.claims?.[0]?.veracity_likelihood || 0.5
    const veracityColor = veracity > 0.7 ? 'green' : veracity < 0.3 ? 'red' : 'yellow'

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <header className="bg-white border-b border-gray-200">
                <div className="container mx-auto px-4 py-4">
                    <h1 className="text-2xl font-bold text-gray-900">Claim Verification</h1>
                </div>
            </header>

            <main className="container mx-auto px-4 py-8 max-w-5xl">
                {/* Claim Card */}
                <div className="bg-white rounded-lg shadow-lg p-8 mb-6">
                    <div className="flex items-start justify-between mb-6">
                        <div className="flex-1">
                            <h2 className="text-2xl font-bold text-gray-900 mb-3">
                                {claim?.title}
                            </h2>
                            <p className="text-gray-700 text-lg">{claim?.text}</p>
                        </div>

                        {/* Veracity Badge */}
                        <div className={`ml-6 px-6 py-4 rounded-lg bg-${veracityColor}-100`}>
                            <div className="text-center">
                                <div className={`text-3xl font-bold text-${veracityColor}-600 mb-1`}>
                                    {(veracity * 100).toFixed(0)}%
                                </div>
                                <div className="text-sm text-gray-600">Veracity</div>
                            </div>
                        </div>
                    </div>

                    {/* Quick Actions */}
                    <div className="flex gap-3 pt-6 border-t border-gray-200">
                        <button className="flex-1 py-3 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 transition flex items-center justify-center gap-2">
                            <CheckCircle className="w-5 h-5" />
                            Verify True
                        </button>
                        <button className="flex-1 py-3 bg-red-600 text-white rounded-lg font-semibold hover:bg-red-700 transition flex items-center justify-center gap-2">
                            <XCircle className="w-5 h-5" />
                            Verify False
                        </button>
                        <button className="flex-1 py-3 bg-yellow-600 text-white rounded-lg font-semibold hover:bg-yellow-700 transition flex items-center justify-center gap-2">
                            <AlertCircle className="w-5 h-5" />
                            Needs Investigation
                        </button>
                    </div>
                </div>

                {/* Evidence Tree */}
                <div className="bg-white rounded-lg shadow-lg p-8">
                    <h3 className="text-xl font-bold text-gray-900 mb-6">Evidence</h3>

                    <div className="space-y-4">
                        {claim?.claims?.[0]?.evidence?.map((evidence: any, index: number) => (
                            <div key={index} className="border-l-4 border-blue-500 pl-4 py-3">
                                <div className="flex items-start justify-between">
                                    <div className="flex-1">
                                        <div className="font-semibold text-gray-900 mb-1">
                                            {evidence.source || 'Unknown Source'}
                                        </div>
                                        <p className="text-gray-700 mb-2">{evidence.text}</p>
                                        {evidence.url && (
                                            <a
                                                href={evidence.url}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="text-blue-600 hover:underline text-sm flex items-center gap-1"
                                            >
                                                View Source
                                                <ExternalLink className="w-4 h-4" />
                                            </a>
                                        )}
                                    </div>
                                    <div className="ml-4 text-right">
                                        <div className={`text-lg font-bold ${evidence.support_score > 0.7 ? 'text-green-600' :
                                                evidence.support_score < 0.3 ? 'text-red-600' : 'text-yellow-600'
                                            }`}>
                                            {((evidence.support_score || 0.5) * 100).toFixed(0)}%
                                        </div>
                                        <div className="text-xs text-gray-500">Support</div>
                                    </div>
                                </div>
                            </div>
                        )) || (
                                <div className="text-center py-8 text-gray-500">
                                    No evidence available
                                </div>
                            )}
                    </div>
                </div>

                {/* Risk Factors */}
                <div className="bg-white rounded-lg shadow-lg p-8 mt-6">
                    <h3 className="text-xl font-bold text-gray-900 mb-6">Risk Assessment</h3>

                    <div className="grid md:grid-cols-2 gap-4">
                        {Object.entries(claim?.claims?.[0]?.risk_factors || {}).map(([key, value]: [string, any]) => (
                            <div key={key} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                                <span className="text-gray-700 capitalize">{key.replace(/_/g, ' ')}</span>
                                <span className="font-semibold text-gray-900">{(value * 100).toFixed(0)}%</span>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Notes */}
                <div className="bg-white rounded-lg shadow-lg p-8 mt-6">
                    <h3 className="text-xl font-bold text-gray-900 mb-4">Analyst Notes</h3>
                    <textarea
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 resize-none"
                        rows={4}
                        placeholder="Add your notes here..."
                    ></textarea>
                    <button className="mt-3 px-6 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition">
                        Save Notes
                    </button>
                </div>
            </main>
        </div>
    )
}
