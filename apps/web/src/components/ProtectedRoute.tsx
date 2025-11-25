'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
    const router = useRouter()
    const [isAuthenticated, setIsAuthenticated] = useState(false)
    const [isLoading, setIsLoading] = useState(true)

    useEffect(() => {
        const token = localStorage.getItem('access_token')

        if (!token) {
            router.push('/login')
            return
        }

        // Verify token validity
        fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/me`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        })
            .then(res => {
                if (res.ok) {
                    setIsAuthenticated(true)
                } else {
                    localStorage.removeItem('access_token')
                    router.push('/login')
                }
            })
            .catch(() => {
                router.push('/login')
            })
            .finally(() => {
                setIsLoading(false)
            })
    }, [router])

    if (isLoading) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        )
    }

    if (!isAuthenticated) {
        return null
    }

    return <>{children}</>
}
