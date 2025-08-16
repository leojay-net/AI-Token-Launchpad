// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Script.sol";
import "../src/TokenFactory.sol";
import "../src/FeeManager.sol";

/**
 * @title Deploy
 * @dev Deployment script for the AI Launchpad platform
 */
contract Deploy is Script {
    
    // Configuration for different networks
    struct NetworkConfig {
        address treasury;
        address aiServiceProvider;
        uint256 basePlatformFee;
        uint256 aiServiceFeePerAgent;
        uint256 maxSupply;
    }
    
    mapping(uint256 => NetworkConfig) public networkConfigs;
    
    function setUp() public {
        
        // Core DAO Testnet (chainId: 1115)
        networkConfigs[1114] = NetworkConfig({
            treasury: 0xBBe238A43b5E310dE976b0c0EA5264B13BE84bCB, // Replace with actual
            aiServiceProvider: 0xBBe238A43b5E310dE976b0c0EA5264B13BE84bCB, // Replace with actual
            basePlatformFee: 0.001 ether, // Lower fees for testnet
            aiServiceFeePerAgent: 0.0005 ether,
            maxSupply: 1000000000 * 10**18
        });
        
        // Core DAO Mainnet (chainId: 1116)
        networkConfigs[1116] = NetworkConfig({
            treasury: 0xBBe238A43b5E310dE976b0c0EA5264B13BE84bCB, // Replace with actual
            aiServiceProvider: 0xBBe238A43b5E310dE976b0c0EA5264B13BE84bCB, // Replace with actual
            basePlatformFee: 0.01 ether,
            aiServiceFeePerAgent: 0.005 ether,
            maxSupply: 1000000000 * 10**18
        });
        
    }
    
    function run() external {
        uint256 chainId = block.chainid;
        NetworkConfig memory config = networkConfigs[chainId];
        
        require(config.treasury != address(0), "Network not configured");
        
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        vm.startBroadcast(deployerPrivateKey);
        
        console.log("Deploying to chain ID:", chainId);
        console.log("Deployer:", vm.addr(deployerPrivateKey));
        console.log("Treasury:", config.treasury);
        console.log("AI Service Provider:", config.aiServiceProvider);
        
        // Deploy FeeManager first
        FeeManager feeManager = new FeeManager(
            address(0), // Factory address will be set later
            config.treasury,
            config.aiServiceProvider
        );
        
        console.log("FeeManager deployed at:", address(feeManager));
        
        // Deploy TokenFactory
        TokenFactory factory = new TokenFactory(address(feeManager));
        
        console.log("TokenFactory deployed at:", address(factory));
        
        // Set factory address in FeeManager
        feeManager.setFactory(address(factory));
        
        // Configure TokenFactory with network-specific parameters
        factory.updateFees(config.basePlatformFee, config.aiServiceFeePerAgent);
        factory.setMaxSupply(config.maxSupply);
        
        // Authorize initial AI agent (deployer for testing)
        factory.authorizeAgent(vm.addr(deployerPrivateKey), true);
        
        vm.stopBroadcast();
        
        // Log deployment info
        console.log("\n=== DEPLOYMENT COMPLETE ===");
        console.log("Network:", getNetworkName(chainId));
        console.log("FeeManager:", address(feeManager));
        console.log("TokenFactory:", address(factory));
        console.log("Base Platform Fee:", config.basePlatformFee);
        console.log("AI Service Fee Per Agent:", config.aiServiceFeePerAgent);
        console.log("Max Token Supply:", config.maxSupply);
        
        // Write deployment info to file for integration
        string memory deploymentInfo = string(abi.encodePacked(
            "{\n",
            '  "network": "', getNetworkName(chainId), '",\n',
            '  "chainId": ', vm.toString(chainId), ',\n',
            '  "feeManager": "', vm.toString(address(feeManager)), '",\n',
            '  "tokenFactory": "', vm.toString(address(factory)), '",\n',
            '  "treasury": "', vm.toString(config.treasury), '",\n',
            '  "aiServiceProvider": "', vm.toString(config.aiServiceProvider), '",\n',
            '  "basePlatformFee": "', vm.toString(config.basePlatformFee), '",\n',
            '  "aiServiceFeePerAgent": "', vm.toString(config.aiServiceFeePerAgent), '"\n',
            "}"
        ));
        
        // Resolve project root and ensure deployments dir exists
        string memory root = vm.projectRoot();
        string memory dir = string.concat(root, "/deployments");
        if (!vm.isDir(dir)) {
            vm.createDir(dir, true);
        }
        string memory outPath = string.concat(dir, "/latest.json");
        vm.writeFile(outPath, deploymentInfo);
    }
    
    function getNetworkName(uint256 chainId) internal pure returns (string memory) {
        if (chainId == 1116) return "Core DAO Mainnet";
        if (chainId == 1115) return "Core DAO Testnet";
        if (chainId == 31337) return "Local Development";
        return "Unknown Network";
    }
}

/**
 * @title DeployVerify
 * @dev Script to verify deployment and test basic functionality
 */
contract DeployVerify is Script {
    
    function run() external {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        address deployer = vm.addr(deployerPrivateKey);
        
        // Load deployment addresses from file
        string memory json = vm.readFile("./deployments/latest.json");
        address factoryAddress = vm.parseJsonAddress(json, ".tokenFactory");
        address feeManagerAddress = vm.parseJsonAddress(json, ".feeManager");
        
        TokenFactory factory = TokenFactory(factoryAddress);
        FeeManager feeManager = FeeManager(payable(feeManagerAddress));
        
        vm.startBroadcast(deployerPrivateKey);
        
        console.log("Verifying deployment...");
        console.log("Factory address:", address(factory));
        console.log("Fee manager address:", address(feeManager));
        
        // Test basic functionality
        uint256 fee = 0.001 ether; // Testnet fee
        
        uint256 launchId = factory.createToken{value: fee}(
            "Verification Token",
            "VERIFY",
            1000000 * 10**18,
            0
        );
        
        console.log("Test token created with launch ID:", launchId);
        
        // Verify token data
        TokenFactory.TokenLaunch memory launch = factory.getLaunch(launchId);
        console.log("Token address:", launch.tokenAddress);
        console.log("Creator:", launch.creator);
        console.log("AI enabled:", launch.aiEnabled);
        
        vm.stopBroadcast();
        
        console.log("\n=== VERIFICATION COMPLETE ===");
        console.log("Deployment verified successfully!");
    }
}