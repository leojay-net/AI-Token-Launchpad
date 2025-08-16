// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title IFeeManager
 * @dev Interface for the FeeManager contract
 */
interface IFeeManager {
    /**
     * @dev Process fees for a token launch
     * @param launchId The launch ID
     * @param payer The address paying the fees
     * @param platformFee The platform fee amount
     * @param aiServiceFee The AI service fee amount
     */
    function processFees(
        uint256 launchId,
        address payer,
        uint256 platformFee,
        uint256 aiServiceFee
    ) external payable;

    /**
     * @dev Calculate total fee required
     * @param platformFee The platform fee
     * @param aiServiceFee The AI service fee
     * @return Total fee amount
     */
    function calculateTotalFee(
        uint256 platformFee,
        uint256 aiServiceFee
    ) external pure returns (uint256);
}