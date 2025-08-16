#!/bin/bash

# AI Launch Pad Deployment Script
# Run this from the contracts directory

set -e  # Exit on any error

echo "🚀 AI Launch Pad Contract Deployment"
echo "===================================="

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please copy .env.example to .env and configure your values"
    exit 1
fi

# Load environment variables
source .env

# Verify required variables
if [ -z "$RPC_URL" ] || [ -z "$PRIVATE_KEY" ]; then
    echo "❌ Error: RPC_URL and PRIVATE_KEY must be set in .env"
    exit 1
fi

echo "📋 Configuration:"
echo "   RPC URL: $RPC_URL"
echo "   Private Key: ${PRIVATE_KEY:0:10}..." 
echo

# Check balance
echo "💰 Checking account balance..."
DEPLOYER_ADDRESS=$(cast wallet address --private-key $PRIVATE_KEY)
echo "   Deployer address: $DEPLOYER_ADDRESS"
BALANCE=$(cast balance $DEPLOYER_ADDRESS --rpc-url $RPC_URL 2>/dev/null || echo "0")
if [ "$BALANCE" = "0" ]; then
    echo "⚠️  Warning: Account balance is 0. Make sure you have CORE tokens for gas fees."
else
    echo "   Balance: $(cast --to-unit $BALANCE ether) CORE"
fi

echo "🔨 Building contracts..."
forge build

echo "🧪 Running tests..."
forge test

echo "📤 Deploying contracts..."
if [ -n "$CORESCAN_API_KEY" ]; then
    echo "   (With verification)"
    forge script script/Deploy.s.sol:Deploy \
        --rpc-url $RPC_URL \
        --private-key $PRIVATE_KEY \
        --broadcast \
        --verify \
        --etherscan-api-key $CORESCAN_API_KEY
else
    echo "   (Without verification - add CORESCAN_API_KEY to .env to enable)"
    forge script script/Deploy.s.sol:Deploy \
        --rpc-url $RPC_URL \
        --private-key $PRIVATE_KEY \
        --broadcast
fi

echo
echo "✅ Deployment complete!"
echo
echo "📝 Next steps:"
echo "1. Check the deployment output above for contract addresses"
echo "2. Update frontend/lib/constants.ts with the deployed addresses"
echo "3. Test the full application flow"
