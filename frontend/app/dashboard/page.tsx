'use client'

import { motion } from 'framer-motion'
import { useState } from 'react'
import Navigation from '@/components/Navigation'
import { BarChart3, TrendingUp, Users, Zap, Calendar, DollarSign } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts'
import Link from 'next/link'
import { useWalletAuth } from '@/lib/useWallet'

const mockData = {
    tokens: [
        {
            id: 1,
            name: 'Alpha Token',
            symbol: 'ALPHA',
            status: 'Active',
            launched: '2024-08-10',
            volume: '$125,430',
            holders: 1247,
            aiAgents: ['Marketing', 'Community'],
            performance: '+12.5%',
            marketCap: '$2.4M'
        },
        {
            id: 2,
            name: 'Beta Coin',
            symbol: 'BETA',
            status: 'Completed',
            launched: '2024-08-08',
            volume: '$89,320',
            holders: 892,
            aiAgents: ['Analytics', 'Launch'],
            performance: '+8.7%',
            marketCap: '$1.8M'
        },
        {
            id: 3,
            name: 'Gamma Protocol',
            symbol: 'GAMMA',
            status: 'Pre-Launch',
            launched: '2024-08-15',
            volume: '$0',
            holders: 0,
            aiAgents: ['Strategy', 'Community'],
            performance: '0%',
            marketCap: 'TBD'
        },
    ],
    analytics: [
        { date: '2024-08-01', volume: 45000, users: 120, tvl: 2100000 },
        { date: '2024-08-02', volume: 52000, users: 135, tvl: 2250000 },
        { date: '2024-08-03', volume: 48000, users: 142, tvl: 2180000 },
        { date: '2024-08-04', volume: 61000, users: 158, tvl: 2400000 },
        { date: '2024-08-05', volume: 55000, users: 171, tvl: 2350000 },
        { date: '2024-08-06', volume: 67000, users: 189, tvl: 2600000 },
        { date: '2024-08-07', volume: 72000, users: 203, tvl: 2750000 },
    ],
    proposals: [
        {
            id: 'ALP-001',
            title: 'Upgrade AI Agent Reward Distribution',
            status: 'Active',
            votes: '12.8M ALP',
            timeLeft: '3 days'
        },
        {
            id: 'ALP-002',
            title: 'Community Treasury Allocation',
            status: 'Active',
            votes: '8.2M ALP',
            timeLeft: '1 day'
        }
    ],
    aiAgents: [
        {
            name: 'Marketing Agent',
            type: 'Social Media',
            status: 'Active',
            performance: '94%',
            tokensManaged: 5
        },
        {
            name: 'Community Agent',
            type: 'Engagement',
            status: 'Active',
            performance: '89%',
            tokensManaged: 3
        },
        {
            name: 'Analytics Agent',
            type: 'Data Analysis',
            status: 'Active',
            performance: '97%',
            tokensManaged: 8
        }
    ]
}

