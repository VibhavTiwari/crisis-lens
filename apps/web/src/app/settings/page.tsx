'use client'

import { useState } from 'react'
import { Users, Shield, Settings as SettingsIcon, Key, Bell } from 'lucide-react'

export default function SettingsPage() {
    const [activeTab, setActiveTab] = useState('profile')

    const tabs = [
        { id: 'profile', name: 'Profile', icon: Users },
        { id: 'security', name: 'Security', icon: Shield },
        { id: 'api-keys', name: 'API Keys', icon: Key },
        { id: 'notifications', name: 'Notifications', icon: Bell },
        { id: 'system', name: 'System', icon: SettingsIcon },
    ]

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <header className="bg-white border-b border-gray-200">
                <div className="container mx-auto px-4 py-4">
                    <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
                </div>
            </header>

            <main className="container mx-auto px-4 py-8 max-w-6xl">
                <div className="grid md:grid-cols-4 gap-6">
                    {/* Sidebar */}
                    <div className="md:col-span-1">
                        <div className="bg-white rounded-lg shadow">
                            {tabs.map((tab) => {
                                const Icon = tab.icon
                                return (
                                    <button
                                        key={tab.id}
                                        onClick={() => setActiveTab(tab.id)}
                                        className={`w-full flex items-center gap-3 px-4 py-3 text-left transition border-b last:border-b-0 ${activeTab === tab.id
                                                ? 'bg-blue-50 text-blue-600 border-l-4 border-l-blue-600'
                                                : 'text-gray-700 hover:bg-gray-50 border-l-4 border-l-transparent'
                                            }`}
                                    >
                                        <Icon className="w-5 h-5" />
                                        {tab.name}
                                    </button>
                                )
                            })}
                        </div>
                    </div>

                    {/* Content */}
                    <div className="md:col-span-3">
                        {activeTab === 'profile' && (
                            <div className="bg-white rounded-lg shadow p-6">
                                <h2 className="text-xl font-bold text-gray-900 mb-6">Profile Settings</h2>

                                <div className="space-y-4">
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">
                                            Full Name
                                        </label>
                                        <input
                                            type="text"
                                            defaultValue="John Doe"
                                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                        />
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">
                                            Email
                                        </label>
                                        <input
                                            type="email"
                                            defaultValue="john@example.com"
                                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                        />
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">
                                            Role
                                        </label>
                                        <input
                                            type="text"
                                            defaultValue="Analyst"
                                            disabled
                                            className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50"
                                        />
                                    </div>

                                    <button className="px-6 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition">
                                        Save Changes
                                    </button>
                                </div>
                            </div>
                        )}

                        {activeTab === 'security' && (
                            <div className="space-y-6">
                                <div className="bg-white rounded-lg shadow p-6">
                                    <h2 className="text-xl font-bold text-gray-900 mb-6">Change Password</h2>

                                    <div className="space-y-4">
                                        <div>
                                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                                Current Password
                                            </label>
                                            <input
                                                type="password"
                                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                            />
                                        </div>

                                        <div>
                                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                                New Password
                                            </label>
                                            <input
                                                type="password"
                                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                            />
                                        </div>

                                        <div>
                                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                                Confirm New Password
                                            </label>
                                            <input
                                                type="password"
                                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                            />
                                        </div>

                                        <button className="px-6 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition">
                                            Update Password
                                        </button>
                                    </div>
                                </div>

                                <div className="bg-white rounded-lg shadow p-6">
                                    <h2 className="text-xl font-bold text-gray-900 mb-4">Two-Factor Authentication</h2>
                                    <p className="text-gray-600 mb-4">Add an extra layer of security to your account</p>
                                    <button className="px-6 py-2 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 transition">
                                        Enable 2FA
                                    </button>
                                </div>
                            </div>
                        )}

                        {activeTab === 'api-keys' && (
                            <div className="bg-white rounded-lg shadow p-6">
                                <div className="flex items-center justify-between mb-6">
                                    <h2 className="text-xl font-bold text-gray-900">API Keys</h2>
                                    <button className="px-4 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition">
                                        Create New Key
                                    </button>
                                </div>

                                <div className="space-y-3">
                                    {[
                                        { name: 'Production API Key', created: '2024-01-10', expires: '2024-04-10' },
                                        { name: 'Development Key', created: '2024-01-05', expires: '2024-07-05' },
                                    ].map((key, index) => (
                                        <div key={index} className="p-4 border border-gray-200 rounded-lg flex items-center justify-between">
                                            <div>
                                                <div className="font-semibold text-gray-900">{key.name}</div>
                                                <div className="text-sm text-gray-500">
                                                    Created: {key.created} | Expires: {key.expires}
                                                </div>
                                            </div>
                                            <button className="px-3 py-1 text-red-600 hover:bg-red-50 rounded">
                                                Revoke
                                            </button>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {activeTab === 'notifications' && (
                            <div className="bg-white rounded-lg shadow p-6">
                                <h2 className="text-xl font-bold text-gray-900 mb-6">Notification Preferences</h2>

                                <div className="space-y-4">
                                    {[
                                        { label: 'High-risk items detected', checked: true },
                                        { label: 'Items assigned to me', checked: true },
                                        { label: 'Advisories published', checked: true },
                                        { label: 'Daily digest', checked: false },
                                        { label: 'Weekly summary', checked: true },
                                    ].map((option, index) => (
                                        <label key={index} className="flex items-center gap-3 cursor-pointer">
                                            <input
                                                type="checkbox"
                                                defaultChecked={option.checked}
                                                className="w-5 h-5 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                                            />
                                            <span className="text-gray-700">{option.label}</span>
                                        </label>
                                    ))}
                                </div>

                                <button className="mt-6 px-6 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition">
                                    Save Preferences
                                </button>
                            </div>
                        )}

                        {activeTab === 'system' && (
                            <div className="bg-white rounded-lg shadow p-6">
                                <h2 className="text-xl font-bold text-gray-900 mb-6">System Settings</h2>

                                <div className="space-y-4">
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">
                                            Theme
                                        </label>
                                        <select className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                                            <option>Light</option>
                                            <option>Dark</option>
                                            <option>Auto</option>
                                        </select>
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">
                                            Language
                                        </label>
                                        <select className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                                            <option>English</option>
                                            <option>Hindi</option>
                                            <option>Marathi</option>
                                        </select>
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">
                                            Timezone
                                        </label>
                                        <select className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                                            <option>IST (UTC+5:30)</option>
                                            <option>UTC</option>
                                            <option>EST</option>
                                        </select>
                                    </div>

                                    <button className="px-6 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition">
                                        Save Settings
                                    </button>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </main>
        </div>
    )
}
