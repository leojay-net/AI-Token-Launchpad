# AI Launchpad Smart Contracts Documentation

## Overview

The AI Launchpad platform consists of three main smart contracts deployed on Core DAO that enable users to create tokens with integrated AI agent assistance. The system automates token promotion, community management, and analytics through AI-powered agents.

## Architecture

### Contract Hierarchy
```
TokenFactory (Main Factory)
├── FeeManager (Fee Processing)
└── LaunchpadToken (Individual Tokens)
```

## Core Contracts

### 1. TokenFactory.sol

**Purpose**: Main factory contract for creating tokens with AI agent integration

**Key Features**:
- Creates new ERC20 tokens through a factory pattern
- Manages AI agent configurations using bitmasks
- Handles fee collection and distribution
- Tracks launch status and user activities
- Provides access control for authorized AI agents

**AI Agent Types** (Bitmask System):
- `MARKETING_AGENT = 1` (0001) - Handles social media and marketing
- `COMMUNITY_AGENT = 2` (0010) - Manages community interactions
- `ANALYTICS_AGENT = 4` (0100) - Provides data analysis and insights
- `LAUNCH_AGENT = 8` (1000) - Coordinates overall launch strategy

**Main Functions**:
```solidity
function createToken(
    string memory name,
    string memory symbol,
    uint256 totalSupply,
    uint256 aiAgentTypes
) external payable returns (uint256 launchId)
```

### 2. LaunchpadToken.sol

**Purpose**: Individual ERC20 token contract with enhanced features

**Key Features**:
- Standard ERC20 functionality with burn capability
- Metadata storage for token information
- Trading controls (can be enabled/disabled)
- Factory integration for management operations

### 3. FeeManager.sol

**Purpose**: Handles all fee processing and distribution

**Key Features**:
- Processes platform and AI service fees
- Distributes fees to treasury and AI service provider
- Tracks fee records and user payments
- Provides emergency withdrawal capabilities

## Fee Structure

| Component | Cost | Description |
|-----------|------|-------------|
| Base Platform Fee | 0.01 CORE | Basic token creation fee |
| Marketing Agent | 0.005 CORE | Social media automation |
| Community Agent | 0.005 CORE | Community management |
| Analytics Agent | 0.005 CORE | Data analysis and insights |
| Launch Agent | 0.005 CORE | Launch coordination |

**Example Calculations**:
- Token with no AI: 0.01 CORE
- Token with Marketing + Community: 0.01 + (2 × 0.005) = 0.02 CORE
- Token with all AI agents: 0.01 + (4 × 0.005) = 0.03 CORE

## AI Agent Integration

### Bitmask System
The platform uses a bitmask system to efficiently store which AI agents are enabled:

```solidity
// Enable marketing and community agents
uint256 agentTypes = MARKETING_AGENT | COMMUNITY_AGENT; // 3 (0011 in binary)

// Check if marketing agent is enabled
bool hasMarketing = (agentTypes & MARKETING_AGENT) != 0;
```

### Agent Workflow
1. **Token Creation**: User selects AI agents during token creation
2. **Event Emission**: Smart contract emits `TokenCreated` event
3. **Agent Initialization**: Backend service detects event and initializes selected AI agents
4. **Automated Operations**: AI agents begin their respective tasks
5. **Status Updates**: Agents can update launch status through authorized calls

## Deployment Guide

### Prerequisites
```bash
# Install Foundry
curl -L https://foundry.paradigm.xyz | bash
foundryup

# Clone and setup project
git clone <your-repo>
cd ai-launchpad-contracts
make install
```

### Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Update .env with your configuration
# - Private keys
# - RPC endpoints
# - Treasury addresses
# - API keys
```

### Local Development
```bash
# Start local node
make node

# Deploy contracts locally
make deploy-local

# Run tests
make test

# Check gas usage
make test-gas
```

### Testnet Deployment
```bash
# Deploy to Core testnet
make deploy-testnet

