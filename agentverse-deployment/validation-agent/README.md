# Dataset Validation Agent - Agentverse Deployment

![ tag:eth-delhi-2025](https://img.shields.io/badge/eth--delhi--2025-3D8BD3)
![ tag:agentverse](https://img.shields.io/badge/agentverse-3D8BD3)
![ tag:dataset-validation](https://img.shields.io/badge/dataset--validation-3D8BD3)

## 🎯 Overview

This is the **Dataset Validation Agent** for ETH Delhi 2025 - a sophisticated autonomous agent that performs comprehensive dataset quality analysis using multiple validation tools and ML algorithms.

### Key Features:

- 📊 **Comprehensive Analysis**: Multi-dimensional dataset quality assessment
- 🔍 **Smart Tool Selection**: Optimized analysis based on dataset characteristics
- 🎯 **Persona Tagging**: Intelligent dataset classification and recommendations
- ⚡ **Mailbox Enabled**: Ready for Agentverse deployment with async messaging
- 🛡️ **Error Resilient**: Robust error handling and graceful degradation

## 🚀 Quick Deploy to Agentverse

### Option 1: Direct Upload (Fastest)

1. **Visit**: [https://agentverse.ai/](https://agentverse.ai/)
2. **Login/Register** with your account
3. **Create New Agent**: Click "New Agent" → "Blank Agent"
4. **Copy Code**: Copy the entire `app.py` file content
5. **Paste & Name**: Paste code and name it "ETH Delhi Dataset Validator"
6. **Deploy**: Click "Deploy" - your agent is live! 🎉

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
    name="eth_delhi_dataset_validator",
    seed="eth_delhi_2025_dataset_validation_agent_unique_seed",
    mailbox=True,  # ✅ Agentverse ready!
)
```

**Important**: The seed `eth_delhi_2025_dataset_validation_agent_unique_seed` generates a unique blockchain address. Keep this consistent for the same agent identity.

## 🔧 Message Protocol

### Request Analysis:

```python
from uagents import Model

class DatasetAnalysisRequest(Model):
    request_id: str
    dataset_path: str                    # Path to dataset file
    dataset_type: Optional[str] = None   # "csv", "json", "xlsx" (auto-detect)
    analysis_depth: str = "complete"     # "basic", "standard", "complete"
    custom_parameters: Optional[Dict[str, Any]] = {}
    requester_id: Optional[str] = None
```

### Example Request:

```json
{
  "request_id": "analysis_001",
  "dataset_path": "/path/to/healthcare_data.csv",
  "dataset_type": "csv",
  "analysis_depth": "complete",
  "requester_id": "client_dashboard"
}
```

### Response Format:

```python
class DatasetAnalysisResult(Model):
    success: bool
    request_id: str
    timestamp: str
    dataset_info: Dict[str, Any]         # Basic dataset information
    raw_tool_outputs: Dict[str, Any]     # All tool results (no scoring)
    persona_tags: List[str]              # ["#Healthcare", "#TimeSeries"]
    primary_persona: str                 # "#Healthcare"
    executive_summary: str               # Human-readable summary
    recommendations: List[str]           # Actionable insights
    next_steps: List[str]               # Suggested actions
    errors: List[str] = []
    warnings: List[str] = []
```

## 🛠 Analysis Pipeline

The agent performs analysis in these steps:

### 1. **Dataset Loading** 📂

- Auto-detects format (CSV, JSON, Excel)
- Validates file integrity
- Extracts metadata (shape, columns, types)

### 2. **Smart Tool Selection** 🎯

```python
# Conditional analysis based on dataset characteristics
if num_numeric_columns > 0:
    run_outlier_detection()

if num_numeric_columns >= 2:
    run_correlation_analysis()

if dataset_size >= 50 and num_features >= 2:
    run_ml_usability_analysis()
```

### 3. **Core Analysis Tools** 🔍

- **Missing Value Analyzer**: Completeness assessment
- **Duplicate Record Detector**: Uniqueness validation
- **Data Type Consistency Checker**: Type validation
- **Outlier Detection Engine**: Statistical anomaly detection
- **Feature Correlation Mapper**: Inter-feature relationships

### 4. **High-Level Intelligence** 🧠

- **Dataset Persona Tagger**: Intelligent classification
- **Contextual Scoring Engine**: Domain-aware evaluation
- **Utility Score Synthesizer**: Comprehensive assessment

## 📊 Tool Categories

### Core Processing

- `data_loader`: Dataset ingestion and parsing
- `data_profiler`: Comprehensive profiling

### Data Integrity

- `missing_value_analyzer`: Completeness scoring
- `duplicate_record_detector`: Uniqueness assessment
- `data_type_consistency_checker`: Type validation

### Statistical Analysis

- `outlier_detection_engine`: Anomaly identification
- `feature_correlation_mapper`: Relationship analysis

### ML Usability

- `baseline_model_performance`: ML readiness assessment
- `feature_importance_analyzer`: Predictive value analysis

### High-Level Analysis

- `dataset_persona_tagger`: Intelligent classification
- `contextual_scoring_engine`: Domain-aware scoring

## 🧪 Testing Your Deployed Agent

### 1. Agentverse Chat Interface

```bash
# Find your agent in Agentverse dashboard
# Click "Chat" and send:
{
  "request_id": "test_001",
  "dataset_path": "sample.csv",
  "analysis_depth": "basic"
}
```

### 2. Python Client Example

```python
from uagents import Agent, Context, Model

# Create client agent
client = Agent(name="test_client", mailbox=True)

@client.on_event("startup")
async def send_test_request(ctx: Context):
    # Your deployed validation agent address
    validator_address = "agent1q...your_agent_address"

    request = DatasetAnalysisRequest(
        request_id="test_001",
        dataset_path="/path/to/test_data.csv",
        analysis_depth="complete",
        requester_id="test_client"
    )

    await ctx.send(validator_address, request)

client.run()
```

### 3. Expected Response

```json
{
  "success": true,
  "request_id": "test_001",
  "timestamp": "2025-01-XX...",
  "persona_tags": ["#Healthcare", "#Clinical"],
  "primary_persona": "#Healthcare",
  "executive_summary": "High-quality healthcare dataset with 95% completeness...",
  "recommendations": [
    "Consider removing outliers in age column",
    "Dataset suitable for ML training"
  ],
  "raw_tool_outputs": {
    "integrity_tools": {...},
    "statistical_tools": {...},
    "ml_tools": {...}
  }
}
```

## 🏥 Sample Use Cases

### Healthcare Data Analysis

```python
request = DatasetAnalysisRequest(
    request_id="healthcare_001",
    dataset_path="patient_records.csv",
    analysis_depth="complete"
)
# → Returns: #Healthcare persona, HIPAA considerations, clinical insights
```

### Financial Data Validation

```python
request = DatasetAnalysisRequest(
    request_id="finance_001",
    dataset_path="transaction_data.csv",
    analysis_depth="complete"
)
# → Returns: #Finance persona, fraud detection readiness, regulatory notes
```

### IoT Sensor Analysis

```python
request = DatasetAnalysisRequest(
    request_id="iot_001",
    dataset_path="sensor_readings.csv",
    analysis_depth="complete"
)
# → Returns: #IoT persona, time series patterns, anomaly detection
```

## ⚠️ Important Notes

1. **Unique Agent Identity**: Keep the same seed for consistent agent address
2. **Resource Limits**: Large datasets (>10MB) may hit Agentverse limits
3. **Async Processing**: All communication is asynchronous via mailbox
4. **Error Handling**: Agent gracefully handles tool failures and network issues
5. **Raw Outputs**: Returns raw tool results without modification for transparency

## 🚨 Troubleshooting

### Agent Not Responding?

```python
# Check agent status
status_request = AgentStatusRequest(requester_id="debug_client")
await ctx.send(agent_address, status_request)
```

### Large Dataset Issues?

```python
# Use basic analysis for large datasets
request.analysis_depth = "basic"  # Faster processing
```

### Tool Failures?

```python
# Check response.errors and response.warnings
if not response.success:
    print(f"Errors: {response.errors}")
    print(f"Warnings: {response.warnings}")
```

## 📚 Dependencies

```
uagents>=0.1.0
uagents-core>=0.1.0
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
python-dotenv>=1.0.0
```

## 🔗 Related Agents

- **Legal Compliance Agent**: PII scanning and legal validation
- **Orchestrator Agent**: Multi-agent coordination and workflow management

## 🏆 ETH Delhi 2025

This agent is part of the **Dataset Intelligence Protocol (DIP)** submission for ETH Delhi 2025, showcasing:

- Autonomous dataset validation
- Decentralized agent coordination
- Blockchain-based verification
- ML-powered analysis pipeline

---

🚀 **Ready to deploy? Copy `app.py` to Agentverse and let the autonomous validation begin!**
