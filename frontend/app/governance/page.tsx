'use client'

import { motion } from 'framer-motion'
import { Vote, Users, DollarSign, Calendar, ExternalLink, Info } from 'lucide-react'
import Navigation from '@/components/Navigation'

const governanceStats = [
    { label: 'Total ALP Supply', value: '100M', icon: DollarSign },
    { label: 'Active Voters', value: '4,329', icon: Users },
    { label: 'Proposals Created', value: '47', icon: Vote },
    { label: 'Days Until Next Epoch', value: '12', icon: Calendar },
]

const activeProposals = [
    {
        id: 'ALP-001',
        title: 'Upgrade AI Agent Reward Distribution Mechanism',
        description: 'Implement a more efficient reward system for AI agents based on performance metrics and community feedback.',
        status: 'Active',
        endsIn: '3 days',
        votesFor: '12.8M ALP',
        votesAgainst: '2.1M ALP',
        participation: '34%',
        author: 'core_team',
        created: '5 days ago'
    },
    {
        id: 'ALP-002',
        title: 'Community Treasury Allocation for Q4 2025',
        description: 'Allocate 5M ALP tokens from community treasury for developer grants, marketing initiatives, and ecosystem growth.',
        status: 'Active',
        endsIn: '1 day',
        votesFor: '8.2M ALP',
        votesAgainst: '1.9M ALP',
        participation: '28%',
        author: 'governance_committee',
        created: '7 days ago'
    },
    {
        id: 'ALP-003',
        title: 'Integration with Additional DeFi Protocols',
        description: 'Expand AI LaunchPad integration to support launches on Arbitrum, Optimism, and Polygon networks.',
        status: 'Draft',
        endsIn: 'Not started',
        votesFor: '0 ALP',
        votesAgainst: '0 ALP',
        participation: '0%',
        author: 'community_builder',
        created: '2 days ago'
    },
]

const recentDecisions = [
    {
        id: 'ALP-047',
        title: 'Fee Structure Optimization',
        result: 'Passed',
        finalVotes: '89% For, 11% Against',
        implemented: '✅ Implemented'
    },
    {
        id: 'ALP-046',
        title: 'AI Agent Performance Standards',
        result: 'Passed',
        finalVotes: '76% For, 24% Against',
        implemented: '✅ Implemented'
    },
    {
        id: 'ALP-045',
        title: 'Community Moderator Elections',
        result: 'Passed',
        finalVotes: '92% For, 8% Against',
        implemented: '✅ Implemented'
    },
]

