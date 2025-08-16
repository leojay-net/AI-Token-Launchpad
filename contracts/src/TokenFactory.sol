// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "./LaunchpadToken.sol";
import "./interfaces/IFeeManager.sol";
import "openzeppelin-contracts/contracts/access/Ownable.sol";
import "openzeppelin-contracts/contracts/utils/ReentrancyGuard.sol";

/**
 * @title TokenFactory
 * @dev Factory contract for creating tokens with AI agent integration
 * @notice This contract handles token creation, AI agent configuration, and fee management
 */
contract TokenFactory is Ownable, ReentrancyGuard {

    // AI Agent Types (bitmask)
    uint256 public constant MARKETING_AGENT = 1;    // 0001
    uint256 public constant COMMUNITY_AGENT = 2;    // 0010
    uint256 public constant ANALYTICS_AGENT = 4;    // 0100
    uint256 public constant LAUNCH_AGENT = 8;       // 1000
    uint256 public constant ALL_AGENTS = 15;        // 1111

    struct TokenLaunch {
        address tokenAddress;
        address creator;
        string name;
        string symbol;
        uint256 totalSupply;
        bool aiEnabled;
        uint256 aiAgentTypes;
        uint256 launchTime;
        uint256 platformFee;
        uint256 aiServiceFee;
        LaunchStatus status;
    }

    enum LaunchStatus {
        Created,
        Active,
        Completed,
        Paused
    }

    // State variables
    uint256 private _launchIdCounter;
    IFeeManager public feeManager;
    
    mapping(uint256 => TokenLaunch) public launches;
    mapping(address => uint256[]) public userLaunches;
    mapping(address => bool) public authorizedAgents;
    
    uint256 public basePlatformFee = 0.01 ether; // 0.01 CORE
    uint256 public aiServiceFeePerAgent = 0.005 ether; // 0.005 CORE per agent
    uint256 public maxSupply = 1000000000 * 10**18; // 1 billion tokens max
    
    // Events
    event TokenCreated(
        uint256 indexed launchId,
        address indexed tokenAddress,
        address indexed creator,
        string name,
        string symbol,
        uint256 totalSupply,
        bool aiEnabled,
        uint256 aiAgentTypes
    );
    
    event LaunchStatusChanged(
        uint256 indexed launchId,
        LaunchStatus oldStatus,
        LaunchStatus newStatus
    );
    
    event AIAgentAuthorized(address indexed agent, bool authorized);
    event FeesUpdated(uint256 platformFee, uint256 aiServiceFee);

    modifier validSupply(uint256 supply) {
        require(supply > 0 && supply <= maxSupply, "Invalid token supply");
        _;
    }

    modifier validAgentTypes(uint256 agentTypes) {
        require(agentTypes <= ALL_AGENTS, "Invalid agent types");
        _;
    }

    modifier onlyAuthorizedAgent() {
        require(authorizedAgents[msg.sender], "Not authorized agent");
        _;
    }

    constructor(address _feeManager) Ownable(msg.sender) {
        feeManager = IFeeManager(_feeManager);
    }

    /**
     * @dev Create a new token with optional AI agents
     * @param name Token name
     * @param symbol Token symbol  
     * @param totalSupply Total token supply
     * @param aiAgentTypes Bitmask of AI agent types to enable
     * @return launchId The ID of the created launch
     */
    function createToken(
        string memory name,
        string memory symbol,
        uint256 totalSupply,
        uint256 aiAgentTypes
    ) 
        external 
        payable 
        nonReentrant
        validSupply(totalSupply)
        validAgentTypes(aiAgentTypes)
        returns (uint256)
    {
        uint256 launchId = _launchIdCounter;
        _launchIdCounter++;

        // Calculate fees
        uint256 platformFee = basePlatformFee;
        uint256 aiServiceFee = 0;
        bool aiEnabled = aiAgentTypes > 0;
        
        if (aiEnabled) {
            aiServiceFee = _calculateAIServiceFee(aiAgentTypes);
        }
        
        uint256 totalFee = platformFee + aiServiceFee;
        require(msg.value >= totalFee, "Insufficient fee payment");

        // Deploy new token contract
        LaunchpadToken newToken = new LaunchpadToken(
            name,
            symbol,
            totalSupply,
            msg.sender,
            address(this)
        );

        // Store launch data
        launches[launchId] = TokenLaunch({
            tokenAddress: address(newToken),
            creator: msg.sender,
            name: name,
            symbol: symbol,
            totalSupply: totalSupply,
            aiEnabled: aiEnabled,
            aiAgentTypes: aiAgentTypes,
            launchTime: block.timestamp,
            platformFee: platformFee,
            aiServiceFee: aiServiceFee,
            status: LaunchStatus.Created
        });

        // Track user launches
        userLaunches[msg.sender].push(launchId);

        // Process fee payment
        if (totalFee > 0) {
            feeManager.processFees{value: totalFee}(
                launchId,
                msg.sender,
                platformFee,
                aiServiceFee
            );
        }

        // Refund excess payment
        if (msg.value > totalFee) {
            payable(msg.sender).transfer(msg.value - totalFee);
        }

        emit TokenCreated(
            launchId,
            address(newToken),
            msg.sender,
            name,
            symbol,
            totalSupply,
            aiEnabled,
            aiAgentTypes
        );

        return launchId;
    }

    /**
     * @dev Update launch status (only authorized agents)
     */
    function updateLaunchStatus(
        uint256 launchId,
        LaunchStatus newStatus
    ) external onlyAuthorizedAgent {
        require(launchId < _launchIdCounter, "Invalid launch ID");
        
        TokenLaunch storage launch = launches[launchId];
        LaunchStatus oldStatus = launch.status;
        launch.status = newStatus;

        emit LaunchStatusChanged(launchId, oldStatus, newStatus);
    }

    /**
     * @dev Add or remove AI agents from a launch (creator only)
     */
    function updateAIAgents(
        uint256 launchId,
        uint256 newAgentTypes
    ) external payable validAgentTypes(newAgentTypes) {
        require(launchId < _launchIdCounter, "Invalid launch ID");
        
        TokenLaunch storage launch = launches[launchId];
        require(msg.sender == launch.creator, "Only creator can update agents");
        
        uint256 currentAgents = launch.aiAgentTypes;
        uint256 addedAgents = newAgentTypes & ~currentAgents;
        
        if (addedAgents > 0) {
            uint256 additionalFee = _calculateAIServiceFee(addedAgents);
            require(msg.value >= additionalFee, "Insufficient fee for new agents");
            
            feeManager.processFees{value: additionalFee}(
                launchId,
                msg.sender,
                0,
                additionalFee
            );
        }
        
        launch.aiAgentTypes = newAgentTypes;
        launch.aiEnabled = newAgentTypes > 0;
        
        // Refund excess if any
        if (msg.value > _calculateAIServiceFee(addedAgents)) {
            payable(msg.sender).transfer(msg.value - _calculateAIServiceFee(addedAgents));
        }
    }

    /**
     * @dev Get launch information
     */
    function getLaunch(uint256 launchId) external view returns (TokenLaunch memory) {
        require(launchId < _launchIdCounter, "Invalid launch ID");
        return launches[launchId];
    }

    /**
     * @dev Get user's launches
     */
    function getUserLaunches(address user) external view returns (uint256[] memory) {
        return userLaunches[user];
    }

    /**
     * @dev Check if specific AI agent is enabled for launch
     */
    function isAgentEnabled(uint256 launchId, uint256 agentType) external view returns (bool) {
        require(launchId < _launchIdCounter, "Invalid launch ID");
        return (launches[launchId].aiAgentTypes & agentType) != 0;
    }

    /**
     * @dev Get total number of launches
     */
    function getTotalLaunches() external view returns (uint256) {
        return _launchIdCounter;
    }

    /**
     * @dev Calculate AI service fee based on agent types
     */
    function _calculateAIServiceFee(uint256 agentTypes) internal view returns (uint256) {
        uint256 agentCount = 0;
        
        // Count enabled agents
        if (agentTypes & MARKETING_AGENT != 0) agentCount++;
        if (agentTypes & COMMUNITY_AGENT != 0) agentCount++;
        if (agentTypes & ANALYTICS_AGENT != 0) agentCount++;
        if (agentTypes & LAUNCH_AGENT != 0) agentCount++;
        
        return agentCount * aiServiceFeePerAgent;
    }

    // Admin functions
    function setFeeManager(address _feeManager) external onlyOwner {
        feeManager = IFeeManager(_feeManager);
    }

    function updateFees(
        uint256 _platformFee,
        uint256 _aiServiceFee
    ) external onlyOwner {
        basePlatformFee = _platformFee;
        aiServiceFeePerAgent = _aiServiceFee;
        
        emit FeesUpdated(_platformFee, _aiServiceFee);
    }

    function setMaxSupply(uint256 _maxSupply) external onlyOwner {
        maxSupply = _maxSupply;
    }

    function authorizeAgent(address agent, bool authorized) external onlyOwner {
        authorizedAgents[agent] = authorized;
        emit AIAgentAuthorized(agent, authorized);
    }

    // Emergency functions
    function pause() external onlyOwner {
        // Implementation for emergency pause
    }

    function unpause() external onlyOwner {
        // Implementation for unpause
    }
}