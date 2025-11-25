{ code: 'bn', name: 'Bengali' },
{ code: 'ta', name: 'Tamil' },
{ code: 'te', name: 'Telugu' },
    ]

const handlePublish = () => {
    console.log('Publishing advisory...', { title, content, selectedLanguages })
}

return (
    <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white border-b border-gray-200">
            <div className="container mx-auto px-4 py-4">
                <h1 className="text-2xl font-bold text-gray-900">Advisory Editor</h1>
            </div>
        </header>

        <main className="container mx-auto px-4 py-8 max-w-5xl">
            <div className="grid md:grid-cols-3 gap-6">
                {/* Editor */}
                <div className="md:col-span-2 space-y-6">
                    {/* Title */}
                    <div className="bg-white rounded-lg shadow p-6">
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Advisory Title
                        </label>
                        <input
                            type="text"
                            value={title}
                            onChange={(e) => setTitle(e.target.value)}
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Summary
                                </label>
                                <textarea
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg resize-none"
                                    rows={2}
                                    placeholder="2-3 sentence summary"
                                ></textarea>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    What Happened
                                </label>
                                <textarea
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg resize-none"
                                    rows={3}
                                    placeholder="Detailed narrative"
                                ></textarea>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    What's Verified
                                </label>
                                <textarea
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg resize-none"
                                    rows={3}
                                    placeholder="Confirmed facts"
                                ></textarea>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Recommended Actions
                                </label>
                                <textarea
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg resize-none"
                                    rows={3}
                                    placeholder="Public guidance"
                                ></textarea>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Sidebar */}
                <div className="space-y-6">
                    {/* Translation */}
                    <div className="bg-white rounded-lg shadow p-6">
                        <div className="flex items-center gap-2 mb-4">
                            <Globe className="w-5 h-5 text-blue-600" />
                            <h3 className="font-semibold text-gray-900">Translations</h3>
                        </div>

                        <div className="space-y-2">
                            {languages.map((lang) => (
                                <label key={lang.code} className="flex items-center gap-2 cursor-pointer">
                                    <input
                                        type="checkbox"
                                        checked={selectedLanguages.includes(lang.code)}
                                        onChange={(e) => {
                                            if (e.target.checked) {
                                                setSelectedLanguages([...selectedLanguages, lang.code])
                                            } else {
                                                setSelectedLanguages(selectedLanguages.filter(l => l !== lang.code))
                                            }
                                        }}
                                        className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                                    />
                                    <span className="text-sm text-gray-700">{lang.name}</span>
                                </label>
                            ))}
                        </div>

                        <button className="w-full mt-4 px-4 py-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition text-sm font-medium">
                            Generate Translations
                        </button>
                    </div>

                    {/* Status */}
                    <div className="bg-white rounded-lg shadow p-6">
                        <h3 className="font-semibold text-gray-900 mb-4">Status</h3>

                        <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 mb-4">
                            <option>Draft</option>
                            <option>Review</option>
                            <option>Ready</option>
                        </select>

                        <div className="text-sm text-gray-600 mb-4">
                            <div className="flex justify-between mb-2">
                                <span>Created:</span>
                                <span className="font-medium">Jan 15, 2024</span>
                            </div>
                            <div className="flex justify-between">
                                <span>Modified:</span>
                                <span className="font-medium">Today, 11:30 AM</span>
                            </div>
                        </div>
                    </div>

                    {/* Publish */}
                    <button
                        onClick={handlePublish}
                        className="w-full py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition flex items-center justify-center gap-2"
                    >
                        <Send className="w-5 h-5" />
                        {code: 'bn', name: 'Bengali' },
                        {code: 'ta', name: 'Tamil' },
                        {code: 'te', name: 'Telugu' },
                        ]

