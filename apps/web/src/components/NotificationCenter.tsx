/**
 * Notification Center Component
 * 
 * Displays real-time notifications with toast-style UI.
 */
'use client'

import { useState, useEffect } from 'react'
import { X, Bell, AlertCircle, Info, CheckCircle, AlertTriangle } from 'lucide-react'
import { useGlobalWebSocket } from '@/hooks/useWebSocket'

interface Notification {
    id: string
    type: 'info' | 'success' | 'warning' | 'error'
    title: string
    message: string
    timestamp: string
    read: boolean
}

export default function NotificationCenter() {
    const [notifications, setNotifications] = useState<Notification[]>([])
    const [isOpen, setIsOpen] = useState(false)
    const [unreadCount, setUnreadCount] = useState(0)

    // Get token from localStorage
    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null

    // WebSocket connection for real-time notifications
    const { notifications: wsNotifications } = useGlobalWebSocket(token || undefined)

    // Update notifications from WebSocket
    useEffect(() => {
        if (wsNotifications.length > 0) {
            const latestNotification = wsNotifications[0]
            const notification: Notification = {
                id: `notif-${Date.now()}`,
                type: latestNotification.data?.severity || 'info',
                title: latestNotification.data?.title || 'New Notification',
                message: latestNotification.data?.message || '',
                timestamp: new Date().toISOString(),
                read: false
            }

            setNotifications((prev) => [notification, ...prev])
            setUnreadCount((prev) => prev + 1)
        }
    }, [wsNotifications])

    const markAsRead = (id: string) => {
        setNotifications((prev) =>
            prev.map((n) => (n.id === id ? { ...n, read: true } : n))
        )
        setUnreadCount((prev) => Math.max(0, prev - 1))
    }

    const markAllAsRead = () => {
        setNotifications((prev) => prev.map((n) => ({ ...n, read: true })))
        setUnreadCount(0)
    }

    const removeNotification = (id: string) => {
        setNotifications((prev) => {
            const notification = prev.find((n) => n.id === id)
            if (notification && !notification.read) {
                setUnreadCount((count) => Math.max(0, count - 1))
            }
            return prev.filter((n) => n.id !== id)
        })
    }

    const getIcon = (type: Notification['type']) => {
        switch (type) {
            case 'success':
                return <CheckCircle className="w-5 h-5 text-green-600" />
            case 'warning':
                return <AlertTriangle className="w-5 h-5 text-yellow-600" />
            case 'error':
                return <AlertCircle className="w-5 h-5 text-red-600" />
            default:
                return <Info className="w-5 h-5 text-blue-600" />
        }
    }

    const getBorderColor = (type: Notification['type']) => {
        switch (type) {
            case 'success':
                return 'border-l-green-500'
            case 'warning':
                return 'border-l-yellow-500'
            case 'error':
                return 'border-l-red-500'
            default:
                return 'border-l-blue-500'
        }
    }

    return (
        <div className="relative">
            {/* Notification Bell */}
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="relative p-2 rounded-lg hover:bg-gray-100 transition-colors"
            >
                <Bell className="w-6 h-6 text-gray-700" />
                {unreadCount > 0 && (
                    <span className="absolute top-0 right-0 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                        {unreadCount > 9 ? '9+' : unreadCount}
                    </span>
                )}
            </button>

            {/* Notification Panel */}
            {isOpen && (
                <>
                    {/* Backdrop */}
                    <div
                        className="fixed inset-0 z-40"
                        onClick={() => setIsOpen(false)}
                    />

                    {/* Panel */}
                    <div className="absolute right-0 mt-2 w-96 bg-white rounded-lg shadow-xl border border-gray-200 z-50 max-h-[600px] overflow-hidden flex flex-col">
                        {/* Header */}
                        <div className="p-4 border-b border-gray-200 flex items-center justify-between bg-gradient-to-r from-blue-50 to-purple-50">
                            <div className="flex items-center gap-2">
                                <Bell className="w-5 h-5 text-blue-600" />
                                <h3 className="font-semibold text-gray-900">Notifications</h3>
                                {unreadCount > 0 && (
                                    <span className="px-2 py-1 bg-red-500 text-white text-xs rounded-full">
                                        {unreadCount}
                                    </span>
                                )}
                            </div>
                            {unreadCount > 0 && (
                                <button
                                    onClick={markAllAsRead}
                                    className="text-sm text-blue-600 hover:text-blue-700"
                                >
                                    Mark all read
                                </button>
                            )}
                        </div>

                        {/* Notifications List */}
                        <div className="flex-1 overflow-y-auto">
                            {notifications.length === 0 ? (
                                <div className="p-8 text-center text-gray-500">
                                    <Bell className="w-12 h-12 mx-auto mb-2 text-gray-300" />
                                    <p>No notifications yet</p>
                                </div>
                            ) : (
                                <div className="divide-y divide-gray-100">
                                    {notifications.map((notification) => (
                                        <div
                                            key={notification.id}
                                            className={`p-4 hover:bg-gray-50 transition-colors border-l-4 ${getBorderColor(
                                                notification.type
                                            )} ${!notification.read ? 'bg-blue-50' : ''}`}
                                            onClick={() => markAsRead(notification.id)}
                                        >
                                            <div className="flex items-start gap-3">
                                                <button
                                                    onClick={(e) => {
                                                        e.stopPropagation()
                                                        removeNotification(notification.id)
                                                    }}
                                                    className="flex-shrink-0 p-1 hover:bg-gray-200 rounded transition-colors"
                                                >
                                                    <X className="w-4 h-4 text-gray-400" />
                                                </button>

                                                <div className="flex-shrink-0 mt-0.5">
                                                    {getIcon(notification.type)}
                                                </div>

                                                <div className="flex-1 min-w-0">
                                                    <h4 className="text-sm font-semibold text-gray-900 mb-1">
                                                        {notification.title}
                                                    </h4>
                                                    <p className="text-sm text-gray-600 mb-2">
                                                        {notification.message}
                                                    </p>
                                                    <p className="text-xs text-gray-400">
                                                        {new Date(notification.timestamp).toLocaleString()}
                                                    </p>
                                                </div>

                                                {!notification.read && (
                                                    <div className="flex-shrink-0 w-2 h-2 bg-blue-600 rounded-full mt-2" />
                                                )}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>

                        {/* Footer */}
                        {notifications.length > 0 && (
                            <div className="p-3 border-t border-gray-200 bg-gray-50">
                                <button
                                    onClick={() => setNotifications([])}
                                    className="w-full text-sm text-red-600 hover:text-red-700 font-medium"
                                >
                                    Clear all notifications
                                </button>
                            </div>
                        )}
                    </div>
                </>
            )}
        </div>
    )
}
