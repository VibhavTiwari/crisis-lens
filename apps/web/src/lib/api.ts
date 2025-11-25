import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const api = {
    async getItems(params?: { status?: string; limit?: number }) {
        const { data } = await axios.get(`${API_URL}/api/items`, { params })
        return data
    },

    async getItem(id: string) {
        const { data } = await axios.get(`${API_URL}/api/items/${id}`)
        return data
    },

    async getStats() {
        // Mock stats for now
        return {
            pending: 45,
            highRisk: 12,
            avgRisk: 0.42,
            locations: 8,
        }
    },

    async login(email: string, password: string) {
        const { data } = await axios.post(`${API_URL}/auth/login`, { email, password })
        return data
    },

    async startWorkflow(rawItem: any) {
        const { data } = await axios.post(`${API_URL}/workflows/start`, { raw_item: rawItem })
        return data
    },

    async getWorkflowStatus(workflowId: string) {
        const { data } = await axios.get(`${API_URL}/workflows/${workflowId}/status`)
        return data
    },
}
