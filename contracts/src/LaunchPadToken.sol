// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "openzeppelin-contracts/contracts/token/ERC20/ERC20.sol";
import "openzeppelin-contracts/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "openzeppelin-contracts/contracts/access/Ownable.sol";

/**
 * @title LaunchpadToken
 * @dev ERC20 token created through the TokenFactory with enhanced features
 */
contract LaunchpadToken is ERC20, ERC20Burnable, Ownable {
    
    address public factory;
    address public creator;
    uint256 public launchTime;
    bool public tradingEnabled;
    
    // Token metadata
    mapping(string => string) public metadata;
    
    // Events
    event TradingEnabled();
    event MetadataUpdated(string key, string value);
    
    modifier onlyFactoryOrCreator() {
        require(
            msg.sender == factory || msg.sender == creator,
            "Only factory or creator"
        );
        _;
    }

    constructor(
        string memory name,
        string memory symbol,
        uint256 totalSupply,
        address _creator,
        address _factory
    ) ERC20(name, symbol) Ownable(_creator) {
        creator = _creator;
        factory = _factory;
        launchTime = block.timestamp;
        tradingEnabled = true; // Enable trading immediately
        
        // Mint total supply to creator
        _mint(_creator, totalSupply);
    }

    /**
     * @dev Enable trading (can be used for phased launches)
     */
    function enableTrading() external onlyFactoryOrCreator {
        tradingEnabled = true;
        emit TradingEnabled();
    }

    /**
     * @dev Set token metadata
     */
    function setMetadata(string memory key, string memory value) external onlyFactoryOrCreator {
        metadata[key] = value;
        emit MetadataUpdated(key, value);
    }

    /**
     * @dev Get token metadata
     */
    function getMetadata(string memory key) external view returns (string memory) {
        return metadata[key];
    }

    /**
     * @dev Override transfer to check trading status
     */
    function _update(
        address from,
        address to,
        uint256 value
    ) internal virtual override {
        // Allow minting (from == address(0)) and factory operations
        if (from != address(0) && from != factory) {
            require(tradingEnabled, "Trading not enabled yet");
        }
        
        super._update(from, to, value);
    }

    /**
     * @dev Get token info
     */
    function getTokenInfo() external view returns (
        string memory tokenName,
        string memory tokenSymbol,
        uint256 supply,
        address tokenCreator,
        uint256 tokenLaunchTime,
        bool trading
    ) {
        return (
            name(),
            symbol(),
            totalSupply(),
            creator,
            launchTime,
            tradingEnabled
        );
    }
}