export default function GovernancePage() {
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
                            Protocol <span className="gradient-text">Governance</span>
                        </h1>
                        <p className="text-xl text-neutral-600 max-w-3xl mx-auto mb-8">
                            Shape the future of AI LaunchPad through decentralized governance. Every ALP token holder has a voice in protocol decisions.
                        </p>

                        <div className="flex justify-center space-x-4">
                            <button className="btn-primary flex items-center space-x-2">
                                <Vote className="w-4 h-4" />
                                <span>Create Proposal</span>
                            </button>
                            <a href="#" className="btn-secondary flex items-center space-x-2">
                                <ExternalLink className="w-4 h-4" />
                                <span>Governance Forum</span>
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
                        {governanceStats.map((stat, index) => (
                            <div key={stat.label} className="stat-card text-center">
                                <stat.icon className="w-8 h-8 text-gold-500 mx-auto mb-3" />
                                <p className="text-2xl font-bold text-neutral-900 mb-1">{stat.value}</p>
                                <p className="text-sm text-neutral-600">{stat.label}</p>
                            </div>
                        ))}
                    </motion.div>

                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                        {/* Active Proposals */}
                        <motion.div
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ duration: 0.6, delay: 0.3 }}
                            className="lg:col-span-2 space-y-8"
                        >
                            <div className="flex items-center justify-between">
                                <h2 className="text-2xl font-bold text-neutral-900">Active Proposals</h2>
                                <span className="text-sm text-neutral-600">{activeProposals.filter(p => p.status === 'Active').length} active</span>
                            </div>

                            <div className="space-y-6">
                                {activeProposals.map((proposal) => (
                                    <div key={proposal.id} className="card hover-lift">
                                        <div className="flex items-start justify-between mb-4">
                                            <div className="flex-1">
                                                <div className="flex items-center gap-3 mb-2">
                                                    <span className="font-mono text-neutral-500 text-sm">{proposal.id}</span>
                                                    <span className={`px-2 py-1 text-xs rounded font-medium ${proposal.status === 'Active'
                                                            ? 'bg-green-100 text-green-800'
                                                            : 'bg-orange-100 text-orange-800'
                                                        }`}>
                                                        {proposal.status}
                                                    </span>
                                                    <span className="text-xs text-neutral-500">by {proposal.author} • {proposal.created}</span>
                                                </div>
                                                <h3 className="font-semibold text-neutral-900 text-lg mb-3">{proposal.title}</h3>
                                                <p className="text-neutral-600 text-sm mb-4">{proposal.description}</p>
                                            </div>
                                        </div>

                                        {proposal.status === 'Active' && (
                                            <div className="bg-neutral-50 rounded-lg p-4 mb-4">
                                                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                                                    <div>
                                                        <p className="text-neutral-600">Ends In</p>
                                                        <p className="font-semibold text-neutral-900">{proposal.endsIn}</p>
                                                    </div>
                                                    <div>
                                                        <p className="text-neutral-600">For</p>
                                                        <p className="font-semibold text-green-600">{proposal.votesFor}</p>
                                                    </div>
                                                    <div>
                                                        <p className="text-neutral-600">Against</p>
                                                        <p className="font-semibold text-red-600">{proposal.votesAgainst}</p>
                                                    </div>
                                                    <div>
                                                        <p className="text-neutral-600">Participation</p>
                                                        <p className="font-semibold text-neutral-900">{proposal.participation}</p>
                                                    </div>
                                                </div>
                                            </div>
                                        )}

                                        <div className="flex items-center justify-between">
                                            <div className="flex space-x-2">
                                                <button className="btn-secondary text-sm">View Details</button>
                                                {proposal.status === 'Active' && (
                                                    <>
                                                        <button className="btn-primary text-sm bg-green-600 hover:bg-green-700">Vote For</button>
                                                        <button className="btn-primary text-sm bg-red-600 hover:bg-red-700">Vote Against</button>
                                                    </>
                                                )}
                                            </div>
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
                            {/* Your Voting Power */}
                            <div className="card">
                                <h3 className="text-lg font-semibold text-neutral-900 mb-4">Your Voting Power</h3>
                                <div className="text-center space-y-3">
                                    <div>
                                        <p className="text-2xl font-bold text-neutral-900">24,500</p>
                                        <p className="text-sm text-neutral-600">ALP Tokens</p>
                                    </div>
                                    <div>
                                        <p className="text-lg font-semibold text-gold-600">0.12%</p>
                                        <p className="text-sm text-neutral-600">of Total Supply</p>
                                    </div>
                                    <div className="pt-2 border-t border-neutral-200">
                                        <p className="text-sm text-neutral-600">Proposals Voted: <span className="font-semibold">7</span></p>
                                    </div>
                                </div>
                                <button className="w-full btn-primary mt-4 text-sm">Delegate Voting Power</button>
                            </div>

                            {/* Recent Decisions */}
                            <div className="card">
                                <h3 className="text-lg font-semibold text-neutral-900 mb-4">Recent Decisions</h3>
                                <div className="space-y-3">
                                    {recentDecisions.map((decision, index) => (
                                        <div key={index} className="border-l-2 border-green-500 pl-3">
                                            <div className="flex items-center justify-between mb-1">
                                                <h4 className="font-medium text-neutral-900 text-sm">{decision.id}</h4>
                                                <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                                                    {decision.result}
                                                </span>
                                            </div>
                                            <p className="text-xs text-neutral-700 font-medium mb-1">{decision.title}</p>
                                            <p className="text-xs text-neutral-600 mb-1">{decision.finalVotes}</p>
                                            <p className="text-xs text-green-600">{decision.implemented}</p>
                                        </div>
                                    ))}
                                </div>
                                <button className="w-full btn-secondary mt-4 text-sm">View All Decisions</button>
                            </div>

                            {/* How to Participate */}
                            <div className="card">
                                <h3 className="text-lg font-semibold text-neutral-900 mb-3">How to Participate</h3>
                                <div className="space-y-2 text-sm text-neutral-600">
                                    <div className="flex items-start space-x-2">
                                        <Info className="w-4 h-4 text-gold-500 mt-0.5 flex-shrink-0" />
                                        <p>Hold ALP tokens to gain voting power</p>
                                    </div>
                                    <div className="flex items-start space-x-2">
                                        <Info className="w-4 h-4 text-gold-500 mt-0.5 flex-shrink-0" />
                                        <p>Create proposals for protocol improvements</p>
                                    </div>
                                    <div className="flex items-start space-x-2">
                                        <Info className="w-4 h-4 text-gold-500 mt-0.5 flex-shrink-0" />
                                        <p>Delegate to trusted community members</p>
                                    </div>
                                </div>
                                <a href="#" className="text-sm text-gold-600 hover:text-gold-700 font-medium block mt-3">
                                    Learn More →
                                </a>
                            </div>
                        </motion.div>
                    </div>
                </div>
            </main>
        </div>
    )
}
