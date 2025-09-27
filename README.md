# ETH Delhi 2025 - Dataset Validation Agent

![ETH Delhi 2025](https://img.shields.io/badge/ETH%20Delhi-2025-orange.svg)
![Fetch.ai](https://img.shields.io/badge/Fetch.ai-uAgents-blue.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-green.svg)
![Status](https://img.shields.io/badge/Status-Ready%20for%20Demo-success.svg)

A sophisticated AI agent system built with Fetch.ai's uAgents framework for autonomous dataset validation and quality assessment. This project provides comprehensive dataset analysis with context-aware scoring and persona-based recommendations for optimal research applications.

## 🎯 Project Overview

This hackathon project creates intelligent agents that can autonomously analyze datasets and provide nuanced quality assessments. Unlike traditional data validation tools that provide generic quality scores, our system identifies specific research domains where each dataset excels and provides context-aware scoring.

### Key Features

- **18 Specialized Analysis Tools**: From basic data loading to advanced legal compliance checking
- **Context-Aware Scoring**: Multiple purpose-driven scores instead of single quality metrics  
- **Persona-Based Tagging**: Automatic identification of optimal research applications
- **Legal Compliance**: Dataset fingerprinting and PII detection for privacy protection
- **Comprehensive Synthesis**: Single Overall Utility Score with detailed executive summary
- **Production-Ready**: Autonomous agents with proper error handling and logging

## 🏗️ Architecture

### Tool Categories

#### 1. Core Data Processing Tools (4 tools)
- **Data Loader Tool**: Multi-format dataset loading (CSV, JSON, Parquet, Excel)
- **Data Profiler Tool**: Comprehensive statistical and quality profiling
- **Validation Rules Tool**: Custom rule-based validation with built-in checks
- **Report Generator Tool**: Multi-format report generation (JSON, Markdown)

#### 2. Data Integrity and Completeness Tools (3 tools)
- **Missing Value Analyzer**: Advanced missing data analysis with pattern detection
- **Duplicate Record Detector**: Intelligent duplicate detection with group analysis
- **Data Type Consistency Checker**: Type validation with improvement suggestions

#### 3. Statistical and Distributional Analysis Tools (3 tools)
- **Outlier Detection Engine**: Multi-method outlier detection (Z-score, IQR, Isolation Forest)
- **Class Balance Assessor**: Classification balance analysis with imbalance scoring
- **Feature Correlation Mapper**: Correlation analysis with multicollinearity detection

#### 4. Machine Learning Usability Tools (3 tools)
- **Baseline Model Performance**: ML readiness assessment through model training
- **Feature Importance Analyzer**: Tree-based feature importance and information distribution
- **Data Separability Scorer**: Class separability using PCA and dimensionality reduction

#### 5. High-Level Analysis Tools (3 tools)
- **Dataset Persona Tagger**: Research domain identification using heuristic rules
- **Contextual Scoring Engine**: Multiple purpose-driven quality scores
- **Utility Score Synthesizer**: Final score synthesis with executive summary

#### 6. Legal Compliance Tools (2 tools)
- **Dataset Fingerprinting & Source Checker**: Verify dataset originality and check against known public datasets using SHA-256 fingerprinting
- **PII Scanner**: Automatically detect sensitive personal data for privacy protection and GDPR/CCPA compliance

## 🎯 Dataset Personas & Scoring

### Supported Research Personas

| Persona | Description | Key Characteristics |
|---------|-------------|-------------------|
| `#AnomalyDetection` | Rare event detection | High class imbalance (>10:1), minority class <5% |
| `#FraudResearch` | Financial fraud detection | Extreme imbalance (>20:1), minority class <2% |
| `#FairnessAudit` | Bias detection studies | Demographic features, measurable imbalance |
| `#GeneralPurposeML` | Standard ML applications | High completeness (>90%), balanced classes |
| `#PredictiveModeling` | Forecasting applications | Strong ML signals, good separability (>60%) |
| `#ImbalancedLearning` | Imbalanced learning research | Moderate imbalance (5:1-20:1) |
| `#ModelRobustnessTesting` | Robustness evaluation | High outliers (>10%), missing data (>5%) |
| `#AdversarialTraining` | Adversarial ML research | Very high outliers (>15%), poor separability |
| `#SociologicalAnalysis` | Social science research | Demographic features, diverse classes |
| `#DataQualityBenchmark` | Data cleaning research | Multiple quality issues present |

### Contextual Scoring Lenses

#### General Purpose Score (0-100)
**Purpose**: Overall dataset quality for standard ML tasks
- **Weights**: Completeness (25%), Consistency (20%), Balance (20%), Cleanliness (15%), ML Readiness (20%)
- **Penalties**: High missing data, severe imbalance, many duplicates
- **Best For**: Clean, balanced datasets ready for immediate ML use

#### Anomaly Research Score (0-100) 
**Purpose**: Quality for anomaly detection and rare event research
- **Weights**: Imbalance Presence (35%), Minority Completeness (25%), Overall Completeness (15%), Separability (15%), Cleanliness (10%)
- **Bonuses**: High imbalance (+25 points), extreme imbalance (+40 points)
- **Best For**: Highly imbalanced datasets with rare positive cases

#### Fairness Audit Score (0-100)
**Purpose**: Quality for bias detection and fairness research  
- **Weights**: Demographic Presence (30%), Bias Detectability (25%), Completeness (20%), Sample Diversity (15%), Feature Richness (10%)
- **Bonuses**: Has demographic features (+30 points), imbalance present (+20 points)
- **Best For**: Datasets with demographic features and detectable bias patterns

#### Predictive Modeling Score (0-100)
**Purpose**: Quality for forecasting and predictive analytics
- **Weights**: ML Performance (30%), Feature Importance (25%), Separability (20%), Completeness (15%), Consistency (10%)
- **Penalties**: Weak signals, poor separability
- **Best For**: Datasets with strong predictive signals and clear patterns

#### Robustness Testing Score (0-100)
**Purpose**: Quality for testing model robustness and resilience
- **Weights**: Noise Presence (30%), Outlier Presence (25%), Missing Patterns (20%), Type Inconsistencies (15%), Completeness (10%)
- **Bonuses**: High outliers (+20 points), missing data (+15 points), type issues (+10 points)
- **Best For**: Noisy datasets with quality challenges

#### Research Benchmark Score (0-100)
**Purpose**: Quality as a research benchmark dataset
- **Weights**: Completeness (20%), Documentation (20%), Balance (15%), Size Adequacy (15%), Feature Diversity (15%), Reproducibility (15%)
- **Bonuses**: Large sample size (+15 points), balanced classes (+20 points)
- **Best For**: Well-documented, comprehensive datasets suitable for academic research

## 🔮 Final Scoring System

### Overall Utility Score Formula
```
Overall Utility Score = (Highest Contextual Score / 100) × Data Integrity Score

Where:
Data Integrity Score = (0.5 × Completeness) + (0.3 × Consistency) + (0.2 × Duplicate Score)
```

### Utility Grades

| Grade | Score Range | Description | Publication Ready |
|-------|-------------|-------------|------------------|
| A+ | 90-100 | Exceptional | ✅ Yes |
| A | 85-89 | Excellent | ✅ Yes |
| A- | 80-84 | Very Good | ✅ Yes |
| B+ | 75-79 | Good | ✅ Yes |
| B | 70-74 | Above Average | ⚠️ Minor improvements |
| B- | 65-69 | Satisfactory | ⚠️ Minor improvements |
| C+ | 60-64 | Fair | ❌ Preprocessing needed |
| C | 55-59 | Acceptable | ❌ Preprocessing needed |
| C- | 50-54 | Below Average | ❌ Preprocessing needed |
| D | 40-49 | Poor | ❌ Major improvements needed |
| F | 0-39 | Unacceptable | ❌ Not recommended |

## 🚀 Getting Started

### Prerequisites

```bash
# Install all dependencies
pip install -r agents/requirements.txt
```

### uAgents Integration

Our system is fully integrated with Fetch.ai's uAgents framework following all best practices:

- ✅ **Proper Agent Patterns**: Agent initialization, message models, event handlers
- ✅ **Network Ready**: Almanac integration, agent discovery, distributed processing
- ✅ **Production Ready**: Error handling, logging, state management
- ✅ **Bureau Support**: Multi-agent coordination for scalability

**📖 See [UAGENTS_INTEGRATION.md](agents/UAGENTS_INTEGRATION.md) for complete integration guide**

## ⚖️ Legal Compliance Features

Our system includes advanced legal compliance tools to ensure dataset usage adheres to privacy regulations and intellectual property requirements.

### Dataset Fingerprinting & Source Checker 🔍

**Purpose**: Verify dataset originality by checking against known public datasets to avoid intellectual property issues.

**How It Works**:
1. **Content Fingerprinting**: Creates format-agnostic SHA-256 fingerprint by normalizing data (sorting columns/rows)
2. **Known Dataset Comparison**: Checks against database of public datasets from Kaggle, Hugging Face, UCI ML Repository
3. **License Detection**: Identifies licensing requirements and attribution needs
4. **Originality Scoring**: 0-100 score based on uniqueness and source verification

**Output**: Verification status (Original/Known Public Dataset/Potential Match), originality score, source attribution, legal compliance assessment.

### PII Scanner 🕵️

**Purpose**: Automatically detect sensitive personal data for privacy protection and GDPR/CCPA compliance.

**Detection Methods**:
- **Pattern Matching**: Regex detection for emails, phones, SSN, Aadhaar/PAN, IP addresses, credit cards
- **Named Entity Recognition**: SpaCy NLP model for person names, locations, organizations
- **Multi-Region Support**: US, India, UK specific patterns

**Compliance Assessment**:
- **GDPR**: Consent requirements, data subject rights, breach notification needs
- **CCPA**: Personal information detection, consumer rights assessment
- **Risk Scoring**: 0-100 risk score with actionable mitigation recommendations

### Legal Compliance Agent 🤖

Autonomous agent providing distributed legal compliance checking through Fetch.ai uAgents:

```python
from legal_compliance_agent import LegalComplianceRequest

# Request comprehensive legal analysis
request = LegalComplianceRequest(
    request_id="compliance_001",
    dataset_name="customer_data",
    dataset_data=your_dataset,
    analysis_type="full",  # "full"|"fingerprinting"|"pii_scan"
    include_ner=True,
    requester_address=your_agent.address
)
```

**Agent Capabilities**:
- Autonomous multi-request processing
- Real-time status updates
- Comprehensive risk assessment
- Regulatory compliance guidance
- Network-distributed processing

**📖 See [LEGAL_TOOLS_DOCUMENTATION.md](agents/LEGAL_TOOLS_DOCUMENTATION.md) for complete legal compliance guide**

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/HarshS1611/eth-delhi-2025.git
   cd eth-delhi-2025
   ```

2. **Install dependencies**
   ```bash
   pip install -r agents/requirements.txt
   ```

3. **Test the system**
   ```bash
   cd agents
   python test_high_level_tools.py
   python test_legal_tools.py
   python uagents_integration_verification.py
   ```

4. **Optional: Install advanced PII detection**
   ```bash
   pip install spacy>=3.4.0
   python -m spacy download en_core_web_sm
   ```

### Running the Agents

#### Option 1: Single Validation Agent
```bash
cd agents
python enhanced_validation_agent.py
```

#### Option 2: Multi-Agent Bureau (Recommended for Production)
```bash
cd agents
python enhanced_validation_agent.py bureau
```

#### Option 3: Legal Compliance Bureau
```bash
cd agents
python legal_compliance_agent.py
```

#### Option 4: Client-Server Demo
```bash
# Terminal 1: Start validation agent
cd agents
python enhanced_validation_agent.py

# Terminal 2: Start client agent  
cd agents
python analysis_client.py

# Terminal 3: Run integration demo
cd agents
python analysis_client.py demo
```

### Basic Usage

#### Individual Tool Usage

```python
from agents.tools import tool_registry
import pandas as pd

# Load a dataset
data_loader = tool_registry.get_tool("data_loader")
result = await data_loader.execute("path/to/dataset.csv")

if result["success"]:
    df = result["data"]
    
    # Analyze missing values
    missing_analyzer = tool_registry.get_tool("missing_value_analyzer")
    missing_result = await missing_analyzer.execute(df)
    
    print(f"Integrity Score: {missing_result['integrity_score']}/100")
```

#### Complete Analysis Workflow

```python
from agents.tools import (
    DatasetPersonaTaggerTool,
    ContextualScoringEngineTool, 
    UtilityScoreSynthesizerTool
)

# Step 1: Run foundational analysis (13 tools)
analysis_results = {}
# ... populate with results from all foundational tools

# Step 2: Identify dataset personas
tagger = DatasetPersonaTaggerTool()
persona_result = await tagger.execute(analysis_results)
persona_tags = persona_result["persona_tags"]

# Step 3: Calculate contextual scores
scorer = ContextualScoringEngineTool()
scoring_result = await scorer.execute(analysis_results, persona_tags)
contextual_scores = scoring_result["contextual_scores"]

# Step 4: Synthesize final utility score
synthesizer = UtilityScoreSynthesizerTool()
final_result = await synthesizer.execute(
    analysis_results, persona_tags, contextual_scores
)

print(f"Overall Utility Score: {final_result['overall_utility_score']}/100")
print(f"Primary Persona: {final_result['primary_persona']}")
print(f"Grade: {final_result['utility_grade']['grade']}")
print(f"Summary: {final_result['executive_summary']}")
```

## 🧪 Testing

### Run All Tests

```bash
# Test foundational tools
python test_tools.py

# Test statistical analysis tools  
python test_statistical_tools.py

# Test ML usability tools
python test_ml_usability_tools.py

# Test high-level analysis tools
python test_high_level_tools.py
```

### Example Test Results

```
🎯 Testing Dataset Persona Tagger Tool...
✅ Success: 7 personas identified
Primary Persona: #FraudResearch
All Personas: ['#AnomalyDetection', '#FraudResearch', '#ImbalancedLearning']

🏆 Testing Contextual Scoring Engine Tool...  
✅ Success: 2 scores calculated
Best Context: anomaly_research_score (100.0)

🔮 Testing Utility Score Synthesizer Tool...
✅ Success: Overall Utility Score calculated
Overall Utility Score: 87.1/100
Utility Grade: A (Excellent)
```

## 📊 Tool Reference

### All 18 Available Tools

| Category | Tool Name | Purpose | Score Output |
|----------|-----------|---------|--------------|
| **Core** | `data_loader` | Multi-format data loading | N/A |
| **Core** | `data_profiler` | Statistical profiling | N/A |
| **Core** | `validation_rules` | Rule-based validation | 0-100 |
| **Core** | `report_generator` | Report generation | N/A |
| **Integrity** | `missing_value_analyzer` | Missing data analysis | 0-100 |
| **Integrity** | `duplicate_record_detector` | Duplicate detection | 0-100 |
| **Integrity** | `data_type_consistency_checker` | Type consistency | 0-100 |
| **Statistical** | `outlier_detection_engine` | Outlier detection | 0-100 |
| **Statistical** | `class_balance_assessor` | Balance analysis | 0-100 |
| **Statistical** | `feature_correlation_mapper` | Correlation analysis | 0-100 |
| **ML Usability** | `baseline_model_performance` | ML readiness | 0-100 |
| **ML Usability** | `feature_importance_analyzer` | Information analysis | 0-100 |
| **ML Usability** | `data_separability_scorer` | Separability analysis | 0-100 |
| **High-Level** | `dataset_persona_tagger` | Research domain tagging | Tags |
| **High-Level** | `contextual_scoring_engine` | Context-aware scoring | Multiple 0-100 |
| **High-Level** | `utility_score_synthesizer` | Final score synthesis | 0-100 |
| **Legal** | `dataset_fingerprinting` | Dataset originality verification | Originality 0-100 |
| **Legal** | `pii_scanner` | Privacy risk assessment | PII Risk 0-100 |

### Scoring Breakdown Examples

#### Excellent General Purpose Dataset (Score: 91.6/100)
- **Data Integrity**: 97.6/100 (Completeness: 98%, Consistency: 96%, Duplicates: 99%)
- **Best Context**: General Purpose Score (93.9/100)
- **Grade**: A+ (Exceptional)
- **Recommendation**: Ready for immediate production use

#### High-Quality Anomaly Detection Dataset (Score: 87.1/100)  
- **Data Integrity**: 94.7/100 (Completeness: 95%, Consistency: 92%, Duplicates: 98%)
- **Best Context**: Anomaly Research Score (100.0/100)
- **Grade**: A (Excellent)
- **Recommendation**: Premier candidate for anomaly detection research

#### Challenging Robustness Testing Dataset (Score: 44.9/100)
- **Data Integrity**: 69.0/100 (Completeness: 65%, Consistency: 75%, Duplicates: 70%)
- **Best Context**: Robustness Testing Score (86.1/100)
- **Grade**: D (Poor)
- **Recommendation**: Not suitable for production, excellent for robustness testing

## 🤝 Contributing

This project is designed for ETH Delhi 2025 hackathon. Contributions welcome for:

- Additional dataset personas
- New scoring lenses  
- Enhanced analysis algorithms
- Integration improvements
- Documentation updates

## 📜 License

This project is developed for ETH Delhi 2025 hackathon. See LICENSE file for details.

## 🙏 Acknowledgments

- **Fetch.ai** for the uAgents framework
- **ETH Delhi 2025** organizers
- **Open source community** for foundational libraries

---

**Built with ❤️ for ETH Delhi 2025 using Fetch.ai's uAgents framework**