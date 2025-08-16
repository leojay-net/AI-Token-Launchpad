'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { usePathname } from 'next/navigation'
import Link from 'next/link'
import { Menu, X, Zap, Users, Vote, BookOpen, Code, Home } from 'lucide-react'
import { useWalletAuth } from '@/lib/useWallet'

export default function Navigation() {
    const [isMenuOpen, setIsMenuOpen] = useState(false)
    const pathname = usePathname()
    const { isConnected, connectWallet, disconnect } = useWalletAuth()

    const navItems = [
        { name: 'Home', href: '/', icon: Home },
        { name: 'Dashboard', href: '/dashboard', icon: Zap },
        { name: 'Governance', href: '/governance', icon: Vote },
        { name: 'Community', href: '/community', icon: Users },
        { name: 'Developers', href: '/developers', icon: Code },
        { name: 'Docs', href: '/docs', icon: BookOpen },
    ]

    return (
        <motion.nav
            initial={{ y: -100, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.6, ease: 'easeOut' }}
            className="fixed top-0 left-0 right-0 z-50 glass-effect"
        >
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between items-center h-16">
                    {/* Logo */}
                    <Link href="/">
                        <motion.div
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            className="flex items-center space-x-2 cursor-pointer"
                        >
                            <div className="w-8 h-8 bg-gold-500 rounded-lg flex items-center justify-center">
                                <Zap className="w-5 h-5 text-white" />
                            </div>
                            <span className="text-xl font-bold gradient-text">AI LaunchPad</span>
                        </motion.div>
                    </Link>

                    {/* Desktop Navigation */}
                    <div className="hidden md:flex items-center space-x-8">
                        {navItems.map((item, index) => (
                            <Link key={item.name} href={item.href}>
                                <motion.div
                                    initial={{ y: -20, opacity: 0 }}
                                    animate={{ y: 0, opacity: 1 }}
                                    transition={{ delay: 0.1 * index, duration: 0.5 }}
                                    className={`flex items-center space-x-2 transition-colors duration-200 cursor-pointer ${pathname === item.href
                                        ? 'text-gold-600'
                                        : 'text-neutral-600 hover:text-gold-600'
                                        }`}
                                    whileHover={{ y: -2 }}
                                >
                                    <item.icon className="w-4 h-4" />
                                    <span className="font-medium">{item.name}</span>
                                </motion.div>
                            </Link>
                        ))}
                    </div>

                    {/* Connect Wallet Button */}
                    <div className="hidden md:flex items-center space-x-3">
                        {!isConnected ? (
                            <motion.button
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                                className="btn-primary"
                                onClick={connectWallet}
                            >
                                Connect Wallet
                            </motion.button>
                        ) : (
                            <>
                                <motion.div
                                    initial={{ opacity: 0, scale: 0.8 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    className="px-3 py-1 bg-green-100 text-green-800 text-sm rounded-full font-medium"
                                >
                                    Wallet Connected
                                </motion.div>
                                <motion.button
                                    whileHover={{ scale: 1.05 }}
                                    whileTap={{ scale: 0.95 }}
                                    className="btn-secondary"
                                    onClick={disconnect}
                                >
                                    Disconnect
                                </motion.button>
                            </>
                        )}
                    </div>

                    {/* Mobile Menu Button */}
                    <motion.button
                        whileTap={{ scale: 0.95 }}
                        onClick={() => setIsMenuOpen(!isMenuOpen)}
                        className="md:hidden p-2 rounded-lg hover:bg-neutral-100 transition-colors"
                    >
                        {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
                    </motion.button>
                </div>
            </div>

            {/* Mobile Menu */}
            {isMenuOpen && (
                <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    className="md:hidden bg-white border-t border-neutral-200"
                >
                    <div className="px-4 py-4 space-y-3">
                        {navItems.map((item) => (
                            <Link
                                key={item.name}
                                href={item.href}
                                className={`flex items-center space-x-3 p-3 rounded-lg transition-colors ${pathname === item.href
                                    ? 'bg-gold-50 text-gold-600'
                                    : 'hover:bg-neutral-50'
                                    }`}
                                onClick={() => setIsMenuOpen(false)}
                            >
                                <item.icon className="w-5 h-5 text-gold-500" />
                                <span className="font-medium">{item.name}</span>
                            </Link>
                        ))}
                        <div className="pt-4 border-t border-neutral-200">
                            <button
                                className="w-full btn-primary mb-2"
                                onClick={() => {
                                    connectWallet()
                                    setIsMenuOpen(false)
                                }}
                                disabled={isConnected}
                            >
                                {isConnected ? 'Wallet Connected' : 'Connect Wallet'}
                            </button>
                            {isConnected && (
                                <button
                                    className="w-full btn-secondary"
                                    onClick={() => {
                                        disconnect()
                                        setIsMenuOpen(false)
                                    }}
                                >
                                    Disconnect
                                </button>
                            )}
                        </div>
                    </div>
                </motion.div>
            )}
        </motion.nav>
    )
}
