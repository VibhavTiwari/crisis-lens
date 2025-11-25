import Link from 'next/link'
import { AlertCircle, LineChart, Shield } from 'lucide-react'

export default function Home() {
    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
            {/* Header */}
            <header className="bg-white/80 backdrop-blur-sm border-b border-gray-200 sticky top-0 z-50">
                <div className="container mx-auto px-4 py-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                            <Shield className="w-8 h-8 text-blue-600" />
                            <h1 className="text-2xl font-bold text-gray-900">CrisisLens</h1>
                        </div>
                        <nav className="flex space-x-6">
                            <Link href="/dashboard" className="text-gray-700 hover:text-blue-600 transition">
                                Dashboard
                            </Link>
                            <Link href="/login" className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">
                                Sign In
                            </Link>
                        </nav>
                    </div>
                </div>
            </header>

            {/* Hero */}
            <main className="container mx-auto px-4 py-20">
                <div className="max-w-4xl mx-auto text-center">
                    <h2 className="text-5xl font-bold text-gray-900 mb-6">
                        AI-Powered Crisis
                        <span className="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent"> Intelligence</span>
                    </h2>
                    <p className="text-xl text-gray-600 mb-8">
                        Real-time verification and analysis of crisis information using advanced AI and machine learning
                    </p>
                    <div className="flex justify-center space-x-4">
                        <Link href="/dashboard" className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition text-lg font-semibold">
                            Get Started
                        </Link>
                        <Link href="/learn-more" className="px-8 py-3 border-2 border-gray-300 text-gray-700 rounded-lg hover:border-blue-600 hover:text-blue-600 transition text-lg font-semibold">
                            Learn More
                        </Link>
                    </div>
                </div>

                {/* Features */}
                <div className="grid md:grid-cols-3 gap-8 mt-20 max-w-6xl mx-auto">
                    <div className="bg-white p-8 rounded-xl shadow-lg hover:shadow-xl transition">
                        <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                            <AlertCircle className="w-6 h-6 text-blue-600" />
                        </div>
                        <h3 className="text-xl font-semibold mb-3">Real-Time Verification</h3>
                        <p className="text-gray-600">
                            Automated fact-checking and evidence retrieval using NLI models and Google Fact Check API
                        </p>
                    </div>

                    <div className="bg-white p-8 rounded-xl shadow-lg hover:shadow-xl transition">
                        <div className="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center mb-4">
                            <LineChart className="w-6 h-6 text-indigo-600" />
                        </div>
                        <h3 className="text-xl font-semibold mb-3">Risk Scoring</h3>
                        <p className="text-gray-600">
                            8-factor composite risk assessment for prioritizing high-impact crisis events
                        </p>
                    </div>

                    <div className="bg-white p-8 rounded-xl shadow-lg hover:shadow-xl transition">
                        <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                            <Shield className="w-6 h-6 text-purple-600" />
                        </div>
                        <h3 className="text-xl font-semibold mb-3">Multi-Language Support</h3>
                        <p className="text-gray-600">
                            Automatic translation to 5 Indian languages for wider crisis alert dissemination
                        </p>
                    </div>
                </div>

                {/* Stats */}
                <div className="mt-20 bg-white rounded-2xl shadow-xl p-12 max-w-4xl mx-auto">
                    <div className="grid grid-cols-3 gap-8 text-center">
                        <div>
                            <div className="text-4xl font-bold text-blue-600 mb-2">1000+</div>
                            <div className="text-gray-600">Items/Hour</div>
                        </div>
                        <div>
                            <div className="text-4xl font-bold text-indigo-600 mb-2">99.9%</div>
                            <div className="text-gray-600">Uptime</div>
                        </div>
                        <div>
                            <div className="text-4xl font-bold text-purple-600 mb-2">&lt;2s</div>
                            <div className="text-gray-600">Response Time</div>
                        </div>
                    </div>
                </div>
            </main>

            {/* Footer */}
            <footer className="bg-white border-t border-gray-200 mt-20">
                <div className="container mx-auto px-4 py-8">
                    <div className="text-center text-gray-600">
                        <p>&copy; 2024 CrisisLens. Built for crisis response teams worldwide.</p>
                    </div>
                </div>
            </footer>
        </div>
    )
}
