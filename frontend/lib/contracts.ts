import { ethers } from 'ethers'
import { CONTRACT_ADDRESSES, FEES, CHAIN_CONFIG } from './constants'

// Token Factory ABI (simplified for demo)
const TOKEN_FACTORY_ABI = [
    'function createToken(string memory name, string memory symbol, uint256 totalSupply, uint256 aiAgentTypes) external payable returns (uint256)',
    'function getLaunch(uint256 launchId) external view returns (tuple(address tokenAddress, address creator, string name, string symbol, uint256 totalSupply, bool aiEnabled, uint256 aiAgentTypes, uint256 launchTime, uint256 platformFee, uint256 aiServiceFee, uint8 status))',
    'function getUserLaunches(address user) external view returns (uint256[])',
    'function getTotalLaunches() external view returns (uint256)',
    'function isAgentEnabled(uint256 launchId, uint256 agentType) external view returns (bool)',
    'event TokenCreated(uint256 indexed launchId, address indexed tokenAddress, address indexed creator, string name, string symbol, uint256 totalSupply, bool aiEnabled, uint256 aiAgentTypes)'
]

// Fee Manager ABI (simplified for demo)
const FEE_MANAGER_ABI = [
    'function getFeeRecord(uint256 launchId) external view returns (tuple(uint256 launchId, address payer, uint256 platformFee, uint256 aiServiceFee, uint256 timestamp))',
    'function calculateTotalFee(uint256 platformFee, uint256 aiServiceFee) external pure returns (uint256)'
]

export class ContractService {
    private provider: ethers.BrowserProvider | null = null
    private signer: ethers.Signer | null = null
    private tokenFactory: ethers.Contract | null = null
    private feeManager: ethers.Contract | null = null

    constructor() {
        this.initializeProvider()
    }

    private async initializeProvider() {
        if (typeof window !== 'undefined' && window.ethereum) {
            this.provider = new ethers.BrowserProvider(window.ethereum)
        }
    }

    async connectWallet(): Promise<string | null> {
        try {
            if (!this.provider) {
                throw new Error('No wallet provider found')
            }

            await window.ethereum.request({ method: 'eth_requestAccounts' })
            this.signer = await this.provider.getSigner()

            // Ensure we're on the expected chain; attempt to switch if not
            const network = await this.provider.getNetwork()
            if (Number(network.chainId) !== CHAIN_CONFIG.chainId) {
                try {
                    await window.ethereum.request({
                        method: 'wallet_switchEthereumChain',
                        params: [{ chainId: `0x${CHAIN_CONFIG.chainId.toString(16)}` }],
                    })
                } catch (switchErr: unknown) {
                    // If the chain is not added, attempt to add it
                    const err = switchErr as { code?: number; message?: string }
                    if (err?.code === 4902 || `${err?.message}`.includes('Unrecognized chain ID')) {
                        await window.ethereum.request({
                            method: 'wallet_addEthereumChain',
                            params: [{
                                chainId: `0x${CHAIN_CONFIG.chainId.toString(16)}`,
                                chainName: CHAIN_CONFIG.name,
                                nativeCurrency: CHAIN_CONFIG.nativeCurrency,
                                rpcUrls: CHAIN_CONFIG.rpcUrls,
                                blockExplorerUrls: CHAIN_CONFIG.blockExplorerUrls,
                            }],
                        })
                    } else {
                        console.warn('Network switch failed:', switchErr)
                    }
                }
                // Refresh signer after potential network change
                this.signer = await this.provider.getSigner()
            }

            this.tokenFactory = new ethers.Contract(
                CONTRACT_ADDRESSES.TOKEN_FACTORY,
                TOKEN_FACTORY_ABI,
                this.signer
            )

            this.feeManager = new ethers.Contract(
                CONTRACT_ADDRESSES.FEE_MANAGER,
                FEE_MANAGER_ABI,
                this.signer
            )

            const address = await this.signer.getAddress()
            return address
        } catch (error) {
            console.error('Error connecting wallet:', error)
            return null
        }
    }

