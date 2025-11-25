/**
 * Cookie Consent Component
 * 
 * GDPR-compliant cookie consent banner for web application.
 */
import React, { useState, useEffect } from 'react';

interface CookiePreferences {
    necessary: boolean;
    analytics: boolean;
    marketing: boolean;
}

export const CookieConsent: React.FC = () => {
    const [showBanner, setShowBanner] = useState(false);
    const [showSettings, setShowSettings] = useState(false);
    const [preferences, setPreferences] = useState<CookiePreferences>({
        necessary: true, // Always required
        analytics: false,
        marketing: false,
    });

    useEffect(() => {
        // Check if user has already set preferences
        const savedPreferences = localStorage.getItem('cookiePreferences');
        if (!savedPreferences) {
            setShowBanner(true);
        } else {
            setPreferences(JSON.parse(savedPreferences));
            applyPreferences(JSON.parse(savedPreferences));
        }
    }, []);

    const applyPreferences = (prefs: CookiePreferences) => {
        // Apply analytics cookies
        if (prefs.analytics) {
            enableAnalytics();
        } else {
            disableAnalytics();
        }

        // Apply marketing cookies
        if (prefs.marketing) {
            enableMarketing();
        } else {
            disableMarketing();
        }
    };

    const enableAnalytics = () => {
        // Initialize Google Analytics or similar
        if (typeof window !== 'undefined' && (window as any).gtag) {
            (window as any).gtag('consent', 'update', {
                analytics_storage: 'granted',
            });
        }
    };

    const disableAnalytics = () => {
        if (typeof window !== 'undefined' && (window as any).gtag) {
            (window as any).gtag('consent', 'update', {
                analytics_storage: 'denied',
            });
        }
    };

    const enableMarketing = () => {
        if (typeof window !== 'undefined' && (window as any).gtag) {
            (window as any).gtag('consent', 'update', {
                ad_storage: 'granted',
            });
        }
    };

    const disableMarketing = () => {
        if (typeof window !== 'undefined' && (window as any).gtag) {
            (window as any).gtag('consent', 'update', {
                ad_storage: 'denied',
            });
        }
    };

    const handleAcceptAll = () => {
        const allAccepted = {
            necessary: true,
            analytics: true,
            marketing: true,
        };
        setPreferences(allAccepted);
        savePreferences(allAccepted);
        setShowBanner(false);
    };

    const handleRejectAll = () => {
        const rejected = {
            necessary: true,
            analytics: false,
            marketing: false,
        };
        setPreferences(rejected);
        savePreferences(rejected);
        setShowBanner(false);
    };

    const handleSavePreferences = () => {
        savePreferences(preferences);
        setShowBanner(false);
        setShowSettings(false);
    };

    const savePreferences = (prefs: CookiePreferences) => {
        localStorage.setItem('cookiePreferences', JSON.stringify(prefs));
        applyPreferences(prefs);
    };

    if (!showBanner) {
        return null;
    }

    return (
        <div className="fixed bottom-0 left-0 right-0 bg-white border-t-2 border-gray-200 shadow-lg z-50">
            {!showSettings ? (
                <div className="max-w-7xl mx-auto p-6">
                    <div className="flex items-center justify-between flex-wrap gap-4">
                        <div className="flex-1 min-w-[300px]">
                            <h3 className="text-lg font-semibold mb-2">
                                Cookie Consent
                            </h3>
                            <p className="text-sm text-gray-600">
                                We use cookies to enhance your experience, analyze site traffic, and serve personalized content.
                                By clicking "Accept All", you consent to our use of cookies.{' '}
                                <a href="/privacy-policy" className="text-blue-600 hover:underline">
                                    Privacy Policy
                                </a>
                            </p>
                        </div>
                        <div className="flex gap-3">
                            <button
                                onClick={() => setShowSettings(true)}
                                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                            >
                                Settings
                            </button>
                            <button
                                onClick={handleRejectAll}
                                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                            >
                                Reject All
                            </button>
                            <button
                                onClick={handleAcceptAll}
                                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                            >
                                Accept All
                            </button>
                        </div>
                    </div>
                </div>
            ) : (
                <div className="max-w-7xl mx-auto p-6">
                    <h3 className="text-lg font-semibold mb-4">Cookie Preferences</h3>

                    <div className="space-y-4 mb-6">
                        {/* Necessary Cookies */}
                        <div className="flex items-start gap-3">
                            <input
                                type="checkbox"
                                checked={preferences.necessary}
                                disabled
                                className="mt-1"
                            />
                            <div className="flex-1">
                                <div className="font-medium">Necessary Cookies</div>
                                <div className="text-sm text-gray-600">
                                    Required for the website to function. Cannot be disabled.
                                </div>
                            </div>
                        </div>

                        {/* Analytics Cookies */}
                        <div className="flex items-start gap-3">
                            <input
                                type="checkbox"
                                checked={preferences.analytics}
                                onChange={(e) =>
                                    setPreferences({ ...preferences, analytics: e.target.checked })
                                }
                                className="mt-1"
                            />
                            <div className="flex-1">
                                <div className="font-medium">Analytics Cookies</div>
                                <div className="text-sm text-gray-600">
                                    Help us understand how visitors interact with our website.
                                </div>
                            </div>
                        </div>

                        {/* Marketing Cookies */}
                        <div className="flex items-start gap-3">
                            <input
                                type="checkbox"
                                checked={preferences.marketing}
                                onChange={(e) =>
                                    setPreferences({ ...preferences, marketing: e.target.checked })
                                }
                                className="mt-1"
                            />
                            <div className="flex-1">
                                <div className="font-medium">Marketing Cookies</div>
                                <div className="text-sm text-gray-600">
                                    Used to track visitors across websites for marketing purposes.
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="flex gap-3 justify-end">
                        <button
                            onClick={() => setShowSettings(false)}
                            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                        >
                            Cancel
                        </button>
                        <button
                            onClick={handleSavePreferences}
                            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                        >
                            Save Preferences
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

// Hook for checking cookie consent
export const useCookieConsent = () => {
    const [hasConsent, setHasConsent] = useState<CookiePreferences | null>(null);

    useEffect(() => {
        const saved = localStorage.getItem('cookiePreferences');
        if (saved) {
            setHasConsent(JSON.parse(saved));
        }
    }, []);

    return hasConsent;
};
