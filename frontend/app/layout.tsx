import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Providers } from './providers'
import { Toaster } from 'react-hot-toast'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
    title: 'AI LaunchPad - Intelligent Token Launch Platform',
    description: 'Launch tokens with AI-powered agents for marketing, community engagement, and analytics.',
}

export default function RootLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <html lang="en">
            <body className={inter.className}>
                <Providers>
                    {children}
                    <Toaster
                        position="top-right"
                        toastOptions={{
                            duration: 4000,
                            style: {
                                background: '#ffffff',
                                color: '#171717',
                                border: '1px solid #e5e5e5',
                                borderRadius: '8px',
                                boxShadow: '0 4px 12px 0 rgba(0, 0, 0, 0.08)',
                            },
                            success: {
                                iconTheme: {
                                    primary: '#f5b041',
                                    secondary: '#ffffff',
                                },
                            },
                        }}
                    />
                </Providers>
            </body>
        </html>
    )
}
