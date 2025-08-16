'use client'

import { motion } from 'framer-motion'
import { Bot, Zap, TrendingUp, Users } from 'lucide-react'

export default function Hero() {
    const aiAgents = [
        { icon: TrendingUp, label: 'Marketing', delay: 0.2 },
        { icon: Users, label: 'Community', delay: 0.4 },
        { icon: Bot, label: 'Analytics', delay: 0.6 },
        { icon: Zap, label: 'Launch', delay: 0.8 },
    ]

    return (
        <section className="relative pt-32 pb-20 overflow-hidden">
            {/* Background Elements */}
            <div className="absolute inset-0 bg-gradient-to-br from-gold-50 to-white"></div>
            <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-gold-100 rounded-full blur-3xl opacity-30 animate-float"></div>
            <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-gold-50 rounded-full blur-3xl opacity-40 animate-pulse-slow"></div>

            <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="text-center">
                    {/* Main Heading */}
                    <motion.h1
                        initial={{ opacity: 0, y: 30 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8, ease: 'easeOut' }}
                        className="text-4xl md:text-6xl lg:text-7xl font-bold leading-tight mb-6"
                    >
                        Launch Tokens with
                        <br />
                        <span className="gradient-text">AI Intelligence</span>
                    </motion.h1>

                    {/* Subtitle */}
                    <motion.p
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8, delay: 0.2, ease: 'easeOut' }}
                        className="text-xl md:text-2xl text-neutral-600 mb-12 max-w-3xl mx-auto leading-relaxed"
                    >
                        The first AI-powered launchpad platform with intelligent agents for marketing,
                        community management, and real-time analytics.
                    </motion.p>

                    {/* CTA Buttons */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8, delay: 0.4, ease: 'easeOut' }}
                        className="flex flex-col sm:flex-row gap-4 justify-center mb-16"
                    >
                        <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            className="btn-primary text-lg px-8 py-4"
                            onClick={() => {
                                const el = document.getElementById('launch')
                                el?.scrollIntoView({ behavior: 'smooth', block: 'start' })
                            }}
                        >
                            Launch Your Token
                        </motion.button>
                        <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            className="btn-secondary text-lg px-8 py-4"
                            onClick={() => {
                                const el = document.getElementById('features')
                                el?.scrollIntoView({ behavior: 'smooth', block: 'start' })
                            }}
                        >
                            Explore Features
                        </motion.button>
                    </motion.div>

                    {/* AI Agents Preview */}
                    <motion.div
                        initial={{ opacity: 0, y: 40 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 1, delay: 0.6, ease: 'easeOut' }}
                        className="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-4xl mx-auto"
                    >
                        {aiAgents.map(agent => (
                            <motion.div
                                key={agent.label}
                                initial={{ opacity: 0, scale: 0.8 }}
                                animate={{ opacity: 1, scale: 1 }}
                                transition={{
                                    duration: 0.6,
                                    delay: agent.delay,
                                    ease: 'easeOut'
                                }}
                                whileHover={{
                                    scale: 1.05,
                                    y: -5,
                                    transition: { duration: 0.2 }
                                }}
                                className="group"
                            >
                                <div className="bg-white rounded-xl p-6 shadow-soft hover:shadow-large transition-all duration-300 border border-neutral-100 hover:border-gold-200">
                                    <div className="w-12 h-12 bg-gold-100 rounded-lg flex items-center justify-center mb-4 mx-auto group-hover:bg-gold-500 transition-colors duration-300">
                                        <agent.icon className="w-6 h-6 text-gold-600 group-hover:text-white transition-colors duration-300" />
                                    </div>
                                    <h3 className="font-semibold text-neutral-900 mb-2">{agent.label} Agent</h3>
                                    <p className="text-sm text-neutral-600">
                                        AI-powered {agent.label.toLowerCase()} automation
                                    </p>
                                </div>
                            </motion.div>
                        ))}
                    </motion.div>
                </div>
            </div>
        </section>
    )
}
