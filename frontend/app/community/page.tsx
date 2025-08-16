'use client'

import { motion } from 'framer-motion'
import { Users, MessageSquare, Trophy, Calendar, ExternalLink, Twitter, Github, MessageCircle } from 'lucide-react'
import Navigation from '@/components/Navigation'

const communityStats = [
    { label: 'Active Members', value: '12,847', icon: Users },
    { label: 'Tokens Launched', value: '342', icon: Trophy },
    { label: 'Discussions', value: '1,628', icon: MessageSquare },
    { label: 'Events This Month', value: '8', icon: Calendar },
]

const featuredPosts = [
    {
        title: 'How I launched my first AI-powered token',
        author: 'crypto_builder_99',
        replies: 23,
        timeAgo: '2 hours ago',
        category: 'Success Stories'
    },
    {
        title: 'Best practices for AI agent configuration',
        author: 'ai_expert',
        replies: 41,
        timeAgo: '4 hours ago',
        category: 'Tutorial'
    },
    {
        title: 'Weekly community call recap - August 2025',
        author: 'team_ai_launchpad',
        replies: 67,
        timeAgo: '1 day ago',
        category: 'Announcements'
    },
]

const upcomingEvents = [
    {
        title: 'Community AMA with Core Team',
        date: 'Aug 20, 2025',
        time: '2:00 PM UTC',
        type: 'Virtual'
    },
    {
        title: 'Token Launch Workshop',
        date: 'Aug 25, 2025',
        time: '6:00 PM UTC',
        type: 'Virtual'
    },
    {
        title: 'AI Agent Deep Dive Session',
        date: 'Sep 2, 2025',
        time: '4:00 PM UTC',
        type: 'Virtual'
    },
]

export default function CommunityPage() {
    return (
        <div className="min-h-screen bg-neutral-50">
            <Navigation />

            <main className="pt-20 pb-16">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    {/* Hero Section */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6 }}
                        className="text-center mb-16"
                    >
                        <h1 className="text-4xl md:text-5xl font-bold text-neutral-900 mb-4">
                            Join Our <span className="gradient-text">Community</span>
                        </h1>
                        <p className="text-xl text-neutral-600 max-w-3xl mx-auto mb-8">
                            Connect with builders, share experiences, and learn from the best minds in AI-powered token launches
                        </p>

                        {/* Social Links */}
                        <div className="flex justify-center space-x-4 mb-12">
                            <a href="#" className="btn-secondary flex items-center space-x-2">
                                <MessageCircle className="w-4 h-4" />
                                <span>Discord</span>
                                <ExternalLink className="w-3 h-3" />
                            </a>
                            <a href="#" className="btn-secondary flex items-center space-x-2">
                                <Twitter className="w-4 h-4" />
                                <span>Twitter</span>
                                <ExternalLink className="w-3 h-3" />
                            </a>
                            <a href="#" className="btn-secondary flex items-center space-x-2">
                                <Github className="w-4 h-4" />
                                <span>GitHub</span>
                                <ExternalLink className="w-3 h-3" />
                            </a>
                        </div>
                    </motion.div>

                    {/* Stats Grid */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6, delay: 0.2 }}
                        className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-16"
                    >
                        {communityStats.map((stat, index) => (
                            <div key={stat.label} className="stat-card text-center">
                                <stat.icon className="w-8 h-8 text-gold-500 mx-auto mb-3" />
                                <p className="text-2xl font-bold text-neutral-900 mb-1">{stat.value}</p>
                                <p className="text-sm text-neutral-600">{stat.label}</p>
                            </div>
                        ))}
                    </motion.div>

                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                        {/* Featured Discussions */}
                        <motion.div
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ duration: 0.6, delay: 0.3 }}
                            className="lg:col-span-2 space-y-6"
                        >
                            <div className="flex items-center justify-between">
                                <h2 className="text-2xl font-bold text-neutral-900">Featured Discussions</h2>
                                <button className="btn-primary">View All Posts</button>
                            </div>

                            <div className="space-y-4">
                                {featuredPosts.map((post, index) => (
                                    <div key={index} className="card hover-lift">
                                        <div className="flex items-start justify-between">
                                            <div className="flex-1">
                                                <div className="flex items-center space-x-2 mb-2">
                                                    <span className="text-xs bg-gold-100 text-gold-800 px-2 py-1 rounded">
                                                        {post.category}
                                                    </span>
                                                    <span className="text-xs text-neutral-500">{post.timeAgo}</span>
                                                </div>
                                                <h3 className="font-semibold text-neutral-900 mb-2 hover:text-gold-600 cursor-pointer">
                                                    {post.title}
                                                </h3>
                                                <div className="flex items-center space-x-4 text-sm text-neutral-600">
                                                    <span>by {post.author}</span>
                                                    <span>{post.replies} replies</span>
                                                </div>
                                            </div>
                                            <MessageSquare className="w-5 h-5 text-neutral-400" />
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </motion.div>

                        {/* Sidebar */}
                        <motion.div
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ duration: 0.6, delay: 0.4 }}
                            className="space-y-8"
                        >
                            {/* Upcoming Events */}
                            <div className="card">
                                <h3 className="text-lg font-semibold text-neutral-900 mb-4">Upcoming Events</h3>
                                <div className="space-y-4">
                                    {upcomingEvents.map((event, index) => (
                                        <div key={index} className="border-l-2 border-gold-500 pl-4">
                                            <h4 className="font-medium text-neutral-900 text-sm">{event.title}</h4>
                                            <p className="text-xs text-neutral-600 mt-1">
                                                {event.date} • {event.time}
                                            </p>
                                            <span className="text-xs bg-neutral-100 text-neutral-700 px-2 py-1 rounded mt-2 inline-block">
                                                {event.type}
                                            </span>
                                        </div>
                                    ))}
                                </div>
                                <button className="w-full btn-secondary mt-4 text-sm">View All Events</button>
                            </div>

                            {/* Quick Actions */}
                            <div className="card">
                                <h3 className="text-lg font-semibold text-neutral-900 mb-4">Quick Actions</h3>
                                <div className="space-y-2">
                                    <button className="w-full btn-secondary text-sm">Start New Discussion</button>
                                    <button className="w-full btn-secondary text-sm">Share Your Launch</button>
                                    <button className="w-full btn-secondary text-sm">Report an Issue</button>
                                    <button className="w-full btn-secondary text-sm">Suggest Feature</button>
                                </div>
                            </div>

                            {/* Community Guidelines */}
                            <div className="card">
                                <h3 className="text-lg font-semibold text-neutral-900 mb-2">Community Guidelines</h3>
                                <p className="text-sm text-neutral-600 mb-3">
                                    Help us maintain a welcoming and productive environment for everyone.
                                </p>
                                <a href="#" className="text-sm text-gold-600 hover:text-gold-700 font-medium">
                                    Read Guidelines →
                                </a>
                            </div>
                        </motion.div>
                    </div>
                </div>
            </main>
        </div>
    )
}
