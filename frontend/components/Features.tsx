'use client'

import { motion } from 'framer-motion'
import { Bot, Zap, Users, Shield, Clock, Target } from 'lucide-react'

export default function Features() {
    const features = [
        {
            icon: Bot,
            title: 'AI Marketing Agents',
            description: 'Intelligent marketing automation that analyzes trends, optimizes campaigns, and maximizes token visibility across platforms.',
            benefits: ['Trend Analysis', 'Campaign Optimization', 'Multi-platform Reach']
        },
        {
            icon: Users,
            title: 'Community Management',
            description: 'AI-powered community engagement that moderates discussions, answers questions, and builds strong token communities.',
            benefits: ['24/7 Moderation', 'Instant Support', 'Engagement Analytics']
        },
        {
            icon: Shield,
            title: 'Security First',
            description: 'Built-in security protocols with smart contract auditing and real-time threat monitoring.',
            benefits: ['Contract Audits', 'Threat Detection', 'Secure Protocols']
        },
        {
            icon: Target,
            title: 'Strategic Planning',
            description: 'AI-driven strategic planning that creates customized roadmaps for successful token launches.',
            benefits: ['Custom Roadmaps', 'Strategic Insights', 'Goal Tracking']
        },
    ]

    return (
        <section id="features" className="py-20 bg-white">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                {/* Section Header */}
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, ease: 'easeOut' }}
                    viewport={{ once: true }}
                    className="text-center mb-16"
                >
                    <h2 className="text-3xl md:text-4xl font-bold text-neutral-900 mb-6">
                        Powerful AI Features
                    </h2>
                    <p className="text-lg text-neutral-600 max-w-3xl mx-auto leading-relaxed">
                        Our AI agents work around the clock to ensure your token launch is successful,
                        handling everything from marketing to community management with intelligent automation.
                    </p>
                </motion.div>

                {/* Features Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                    {features.map((feature, index) => (
                        <motion.div
                            key={feature.title}
                            initial={{ opacity: 0, y: 30 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            transition={{
                                duration: 0.6,
                                delay: index * 0.1,
                                ease: 'easeOut'
                            }}
                            viewport={{ once: true }}
                            whileHover={{
                                y: -5,
                                transition: { duration: 0.3 }
                            }}
                            className="group"
                        >
                            <div className="card h-full hover:border-gold-200 group-hover:shadow-gold transition-all duration-300">
                                {/* Icon */}
                                <div className="w-14 h-14 bg-gold-100 rounded-xl flex items-center justify-center mb-6 group-hover:bg-gold-500 transition-colors duration-300">
                                    <feature.icon className="w-7 h-7 text-gold-600 group-hover:text-white transition-colors duration-300" />
                                </div>

                                {/* Content */}
                                <div className="space-y-4">
                                    <h3 className="text-xl font-bold text-neutral-900 group-hover:text-gold-600 transition-colors duration-300">
                                        {feature.title}
                                    </h3>

                                    <p className="text-neutral-600 leading-relaxed">
                                        {feature.description}
                                    </p>

                                    {/* Benefits List */}
                                    <div className="space-y-2">
                                        {feature.benefits.map((benefit, benefitIndex) => (
                                            <motion.div
                                                key={benefit}
                                                initial={{ opacity: 0, x: -10 }}
                                                whileInView={{ opacity: 1, x: 0 }}
                                                transition={{
                                                    duration: 0.4,
                                                    delay: index * 0.1 + benefitIndex * 0.1 + 0.3
                                                }}
                                                viewport={{ once: true }}
                                                className="flex items-center space-x-2"
                                            >
                                                <div className="w-1.5 h-1.5 bg-gold-500 rounded-full"></div>
                                                <span className="text-sm text-neutral-700 font-medium">{benefit}</span>
                                            </motion.div>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        </motion.div>
                    ))}
                </div>

                {/* Bottom CTA */}
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, delay: 0.6, ease: 'easeOut' }}
                    viewport={{ once: true }}
                    className="text-center mt-16"
                >
                    <div className="bg-gold-50 rounded-2xl p-8 md:p-12">
                        <div className="flex items-center justify-center mb-6">
                            <Clock className="w-8 h-8 text-gold-600 mr-3" />
                            <span className="text-lg font-semibold text-neutral-900">
                                Ready to launch in minutes, not days
                            </span>
                        </div>

                        <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            className="btn-primary text-lg px-8 py-4"
                            onClick={() => {
                                const el = document.getElementById('launch')
                                el?.scrollIntoView({ behavior: 'smooth', block: 'start' })
                            }}
                        >
                            Start Your AI-Powered Launch
                        </motion.button>
                    </div>
                </motion.div>
            </div>
        </section>
    )
}
