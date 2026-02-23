// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/**
 * @title ServicePaymentEscrow
 * @dev 服务支付托管合约 - 安全处理 USDC 支付
 */
contract ServicePaymentEscrow is ReentrancyGuard {
    
    struct Escrow {
        address payer;
        address payee;
        address token;
        uint256 amount;
        uint256 createdAt;
        uint256 releasedAt;
        bool released;
        bool disputed;
        string serviceId;
    }
    
    mapping(bytes32 => Escrow) public escrows;
    bytes32[] public allEscrows;
    
    uint256 public platformFeePercent = 1; // 1% 平台费
    
    event EscrowCreated(
        bytes32 indexed escrowId,
        address indexed payer,
        address indexed payee,
        uint256 amount,
        string serviceId
    );
    
    event EscrowReleased(
        bytes32 indexed escrowId,
        address indexed payee,
        uint256 amount,
        uint256 fee
    );
    
    event EscrowDisputed(
        bytes32 indexed escrowId,
        address indexed disputer
    );
    
    event EscrowRefunded(
        bytes32 indexed escrowId,
        address indexed payer,
        uint256 amount
    );
    
    /**
     * @dev 创建托管
     */
    function createEscrow(
        address _payee,
        address _token,
        uint256 _amount,
        string memory _serviceId
    ) external nonReentrant returns (bytes32) {
        require(_amount > 0, "Amount must be > 0");
        require(_payee != address(0), "Invalid payee");
        require(_token != address(0), "Invalid token");
        
        // 生成唯一 ID
        bytes32 escrowId = keccak256(
            abi.encodePacked(
                msg.sender,
                _payee,
                _serviceId,
                block.timestamp
            )
        );
        
        // 转账到合约
        IERC20(_token).transferFrom(msg.sender, address(this), _amount);
        
        escrows[escrowId] = Escrow({
            payer: msg.sender,
            payee: _payee,
            token: _token,
            amount: _amount,
            createdAt: block.timestamp,
            releasedAt: 0,
            released: false,
            disputed: false,
            serviceId: _serviceId
        });
        
        allEscrows.push(escrowId);
        
        emit EscrowCreated(escrowId, msg.sender, _payee, _amount, _serviceId);
        
        return escrowId;
    }
    
    /**
     * @dev 释放托管 (收款方调用)
     */
    function releaseEscrow(bytes32 _escrowId) external nonReentrant {
        Escrow storage escrow = escrows[_escrowId];
        
        require(escrow.payee == msg.sender, "Not payee");
        require(!escrow.released, "Already released");
        require(!escrow.disputed, "Disputed");
        
        escrow.released = true;
        escrow.releasedAt = block.timestamp;
        
        // 计算费用
        uint256 fee = (escrow.amount * platformFeePercent) / 100;
        uint256 payout = escrow.amount - fee;
        
        // 转账给收款方
        IERC20(escrow.token).transfer(escrow.payee, payout);
        
        // 平台费转账 (暂时转给合约所有者)
        if (fee > 0) {
            IERC20(escrow.token).transfer(owner(), fee);
        }
        
        emit EscrowReleased(_escrowId, escrow.payee, payout, fee);
    }
    
    /**
     * @dev 退款 (付款方调用，需要时间锁)
     */
    function refundEscrow(bytes32 _escrowId) external nonReentrant {
        Escrow storage escrow = escrows[_escrowId];
        
        require(escrow.payer == msg.sender, "Not payer");
        require(!escrow.released, "Already released");
        require(block.timestamp > escrow.createdAt + 7 days, "Too early");
        
        escrow.released = true;
        
        // 全额退款
        IERC20(escrow.token).transfer(escrow.payer, escrow.amount);
        
        emit EscrowRefunded(_escrowId, escrow.payer, escrow.amount);
    }
    
    /**
     * @dev 争议 (任何一方可以发起)
     */
    function disputeEscrow(bytes32 _escrowId) external {
        Escrow storage escrow = escrows[_escrowId];
        
        require(
            msg.sender == escrow.payer || msg.sender == escrow.payee,
            "Not involved"
        );
        require(!escrow.disputed, "Already disputed");
        
        escrow.disputed = true;
        
        emit EscrowDisputed(_escrowId, msg.sender);
        
        // 这里可以添加仲裁逻辑
    }
    
    /**
     * @dev 获取托管详情
     */
    function getEscrow(bytes32 _escrowId) external view returns (
        address payer,
        address payee,
        address token,
        uint256 amount,
        uint256 createdAt,
        bool released,
        bool disputed,
        string memory serviceId
    ) {
        Escrow memory escrow = escrows[_escrowId];
        return (
            escrow.payer,
            escrow.payee,
            escrow.token,
            escrow.amount,
            escrow.createdAt,
            escrow.released,
            escrow.disputed,
            escrow.serviceId
        );
    }
    
    /**
     * @dev 获取所有托管 ID
     */
    function getAllEscrows() external view returns (bytes32[] memory) {
        return allEscrows;
    }
    
    /**
     * @dev 获取合约中的代币余额
     */
    function getTokenBalance(address _token) external view returns (uint256) {
        return IERC20(_token).balanceOf(address(this));
    }
}
