/**
 * Offline Manager Service
 * 
 * Handles offline data caching and synchronization.
 */
import AsyncStorage from '@react-native-async-storage/async-storage';
import NetInfo from '@react-native-community/netinfo';

interface QueuedAction {
    id: string;
    type: string;
    data: any;
    timestamp: number;
}

class OfflineManager {
    private syncQueue: QueuedAction[] = [];
    private isOnline: boolean = true;

    constructor() {
        this.initNetworkListener();
        this.loadQueue();
    }

    private initNetworkListener() {
        NetInfo.addEventListener((state) => {
            this.isOnline = state.isConnected ?? false;

            if (this.isOnline) {
                this.processSyncQueue();
            }
        });
    }

    async checkIsOnline(): Promise<boolean> {
        const state = await NetInfo.fetch();
        return state.isConnected ?? false;
    }

    // Cache management
    async cacheData(key: string, data: any): Promise<void> {
        try {
            await AsyncStorage.setItem(`cache_${key}`, JSON.stringify(data));
        } catch (error) {
            console.error('Cache write error:', error);
        }
    }

    async getCachedData<T>(key: string): Promise<T | null> {
        try {
            const data = await AsyncStorage.getItem(`cache_${key}`);
            return data ? JSON.parse(data) : null;
        } catch (error) {
            console.error('Cache read error:', error);
            return null;
        }
    }

    async clearCache(key?: string): Promise<void> {
        try {
            if (key) {
                await AsyncStorage.removeItem(`cache_${key}`);
            } else {
                const keys = await AsyncStorage.getAllKeys();
                const cacheKeys = keys.filter((k) => k.startsWith('cache_'));
                await AsyncStorage.multiRemove(cacheKeys);
            }
        } catch (error) {
            console.error('Cache clear error:', error);
        }
    }

    // Sync queue management
    async addToQueue(type: string, data: any): Promise<void> {
        const action: QueuedAction = {
            id: `${Date.now()}_${Math.random()}`,
            type,
            data,
            timestamp: Date.now(),
        };

        this.syncQueue.push(action);
        await this.saveQueue();

        // Try to sync immediately if online
        if (this.isOnline) {
            await this.processSyncQueue();
        }
    }

    private async loadQueue(): Promise<void> {
        try {
            const queueData = await AsyncStorage.getItem('sync_queue');
            if (queueData) {
                this.syncQueue = JSON.parse(queueData);
            }
        } catch (error) {
            console.error('Queue load error:', error);
        }
    }

    private async saveQueue(): Promise<void> {
        try {
            await AsyncStorage.setItem('sync_queue', JSON.stringify(this.syncQueue));
        } catch (error) {
            console.error('Queue save error:', error);
        }
    }

    private async processSyncQueue(): Promise<void> {
        if (!this.isOnline || this.syncQueue.length === 0) {
            return;
        }

        const actionsToProcess = [...this.syncQueue];
        this.syncQueue = [];
        await this.saveQueue();

        for (const action of actionsToProcess) {
            try {
                await this.executeAction(action);
            } catch (error) {
                console.error(`Failed to sync action ${action.type}:`, error);
                // Re-add to queue on failure
                this.syncQueue.push(action);
            }
        }

        await this.saveQueue();
    }

    private async executeAction(action: QueuedAction): Promise<void> {
        // Implement action execution based on type
        switch (action.type) {
            case 'create_item':
                // await api.createItem(action.data);
                break;
            case 'verify_claim':
                // await api.verifyClaim(action.data.id, action.data.verdict);
                break;
            // Add more action types as needed
            default:
                console.warn(`Unknown action type: ${action.type}`);
        }
    }

    getQueueLength(): number {
        return this.syncQueue.length;
    }

    isNetworkOnline(): boolean {
        return this.isOnline;
    }
}

export const offlineManager = new OfflineManager();
export default offlineManager;
