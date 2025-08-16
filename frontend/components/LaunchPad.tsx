'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { Bot, TrendingUp, Users, BarChart3, Plus, Info } from 'lucide-react'
import { contractService } from '../lib/contracts'
import { FEES } from '../lib/constants'
import { createLaunch, attachTx, web3GetNonce, web3Verify } from '../lib/api'
import { ethers } from 'ethers'

export default function LaunchPad() {
    const router = useRouter()
    const [tokenName, setTokenName] = useState('')
    const [tokenSymbol, setTokenSymbol] = useState('')
    const [totalSupply, setTotalSupply] = useState('')
    const [selectedAgents, setSelectedAgents] = useState<number[]>([])
    const [apiToken, setApiToken] = useState<string | null>(null)
    const [wallet, setWallet] = useState<string | null>(null)
    const [busy, setBusy] = useState(false)
    const [status, setStatus] = useState<string | null>(null)

    useEffect(() => {
        const t = typeof window !== 'undefined' ? localStorage.getItem('authToken') : null
        if (t) setApiToken(t)
        const detectWallet = async () => {
            try {
                if (typeof window !== 'undefined' && window.ethereum) {
                    const res = await window.ethereum.request({ method: 'eth_accounts' })
                    const accounts = (res as string[]) || []
                    if (accounts.length > 0) setWallet(accounts[0])
                }
            } catch {
                // ignore
            }
        }
        detectWallet()
    }, [])

    const aiAgents = [
        { id: 1, name: 'Marketing Agent', icon: TrendingUp, description: 'AI-powered marketing campaigns and trend analysis', fee: 0.005, features: ['Social Media Management', 'Trend Analysis', 'Campaign Optimization'] },
        { id: 2, name: 'Community Agent', icon: Users, description: '24/7 community engagement and moderation', fee: 0.005, features: ['Community Moderation', 'User Engagement', 'Support Automation'] },
        { id: 4, name: 'Analytics Agent', icon: BarChart3, description: 'Real-time analytics and performance tracking', fee: 0.005, features: ['Performance Metrics', 'Predictive Analysis', 'Custom Reports'] },
        { id: 8, name: 'Launch Agent', icon: Bot, description: 'Automated launch coordination and optimization', fee: 0.005, features: ['Launch Timing', 'Price Optimization', 'Deployment Automation'] },
    ]

    const platformFee = FEES.PLATFORM_FEE
    const totalAgentFees = selectedAgents.length * FEES.AI_SERVICE_FEE_PER_AGENT
    const totalFee = platformFee + totalAgentFees

    const toggleAgent = (agentId: number) => {
        setSelectedAgents(prev => prev.includes(agentId) ? prev.filter(id => id !== agentId) : [...prev, agentId])
    }

    const ensureAuth = async () => {
        if (apiToken) return apiToken
        if (!wallet) throw new Error('Please connect your wallet first')
        const { nonce } = await web3GetNonce(wallet)
        if (!window.ethereum) throw new Error('No wallet provider')
        const provider = new ethers.BrowserProvider(window.ethereum)
        const signer = await provider.getSigner()
        const signature = await signer.signMessage(`AI-Launch-Pad login: ${nonce}`)
        const { token } = await web3Verify(wallet, signature)
        setApiToken(token)
        if (typeof window !== 'undefined') localStorage.setItem('authToken', token)
        return token
    }

    const ensureWallet = async () => {
        if (wallet) return wallet
        const addr = await contractService.connectWallet()
        if (!addr) throw new Error('Wallet connection failed')
        setWallet(addr)
        return addr
    }

    const handleLaunch = async () => {
        try {
            setBusy(true)
            if (!wallet) { setStatus('Please connect your wallet first'); return }
            if (!apiToken) { setStatus('Please sign in (Web3) first'); return }
            const token = apiToken
            setStatus('Creating launch (backend)...')
            const created = await createLaunch(token, { name: tokenName, symbol: tokenSymbol, total_supply: totalSupply, network: 'CORE' })
            setStatus('Creating token on-chain...')
            const { success, txHash, tokenAddress, error } = await contractService.createToken(tokenName, tokenSymbol, totalSupply, selectedAgents)
            if (!success || !txHash) throw new Error(error || 'Failed to create token')
            setStatus('Attaching transaction to launch...')
            await attachTx(token, created.id, txHash, tokenAddress)
            setStatus('Launch linked successfully! Redirecting to dashboard...')
            const params = new URLSearchParams()
            if (txHash) params.set('tx', txHash)
            if (tokenAddress) params.set('addr', tokenAddress)
            // Redirect to dashboard as requested
            router.push(`/dashboard`)
        } catch (e: unknown) {
            const msg = e instanceof Error ? e.message : 'Failed to launch'
            setStatus(msg)
        } finally {
            setBusy(false)
        }
    }

    return (
        <section id="launch" className="py-20 bg-neutral-50">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <motion.div initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} transition={{ duration: 0.8, ease: 'easeOut' }} viewport={{ once: true }} className="text-center mb-16">
                    <h2 className="text-3xl md:text-4xl font-bold text-neutral-900 mb-6">Launch Your Token</h2>
                    <p className="text-lg text-neutral-600 max-w-2xl mx-auto">Configure your token parameters and select AI agents to power your launch</p>
                </motion.div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
                    <motion.div initial={{ opacity: 0, x: -30 }} whileInView={{ opacity: 1, x: 0 }} transition={{ duration: 0.8, ease: 'easeOut' }} viewport={{ once: true }} className="space-y-6">
                        <div className="card">
                            <h3 className="text-xl font-bold text-neutral-900 mb-6">Token Details</h3>
                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-neutral-700 mb-2">Token Name</label>
                                    <input type="text" value={tokenName} onChange={(e) => setTokenName(e.target.value)} placeholder="e.g., My Awesome Token" className="input-field" />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-neutral-700 mb-2">Token Symbol</label>
                                    <input type="text" value={tokenSymbol} onChange={(e) => setTokenSymbol(e.target.value.toUpperCase())} placeholder="e.g., MAT" className="input-field" maxLength={10} />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-neutral-700 mb-2">Total Supply</label>
                                    <input type="number" value={totalSupply} onChange={(e) => setTotalSupply(e.target.value)} placeholder="e.g., 1000000" className="input-field" min="1" max="1000000000" />
                                    <p className="text-xs text-neutral-500 mt-1">Maximum supply: 1,000,000,000 tokens</p>
                                </div>
                            </div>
                        </div>

                        <div className="card">
                            <h3 className="text-xl font-bold text-neutral-900 mb-4">Wallet & Auth</h3>
                            <div className="space-y-2">
                                <p className="text-sm text-neutral-700">Wallet: {wallet ? wallet : 'not connected'}</p>
                                <p className="text-xs text-neutral-500">Token: {apiToken ? '✅ stored' : '❌ not set'}</p>
                            </div>
                        </div>

                        <div className="card">
                            <h3 className="text-xl font-bold text-neutral-900 mb-4">Fee Summary</h3>
                            <div className="space-y-3">
                                <div className="flex justify-between items-center"><span className="text-neutral-600">Platform Fee</span><span className="font-medium">{platformFee} CORE</span></div>
                                <div className="flex justify-between items-center"><span className="text-neutral-600">AI Agent Fees</span><span className="font-medium">{totalAgentFees.toFixed(3)} CORE</span></div>
                                <div className="border-t border-neutral-200 pt-3">
                                    <div className="flex justify-between items-center"><span className="font-semibold text-neutral-900">Total Fee</span><span className="font-bold text-gold-600">{totalFee.toFixed(3)} CORE</span></div>
                                    <div className="mt-4 flex gap-3">
                                        <button className="btn-secondary" onClick={async () => { try { setBusy(true); setStatus('Connecting wallet...'); const addr = await ensureWallet(); setStatus(`Wallet connected: ${addr.slice(0, 6)}...${addr.slice(-4)}`) } catch (e: unknown) { const msg = e instanceof Error ? e.message : 'Wallet connect failed'; setStatus(msg) } finally { setBusy(false) } }} disabled={!!wallet}>{wallet ? 'Wallet Connected' : 'Connect Wallet'}</button>
                                        <button className="btn-secondary" onClick={async () => { try { setBusy(true); setStatus('Signing in...'); await ensureAuth(); setStatus('Signed in') } catch (e: unknown) { const msg = e instanceof Error ? e.message : 'Sign-in failed'; setStatus(msg) } finally { setBusy(false) } }} disabled={!wallet || !!apiToken}>{apiToken ? 'Signed In' : 'Sign In (Web3)'}</button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </motion.div>

                    <motion.div initial={{ opacity: 0, x: 30 }} whileInView={{ opacity: 1, x: 0 }} transition={{ duration: 0.8, ease: 'easeOut' }} viewport={{ once: true }} className="space-y-6">
                        <div className="card">
                            <h3 className="text-xl font-bold text-neutral-900 mb-6">Select AI Agents</h3>
                            <div className="space-y-4">
                                {aiAgents.map((agent, index) => (
                                    <motion.div key={agent.id} initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} transition={{ duration: 0.5, delay: index * 0.1 }} viewport={{ once: true }} className={`border rounded-lg p-4 cursor-pointer transition-all duration-200 ${selectedAgents.includes(agent.id) ? 'border-gold-300 bg-gold-50' : 'border-neutral-200 hover:border-gold-200'}`} onClick={() => toggleAgent(agent.id)}>
                                        <div className="flex items-start justify-between">
                                            <div className="flex items-start space-x-3">
                                                <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${selectedAgents.includes(agent.id) ? 'bg-gold-500' : 'bg-gold-100'}`}>
                                                    <agent.icon className={`w-5 h-5 ${selectedAgents.includes(agent.id) ? 'text-white' : 'text-gold-600'}`} />
                                                </div>
                                                <div className="flex-1">
                                                    <h4 className="font-semibold text-neutral-900 mb-1">{agent.name}</h4>
                                                    <p className="text-sm text-neutral-600 mb-2">{agent.description}</p>
                                                    <div className="flex flex-wrap gap-1">
                                                        {agent.features.map((feature) => (<span key={feature} className="text-xs bg-neutral-100 text-neutral-600 px-2 py-1 rounded">{feature}</span>))}
                                                    </div>
                                                </div>
                                            </div>
                                            <div className="flex items-center space-x-2">
                                                <span className="text-sm font-medium text-neutral-900">{agent.fee} CORE</span>
                                                <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${selectedAgents.includes(agent.id) ? 'border-gold-500 bg-gold-500' : 'border-neutral-300'}`}>
                                                    {selectedAgents.includes(agent.id) && (<Plus className="w-3 h-3 text-white rotate-45" />)}
                                                </div>
                                            </div>
                                        </div>
                                    </motion.div>
                                ))}
                            </div>
                        </div>

                        <motion.button whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }} onClick={handleLaunch} disabled={busy || !tokenName || !tokenSymbol || !totalSupply} className="w-full btn-primary text-lg py-4 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100">{busy ? 'Launching...' : 'Launch Token with AI Agents'}</motion.button>
                        {status && (<div className="text-sm text-neutral-700">{status}</div>)}
                        <div className="flex items-center space-x-2 text-sm text-neutral-600"><Info className="w-4 h-4" /><span>Token will be deployed to Core blockchain with selected AI agents activated</span></div>
                    </motion.div>
                </div>
            </div>
        </section>
    )
}