const handlePublish = () => {
                            console.log('Publishing advisory...', { title, content, selectedLanguages })
                        }

                        return (
                        <div className="min-h-screen bg-gray-50">
                            {/* Header */}
                            <header className="bg-white border-b border-gray-200">
                                <div className="container mx-auto px-4 py-4">
                                    <h1 className="text-2xl font-bold text-gray-900">Advisory Editor</h1>
                                </div>
                            </header>

                            <main className="container mx-auto px-4 py-8 max-w-5xl">
                                <div className="grid md:grid-cols-3 gap-6">
                                    {/* Editor */}
                                    <div className="md:col-span-2 space-y-6">
                                        {/* Title */}
                                        <div className="bg-white rounded-lg shadow p-6">
                                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                                Advisory Title
                                            </label>
                                            <input
                                                type="text"
                                                value={title}
                                                onChange={(e) => setTitle(e.target.value)}
                        <div className="space-y-4">
                                                <div>
                                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                                        Summary
                                                    </label>
                                                    <textarea
                                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg resize-none"
                                                        rows={2}
                                                        placeholder="2-3 sentence summary"
                                                    ></textarea>
                                                </div>

                                                <div>
                                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                                        What Happened
                                                    </label>
                                                    <textarea
                                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg resize-none"
                                                        rows={3}
                                                        placeholder="Detailed narrative"
                                                    ></textarea>
                                                </div>

                                                <div>
                                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                                        What's Verified
                                                    </label>
                                                    <textarea
                                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg resize-none"
                                                        rows={3}
                                                        placeholder="Confirmed facts"
                                                    ></textarea>
                                                </div>

                                                <div>
                                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                                        Recommended Actions
                                                    </label>
                                                    <textarea
                                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg resize-none"
                                                        rows={3}
                                                        placeholder="Public guidance"
                                                    ></textarea>
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Sidebar */}
                                    <div className="space-y-6">
                                        {/* Translation */}
                                        <div className="bg-white rounded-lg shadow p-6">
                                            <div className="flex items-center gap-2 mb-4">
                                                <Globe className="w-5 h-5 text-blue-600" />
                                                <h3 className="font-semibold text-gray-900">Translations</h3>
                                            </div>

                                            <div className="space-y-2">
                                                {languages.map((lang) => (
                                                    <label key={lang.code} className="flex items-center gap-2 cursor-pointer">
                                                        <input
                                                            type="checkbox"
                                                            checked={selectedLanguages.includes(lang.code)}
                                                            onChange={(e) => {
                                                                if (e.target.checked) {
                                                                    setSelectedLanguages([...selectedLanguages, lang.code])
                                                                } else {
                                                                    setSelectedLanguages(selectedLanguages.filter(l => l !== lang.code))
                                                                }
                                                            }}
                                                            className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                                                        />
                                                        <span className="text-sm text-gray-700">{lang.name}</span>
                                                    </label>
                                                ))}
                                            </div>

                                            <button className="w-full mt-4 px-4 py-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition text-sm font-medium">
                                                Generate Translations
                                            </button>
                                        </div>

                                        {/* Status */}
                                        <div className="bg-white rounded-lg shadow p-6">
                                            <h3 className="font-semibold text-gray-900 mb-4">Status</h3>

                                            <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 mb-4">
                                                <option>Draft</option>
                                                <option>Review</option>
                                                <option>Ready</option>
                                            </select>

                                            <div className="text-sm text-gray-600 mb-4">
                                                <div className="flex justify-between mb-2">
                                                    <span>Created:</span>
                                                    <span className="font-medium">Jan 15, 2024</span>
                                                </div>
                                                <div className="flex justify-between">
                                                    <span>Modified:</span>
                                                    <span className="font-medium">Today, 11:30 AM</span>
                                                </div>
                                            </div>
                                        </div>

                                        {/* Publish */}
                                        <button
                                            onClick={handlePublish}
                                            className="w-full py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition flex items-center justify-center gap-2"
                                        >
                                            <Send className="w-5 h-5" />
                                            Publish Advisory
                                        </button>
                                    </div>
                                </div>
                            </main>
                        </div>
                        )
}
                        ```
