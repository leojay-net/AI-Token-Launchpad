export const CONTRACT_ADDRESSES = {
    // Deployed on chain 1114 per latest logs
    TOKEN_FACTORY: '0x1420A630c00Ff9fbd99cD90B7E01Df0AF2cfcAb1',
    FEE_MANAGER: '0x40e4719B290c7D0992b7C976309eB9EEc30a22E5',
} as const

export const AI_AGENT_TYPES = {
    MARKETING_AGENT: 1,
    COMMUNITY_AGENT: 2,
    ANALYTICS_AGENT: 4,
    LAUNCH_AGENT: 8,
    ALL_AGENTS: 15,
} as const

export const CHAIN_CONFIG = {
    // Using chainId 1114 as per deployment output
    chainId: 1114,
    name: 'Core (custom 1114)',
    nativeCurrency: {
        name: 'CORE',
        symbol: 'CORE',
        decimals: 18,
    },
    // RPC for chain 1114 (Core Testnet v2). Add more RPCs if needed.
    rpcUrls: ['https://rpc.test2.btcs.network', 'https://rpc.test.btcs.network'],
    // Explorer (may differ for chain 1114)
    blockExplorerUrls: ['https://scan.test.btcs.network'],
}

export const FEES = {
    // Match testnet config used during deployment
    PLATFORM_FEE: 0.001, // 0.001 CORE
    AI_SERVICE_FEE_PER_AGENT: 0.0005, // 0.0005 CORE per agent
} as const
