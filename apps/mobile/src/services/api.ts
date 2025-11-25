/**
 * API Client for CrisisLens Mobile App
 * 
 * Handles all API requests with automatic token injection and error handling.
 */
import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import * as SecureStore from 'expo-secure-store';
import Constants from 'expo-constants';

const API_URL = Constants.expoConfig?.extra?.apiUrl || 'http://localhost:8000';

class APIClient {
    private client: AxiosInstance;

    constructor() {
        this.client = axios.create({
            baseURL: API_URL,
            timeout: 30000,
            headers: {
                'Content-Type': 'application/json',
            },
        });

        // Request interceptor to add auth token
        this.client.interceptors.request.use(
            async (config) => {
                const token = await SecureStore.getItemAsync('access_token');
                if (token) {
                    config.headers.Authorization = `Bearer ${token}`;
                }
                return config;
            },
            (error) => Promise.reject(error)
        );

        // Response interceptor for error handling
        this.client.interceptors.response.use(
            (response) => response,
            async (error) => {
                if (error.response?.status === 401) {
                    // Token expired, clear and redirect to login
                    await SecureStore.deleteItemAsync('access_token');
                    // Navigation will be handled by AuthContext
                }
                return Promise.reject(error);
            }
        );
    }

    // Auth endpoints
    async login(email: string, password: string) {
        const response = await this.client.post('/auth/login', { email, password });
        return response.data;
    }

    async oauthLogin(provider: string, code: string) {
        const response = await this.client.post(`/auth/oauth/${provider}/callback`, { code });
        return response.data;
    }

    async getProfile() {
        const response = await this.client.get('/auth/me');
        return response.data;
    }

    // Items endpoints
    async getItems(params?: {
        status?: string;
        search?: string;
        limit?: number;
        offset?: number;
    }) {
        const response = await this.client.get('/items', { params });
        return response.data;
    }

    async getItem(id: string) {
        const response = await this.client.get(`/items/${id}`);
        return response.data;
    }

    async createItem(data: any) {
        const response = await this.client.post('/items', data);
        return response.data;
    }

    // Claims endpoints
    async getClaims(itemId?: string) {
        const response = await this.client.get('/claims', {
            params: itemId ? { item_id: itemId } : undefined,
        });
        return response.data;
    }

    async getClaim(id: string) {
        const response = await this.client.get(`/claims/${id}`);
        return response.data;
    }

    async verifyClaim(id: string, verdict: string, evidence?: any) {
        const response = await this.client.post(`/claims/${id}/verify`, {
            verdict,
            evidence,
        });
        return response.data;
    }

    // Upload media
    async uploadMedia(file: {
        uri: string;
        name: string;
        type: string;
    }) {
        const formData = new FormData();
        formData.append('file', file as any);

        const response = await this.client.post('/media/upload', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    }

    // Stats
    async getStats() {
        const response = await this.client.get('/stats');
        return response.data;
    }

    // Notifications
    async registerPushToken(token: string, platform: 'ios' | 'android') {
        const response = await this.client.post('/notifications/register', {
            token,
            platform,
        });
        return response.data;
    }
}

export const api = new APIClient();
export default api;
