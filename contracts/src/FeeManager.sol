// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "./interfaces/IFeeManager.sol";
import "openzeppelin-contracts/contracts/access/Ownable.sol";
import "openzeppelin-contracts/contracts/utils/ReentrancyGuard.sol";

/**
 * @title FeeManager
 * @dev Manages platform fees and AI service payments
 */
contract FeeManager is IFeeManager, Ownable, ReentrancyGuard {
    
    struct FeeRecord {
        uint256 launchId;
        address payer;
        uint256 platformFee;
        uint256 aiServiceFee;
        uint256 timestamp;
    }
    
    address public factory;
    address public treasury;
    address public aiServiceProvider;
    
    mapping(uint256 => FeeRecord) public feeRecords;
    mapping(address => uint256) public totalPaidByUser;
    
    uint256 public totalPlatformFeesCollected;
    uint256 public totalAIFeesCollected;
    
    event FeesProcessed(
        uint256 indexed launchId,
        address indexed payer,
        uint256 platformFee,
        uint256 aiServiceFee
    );
    
    event TreasuryUpdated(address oldTreasury, address newTreasury);
    event AIServiceProviderUpdated(address oldProvider, address newProvider);

    modifier onlyFactory() {
        require(msg.sender == factory, "Only factory can call");
        _;
    }

    constructor(
        address _factory,
        address _treasury,
        address _aiServiceProvider
    ) Ownable(msg.sender) {
        factory = _factory;
        treasury = _treasury;
        aiServiceProvider = _aiServiceProvider;
    }

    /**
     * @dev Process fees for a token launch
     */
    function processFees(
        uint256 launchId,
        address payer,
        uint256 platformFee,
        uint256 aiServiceFee
    ) external payable onlyFactory nonReentrant {
        require(msg.value == platformFee + aiServiceFee, "Incorrect fee amount");
        
        // Record the fee payment
        feeRecords[launchId] = FeeRecord({
            launchId: launchId,
            payer: payer,
            platformFee: platformFee,
            aiServiceFee: aiServiceFee,
            timestamp: block.timestamp
        });
        
        // Update totals
        totalPaidByUser[payer] += msg.value;
        totalPlatformFeesCollected += platformFee;
        totalAIFeesCollected += aiServiceFee;
        
        // Distribute fees
        if (platformFee > 0) {
            payable(treasury).transfer(platformFee);
        }
        
        if (aiServiceFee > 0) {
            payable(aiServiceProvider).transfer(aiServiceFee);
        }
        
        emit FeesProcessed(launchId, payer, platformFee, aiServiceFee);
    }

    /**
     * @dev Get fee record for a launch
     */
    function getFeeRecord(uint256 launchId) external view returns (FeeRecord memory) {
        return feeRecords[launchId];
    }

    /**
     * @dev Calculate total fees for given parameters
     */
    function calculateTotalFee(
        uint256 platformFee,
        uint256 aiServiceFee
    ) external pure returns (uint256) {
        return platformFee + aiServiceFee;
    }

    // Admin functions
    function setTreasury(address _treasury) external onlyOwner {
        require(_treasury != address(0), "Invalid treasury address");
        address oldTreasury = treasury;
        treasury = _treasury;
        emit TreasuryUpdated(oldTreasury, _treasury);
    }

    function setAIServiceProvider(address _aiServiceProvider) external onlyOwner {
        require(_aiServiceProvider != address(0), "Invalid AI service provider");
        address oldProvider = aiServiceProvider;
        aiServiceProvider = _aiServiceProvider;
        emit AIServiceProviderUpdated(oldProvider, _aiServiceProvider);
    }

    function setFactory(address _factory) external onlyOwner {
        factory = _factory;
    }

    // Emergency withdrawal (owner only)
    function emergencyWithdraw() external onlyOwner {
        payable(owner()).transfer(address(this).balance);
    }
}