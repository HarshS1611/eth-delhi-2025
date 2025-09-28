# Orchestrator Agent - Agentverse Deployment

![ tag:eth-delhi-2025](https://img.shields.io/badge/eth--delhi--2025-3D8BD3)
![ tag:agentverse](https://img.shields.io/badge/agentverse-3D8BD3)
![ tag:orchestrator](https://img.shields.io/badge/orchestrator-3D8BD3)

## 🎭 Overview

This is the **Orchestrator Agent** for ETH Delhi 2025 - the master coordinator that orchestrates comprehensive dataset analysis by coordinating validation and legal compliance agents for complete dataset intelligence.

### Key Features:

- 🎭 **Multi-Agent Coordination**: Orchestrates validation and legal agents
- 🔄 **Workflow Management**: Manages complex analysis pipelines
- 📊 **Result Synthesis**: Combines multiple agent outputs intelligently
- ⚡ **Async Processing**: Handles concurrent agent communications
- 🛡️ **Error Resilience**: Graceful handling of agent failures

## 🚀 Quick Deploy to Agentverse

### Option 1: Direct Upload (Fastest)

1. **Visit**: [https://agentverse.ai/](https://agentverse.ai/)
2. **Login/Register** with your account
3. **Create New Agent**: Click "New Agent" → "Blank Agent"
4. **Copy Code**: Copy the entire `app.py` file content
5. **Paste & Name**: Paste code and name it "ETH Delhi Orchestrator"
6. **Deploy**: Click "Deploy" - your orchestrator is live! 🎉

### Option 2: Deploy via Render

1. **Fork/Clone** this repository
2. **Create Render Account**: [https://render.com/](https://render.com/)
3. **New Background Worker**: Connect your repo
4. **Configure**:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python app.py`
5. **Deploy**: Your agent runs 24/7 in the cloud

## 📡 Agent Configuration

```python
agent = Agent(
    name="eth_delhi_orchestrator",
    seed="eth_delhi_2025_orchestrator_agent_unique_seed",
    mailbox=True,  # ✅ Agentverse ready!
)
```

**Important**: The seed `eth_delhi_2025_orchestrator_agent_unique_seed` generates a unique blockchain address for coordinating other agents.

## 🔧 Message Protocol

### Request Comprehensive Analysis:

```python
from uagents import Model

class ComprehensiveValidationRequest(Model):
    request_id: str
    dataset_path: Optional[str] = None              # Path to dataset file
    dataset_name: str = "unknown"                   # Descriptive dataset name
    dataset_data: Optional[Dict[str, Any]] = None   # Small datasets as dict
    analysis_depth: str = "complete"                # Analysis thoroughness
    include_legal_analysis: bool = True             # Enable legal compliance check
    requester_address: str                          # Your agent address
    timestamp: str = datetime.now().isoformat()
```

### Example Request:

```json
{
  "request_id": "comprehensive_001",
  "dataset_name": "healthcare_patient_records",
  "dataset_path": "/data/patients.csv",
  "analysis_depth": "complete",
  "include_legal_analysis": true,
  "requester_address": "agent1q...your_client_address"
}
```

### Response Format:

```python
class ComprehensiveValidationResult(Model):
    request_id: str
    success: bool
    timestamp: str
    processing_time_seconds: float

    # Dataset information
    dataset_name: str
    dataset_info: Dict[str, Any]

    # Raw tool results (no combining or scoring)
    validation_tool_results: Optional[Dict[str, Any]] = None  # All validation outputs
    legal_tool_results: Optional[Dict[str, Any]] = None       # All legal outputs

    # Processing status
    validation_status: str = "unknown"  # "completed", "failed", "skipped"
    legal_status: str = "unknown"       # "completed", "failed", "skipped"
    errors: List[str] = []
    warnings: List[str] = []
```

## 🎯 Orchestration Workflow

The orchestrator manages this intelligent workflow:

### 1. **Request Processing** 📥

```python
# Initialize tracking for multi-agent coordination
active_requests[request_id] = {
    "request": msg,
    "sender": sender,
    "start_time": datetime.now(),
    "validation_status": "pending",
    "legal_status": "pending",
    "validation_result": None,
    "legal_result": None
}
```

### 2. **Dataset Preparation** 📂

```python
async def prepare_dataset(request):
    if request.dataset_data:
        return pd.DataFrame(request.dataset_data)
    elif request.dataset_path:
        # Support multiple formats
        if path.endswith('.csv'): return pd.read_csv(path)
        elif path.endswith('.json'): return pd.read_json(path)
        elif path.endswith('.xlsx'): return pd.read_excel(path)
    else:
        # Create demo dataset for testing
        return create_sample_dataset()
```

### 3. **Parallel Agent Coordination** 🤝

```python
# Run validation analysis
validation_result = await run_validation_analysis(ctx, request, dataset)

# Conditionally run legal analysis
if request.include_legal_analysis:
    legal_result = await run_legal_analysis(ctx, request, dataset)
else:
    legal_result = {"status": "skipped"}
```

### 4. **Result Synthesis** 🔄

```python
# Combine results without modification - preserve raw outputs
combined_result = ComprehensiveValidationResult(
    validation_tool_results=validation_result.get("raw_tool_outputs"),
    legal_tool_results=legal_result.get("raw_tool_outputs"),
    validation_status="completed",
    legal_status="completed"
)
```

## 📊 Analysis Coordination

### Validation Analysis Coordination

```python
async def run_validation_analysis(ctx, request, dataset):
    # Basic dataset statistics
    dataset_info = {
        "shape": dataset.shape,
        "columns": list(dataset.columns),
        "dtypes": {col: str(dtype) for col, dtype in dataset.dtypes.items()},
        "missing_values": dataset.isnull().sum().to_dict(),
        "duplicates": int(dataset.duplicated().sum())
    }

    # Quality scoring
    completeness_score = (1 - dataset.isnull().sum().sum() /
                         (dataset.shape[0] * dataset.shape[1])) * 100
    uniqueness_score = (1 - dataset.duplicated().sum() / len(dataset)) * 100

    return {
        "success": True,
        "dataset_info": dataset_info,
        "raw_tool_outputs": {
            "quality_scores": {
                "completeness_score": completeness_score,
                "uniqueness_score": uniqueness_score
            }
        }
    }
```

### Legal Analysis Coordination

```python
async def run_legal_analysis(ctx, request, dataset):
    # PII detection
    pii_indicators = 0
    pii_columns = []

    for col in dataset.columns:
        if any(pii_term in col.lower() for pii_term in
               ['email', 'phone', 'name', 'address', 'ssn', 'id']):
            pii_indicators += 1
            pii_columns.append(col)

    # Risk assessment
    pii_risk_score = min(100, (pii_indicators / len(dataset.columns)) * 100)
    risk_level = "High" if pii_risk_score >= 50 else "Medium" if pii_risk_score >= 25 else "Low"

    return {
        "success": True,
        "raw_tool_outputs": {
            "pii_analysis": {
                "pii_risk_score": pii_risk_score,
                "risk_level": risk_level,
                "pii_columns": pii_columns
            }
        }
    }
```

## 🧪 Testing Your Deployed Orchestrator

### 1. Healthcare Dataset Test

```python
request = ComprehensiveValidationRequest(
    request_id="healthcare_001",
    dataset_name="patient_clinical_data",
    dataset_data={
        "patient_id": [1001, 1002, 1003, 1004, 1005],
        "age": [34, 67, 45, 23, 56],
        "diagnosis": ["diabetes", "hypertension", "flu", "covid", "pneumonia"],
        "email": ["patient1@hospital.com", "patient2@clinic.org", None, "patient4@health.net", "patient5@medical.com"],
        "treatment_cost": [1200.50, 2300.75, 150.25, 890.00, 1750.30]
    },
    analysis_depth="complete",
    include_legal_analysis=True,
    requester_address="test_client"
)
```

### 2. Expected Comprehensive Response

```json
{
  "request_id": "healthcare_001",
  "success": true,
  "timestamp": "2025-01-XX...",
  "processing_time_seconds": 2.45,
  "dataset_name": "patient_clinical_data",
  "dataset_info": {
    "shape": [5, 5],
    "columns": ["patient_id", "age", "diagnosis", "email", "treatment_cost"],
    "missing_values": { "email": 1 },
    "duplicates": 0
  },
  "validation_tool_results": {
    "quality_scores": {
      "completeness_score": 96.0,
      "uniqueness_score": 100.0,
      "overall_quality": 98.0
    },
    "analysis_summary": "Dataset has 5 rows and 5 columns with 96.0% completeness"
  },
  "legal_tool_results": {
    "pii_analysis": {
      "pii_risk_score": 40.0,
      "risk_level": "Medium",
      "pii_columns": ["patient_id", "email"],
      "columns_analyzed": 5
    },
    "compliance_summary": {
      "overall_risk": "Medium",
      "requires_action": true,
      "recommendations": [
        "Review data usage policies",
        "Consider data anonymization"
      ]
    }
  },
  "validation_status": "completed",
  "legal_status": "completed"
}
```

### 3. Financial Dataset Test

```python
request = ComprehensiveValidationRequest(
    request_id="finance_001",
    dataset_name="transaction_records",
    dataset_data={
        "transaction_id": ["txn_001", "txn_002", "txn_003"],
        "account_number": ["123456789", "987654321", "456789123"],
        "amount": [1500.00, 250.75, 3200.50],
        "merchant": ["Amazon", "Starbucks", "Shell"],
        "timestamp": ["2025-01-01 10:30:00", "2025-01-01 14:15:00", "2025-01-01 16:45:00"]
    },
    include_legal_analysis=True
)
```

## 🎛 Status Monitoring

### Check Processing Status

```python
status_request = ValidationStatusRequest(
    request_id="healthcare_001",
    requester_address="monitoring_client"
)

# Response includes:
{
  "request_id": "healthcare_001",
  "status": "processing",  # "processing", "completed", "failed"
  "progress": {
    "validation": "completed",
    "legal": "running"
  },
  "message": "Validation: completed, Legal: running"
}
```

## 🚀 Advanced Use Cases

### 1. Validation-Only Analysis

```python
request = ComprehensiveValidationRequest(
    request_id="validation_only_001",
    dataset_name="ml_training_data",
    dataset_path="/data/features.csv",
    analysis_depth="complete",
    include_legal_analysis=False  # Skip legal analysis
)
# → Returns: Only validation_tool_results, legal_status="skipped"
```

### 2. Quick Legal Scan

```python
request = ComprehensiveValidationRequest(
    request_id="legal_scan_001",
    dataset_name="user_profiles",
    analysis_depth="basic",        # Faster processing
    include_legal_analysis=True    # Focus on compliance
)
# → Returns: Basic validation + comprehensive legal analysis
```

### 3. Demo Mode (No Dataset)

```python
request = ComprehensiveValidationRequest(
    request_id="demo_001",
    dataset_name="sample_demo_data"
    # No dataset_path or dataset_data provided
    # → Orchestrator creates sample data for demonstration
)
```

## ⚡ Performance Optimization

### Request Batching

```python
# Process multiple datasets concurrently
requests = [
    ComprehensiveValidationRequest(request_id="batch_001", ...),
    ComprehensiveValidationRequest(request_id="batch_002", ...),
    ComprehensiveValidationRequest(request_id="batch_003", ...)
]
# Send all requests - orchestrator handles concurrent processing
```

### Resource Management

```python
# For large datasets, use basic analysis
if dataset_size_mb > 50:
    request.analysis_depth = "basic"  # Faster processing

# Skip legal analysis for non-sensitive data
if dataset_type == "synthetic":
    request.include_legal_analysis = False
```

## 🛠 Error Handling

### Graceful Degradation

```python
# If validation agent fails, still attempt legal analysis
if validation_failed:
    result.validation_status = "failed"
    result.validation_tool_results = {"error": "Validation agent unavailable"}
    # Continue with legal analysis
```

### Timeout Management

```python
# Handle agent communication timeouts
async with asyncio.timeout(60):  # 60 second timeout
    result = await coordinate_agents(request)
```

### Retry Logic

```python
# Retry failed agent communications
for attempt in range(3):
    try:
        result = await send_to_agent(agent_address, request)
        break
    except Exception as e:
        if attempt == 2:  # Last attempt
            return error_result(f"Agent communication failed: {e}")
        await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

## 🌐 Multi-Agent Architecture

The orchestrator coordinates these agent types:

### Core Agents

- **Validation Agent**: Data quality and ML readiness assessment
- **Legal Agent**: Compliance and privacy analysis
- **Orchestrator**: Workflow coordination and result synthesis

### Optional Agents (Future Extensions)

- **Security Agent**: Data security and access control analysis
- **Performance Agent**: Dataset performance and optimization recommendations
- **Documentation Agent**: Automated dataset documentation generation

## ⚠️ Important Coordination Notes

1. **Agent Discovery**: Orchestrator automatically discovers available agents
2. **Fault Tolerance**: Continues processing if individual agents fail
3. **Result Preservation**: Raw agent outputs preserved without modification
4. **Async Communication**: All agent communication is asynchronous
5. **Resource Sharing**: Agents may share computational resources in Agentverse

## 🛠 Dependencies

```
uagents>=0.1.0
uagents-core>=0.1.0
pandas>=2.0.0
python-dotenv>=1.0.0
requests>=2.31.0
```

## 🔗 Related Agents

This orchestrator coordinates:

- **Dataset Validation Agent**: Comprehensive data quality analysis
- **Legal Compliance Agent**: PII scanning and regulatory compliance

## 🏆 ETH Delhi 2025

This orchestrator is the centerpiece of the **Dataset Intelligence Protocol (DIP)**, demonstrating:

- **Multi-Agent Coordination**: Orchestrated autonomous agent workflows
- **Blockchain Integration**: Decentralized agent communication
- **Intelligent Routing**: Smart agent selection and load balancing
- **Comprehensive Analysis**: End-to-end dataset intelligence pipeline

---

🎭 **Ready to orchestrate? Deploy the conductor of autonomous dataset intelligence!**
