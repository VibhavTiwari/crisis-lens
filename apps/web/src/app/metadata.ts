import type { Metadata } from 'next'

export const metadata: Metadata = {
    metadataBase: new URL('https://crisislen.example.com'),
    title: {
        default: 'CrisisLens - AI-Powered Crisis Intelligence Platform',
        template: '%s | CrisisLens'
    },
    description: 'Real-time verification and analysis of crisis information using advanced AI and machine learning. Automated fact-checking, risk scoring, and multi-language advisory dissemination.',
    keywords: ['crisis management', 'AI verification', 'fact-checking', 'disaster response', 'intelligence platform', 'misinformation detection'],
    authors: [{ name: 'CrisisLens Team' }],
    creator: 'CrisisLens',
    publisher: 'CrisisLens',
    formatDetection: {
        email: false,
        address: false,
        telephone: false,
    },
    openGraph: {
        type: 'website',
        locale: 'en_US',
        url: 'https://crisislen.example.com',
        siteName: 'CrisisLens',
        title: 'CrisisLens - AI-Powered Crisis Intelligence',
        description: 'Real-time crisis verification and intelligence platform powered by advanced AI',
        images: [
            {
                url: '/og-image.png',
                width: 1200,
                height: 630,
                alt: 'CrisisLens Platform',
            },
        ],
    },
    twitter: {
        card: 'summary_large_image',
        title: 'CrisisLens - AI-Powered Crisis Intelligence',
        description: 'Real-time crisis verification and intelligence platform',
        creator: '@CrisisLensAI',
        images: ['/twitter-image.png'],
    },
    robots: {
        index: true,
        follow: true,
        googleBot: {
            index: true,
            follow: true,
            'max-video-preview': -1,
            'max-image-preview': 'large',
            'max-snippet': -1,
        },
    },
    icons: {
        icon: '/favicon.ico',
        shortcut: '/favicon-16x16.png',
        apple: '/apple-touch-icon.png',
    },
    manifest: '/site.webmanifest',
}
