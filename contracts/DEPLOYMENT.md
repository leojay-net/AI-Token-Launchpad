# AI Launch Pad - Contract Deployment Guide

## Prerequisites

1. **Install Foundry** (already done ✓)
   ```bash
   curl -L https://foundry.paradigm.xyz | bash
   foundryup
   ```

2. **Get Core DAO Testnet Setup**
   - Visit Core DAO Testnet Faucet: https://faucet.test.btcs.network/
   - Add Core Testnet to MetaMask:
     - Network Name: Core Blockchain Testnet
     - RPC URL: https://rpc.test.btcs.network
     - Chain ID: 1115
     - Currency Symbol: CORE
     - Block Explorer: https://scan.test.btcs.network

3. **Get API Key**
   - Visit Core Scan: https://scan.test.btcs.network
   - Create account and get API key for contract verification

## Deployment Steps

### Step 1: Configure Environment
Edit `contracts/.env` with your actual values:

```bash
# Core DAO Testnet Configuration
RPC_URL=https://rpc.test.btcs.network
PRIVATE_KEY=your_actual_private_key_here_without_0x_prefix
CORESCAN_API_KEY=your_actual_api_key_here
API_URL=https://api.test.btcs.network/api

# Optional: Custom treasury and service provider addresses
TREASURY_ADDRESS=your_treasury_address
AI_SERVICE_PROVIDER_ADDRESS=your_ai_service_address
```

### Step 2: Load Environment Variables
```bash
cd contracts
source .env
```

### Step 3: Deploy Contracts
```bash
# Deploy to Core Testnet
forge script script/Deploy.s.sol:Deploy --rpc-url $RPC_URL --private-key $PRIVATE_KEY --broadcast --verify --etherscan-api-key $CORESCAN_API_KEY

# Or deploy without verification first (faster)
forge script script/Deploy.s.sol:Deploy --rpc-url $RPC_URL --private-key $PRIVATE_KEY --broadcast
```

### Step 4: Verify Contracts (if not done during deployment)
After deployment, get the contract addresses and verify:

```bash
# Verify FeeManager
forge verify-contract <FEE_MANAGER_ADDRESS> FeeManager --verifier-url $API_URL --etherscan-api-key $CORESCAN_API_KEY --watch

# Verify TokenFactory  
forge verify-contract <TOKEN_FACTORY_ADDRESS> TokenFactory --verifier-url $API_URL --etherscan-api-key $CORESCAN_API_KEY --watch
```

### Step 5: Update Frontend
After successful deployment, update `frontend/lib/constants.ts` with the deployed addresses:

```typescript
export const CONTRACT_ADDRESSES = {
    TOKEN_FACTORY: '0xYourTokenFactoryAddress',
    FEE_MANAGER: '0xYourFeeManagerAddress',
} as const
```

## Testing the Deployment

After deployment, you can test the contracts:

```bash
# Test contract interaction
cast call $TOKEN_FACTORY_ADDRESS "basePlatformFee()" --rpc-url $RPC_URL

# Check contract is verified
cast call $TOKEN_FACTORY_ADDRESS "owner()" --rpc-url $RPC_URL
```

## Mainnet Deployment (When Ready)

For mainnet deployment, update your .env:

```bash
RPC_URL=https://rpc.coredao.org
API_URL=https://openapi.coredao.org/api
# Use your mainnet private key with real CORE tokens
```

## Deployment Output

The deployment script will output something like:

```
=== DEPLOYMENT COMPLETE ===
FeeManager: 0x1234...
TokenFactory: 0x5678...

Update frontend/lib/constants.ts with these addresses:
TOKEN_FACTORY: '0x5678...',
FEE_MANAGER: '0x1234...',
```

Copy these addresses to update your frontend configuration.

## Security Notes

- Never commit your actual private keys to version control
- Use different addresses for treasury and AI service provider in production
- Test thoroughly on testnet before mainnet deployment
- Consider using a multisig wallet for admin functions in production

## Troubleshooting

1. **"Insufficient funds" error**: Ensure your address has enough CORE tokens for gas fees
2. **"Invalid nonce" error**: Check if you have pending transactions
3. **Verification failed**: Ensure API key is correct and wait a few minutes before retrying

## Next Steps

1. Deploy contracts to Core Testnet
2. Update frontend with deployed addresses  
3. Test end-to-end flow (Frontend ↔ Backend ↔ Contracts)
4. Deploy to mainnet when ready
