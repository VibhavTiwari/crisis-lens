/**
 * WebSocket Hook for CrisisLens
 * 
 * Provides WebSocket connection management with auto-reconnection.
 */
import { useEffect, useRef, useState, useCallback } from 'react'

export interface WebSocketMessage {
    type: string
    [key: string]: any
}

export interface UseWebSocketOptions {
    url: string
    token?: string
    onMessage?: (message: WebSocketMessage) => void
    onConnect?: () => void
    onDisconnect?: () => void
    onError?: (error: Event) => void
    autoReconnect?: boolean
    reconnectInterval?: number
    maxReconnectAttempts?: number
}

export function useWebSocket({
    url,
    token,
    onMessage,
    onConnect,
    onDisconnect,
    onError,
    autoReconnect = true,
    reconnectInterval = 3000,
    maxReconnectAttempts = 10
}: UseWebSocketOptions) {
    const [isConnected, setIsConnected] = useState(false)
    const [reconnectAttempts, setReconnectAttempts] = useState(0)
    const wsRef = useRef<WebSocket | null>(null)
    const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
    const shouldReconnectRef = useRef(true)

    const connect = useCallback(() => {
        try {
            // Build WebSocket URL with token
            const wsUrl = token ? `${url}?token=${token}` : url

            const ws = new WebSocket(wsUrl)

            ws.onopen = () => {
                console.log('WebSocket connected')
                setIsConnected(true)
                setReconnectAttempts(0)
                onConnect?.()
            }

            ws.onmessage = (event) => {
                try {
                    const message = JSON.parse(event.data)
                    onMessage?.(message)
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error)
                }
            }

            ws.onclose = () => {
                console.log('WebSocket disconnected')
                setIsConnected(false)
                wsRef.current = null
                onDisconnect?.()

                // Auto-reconnect
                if (
                    autoReconnect &&
                    shouldReconnectRef.current &&
                    reconnectAttempts < maxReconnectAttempts
                ) {
                    console.log(`Reconnecting in ${reconnectInterval}ms...`)
                    reconnectTimeoutRef.current = setTimeout(() => {
                        setReconnectAttempts((prev) => prev + 1)
                        connect()
                    }, reconnectInterval)
                }
            }

            ws.onerror = (error) => {
                console.error('WebSocket error:', error)
                onError?.(error)
            }

            wsRef.current = ws
        } catch (error) {
            console.error('Error creating WebSocket:', error)
        }
    }, [
        url,
        token,
        onMessage,
        onConnect,
        onDisconnect,
        onError,
        autoReconnect,
        reconnectInterval,
        maxReconnectAttempts,
        reconnectAttempts
    ])

    const disconnect = useCallback(() => {
        shouldReconnectRef.current = false

        if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current)
        }

        if (wsRef.current) {
            wsRef.current.close()
            wsRef.current = null
        }

        setIsConnected(false)
    }, [])

    const send = useCallback((data: WebSocketMessage) => {
        if (wsRef.current && isConnected) {
            wsRef.current.send(JSON.stringify(data))
        } else {
            console.warn('WebSocket is not connected')
        }
    }, [isConnected])

    const joinRoom = useCallback((room: string) => {
        send({ type: 'join_room', room })
    }, [send])

    const leaveRoom = useCallback((room: string) => {
        send({ type: 'leave_room', room })
    }, [send])

    useEffect(() => {
        shouldReconnectRef.current = true
        connect()

        return () => {
            disconnect()
        }
    }, [connect, disconnect])

    return {
        isConnected,
        send,
        joinRoom,
        leaveRoom,
        disconnect,
        reconnect: connect
    }
}


/**
 * Hook for item-specific WebSocket connection
 */
export function useItemWebSocket(itemId: string, token?: string) {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    const wsUrl = `${apiUrl.replace('http', 'ws')}/ws/items/${itemId}`

    const [updates, setUpdates] = useState<WebSocketMessage[]>([])
    const [activeCursors, setActiveCursors] = useState<Record<string, any>>({})

    const handleMessage = useCallback((message: WebSocketMessage) => {
        setUpdates((prev) => [...prev, message])

        // Handle specific message types
        switch (message.type) {
            case 'cursor_update':
                setActiveCursors((prev) => ({
                    ...prev,
                    [message.user_id]: message.position
                }))
                break

            case 'item_update':
                // Handle item updates
                console.log('Item updated:', message.updates)
                break
        }
    }, [])

    const ws = useWebSocket({
        url: wsUrl,
        token,
        onMessage: handleMessage
    })

    return {
        ...ws,
        updates,
        activeCursors
    }
}


/**
 * Hook for global updates (dashboard, notifications, etc.)
 */
export function useGlobalWebSocket(token?: string) {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    const wsUrl = `${apiUrl.replace('http', 'ws')}/ws`

    const [newItems, setNewItems] = useState<any[]>([])
    const [alerts, setAlerts] = useState<any[]>([])
    const [notifications, setNotifications] = useState<any[]>([])

    const handleMessage = useCallback((message: WebSocketMessage) => {
        switch (message.type) {
            case 'new_item':
                setNewItems((prev) => [message.data, ...prev])
                break

            case 'alert':
                setAlerts((prev) => [message.data, ...prev])
                break

            case 'notification':
                setNotifications((prev) => [message.data, ...prev])
                break
        }
    }, [])

    const ws = useWebSocket({
        url: wsUrl,
        token,
        onMessage: handleMessage
    })

    return {
        ...ws,
        newItems,
        alerts,
        notifications,
        clearNewItems: () => setNewItems([]),
        clearAlerts: () => setAlerts([]),
        clearNotifications: () => setNotifications([])
    }
}
