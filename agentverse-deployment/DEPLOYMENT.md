# ETH Delhi 2025 - Agentverse Deployment Guide

This directory contains the deployment-ready versions of our ETH Delhi 2025 agents optimized for Agentverse deployment.

## 📁 Directory Structure

```
agentverse-deployment/
├── validation-agent/
│   ├── app.py              # Dataset validation agent (mailbox-enabled)
│   ├── requirements.txt    # Python dependencies
│   └── README.md          # Deployment instructions
├── legal-agent/
│   ├── app.py              # Legal compliance agent (mailbox-enabled)
│   ├── requirements.txt    # Python dependencies
│   └── README.md          # Deployment instructions
├── orchestrator-agent/
│   ├── app.py              # Orchestrator agent (mailbox-enabled)
│   ├── requirements.txt    # Python dependencies
│   └── README.md          # Deployment instructions
└── DEPLOYMENT.md           # This file
```

## 🚀 Deployment Options

### Option 1: Direct Agentverse Upload (Recommended)

1. **Visit Agentverse**: Go to [https://agentverse.ai/](https://agentverse.ai/)
2. **Create New Agent**: Click "New Agent" and select "Blank Agent"
3. **Upload Code**: Copy and paste the `app.py` content directly into the Agentverse editor
4. **Install Dependencies**: Agentverse will automatically install packages from `requirements.txt`
5. **Deploy**: Click "Deploy" and your agent will be live!

### Option 2: Deploy via Render (Cloud Hosting)

Follow the steps in each agent's README.md for Render deployment instructions.

## 🔧 Key Agentverse Optimizations Made

### 1. **Mailbox Configuration**

```python
agent = Agent(
    name="eth_delhi_dataset_validator",
    seed="eth_delhi_2025_dataset_validation_agent_unique_seed",
    mailbox=True,  # ✅ Enable mailbox for Agentverse deployment
)
```

### 2. **Removed Local Endpoints**

- Removed `port` and `endpoint` configurations
- Agents communicate via Agentverse mailbox system

### 3. **Unique Seeds**

Each agent has a unique seed for distinct blockchain identities:

- Validation Agent: `eth_delhi_2025_dataset_validation_agent_unique_seed`
- Legal Agent: `eth_delhi_2025_legal_compliance_agent_unique_seed`
- Orchestrator: `eth_delhi_2025_orchestrator_agent_unique_seed`

### 4. **Self-Contained Code**

- Embedded essential tool functionality directly in agent code
- Removed complex external dependencies for easier deployment
- Simplified message models for reliable network communication

### 5. **Error Handling**

- Robust error handling for network communication
- Graceful degradation when tools are unavailable
- Clear error messages for debugging

## 📋 Deployment Steps

### For Each Agent:

1. **Copy Agent Code**

   ```bash
   # Navigate to the specific agent directory
   cd agentverse-deployment/validation-agent/
   cat app.py  # Copy this content
   ```

2. **Create Agent on Agentverse**

   - Go to [Agentverse](https://agentverse.ai/)
   - Click "New Agent"
   - Paste the `app.py` code
   - Set agent name (e.g., "ETH Delhi Dataset Validator")

3. **Install Dependencies**

   - Copy `requirements.txt` content to Agentverse
   - Dependencies are automatically installed

4. **Deploy**
   - Click "Deploy"
   - Wait for deployment confirmation
   - Note the agent address for inter-agent communication

## 🌐 Agent Addresses (After Deployment)

After deploying each agent, you'll get unique addresses like:

```
Validation Agent: agent1q...abc123
Legal Agent: agent1q...def456
Orchestrator: agent1q...ghi789
```

## 📡 Testing Deployed Agents

### 1. **Using Agentverse Chat Interface**

- Find your deployed agent in the Agentverse dashboard
- Click "Chat" to interact with the agent directly
- Send test messages to verify functionality

### 2. **Agent-to-Agent Communication**

- Use the orchestrator agent to coordinate validation requests
- Agents will communicate via Agentverse mailbox system

### 3. **API Integration**

- Agentverse provides HTTP APIs to interact with your agents
- Use agent addresses to send programmatic requests

## 🛠 Message Examples

### Request Dataset Analysis:

```json
{
  "request_id": "test_001",
  "dataset_name": "sample_healthcare_data",
  "dataset_data": {
    "patient_id": [1, 2, 3],
    "age": [25, 30, 35],
    "condition": ["flu", "cold", "fever"]
  },
  "analysis_depth": "complete",
  "requester_id": "test_client"
}
```

### Request Legal Compliance Check:

```json
{
  "request_id": "legal_001",
  "dataset_name": "user_data",
  "dataset_path": "/path/to/data.csv",
  "analysis_type": "full",
  "include_ner": true,
  "requester_address": "agent1q...xyz"
}
```

## 🚨 Important Notes

1. **Unique Seeds**: Each deployed agent must have a unique seed to avoid address conflicts
2. **Network Communication**: Agents communicate asynchronously via Agentverse mailbox
3. **Resource Limits**: Be mindful of Agentverse resource limits for large datasets
4. **Error Handling**: Always include proper error handling for network failures
5. **Testing**: Test each agent individually before deploying the full system

## 📚 Additional Resources

- [Agentverse Documentation](https://docs.agentverse.ai/)
- [uAgents Framework](https://github.com/fetchai/uAgents)
- [Fetch.ai Innovation Lab](https://innovationlab.fetch.ai/)
- [ETH Delhi 2025 Project Repository](../README.md)

## 🏆 ETH Delhi 2025 Integration

These agents are specifically designed for the ETH Delhi 2025 hackathon, featuring:

- **Dataset Intelligence Protocol (DIP)** integration
- **Autonomous dataset validation**
- **Legal compliance checking**
- **Blockchain-based verification**
- **Decentralized agent coordination**

---

🚀 **Ready to deploy? Start with the validation-agent and work your way up to the orchestrator!**
