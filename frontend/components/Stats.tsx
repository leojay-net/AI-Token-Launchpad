'use client'

import { motion } from 'framer-motion'
import { TrendingUp, Users, DollarSign, Zap } from 'lucide-react'

export default function Stats() {
    const stats = [
        {
            icon: Zap,
            value: '1,247',
            label: 'Tokens Launched',
            change: '+12.5%',
            positive: true,
        },
        {
            icon: DollarSign,
            value: '$2.4M',
            label: 'Total Volume',
            change: '+28.3%',
            positive: true,
        },
        {
            icon: Users,
            value: '8,932',
            label: 'Active Users',
            change: '+15.7%',
            positive: true,
        },
        {
            icon: TrendingUp,
            value: '94.2%',
            label: 'Success Rate',
            change: '+2.1%',
            positive: true,
        },
    ]

    return (
        <section className="py-20 bg-neutral-50">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, ease: 'easeOut' }}
                    viewport={{ once: true }}
                    className="text-center mb-16"
                >
                    <h2 className="text-3xl md:text-4xl font-bold text-neutral-900 mb-4">
                        Platform Performance
                    </h2>
                    <p className="text-lg text-neutral-600 max-w-2xl mx-auto">
                        Real-time metrics showing the power of AI-driven token launches
                    </p>
                </motion.div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    {stats.map((stat, index) => (
                        <motion.div
                            key={stat.label}
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            transition={{
                                duration: 0.6,
                                delay: index * 0.1,
                                ease: 'easeOut'
                            }}
                            viewport={{ once: true }}
                            whileHover={{
                                scale: 1.02,
                                y: -2,
                                transition: { duration: 0.2 }
                            }}
                            className="stat-card group cursor-pointer"
                        >
                            <div className="flex items-center justify-between mb-4">
                                <div className="w-12 h-12 bg-gold-100 rounded-lg flex items-center justify-center group-hover:bg-gold-500 transition-colors duration-300">
                                    <stat.icon className="w-6 h-6 text-gold-600 group-hover:text-white transition-colors duration-300" />
                                </div>
                                <div className={`text-sm font-medium px-2 py-1 rounded-full ${stat.positive
                                        ? 'text-green-600 bg-green-50'
                                        : 'text-red-600 bg-red-50'
                                    }`}>
                                    {stat.change}
                                </div>
                            </div>

                            <div className="space-y-1">
                                <motion.div
                                    initial={{ scale: 0.8 }}
                                    whileInView={{ scale: 1 }}
                                    transition={{ duration: 0.5, delay: index * 0.1 + 0.3 }}
                                    viewport={{ once: true }}
                                    className="text-2xl lg:text-3xl font-bold text-neutral-900"
                                >
                                    {stat.value}
                                </motion.div>
                                <div className="text-neutral-600 font-medium">
                                    {stat.label}
                                </div>
                            </div>
                        </motion.div>
                    ))}
                </div>

                {/* Additional Metrics */}
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, delay: 0.4, ease: 'easeOut' }}
                    viewport={{ once: true }}
                    className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-6"
                >
                    <div className="text-center p-6 bg-white rounded-lg border border-neutral-200 shadow-soft">
                        <div className="text-2xl font-bold text-gold-600 mb-2">24/7</div>
                        <div className="text-neutral-600">AI Agent Monitoring</div>
                    </div>

                    <div className="text-center p-6 bg-white rounded-lg border border-neutral-200 shadow-soft">
                        <div className="text-2xl font-bold text-gold-600 mb-2">&lt; 30s</div>
                        <div className="text-neutral-600">Average Launch Time</div>
                    </div>

                    <div className="text-center p-6 bg-white rounded-lg border border-neutral-200 shadow-soft">
                        <div className="text-2xl font-bold text-gold-600 mb-2">99.9%</div>
                        <div className="text-neutral-600">Platform Uptime</div>
                    </div>
                </motion.div>
            </div>
        </section>
    )
}
