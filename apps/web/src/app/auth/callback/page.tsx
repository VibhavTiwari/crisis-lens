'use client'

import { useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { Shield } from 'lucide-react'

export default function OAuthCallbackPage() {
    const router = useRouter()
    const searchParams = useSearchParams()

    useEffect(() => {
        const code = searchParams.get('code')
        const error = searchParams.get('error')

        if (error) {
            console.error('OAuth error:', error)
            router.push('/login?error=oauth_failed')
            return
        }

        if (code) {
            // Exchange code for token
            fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/oauth/callback?code=${code}`)
                .then(res => res.json())
                .then(data => {
                    if (data.access_token) {
                        localStorage.setItem('access_token', data.access_token)
                        router.push('/dashboard')
                    } else {
                        router.push('/login?error=token_exchange_failed')
                    }
                })
                .catch(() => {
                    router.push('/login?error=network_error')
                })
        }
    }, [searchParams, router])

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 flex items-center justify-center">
            <div className="text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-600 rounded-2xl mb-4 animate-pulse">
                    <Shield className="w-10 h-10 text-white" />
                </div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">Signing you in...</h2>
                <p className="text-gray-600">Please wait a moment</p>
            </div>
        </div>
    )
}
