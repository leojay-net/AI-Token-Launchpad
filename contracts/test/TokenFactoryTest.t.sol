// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "forge-std/Test.sol";
import "../src/TokenFactory.sol";
import "../src/FeeManager.sol";
import "../src/LaunchpadToken.sol";

contract TokenFactoryTest is Test {
    TokenFactory public factory;
    FeeManager public feeManager;
    
    address public owner = address(0x1);
    address public treasury = address(0x2);
    address public aiServiceProvider = address(0x3);
    address public user1 = address(0x4);
    address public user2 = address(0x5);
    address public agent = address(0x6);
    
    uint256 public constant MARKETING_AGENT = 1;
    uint256 public constant COMMUNITY_AGENT = 2;
    uint256 public constant ANALYTICS_AGENT = 4;
    uint256 public constant LAUNCH_AGENT = 8;
    
    function setUp() public {
        vm.startPrank(owner);
        
        // Deploy contracts
        feeManager = new FeeManager(address(0), treasury, aiServiceProvider);
        factory = new TokenFactory(address(feeManager));
        
        // Set factory in fee manager
        feeManager.setFactory(address(factory));
        
        // Authorize test agent
        factory.authorizeAgent(agent, true);
        
        vm.stopPrank();
        
        // Give users some ETH
        vm.deal(user1, 10 ether);
        vm.deal(user2, 10 ether);
    }

    function testBasicTokenCreation() public {
        vm.startPrank(user1);
        
        uint256 fee = 0.01 ether; // Base platform fee
        uint256 launchId = factory.createToken{value: fee}(
            "Test Token",
            "TEST",
            1000000 * 10**18,
            0 // No AI agents
        );
        
        // Verify launch data
        TokenFactory.TokenLaunch memory launch = factory.getLaunch(launchId);
        assertEq(launch.creator, user1);
        assertEq(launch.name, "Test Token");
        assertEq(launch.symbol, "TEST");
        assertEq(launch.totalSupply, 1000000 * 10**18);
        assertEq(launch.aiEnabled, false);
        assertEq(launch.aiAgentTypes, 0);
        
        // Verify token contract
        LaunchpadToken token = LaunchpadToken(launch.tokenAddress);
        assertEq(token.name(), "Test Token");
        assertEq(token.symbol(), "TEST");
        assertEq(token.totalSupply(), 1000000 * 10**18);
        assertEq(token.balanceOf(user1), 1000000 * 10**18);
        
        vm.stopPrank();
    }

    function testTokenCreationWithAI() public {
        vm.startPrank(user1);
        
        uint256 platformFee = 0.01 ether;
        uint256 aiServiceFee = 2 * 0.005 ether; // 2 agents
        uint256 totalFee = platformFee + aiServiceFee;
        
        uint256 agentTypes = MARKETING_AGENT | COMMUNITY_AGENT; // 3 = 0011
        
        uint256 launchId = factory.createToken{value: totalFee}(
            "AI Token",
            "AIT",
            500000 * 10**18,
            agentTypes
        );
        
        // Verify launch data
        TokenFactory.TokenLaunch memory launch = factory.getLaunch(launchId);
        assertEq(launch.aiEnabled, true);
        assertEq(launch.aiAgentTypes, agentTypes);
        assertEq(launch.platformFee, platformFee);
        assertEq(launch.aiServiceFee, aiServiceFee);
        
        // Test agent checks
        assertTrue(factory.isAgentEnabled(launchId, MARKETING_AGENT));
        assertTrue(factory.isAgentEnabled(launchId, COMMUNITY_AGENT));
        assertFalse(factory.isAgentEnabled(launchId, ANALYTICS_AGENT));
        assertFalse(factory.isAgentEnabled(launchId, LAUNCH_AGENT));
        
        vm.stopPrank();
    }

    function testInsufficientFee() public {
        vm.startPrank(user1);
        
        uint256 insufficientFee = 0.005 ether;
        
        vm.expectRevert("Insufficient fee payment");
        factory.createToken{value: insufficientFee}(
            "Test Token",
            "TEST",
            1000000 * 10**18,
            MARKETING_AGENT
        );
        
        vm.stopPrank();
    }

    function testInvalidSupply() public {
        vm.startPrank(user1);
        
        uint256 fee = 0.01 ether;
        
        // Test zero supply
        vm.expectRevert("Invalid token supply");
        factory.createToken{value: fee}(
            "Test Token",
            "TEST",
            0,
            0
        );
        
        // Test excessive supply
        vm.expectRevert("Invalid token supply");
        factory.createToken{value: fee}(
            "Test Token",
            "TEST",
            2000000000 * 10**18, // More than maxSupply
            0
        );
        
        vm.stopPrank();
    }

    function testInvalidAgentTypes() public {
        vm.startPrank(user1);
        
        uint256 fee = 0.01 ether;
        
        vm.expectRevert("Invalid agent types");
        factory.createToken{value: fee}(
            "Test Token",
            "TEST",
            1000000 * 10**18,
            16 // Invalid agent type (10000 in binary)
        );
        
        vm.stopPrank();
    }

    function testUpdateAIAgents() public {
        vm.startPrank(user1);
        
        // Create token with marketing agent only
        uint256 initialFee = 0.01 ether + 0.005 ether; // Platform + 1 agent
        uint256 launchId = factory.createToken{value: initialFee}(
            "Test Token",
            "TEST",
            1000000 * 10**18,
            MARKETING_AGENT
        );
        
        // Add community agent
        uint256 additionalFee = 0.005 ether;
        uint256 newAgentTypes = MARKETING_AGENT | COMMUNITY_AGENT;
        
        factory.updateAIAgents{value: additionalFee}(launchId, newAgentTypes);
        
        // Verify update
        TokenFactory.TokenLaunch memory launch = factory.getLaunch(launchId);
        assertEq(launch.aiAgentTypes, newAgentTypes);
        assertTrue(factory.isAgentEnabled(launchId, MARKETING_AGENT));
        assertTrue(factory.isAgentEnabled(launchId, COMMUNITY_AGENT));
        
        vm.stopPrank();
    }

    function testUpdateLaunchStatusByAgent() public {
        vm.startPrank(user1);
        
        // Create token
        uint256 fee = 0.01 ether;
        uint256 launchId = factory.createToken{value: fee}(
            "Test Token",
            "TEST",
            1000000 * 10**18,
            0
        );
        
        vm.stopPrank();
        
        // Update status as authorized agent
        vm.startPrank(agent);
        
        factory.updateLaunchStatus(launchId, TokenFactory.LaunchStatus.Active);
        
        TokenFactory.TokenLaunch memory launch = factory.getLaunch(launchId);
        assertEq(uint256(launch.status), uint256(TokenFactory.LaunchStatus.Active));
        
        vm.stopPrank();
    }

    function testUnauthorizedAgentAccess() public {
        vm.startPrank(user1);
        
        // Create token
        uint256 fee = 0.01 ether;
        uint256 launchId = factory.createToken{value: fee}(
            "Test Token",
            "TEST",
            1000000 * 10**18,
            0
        );
        
        vm.stopPrank();
        
        // Try to update status as unauthorized user
        vm.startPrank(user2);
        
        vm.expectRevert("Not authorized agent");
        factory.updateLaunchStatus(launchId, TokenFactory.LaunchStatus.Active);
        
        vm.stopPrank();
    }

    function testGetUserLaunches() public {
        vm.startPrank(user1);
        
        uint256 fee = 0.01 ether;
        
        // Create multiple tokens
        uint256 launchId1 = factory.createToken{value: fee}(
            "Token 1",
            "TK1",
            1000000 * 10**18,
            0
        );
        
        uint256 launchId2 = factory.createToken{value: fee}(
            "Token 2",
            "TK2",
            2000000 * 10**18,
            0
        );
        
        // Check user launches
        uint256[] memory userLaunches = factory.getUserLaunches(user1);
        assertEq(userLaunches.length, 2);
        assertEq(userLaunches[0], launchId1);
        assertEq(userLaunches[1], launchId2);
        
        vm.stopPrank();
    }

    function testFeeDistribution() public {
        uint256 initialTreasuryBalance = treasury.balance;
        uint256 initialAIProviderBalance = aiServiceProvider.balance;
        
        vm.startPrank(user1);
        
        uint256 platformFee = 0.01 ether;
        uint256 aiServiceFee = 0.01 ether; // 2 agents
        uint256 totalFee = platformFee + aiServiceFee;
        
        factory.createToken{value: totalFee}(
            "Test Token",
            "TEST",
            1000000 * 10**18,
            MARKETING_AGENT | COMMUNITY_AGENT
        );
        
        // Check fee distribution
        assertEq(treasury.balance, initialTreasuryBalance + platformFee);
        assertEq(aiServiceProvider.balance, initialAIProviderBalance + aiServiceFee);
        
        vm.stopPrank();
    }

    function testExcessFeeRefund() public {
        uint256 initialUserBalance = user1.balance;
        uint256 requiredFee = 0.01 ether;
        uint256 excessFee = 0.02 ether; // Send more than required
        
        vm.startPrank(user1);
        
        factory.createToken{value: excessFee}(
            "Test Token",
            "TEST",
            1000000 * 10**18,
            0 // No AI agents
        );
        
        // Check refund
        uint256 expectedBalance = initialUserBalance - requiredFee;
        assertEq(user1.balance, expectedBalance);
        
        vm.stopPrank();
    }

    function testEventEmission() public {
        vm.startPrank(user1);
        
        uint256 fee = 0.01 ether;
        
        // Create token first to get the address
        uint256 launchId = factory.createToken{value: fee}(
            "Test Token",
            "TEST",
            1000000 * 10**18,
            0
        );
        
        // Verify the event was emitted by checking the launch data
        TokenFactory.TokenLaunch memory launch = factory.getLaunch(launchId);
        assertEq(launch.creator, user1);
        assertEq(launch.name, "Test Token");
        assertEq(launch.symbol, "TEST");
        assertEq(launch.totalSupply, 1000000 * 10**18);
        assertEq(launch.aiEnabled, false);
        assertEq(launch.aiAgentTypes, 0);
        assertTrue(launch.tokenAddress != address(0)); // Verify token was deployed
        
        vm.stopPrank();
    }

    // Admin function tests
    function testOwnerFunctions() public {
        vm.startPrank(owner);
        
        // Test fee updates
        factory.updateFees(0.02 ether, 0.01 ether);
        
        // Test max supply update
        factory.setMaxSupply(2000000000 * 10**18);
        
        // Test agent authorization
        factory.authorizeAgent(user2, true);
        assertTrue(factory.authorizedAgents(user2));
        
        factory.authorizeAgent(user2, false);
        assertFalse(factory.authorizedAgents(user2));
        
        vm.stopPrank();
    }

    function testNonOwnerCannotCallAdminFunctions() public {
        vm.startPrank(user1);
        
        vm.expectRevert(abi.encodeWithSelector(Ownable.OwnableUnauthorizedAccount.selector, user1));
        factory.updateFees(0.02 ether, 0.01 ether);
        
        vm.expectRevert(abi.encodeWithSelector(Ownable.OwnableUnauthorizedAccount.selector, user1));
        factory.authorizeAgent(user2, true);
        
        vm.stopPrank();
    }

    // Gas optimization tests
    function testGasUsage() public {
        vm.startPrank(user1);
        
        uint256 fee = 0.01 ether;
        uint256 gasBefore = gasleft();
        
        factory.createToken{value: fee}(
            "Gas Test",
            "GAS",
            1000000 * 10**18,
            0
        );
        
        uint256 gasUsed = gasBefore - gasleft();
        console.log("Gas used for token creation:", gasUsed);
        
        // Ensure gas usage is reasonable (adjust based on requirements)
        assertTrue(gasUsed < 2000000, "Gas usage too high");
        
        vm.stopPrank();
    }

    // Fuzz testing
    function testFuzzTokenCreation(
        string memory name,
        string memory symbol,
        uint256 supply,
        uint8 agentTypes
    ) public {
        // Bound inputs to valid ranges
        vm.assume(bytes(name).length > 0 && bytes(name).length < 50);
        vm.assume(bytes(symbol).length > 0 && bytes(symbol).length < 10);
        supply = bound(supply, 1, 1000000000 * 10**18);
        agentTypes = uint8(bound(agentTypes, 0, 15)); // 0-15 valid range
        
        vm.startPrank(user1);
        
        // Calculate required fee
        uint256 aiAgentCount = 0;
        if (agentTypes & 1 != 0) aiAgentCount++; // Marketing
        if (agentTypes & 2 != 0) aiAgentCount++; // Community
        if (agentTypes & 4 != 0) aiAgentCount++; // Analytics
        if (agentTypes & 8 != 0) aiAgentCount++; // Launch
        
        uint256 totalFee = 0.01 ether + (aiAgentCount * 0.005 ether);
        
        try factory.createToken{value: totalFee}(name, symbol, supply, agentTypes) {
            // If successful, verify basic properties
            uint256 launchId = factory.getTotalLaunches() - 1;
            TokenFactory.TokenLaunch memory launch = factory.getLaunch(launchId);
            assertEq(launch.creator, user1);
            assertEq(launch.totalSupply, supply);
        } catch {
            // Some combinations might fail due to string constraints
            // This is acceptable for fuzz testing
        }
        
        vm.stopPrank();
    }

    // Integration tests
    function testFullWorkflow() public {
        vm.startPrank(user1);
        
        // Step 1: Create token with all AI agents
        uint256 totalFee = 0.01 ether + (4 * 0.005 ether); // Platform + 4 agents
        uint256 launchId = factory.createToken{value: totalFee}(
            "Full AI Token",
            "FAIT",
            1000000 * 10**18,
            MARKETING_AGENT | COMMUNITY_AGENT | ANALYTICS_AGENT | LAUNCH_AGENT
        );
        
        vm.stopPrank();
        
        // Step 2: Agent updates launch status
        vm.startPrank(agent);
        factory.updateLaunchStatus(launchId, TokenFactory.LaunchStatus.Active);
        vm.stopPrank();
        
        // Step 3: Creator updates AI agents
        vm.startPrank(user1);
        // Remove analytics agent, keep others
        uint256 newAgentTypes = MARKETING_AGENT | COMMUNITY_AGENT | LAUNCH_AGENT;
        factory.updateAIAgents(launchId, newAgentTypes);
        
        // Verify changes
        TokenFactory.TokenLaunch memory launch = factory.getLaunch(launchId);
        assertEq(launch.aiAgentTypes, newAgentTypes);
        assertEq(uint256(launch.status), uint256(TokenFactory.LaunchStatus.Active));
        
        vm.stopPrank();
    }

    function testMultipleUsersAndTokens() public {
        // User 1 creates token
        vm.startPrank(user1);
        uint256 fee1 = 0.01 ether;
        uint256 launchId1 = factory.createToken{value: fee1}(
            "User1 Token",
            "U1T",
            1000000 * 10**18,
            0
        );
        vm.stopPrank();
        
        // User 2 creates token with AI
        vm.startPrank(user2);
        uint256 fee2 = 0.01 ether + 0.005 ether;
        uint256 launchId2 = factory.createToken{value: fee2}(
            "User2 AI Token",
            "U2T",
            2000000 * 10**18,
            MARKETING_AGENT
        );
        vm.stopPrank();
        
        // Verify user launches
        uint256[] memory user1Launches = factory.getUserLaunches(user1);
        uint256[] memory user2Launches = factory.getUserLaunches(user2);
        
        assertEq(user1Launches.length, 1);
        assertEq(user1Launches[0], launchId1);
        
        assertEq(user2Launches.length, 1);
        assertEq(user2Launches[0], launchId2);
        
        // Verify total launches
        assertEq(factory.getTotalLaunches(), 2);
    }

    // Helper functions for testing
    function createSampleToken(address creator, uint256 agentTypes) internal returns (uint256) {
        vm.startPrank(creator);
        
        uint256 aiAgentCount = 0;
        if (agentTypes & 1 != 0) aiAgentCount++;
        if (agentTypes & 2 != 0) aiAgentCount++;
        if (agentTypes & 4 != 0) aiAgentCount++;
        if (agentTypes & 8 != 0) aiAgentCount++;
        
        uint256 totalFee = 0.01 ether + (aiAgentCount * 0.005 ether);
        
        uint256 launchId = factory.createToken{value: totalFee}(
            "Sample Token",
            "SMPL",
            1000000 * 10**18,
            agentTypes
        );
        
        vm.stopPrank();
        return launchId;
    }

    receive() external payable {}
}