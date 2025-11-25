/**
 * Presence Indicator Component
 * 
 * Shows active users in collaborative editing sessions.
 */
'use client'

import { useState, useEffect } from 'react'
import { User, Users } from 'lucide-react'

interface UserPresence {
    userId: string
    username: string
    avatar?: string
    color: string
    cursorPosition?: { x: number; y: number }
}

interface PresenceIndicatorProps {
    resourceId: string
    currentUserId: string
}

const AVATAR_COLORS = [
    '#3b82f6', // blue
    '#10b981', // green
    '#f59e0b', // yellow
    '#ef4444', // red
    '#8b5cf6', // purple
    '#ec4899', // pink
    '#14b8a6', // teal
    '#f97316', // orange
]

export default function PresenceIndicator({ resourceId, currentUserId }: PresenceIndicatorProps) {
    const [activeUsers, setActiveUsers] = useState<UserPresence[]>([])
    const [showList, setShowList] = useState(false)

    useEffect(() => {
        // Fetch initial presence data
        fetchPresence()

        // Set up interval to refresh presence
        const interval = setInterval(fetchPresence, 5000)

        return () => clearInterval(interval)
    }, [resourceId])

    const fetchPresence = async () => {
        try {
            const response = await fetch(
                `${process.env.NEXT_PUBLIC_API_URL}/collaboration/presence/${resourceId}`,
                {
                    headers: {
                        Authorization: `Bearer ${localStorage.getItem('access_token')}`
                    }
                }
            )

            if (response.ok) {
                const data = await response.json()

                // Convert to user presence objects
                const users: UserPresence[] = data.active_users
                    .filter((userId: string) => userId !== currentUserId)
                    .map((userId: string, index: number) => ({
                        userId,
                        username: `User ${userId.substring(0, 8)}`,
                        color: AVATAR_COLORS[index % AVATAR_COLORS.length],
                        cursorPosition: data.cursors?.[userId]?.position
                    }))

                setActiveUsers(users)
            }
        } catch (error) {
            console.error('Error fetching presence:', error)
        }
    }

    if (activeUsers.length === 0) {
        return null
    }

    return (
        <div className="relative">
            {/* Active Users Avatars */}
            <div className="flex items-center gap-2">
                <div className="flex -space-x-2">
                    {activeUsers.slice(0, 3).map((user) => (
                        <div
                            key={user.userId}
                            className="w-8 h-8 rounded-full border-2 border-white flex items-center justify-center text-white font-semibold text-sm shadow-md transition-transform hover:scale-110 cursor-pointer"
                            style={{ backgroundColor: user.color }}
                            onClick={() => setShowList(!showList)}
                            title={user.username}
                        >
                            {user.username.charAt(0).toUpperCase()}
                        </div>
                    ))}
                    {activeUsers.length > 3 && (
                        <div
                            className="w-8 h-8 rounded-full border-2 border-white bg-gray-400 flex items-center justify-center text-white font-semibold text-xs shadow-md cursor-pointer"
                            onClick={() => setShowList(!showList)}
                        >
                            +{activeUsers.length - 3}
                        </div>
                    )}
                </div>

                <button
                    onClick={() => setShowList(!showList)}
                    className="flex items-center gap-1 px-2 py-1 rounded-lg hover:bg-gray-100 transition-colors text-sm text-gray-600"
                >
                    <Users className="w-4 h-4" />
                    <span>{activeUsers.length} active</span>
                </button>
            </div>

            {/* Active Users List */}
            {showList && (
                <>
                    {/* Backdrop */}
                    <div
                        className="fixed inset-0 z-40"
                        onClick={() => setShowList(false)}
                    />

                    {/* List Panel */}
                    <div className="absolute right-0 mt-2 w-64 bg-white rounded-lg shadow-xl border border-gray-200 z-50 overflow-hidden">
                        <div className="p-3 bg-gradient-to-r from-blue-50 to-purple-50 border-b border-gray-200">
                            <h3 className="font-semibold text-gray-900 flex items-center gap-2">
                                <Users className="w-4 h-4" />
                                Active Users ({activeUsers.length})
                            </h3>
                        </div>

                        <div className="max-h-64 overflow-y-auto">
                            {activeUsers.map((user) => (
                                <div
                                    key={user.userId}
                                    className="p-3 hover:bg-gray-50 transition-colors flex items-center gap-3"
                                >
                                    <div
                                        className="w-10 h-10 rounded-full flex items-center justify-center text-white font-semibold shadow-sm"
                                        style={{ backgroundColor: user.color }}
                                    >
                                        {user.username.charAt(0).toUpperCase()}
                                    </div>
                                    <div className="flex-1">
                                        <p className="text-sm font-medium text-gray-900">
                                            {user.username}
                                        </p>
                                        <p className="text-xs text-gray-500">
                                            {user.cursorPosition
                                                ? 'Currently editing'
                                                : 'Viewing'}
                                        </p>
                                    </div>
                                    <div className="w-2 h-2 bg-green-500 rounded-full" />
                                </div>
                            ))}
                        </div>
                    </div>
                </>
            )}
        </div>
    )
}