    calculateTotalFee(selectedAgents: number[]): number {
        const agentCount = selectedAgents.length
        return FEES.PLATFORM_FEE + (agentCount * FEES.AI_SERVICE_FEE_PER_AGENT)
    }

    calculateAgentTypesBitmask(selectedAgents: number[]): number {
        return selectedAgents.reduce((bitmask, agentId) => bitmask | agentId, 0)
    }

    async createToken(
        name: string,
        symbol: string,
        totalSupply: string,
        selectedAgents: number[]
    ): Promise<{ success: boolean; txHash?: string; tokenAddress?: string; launchId?: string; error?: string }> {
        try {
            if (!this.tokenFactory || !this.signer) {
                throw new Error('Wallet not connected')
            }

            const supply = ethers.parseEther(totalSupply)
            const agentTypes = this.calculateAgentTypesBitmask(selectedAgents)
            const totalFee = this.calculateTotalFee(selectedAgents)
            const feeInWei = ethers.parseEther(totalFee.toString())

            const tx = await this.tokenFactory.createToken(
                name,
                symbol,
                supply,
                agentTypes,
                { value: feeInWei }
            )

            const receipt = await tx.wait()
            // Try to parse TokenCreated event
            let tokenAddress: string | undefined
            let launchId: string | undefined
            try {
                const iface = new ethers.Interface(TOKEN_FACTORY_ABI)
                for (const log of receipt.logs) {
                    try {
                        const parsed = iface.parseLog({ topics: log.topics as string[], data: log.data as string })
                        if (parsed?.name === 'TokenCreated') {
                            launchId = (parsed.args[0] as bigint).toString()
                            tokenAddress = (parsed.args[1] as string)
                            break
                        }
                    } catch { /* ignore non-matching logs */ }
                }
            } catch { /* non-fatal */ }
            return { success: true, txHash: tx.hash, tokenAddress, launchId }
        } catch (error: unknown) {
            console.error('Error creating token:', error)
            const message = error instanceof Error ? error.message : 'Failed to create token'
            return {
                success: false,
                error: message
            }
        }
    }

    async getUserLaunches(userAddress: string): Promise<Array<Record<string, unknown>>> {
        try {
            if (!this.tokenFactory) {
                throw new Error('Contract not initialized')
            }

            const launchIds = await this.tokenFactory.getUserLaunches(userAddress)
            const launches = await Promise.all(
                launchIds.map(async (id: bigint) => {
                    const launch = await this.tokenFactory!.getLaunch(id)
                    return {
                        id: id.toString(),
                        ...launch
                    }
                })
            )

            return launches
        } catch (error) {
            console.error('Error getting user launches:', error)
            return []
        }
    }

    async getTotalLaunches(): Promise<number> {
        try {
            if (!this.tokenFactory) {
                throw new Error('Contract not initialized')
            }

            const total = await this.tokenFactory.getTotalLaunches()
            return Number(total)
        } catch (error) {
            console.error('Error getting total launches:', error)
            return 0
        }
    }

    async isAgentEnabled(launchId: number, agentType: number): Promise<boolean> {
        try {
            if (!this.tokenFactory) {
                throw new Error('Contract not initialized')
            }

            return await this.tokenFactory.isAgentEnabled(launchId, agentType)
        } catch (error) {
            console.error('Error checking agent status:', error)
            return false
        }
    }
}

export const contractService = new ContractService()

// Utility functions
export const formatAddress = (address: string): string => {
    return `${address.slice(0, 6)}...${address.slice(-4)}`
}

export const formatNumber = (num: number): string => {
    if (num >= 1000000) {
        return `${(num / 1000000).toFixed(1)}M`
    }
    if (num >= 1000) {
        return `${(num / 1000).toFixed(1)}K`
    }
    return num.toString()
}

export const formatCurrency = (amount: number): string => {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
    }).format(amount)
}
