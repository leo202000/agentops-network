// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title AgentRegistry
 * @dev 代理注册合约 - 记录 AI 代理信息和状态
 */
contract AgentRegistry {
    
    struct Agent {
        string name;
        string description;
        address owner;
        uint256 registeredAt;
        bool isActive;
        uint256 totalEarnings;
        uint256 completedTasks;
    }
    
    mapping(string => Agent) public agents;
    mapping(address => string[]) public ownerAgents;
    
    event AgentRegistered(
        string indexed agentId,
        string name,
        address indexed owner,
        uint256 timestamp
    );
    
    event AgentStatusChanged(
        string indexed agentId,
        bool isActive,
        uint256 timestamp
    );
    
    event TaskCompleted(
        string indexed agentId,
        uint256 earnings,
        uint256 timestamp
    );
    
    /**
     * @dev 注册新代理
     * @param agentId 代理 ID
     * @param name 代理名称
     * @param description 代理描述
     */
    function registerAgent(
        string memory agentId,
        string memory name,
        string memory description
    ) external {
        require(agents[agentId].registeredAt == 0, "Agent already exists");
        
        agents[agentId] = Agent({
            name: name,
            description: description,
            owner: msg.sender,
            registeredAt: block.timestamp,
            isActive: true,
            totalEarnings: 0,
            completedTasks: 0
        });
        
        ownerAgents[msg.sender].push(agentId);
        
        emit AgentRegistered(agentId, name, msg.sender, block.timestamp);
    }
    
    /**
     * @dev 更新代理状态
     */
    function setAgentStatus(string memory agentId, bool isActive) external {
        require(agents[agentId].owner == msg.sender, "Not owner");
        agents[agentId].isActive = isActive;
        
        emit AgentStatusChanged(agentId, isActive, block.timestamp);
    }
    
    /**
     * @dev 记录任务完成
     */
    function recordTaskCompletion(
        string memory agentId,
        uint256 earnings
    ) external {
        require(agents[agentId].owner == msg.sender, "Not owner");
        
        agents[agentId].completedTasks += 1;
        agents[agentId].totalEarnings += earnings;
        
        emit TaskCompleted(agentId, earnings, block.timestamp);
    }
    
    /**
     * @dev 获取代理信息
     */
    function getAgent(string memory agentId) external view returns (
        string memory name,
        string memory description,
        address owner,
        uint256 registeredAt,
        bool isActive,
        uint256 totalEarnings,
        uint256 completedTasks
    ) {
        Agent memory agent = agents[agentId];
        return (
            agent.name,
            agent.description,
            agent.owner,
            agent.registeredAt,
            agent.isActive,
            agent.totalEarnings,
            agent.completedTasks
        );
    }
    
    /**
     * @dev 获取所有者的代理列表
     */
    function getOwnerAgents(address owner) external view returns (string[] memory) {
        return ownerAgents[owner];
    }
}
