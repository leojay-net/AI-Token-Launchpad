'use client'

import { useCallback, useEffect, useState } from 'react'
import { ethers } from 'ethers'
import { contractService } from './contracts'
import { web3GetNonce, web3Verify } from './api'

export function useWalletAuth() {
    const [wallet, setWallet] = useState<string | null>(null)
    const [apiToken, setApiToken] = useState<string | null>(null)
    const isConnected = !!wallet
    const isSignedIn = !!apiToken

    // Load initial state
    useEffect(() => {
        const t = typeof window !== 'undefined' ? localStorage.getItem('authToken') : null
        if (t) setApiToken(t)
        const detect = async () => {
            try {
                if (typeof window !== 'undefined' && window.ethereum) {
                    const res = await window.ethereum.request({ method: 'eth_accounts' })
                    const accounts = (res as string[]) || []
                    if (accounts.length) setWallet(accounts[0])
                }
            } catch { }
        }
        detect()
    }, [])

    // React to wallet changes
    useEffect(() => {
        const eth = typeof window !== 'undefined' ? window.ethereum : undefined
        if (!eth) return
        const onAccountsChanged = (accounts: unknown[]) => {
            const accs = accounts as string[]
            setWallet(accs && accs.length ? accs[0] : null)
        }
        eth.on?.('accountsChanged', onAccountsChanged)
        return () => {
            eth.removeListener?.('accountsChanged', onAccountsChanged)
        }
    }, [])

    const connectWallet = useCallback(async () => {
        const addr = await contractService.connectWallet()
        if (addr) setWallet(addr)
        return addr
    }, [])

    const signIn = useCallback(async () => {
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
    }, [wallet])

    const disconnect = useCallback(() => {
        setWallet(null)
        setApiToken(null)
        if (typeof window !== 'undefined') localStorage.removeItem('authToken')
    }, [])

    return {
        wallet,
        apiToken,
        isConnected,
        isSignedIn,
        connectWallet,
        signIn,
        disconnect,
        setApiToken,
    }
}
