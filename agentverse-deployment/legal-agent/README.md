# Legal Compliance Agent - Agentverse Deployment

![ tag:eth-delhi-2025](https://img.shields.io/badge/eth--delhi--2025-3D8BD3)
![ tag:agentverse](https://img.shields.io/badge/agentverse-3D8BD3)
![ tag:legal-compliance](https://img.shields.io/badge/legal--compliance-3D8BD3)

## ⚖️ Overview

This is the **Legal Compliance Agent** for ETH Delhi 2025 - an autonomous agent that performs comprehensive legal compliance analysis including PII scanning, dataset fingerprinting, and regulatory compliance checking.

### Key Features:

- 🕵️ **PII Detection**: Advanced personally identifiable information scanning
- 🔍 **Dataset Fingerprinting**: Unique dataset identification and verification
- ⚖️ **Compliance Assessment**: GDPR, HIPAA, and privacy regulation analysis
- 🛡️ **Risk Scoring**: Intelligent risk assessment and recommendations
- ⚡ **Mailbox Enabled**: Ready for Agentverse deployment with async messaging

## 🚀 Quick Deploy to Agentverse

### Option 1: Direct Upload (Fastest)

1. **Visit**: [https://agentverse.ai/](https://agentverse.ai/)
2. **Login/Register** with your account
3. **Create New Agent**: Click "New Agent" → "Blank Agent"
4. **Copy Code**: Copy the entire `app.py` file content
5. **Paste & Name**: Paste code and name it "ETH Delhi Legal Compliance"
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
    name="eth_delhi_legal_compliance",
    seed="eth_delhi_2025_legal_compliance_agent_unique_seed",
    mailbox=True,  # ✅ Agentverse ready!
)
```

**Important**: The seed `eth_delhi_2025_legal_compliance_agent_unique_seed` generates a unique blockchain address for legal compliance operations.

## 🔧 Message Protocol

### Request Compliance Analysis:

```python
from uagents import Model

class LegalComplianceRequest(Model):
    request_id: str
    dataset_name: str
    dataset_path: Optional[str] = None              # File path to dataset
    dataset_data: Optional[Dict[str, Any]] = None   # Small datasets as dict
    analysis_type: str = "full"                     # "full", "fingerprinting", "pii_scan"
    include_ner: bool = True                        # Include NER-based PII detection
    requester_address: str
```

### Example Request:

```json
{
  "request_id": "legal_001",
  "dataset_name": "customer_database",
  "dataset_path": "/path/to/customer_data.csv",
  "analysis_type": "full",
  "include_ner": true,
  "requester_address": "agent1q...client_address"
}
```

### Response Format:

```python
class LegalComplianceResult(Model):
    request_id: str
    success: bool
    dataset_name: str
    analysis_type: str

    # Raw analysis outputs (no combined scoring)
    raw_tool_outputs: Dict[str, Any]     # All tool results as-is

    # High-level assessment
    legal_summary: str                   # Executive summary
    requires_action: bool                # True if compliance issues found
    key_findings: List[str]              # Major discoveries
    critical_recommendations: List[str]   # Priority actions

    # Processing metadata
    error_message: Optional[str] = None
    analysis_timestamp: str
    processing_time_seconds: float = 0.0
    errors: List[str] = []
```

## 🔍 Analysis Pipeline

The agent performs comprehensive legal analysis in these stages:

### 1. **Dataset Fingerprinting** 🔐

```python
# Creates unique cryptographic fingerprint
fingerprint_data = {
    "dataset_name": dataset_name,
    "shape": dataset.shape,
    "columns": sorted(dataset.columns.tolist()),
    "dtypes": {col: str(dtype) for col, dtype in dataset.dtypes.items()}
}

dataset_fingerprint = hashlib.sha256(fingerprint_str.encode()).hexdigest()
```

**Features**:

- **Unique Identity**: SHA-256 hash of dataset structure
- **Originality Scoring**: Heuristic-based originality assessment
- **Verification Status**: Known dataset detection
- **Tamper Detection**: Structure integrity verification

### 2. **PII Detection Engine** 🕵️

```python
pii_patterns = {
    'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    'phone': r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b',
    'ssn': r'\b\d{3}-?\d{2}-?\d{4}\b',
    'credit_card': r'\b(?:\d{4}[-\s]?){3}\d{4}\b'
}
```

**Detection Methods**:

- **Regex Patterns**: Email, phone, SSN, credit cards
- **Column Name Analysis**: PII keyword detection
- **Statistical Analysis**: Pattern frequency assessment
- **Risk Categorization**: High/Medium/Low risk classification

### 3. **Compliance Assessment** ⚖️

```python
# Risk level calculation
if pii_risk_score >= 70:
    risk_level = "High"      # Immediate action required
elif pii_risk_score >= 40:
    risk_level = "Medium"    # Review recommended
elif pii_risk_score >= 20:
    risk_level = "Low"       # Monitor
else:
    risk_level = "Minimal"   # Compliant
```

## 📊 Analysis Types

### Full Analysis (`"full"`)

- Complete dataset fingerprinting
- Comprehensive PII scanning
- Regulatory compliance assessment
- Risk scoring and recommendations

### Fingerprinting Only (`"fingerprinting"`)

- Dataset identity verification
- Originality assessment
- Known dataset detection
- Structural integrity check

### PII Scan Only (`"pii_scan"`)

- Personal data identification
- Privacy risk assessment
- Column-level risk analysis
- GDPR compliance check

## 🧪 Testing Your Deployed Agent

### 1. Basic PII Test

```python
request = LegalComplianceRequest(
    request_id="pii_test_001",
    dataset_name="test_customer_data",
    dataset_data={
        "customer_id": [1, 2, 3],
        "email": ["john@example.com", "jane@test.org", "bob@demo.net"],
        "phone": ["555-123-4567", "555-987-6543", "555-456-7890"],
        "purchase_amount": [99.99, 149.50, 75.25]
    },
    analysis_type="pii_scan",
    include_ner=True,
    requester_address="test_client"
)
```

### 2. Expected PII Response

```json
{
  "success": true,
  "request_id": "pii_test_001",
  "legal_summary": "Legal Analysis Complete - Risk Level: High, Compliance Score: 45.0/100",
  "requires_action": true,
  "key_findings": [
    "PII risk score: 66.7/100",
    "PII risk level: High",
    "Columns with PII: 2"
  ],
  "critical_recommendations": [
    "Review 2 columns with potential PII data",
    "Consider data anonymization or pseudonymization"
  ],
  "raw_tool_outputs": {
    "pii_scanner": {
      "success": true,
      "pii_risk_score": 66.7,
      "risk_level": "High",
      "risk_assessment": {
        "columns_with_pii": 2,
        "pii_columns": ["email", "phone"],
        "column_risks": {
          "email": "High",
          "phone": "High"
        }
      }
    }
  }
}
```

### 3. Fingerprinting Test

```python
request = LegalComplianceRequest(
    request_id="fingerprint_001",
    dataset_name="healthcare_records",
    dataset_path="/path/to/medical_data.csv",
    analysis_type="fingerprinting",
    requester_address="compliance_team"
)
```

## 🏥 Use Case Examples

### Healthcare Data Compliance

```python
# HIPAA compliance check for medical records
request = LegalComplianceRequest(
    request_id="hipaa_001",
    dataset_name="patient_records",
    dataset_path="medical_db.csv",
    analysis_type="full"
)
# → Returns: PHI detection, HIPAA risk assessment, de-identification recommendations
```

### Financial Services Compliance

```python
# PCI DSS and financial regulation compliance
request = LegalComplianceRequest(
    request_id="finserv_001",
    dataset_name="transaction_data",
    analysis_type="full"
)
# → Returns: Payment card detection, financial PII risks, regulatory guidance
```

### GDPR Compliance Assessment

```python
# European data privacy compliance
request = LegalComplianceRequest(
    request_id="gdpr_001",
    dataset_name="eu_customer_data",
    analysis_type="pii_scan",
    include_ner=True
)
# → Returns: Personal data inventory, GDPR Article 30 compliance, consent requirements
```

## 📈 Risk Scoring System

### PII Risk Score (0-100)

- **0-19**: Minimal risk - No obvious personal data
- **20-39**: Low risk - Limited personal identifiers
- **40-69**: Medium risk - Moderate PII presence
- **70-100**: High risk - Significant personal data exposure

### Originality Score (0-100)

- **0-39**: Low originality - Common dataset structure
- **40-79**: Medium originality - Some unique characteristics
- **80-100**: High originality - Novel dataset structure

### Overall Compliance Score

```python
compliance_score = 100.0
- originality_deductions    # Based on known datasets
- pii_risk_deductions      # Based on personal data exposure
- regulatory_deductions    # Based on compliance violations
```

## 🚨 Critical Recommendations

The agent provides actionable compliance guidance:

### High Priority Actions

- **Data Anonymization**: Remove direct identifiers
- **Access Controls**: Implement role-based data access
- **Encryption**: Secure data at rest and in transit
- **Consent Management**: Verify data collection permissions

### Medium Priority Actions

- **Data Retention**: Review retention policies
- **Documentation**: Update privacy notices
- **Training**: Staff privacy awareness programs
- **Monitoring**: Implement ongoing compliance checks

### Regulatory Guidance

- **GDPR**: Right to erasure, data portability, consent
- **HIPAA**: PHI safeguards, minimum necessary rule
- **CCPA**: Consumer rights, opt-out mechanisms
- **SOX**: Data integrity, audit trails

## ⚠️ Important Compliance Notes

1. **Not Legal Advice**: Agent provides technical analysis, consult legal professionals
2. **Regional Variations**: Compliance requirements vary by jurisdiction
3. **False Positives**: Manual review recommended for critical decisions
4. **Data Sensitivity**: Agent processes metadata, not actual sensitive content
5. **Continuous Monitoring**: Compliance is ongoing, not one-time assessment

## 🛠 Dependencies

```
uagents>=0.1.0
uagents-core>=0.1.0
pandas>=2.0.0
numpy>=1.24.0
python-dotenv>=1.0.0
requests>=2.31.0
```

## 🔗 Related Agents

- **Dataset Validation Agent**: Data quality and ML readiness assessment
- **Orchestrator Agent**: Coordinates comprehensive validation workflows

## 🏆 ETH Delhi 2025

This agent is part of the **Dataset Intelligence Protocol (DIP)** submission, featuring:

- Autonomous legal compliance checking
- Blockchain-based compliance verification
- Decentralized regulatory assessment
- Privacy-preserving analysis techniques

---

⚖️ **Ready for deployment? Ensure your data meets legal standards with autonomous compliance checking!**