export default function Dashboard() {
    const [activeTab, setActiveTab] = useState('overview')
    const { isConnected, isSignedIn, connectWallet, signIn } = useWalletAuth()

    const tabs = [
        { id: 'overview', label: 'Overview', icon: BarChart3 },
        { id: 'tokens', label: 'My Tokens', icon: Zap },
        { id: 'analytics', label: 'Analytics', icon: TrendingUp },
        { id: 'agents', label: 'AI Agents', icon: Users },
        { id: 'governance', label: 'Governance', icon: Calendar },
    ]

    return (
        <div className="min-h-screen bg-neutral-50">
            <Navigation />

            <div className="pt-20 pb-8">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    {/* Header */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6 }}
                        className="mb-8"
                    >
                        <h1 className="text-3xl font-bold text-neutral-900 mb-2">Dashboard</h1>
                        <p className="text-neutral-600">Manage your tokens and monitor AI agent performance</p>
                    </motion.div>

                    {/* Tabs */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6, delay: 0.1 }}
                        className="border-b border-neutral-200 mb-8"
                    >
                        <nav className="flex space-x-8 items-center">
                            {tabs.map((tab) => (
                                <button
                                    key={tab.id}
                                    onClick={() => setActiveTab(tab.id)}
                                    className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors ${activeTab === tab.id
                                        ? 'border-gold-500 text-gold-600'
                                        : 'border-transparent text-neutral-500 hover:text-neutral-700'
                                        }`}
                                >
                                    <tab.icon className="w-4 h-4" />
                                    <span>{tab.label}</span>
                                </button>
                            ))}
                            <div className="ml-auto flex items-center gap-2">
                                <button className="btn-secondary" onClick={connectWallet} disabled={isConnected}>
                                    {isConnected ? 'Wallet Connected' : 'Connect Wallet'}
                                </button>
                                <button className="btn-secondary" onClick={signIn} disabled={!isConnected || isSignedIn}>
                                    {isSignedIn ? 'Signed In' : 'Sign In (Web3)'}
                                </button>
                            </div>
                        </nav>
                    </motion.div>

                    {/* Content */}
                    <motion.div
                        key={activeTab}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.4 }}
                    >
                        {activeTab === 'overview' && (
                            <div className="space-y-6">
                                {/* Stats Grid */}
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                                    <div className="stat-card">
                                        <div className="flex items-center justify-between">
                                            <div>
                                                <p className="text-sm text-neutral-600">Active Tokens</p>
                                                <p className="text-2xl font-bold text-neutral-900">3</p>
                                            </div>
                                            <Zap className="w-8 h-8 text-gold-500" />
                                        </div>
                                    </div>

                                    <div className="stat-card">
                                        <div className="flex items-center justify-between">
                                            <div>
                                                <p className="text-sm text-neutral-600">Total TVL</p>
                                                <p className="text-2xl font-bold text-neutral-900">$2.75M</p>
                                            </div>
                                            <TrendingUp className="w-8 h-8 text-gold-500" />
                                        </div>
                                    </div>

                                    <div className="stat-card">
                                        <div className="flex items-center justify-between">
                                            <div>
                                                <p className="text-sm text-neutral-600">Protocol Revenue</p>
                                                <p className="text-2xl font-bold text-neutral-900">$47.8K</p>
                                            </div>
                                            <DollarSign className="w-8 h-8 text-gold-500" />
                                        </div>
                                    </div>

                                    <div className="stat-card">
                                        <div className="flex items-center justify-between">
                                            <div>
                                                <p className="text-sm text-neutral-600">AI Agents</p>
                                                <p className="text-2xl font-bold text-neutral-900">8</p>
                                            </div>
                                            <BarChart3 className="w-8 h-8 text-gold-500" />
                                        </div>
                                    </div>
                                </div>

                                {/* Charts */}
                                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                    <div className="card">
                                        <h3 className="text-lg font-semibold text-neutral-900 mb-4">TVL Growth</h3>
                                        <ResponsiveContainer width="100%" height={300}>
                                            <AreaChart data={mockData.analytics}>
                                                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                                                <XAxis dataKey="date" tick={false} />
                                                <YAxis />
                                                <Tooltip />
                                                <Area type="monotone" dataKey="tvl" stroke="#f5b041" fill="#f5b041" fillOpacity={0.2} />
                                            </AreaChart>
                                        </ResponsiveContainer>
                                    </div>

                                    <div className="card">
                                        <h3 className="text-lg font-semibold text-neutral-900 mb-4">Daily Volume</h3>
                                        <ResponsiveContainer width="100%" height={300}>
                                            <LineChart data={mockData.analytics}>
                                                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                                                <XAxis dataKey="date" tick={false} />
                                                <YAxis />
                                                <Tooltip />
                                                <Line type="monotone" dataKey="volume" stroke="#f5b041" strokeWidth={3} />
                                            </LineChart>
                                        </ResponsiveContainer>
                                    </div>
                                </div>
                            </div>
                        )}

                        {activeTab === 'tokens' && (
                            <div className="space-y-6">
                                <div className="flex justify-between items-center">
                                    <h2 className="text-xl font-semibold text-neutral-900">My Tokens</h2>
                                    <Link href="/#launch" className="btn-primary">Launch New Token</Link>
                                </div>

                                <div className="grid gap-6">
                                    {mockData.tokens.map((token) => (
                                        <div key={token.id} className="card">
                                            <div className="flex items-center justify-between">
                                                <div className="flex items-center space-x-4">
                                                    <div className="w-12 h-12 bg-gold-100 rounded-lg flex items-center justify-center">
                                                        <span className="font-bold text-gold-600">{token.symbol[0]}</span>
                                                    </div>
                                                    <div>
                                                        <h3 className="text-lg font-semibold text-neutral-900">{token.name}</h3>
                                                        <p className="text-neutral-600">{token.symbol}</p>
                                                    </div>
                                                </div>

                                                <div className="flex items-center space-x-6">
                                                    <div className="text-center">
                                                        <p className="text-sm text-neutral-600">Volume</p>
                                                        <p className="font-semibold">{token.volume}</p>
                                                    </div>
                                                    <div className="text-center">
                                                        <p className="text-sm text-neutral-600">Holders</p>
                                                        <p className="font-semibold">{token.holders}</p>
                                                    </div>
                                                    <div className="text-center">
                                                        <p className="text-sm text-neutral-600">Performance</p>
                                                        <p className="font-semibold">{token.performance}</p>
                                                    </div>
                                                    <div className="text-center">
                                                        <p className="text-sm text-neutral-600">Market Cap</p>
                                                        <p className="font-semibold">{token.marketCap}</p>
                                                    </div>
                                                    <div className="text-center">
                                                        <p className="text-sm text-neutral-600">Status</p>
                                                        <span className={`inline-block px-2 py-1 rounded text-xs font-medium ${token.status === 'Active'
                                                            ? 'bg-green-100 text-green-800'
                                                            : token.status === 'Pre-Launch'
                                                                ? 'bg-orange-100 text-orange-800'
                                                                : 'bg-blue-100 text-blue-800'
                                                            }`}>
                                                            {token.status}
                                                        </span>
                                                    </div>
                                                </div>
                                            </div>

                                            <div className="mt-4 flex justify-between items-center">
                                                <div className="flex space-x-2">
                                                    {token.aiAgents.map((agent, agentIndex) => (
                                                        <span key={agentIndex} className="text-xs bg-gold-100 text-gold-800 px-2 py-1 rounded">
                                                            {agent}
                                                        </span>
                                                    ))}
                                                </div>
                                                <div className="flex space-x-2">
                                                    <button className="btn-secondary text-sm">Manage</button>
                                                    <button className="btn-primary text-sm">View Details</button>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {activeTab === 'analytics' && (
                            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                <div className="card">
                                    <h3 className="text-lg font-semibold text-neutral-900 mb-4">Protocol Metrics</h3>
                                    <div className="space-y-4">
                                        <div className="flex justify-between">
                                            <span className="text-neutral-600">Total Value Locked</span>
                                            <span className="font-semibold">$2.75M</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-neutral-600">24h Volume</span>
                                            <span className="font-semibold">$72K</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-neutral-600">Active Tokens</span>
                                            <span className="font-semibold">3</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-neutral-600">Protocol Revenue</span>
                                            <span className="font-semibold">$47.8K</span>
                                        </div>
                                    </div>
                                </div>

                                <div className="card">
                                    <h3 className="text-lg font-semibold text-neutral-900 mb-4">Performance Overview</h3>
                                    <ResponsiveContainer width="100%" height={200}>
                                        <AreaChart data={mockData.analytics}>
                                            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                                            <XAxis dataKey="date" tick={false} />
                                            <YAxis />
                                            <Tooltip />
                                            <Area type="monotone" dataKey="tvl" stroke="#f5b041" fill="#f5b041" fillOpacity={0.2} />
                                        </AreaChart>
                                    </ResponsiveContainer>
                                </div>
                            </div>
                        )}

                        {activeTab === 'agents' && (
                            <div className="space-y-6">
                                <div className="flex justify-between items-center">
                                    <h2 className="text-xl font-semibold text-neutral-900">AI Agent Management</h2>
                                    <button className="btn-primary" disabled={!isSignedIn}>Deploy New Agent</button>
                                </div>

                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                    {mockData.aiAgents.map((agent, index) => (
                                        <div key={index} className="card hover-lift">
                                            <div className="flex items-center justify-between mb-4">
                                                <div>
                                                    <h3 className="font-semibold text-neutral-900">{agent.name}</h3>
                                                    <p className="text-sm text-neutral-600">{agent.type}</p>
                                                </div>
                                                <span className={`px-2 py-1 rounded text-xs font-medium ${agent.status === 'Active'
                                                    ? 'bg-green-100 text-green-800'
                                                    : 'bg-neutral-100 text-neutral-800'
                                                    }`}>
                                                    {agent.status}
                                                </span>
                                            </div>

                                            <div className="space-y-3">
                                                <div className="flex justify-between">
                                                    <span className="text-sm text-neutral-600">Performance</span>
                                                    <span className="font-medium text-green-600">{agent.performance}</span>
                                                </div>
                                                <div className="flex justify-between">
                                                    <span className="text-sm text-neutral-600">Tokens Managed</span>
                                                    <span className="font-medium">{agent.tokensManaged}</span>
                                                </div>
                                            </div>

                                            <div className="mt-4 flex space-x-2">
                                                <button className="btn-secondary text-sm flex-1" disabled={!isSignedIn}>Configure</button>
                                                <button className="btn-primary text-sm flex-1" disabled={!isSignedIn}>View Metrics</button>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {activeTab === 'governance' && (
                            <div className="space-y-6">
                                <div className="flex justify-between items-center">
                                    <h2 className="text-xl font-semibold text-neutral-900">Active Proposals</h2>
                                    <button className="btn-primary" disabled={!isSignedIn}>Create Proposal</button>
                                </div>

                                <div className="space-y-4">
                                    {mockData.proposals.map((proposal, index) => (
                                        <div key={index} className="card hover-lift">
                                            <div className="flex items-center justify-between">
                                                <div className="flex-1">
                                                    <div className="flex items-center space-x-3 mb-2">
                                                        <span className="text-sm font-mono text-neutral-500">{proposal.id}</span>
                                                        <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                                                            {proposal.status}
                                                        </span>
                                                    </div>
                                                    <h3 className="font-semibold text-neutral-900 mb-1">{proposal.title}</h3>
                                                    <p className="text-sm text-neutral-600">
                                                        {proposal.votes} votes • {proposal.timeLeft} remaining
                                                    </p>
                                                </div>
                                                <div className="flex space-x-2">
                                                    <button className="btn-secondary text-sm">View Details</button>
                                                    <button className="btn-primary text-sm" disabled={!isSignedIn}>Vote</button>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>

                                <div className="card">
                                    <h3 className="text-lg font-semibold text-neutral-900 mb-4">Your Voting Power</h3>
                                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                        <div className="text-center">
                                            <p className="text-2xl font-bold text-neutral-900">24,500</p>
                                            <p className="text-sm text-neutral-600">ALP Tokens</p>
                                        </div>
                                        <div className="text-center">
                                            <p className="text-2xl font-bold text-neutral-900">0.12%</p>
                                            <p className="text-sm text-neutral-600">Voting Power</p>
                                        </div>
                                        <div className="text-center">
                                            <p className="text-2xl font-bold text-neutral-900">7</p>
                                            <p className="text-sm text-neutral-600">Votes Cast</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}
                    </motion.div>
                </div>
            </div>
        </div>
    )
}