# Verify deployment
make verify-deployment

# Create sample token for testing
make create-sample
```

### Mainnet Deployment
```bash
# Deploy to Core mainnet (use with caution)
make deploy-mainnet

# Verify deployment
make verify-deployment NETWORK=core_mainnet
```

## Testing Strategy

### Test Categories

**Unit Tests**:
- Individual function testing
- Input validation
- Access control verification
- Fee calculation accuracy

**Integration Tests**:
- Multi-contract interactions
- End-to-end workflows
- Event emission verification

**Fuzz Tests**:
- Random input validation
- Edge case discovery
- Gas optimization verification

**Security Tests**:
- Reentrancy protection
- Overflow/underflow prevention
- Access control enforcement

### Running Tests
```bash
# All tests
forge test

# Specific test file
forge test --match-path test/TokenFactory.t.sol

# Specific test function
forge test --match-test testBasicTokenCreation

# Gas optimization tests
forge test --gas-report

# Coverage analysis
forge coverage --report lcov
```

## Gas Optimization

### Contract Sizes
- TokenFactory: ~15KB (well under 24KB limit)
- FeeManager: ~8KB
- LaunchpadToken: ~12KB

### Gas Estimates
| Operation | Gas Cost | USD Cost* |
|-----------|----------|-----------|
| Create Token (no AI) | ~450,000 | ~$0.09 |
| Create Token (all AI) | ~480,000 | ~$0.096 |
| Update AI Agents | ~85,000 | ~$0.017 |
| Update Launch Status | ~45,000 | ~$0.009 |

*Based on 20 gwei gas price and $2000 ETH

### Optimization Techniques Used
- Packed structs for storage efficiency
- Bitmasks for multiple boolean flags
- Minimal external calls
- Efficient loops and calculations
- Use of `immutable` and `constant` variables

## Security Considerations

### Access Control
- Owner-only functions for admin operations
- Creator-only functions for token management
- Authorized agent system for AI operations
- Proper modifier usage throughout

### Reentrancy Protection
- `ReentrancyGuard` on all payable functions
- Checks-Effects-Interactions pattern
- State updates before external calls

### Input Validation
- Supply limits (1 billion token maximum)
- Agent type validation (bitmask bounds)
- Address validation (non-zero checks)
- Fee validation (exact payment requirements)

### Emergency Controls
- Pause/unpause functionality
- Emergency withdrawal capabilities
- Owner-controlled parameter updates

## Frontend Integration

### Contract ABIs
After deployment, generate ABI files:
```bash
make generate-abi
```

### Web3 Integration Example
```javascript
import { ethers } from 'ethers';
import TokenFactoryABI from './abi/TokenFactory.json';

const provider = new ethers.JsonRpcProvider('https://rpc.coredao.org');
const factory = new ethers.Contract(factoryAddress, TokenFactoryABI, provider);

// Create token with AI agents
const agentTypes = 1 | 2; // Marketing + Community
const fee = ethers.utils.parseEther('0.02'); // Platform + AI fees

const tx = await factory.createToken(
    'My Token',
    'MTK',
    ethers.utils.parseEther('1000000'),
    agentTypes,
    { value: fee }
);
```

### Event Listening
```javascript
// Listen for new token creations
factory.on('TokenCreated', (launchId, tokenAddress, creator, name, symbol, supply, aiEnabled, aiAgentTypes) => {
    console.log('New token created:', {
        launchId: launchId.toString(),
        tokenAddress,
        creator,
        name,
        symbol,
        aiEnabled,
        agentTypes: aiAgentTypes.toString()
    });
});
```

## AI Agent Backend Integration

### Event Processing
```javascript
// Backend service to process blockchain events
const factory = new ethers.Contract(factoryAddress, abi, provider);

factory.on('TokenCreated', async (launchId, tokenAddress, creator, name, symbol, supply, aiEnabled, aiAgentTypes, event) => {
    if (aiEnabled) {
        await initializeAIAgents({
            launchId: launchId.toString(),
            tokenAddress,
            creator,
            name,
            symbol,
            aiAgentTypes: aiAgentTypes.toString(),
            blockNumber: event.blockNumber,
            transactionHash: event.transactionHash
        });
    }
});
```

### Agent Status Updates
```javascript
// Update launch status from AI agent
const factoryWithSigner = factory.connect(authorizedAgentSigner);
await factoryWithSigner.updateLaunchStatus(launchId, 1); // Set to Active
```

## Monitoring and Analytics

### Key Metrics to Track
- Total tokens created
- AI agent usage statistics
- Fee collection amounts
- Gas usage optimization
- User adoption rates

### On-chain Queries
```javascript
// Get launch statistics
const totalLaunches = await factory.getTotalLaunches();
const userLaunches = await factory.getUserLaunches(userAddress);
const launch = await factory.getLaunch(launchId);

// Check agent configuration
const hasMarketing = await factory.isAgentEnabled(launchId, 1);
const hasCommunity = await factory.isAgentEnabled(launchId, 2);
```

## Troubleshooting

### Common Issues

**Deployment Failures**:
- Check RPC endpoint connectivity
- Verify sufficient balance for deployment
- Ensure environment variables are set correctly

**Transaction Reverts**:
- `"Insufficient fee payment"`: Calculate exact fee required
- `"Invalid token supply"`: Check supply is within bounds (1 to 1B tokens)
- `"Invalid agent types"`: Ensure bitmask is ≤ 15
- `"Not authorized agent"`: Verify agent authorization

**Gas Issues**:
- Use `--gas-limit` flag for large deployments
- Optimize contract size if near 24KB limit
- Consider deploying in phases if needed

### Debug Commands
```bash
# Detailed test output
forge test -vvvv

# Trace specific transaction
forge test --match-test testName -vvvv

# Check contract storage
forge inspect TokenFactory storage-layout

# Analyze gas usage
forge test --gas-report
```

## Maintenance and Upgrades

### Contract Upgradability
The current implementation uses a non-upgradeable pattern for security. For future upgrades:
- Deploy new contracts
- Migrate data if necessary
- Update frontend configurations
- Notify users of new contract addresses

### Parameter Updates
Contract owner can update:
- Platform fees
- AI service fees
- Maximum token supply
- Treasury and AI service provider addresses
- Authorized agent list

### Monitoring Checklist
- [ ] Contract balance levels
- [ ] Fee distribution accuracy
- [ ] Agent authorization status
- [ ] Gas price optimization
- [ ] Event emission patterns
- [ ] User adoption metrics

## Security Audit Recommendations

Before mainnet deployment:
1. **Professional Audit**: Engage reputable audit firm
2. **Bug Bounty**: Launch controlled bug bounty program
3. **Testnet Testing**: Extensive testing on Core testnet
4. **Community Review**: Open source review period
5. **Gradual Rollout**: Phased deployment with usage limits

## Future Enhancements

### Potential Upgrades
- **Governance Integration**: DAO-based parameter updates
- **Liquidity Pool Creation**: Automatic DEX listing
- **Cross-chain Support**: Bridge to other networks
- **Advanced AI Features**: More sophisticated agent types
- **Revenue Sharing**: Token holder profit distribution

### Scalability Considerations
- **Layer 2 Integration**: Consider scaling solutions
- **Batch Operations**: Multiple token creation in single transaction
- **State Pruning**: Archive old launch data
- **Caching Strategies**: Optimize frequent queries

## Conclusion

This smart contract system provides a robust foundation for an AI-powered token launchpad on Core DAO. The modular design allows for future enhancements while maintaining security and efficiency. The comprehensive testing suite ensures reliability, and the detailed documentation supports both development and integration efforts.

For questions or support, refer to the troubleshooting section or reach out to the development team.