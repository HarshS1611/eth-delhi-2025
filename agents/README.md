# Local Dataset Validation Agent with Tools System

A Fetch.ai uAgent for local dataset validation development - ETH Delhi 2025.

## Overview

This is a clean, local-focused validation agent built with a modular tools system for developing and testing dataset validation logic without external dependencies.

## Architecture

The agent is built using a **tools-based architecture** with the following components:

### 🛠️ Tools System (13 Specialized Tools)
- **Core Tools (4)**:
  - **`DataLoaderTool`**: Load datasets from various formats (CSV, JSON, Parquet, Excel)
  - **`DataProfilerTool`**: Generate comprehensive data quality profiles
  - **`ValidationRulesTool`**: Execute validation rules (completeness, types, ranges, uniqueness)
  - **`ReportGeneratorTool`**: Generate detailed reports in multiple formats
- **Data Integrity Tools (3)**:
  - **`MissingValueAnalyzerTool`**: Analyze missing data patterns with scoring
  - **`DuplicateRecordDetectorTool`**: Detect and score duplicate records
  - **`DataTypeConsistencyCheckerTool`**: Check data type consistency and schema compliance
- **Statistical Analysis Tools (3)**:
  - **`OutlierDetectionEngineTool`**: Multi-method outlier detection (Z-score, IQR, Isolation Forest)
  - **`ClassBalanceAssessorTool`**: Analyze class distribution for ML tasks
  - **`FeatureCorrelationMapperTool`**: Detect multicollinearity and correlation patterns
- **ML Usability Tools (3)**:
  - **`BaselineModelPerformanceTool`**: Train baseline ML models to assess dataset predictive power
  - **`FeatureImportanceAnalyzerTool`**: Analyze feature importance and information distribution
  - **`DataSeparabilityScoreTool`**: Assess class separability using dimensionality reduction

### 🤖 Agent Components
- **`local_validation_agent.py`**: Main agent using the tools system
- **`test_tools.py`**: Test script for tools functionality

## Features

- **Modular Design**: Extensible tools system with 13 specialized data validation tools
- **Local Development**: Works entirely offline without Agentverse connectivity
- **Multiple Data Formats**: CSV, JSON, Parquet, Excel support with automatic format detection
- **Comprehensive Validation**: Completeness, types, ranges, uniqueness, custom rules with scoring
- **Data Integrity Analysis**: Missing value analysis, duplicate detection, type consistency checking
- **Statistical Analysis**: Multi-method outlier detection, class balance assessment, correlation analysis
- **ML Usability Assessment**: Direct ML performance testing through baseline model training
- **Feature Intelligence**: Automated feature importance analysis and information distribution scoring
- **Class Separability**: PCA and LDA-based separability analysis for classification tasks
- **ML-Ready Evaluation**: Comprehensive dataset assessment for machine learning pipeline readiness
- **Detailed Profiling**: Statistical analysis and data quality metrics with 0-100 scoring systems
- **Smart Reporting**: Automated recommendations and executive summaries in multiple formats
- **Easy Testing**: Comprehensive test suites for all tool categories with graceful dependency handling

## Installation

1. **Install Python 3.8+** (if not already installed)

2. **Install required packages**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Optional: Install ML dependencies for advanced tools**:
   ```bash
   pip install scikit-learn scipy
   ```
   
   > **Note**: The ML Usability Tools require scikit-learn and scipy for full functionality. Without these packages, the tools will return informative error messages and gracefully handle missing dependencies.

## Usage

### Method 1: Run the Validation Agent

```bash
cd agents
python local_validation_agent.py
```

### Method 2: Test Tools System

```bash
python test_tools.py
```

### Method 3: Test Data Integrity Tools

```bash
python test_integrity_tools.py
```

### Method 4: Test Statistical Analysis Tools

```bash
python test_statistical_tools.py
```

### Method 5: Test ML Usability Tools

```bash
python test_ml_usability_tools.py
```

### Method 3: Use Tools Directly

```python
from tools import tool_registry
import asyncio

async def example():
    # Load data
    result = await tool_registry.execute_tool(
        "data_loader", 
        file_path="data.csv"
    )
    
    # Profile data
    profile = await tool_registry.execute_tool(
        "data_profiler", 
        data=result["data"]
    )

asyncio.run(example())
```

## Configuration

Validation rules configuration:

```python
validation_params = {
    "max_missing_percentage": 5.0,  # Max 5% missing values per column
    "validity_threshold": 0.8,      # 80% of checks must pass
    "expected_types": {
        "id": "int64",
        "name": "object",
        "age": "int64",
        "salary": "float64"
    },
    "value_ranges": {
        "age": {"min": 18, "max": 120},
        "salary": {"min": 0, "max": 1000000}
    },
    "unique_columns": ["id"],       # ID should be unique
    "check_duplicate_rows": True,   # Check for duplicate rows
    "custom_rules": [
        {
            "name": "Age-Salary Consistency",
            "condition": "(df['age'] >= 18) | (df['salary'] == 0)",
            "max_violations": 0
        }
    ]
}
```

### Step 3: Send Validation Requests

You can interact with the agent in several ways:

#### Option A: Use the Client Script

```bash
python3 validation_client.py
```

#### Option B: Send Direct Messages (programmatically)

```python
from uagents import Agent, Context
from dataset_validation_agent import DatasetValidationRequest

# Create your client agent
client = Agent(name="my_client", port=8003)

@client.on_event("startup")
async def send_validation_request(ctx: Context):
    validator_address = "agent1q..."  # Get from validator logs

    request = DatasetValidationRequest(
        dataset_path="path/to/your/dataset.csv",
        validation_parameters=validation_params,
        dataset_type="csv"
    )

    await ctx.send(validator_address, request)

client.run()
```

#### Option C: Use Agentverse (Web Interface)

1. Deploy your agent to Agentverse
2. Create a hosted agent to interact with it
3. Send validation requests through the web interface

## Validation Parameters

### Basic Parameters

- `max_missing_percentage`: Maximum percentage of missing values allowed per column
- `validity_threshold`: Minimum score (0-1) required for dataset to be considered valid

### Data Type Validation

- `expected_types`: Dictionary mapping column names to expected pandas dtypes

### Value Range Validation

- `value_ranges`: Dictionary with min/max constraints for numeric columns

### Uniqueness Constraints

- `unique_columns`: List of columns that should have unique values
- `check_duplicate_rows`: Boolean to check for duplicate rows

### Custom Rules

- `custom_rules`: List of custom validation rules with:
  - `name`: Rule description
  - `condition`: Pandas expression that should be true
  - `max_violations`: Maximum allowed violations

## Example Dataset Structure

Your dataset should be in a supported format (CSV, JSON, Parquet, Excel):

```csv
id,name,age,salary,department
1,John Doe,25,50000,Engineering
2,Jane Smith,30,60000,Marketing
3,Bob Johnson,35,70000,Sales
```

## Validation Results

The agent returns a `ValidationResult` with:

- `is_valid`: Boolean indicating if dataset passes validation
- `validation_score`: Score from 0-1 indicating overall quality
- `errors`: List of validation errors that must be fixed
- `warnings`: List of potential issues that should be reviewed
- `statistics`: Detailed metrics about the dataset
- `recommendations`: Suggestions for improving data quality

## Available Tools

### Core Tools

#### DataLoaderTool
- **Purpose**: Load datasets from various formats
- **Supported Formats**: CSV, JSON, Parquet, Excel
- **Usage**: `await tool_registry.execute_tool("data_loader", file_path="data.csv")`

#### DataProfilerTool  
- **Purpose**: Generate comprehensive data quality profiles
- **Features**: Basic info, quality metrics, statistical summaries, correlations
- **Usage**: `await tool_registry.execute_tool("data_profiler", data=df)`

#### ValidationRulesTool
- **Purpose**: Execute validation rules on datasets
- **Built-in Rules**: completeness, data_types, value_ranges, uniqueness, patterns, custom_logic
- **Usage**: `await tool_registry.execute_tool("validation_rules", data=df, rules=config)`

#### ReportGeneratorTool
- **Purpose**: Generate comprehensive reports
- **Formats**: JSON, Markdown
- **Usage**: `await tool_registry.execute_tool("report_generator", validation_results=results)`

### Data Integrity and Completeness Tools

#### MissingValueAnalyzerTool
- **Purpose**: Analyze missing data patterns and calculate integrity scores
- **Scoring**: 0-100 scale with exponential penalty for missing data
- **Features**: Column-level analysis, pattern detection, severity classification
- **Usage**: `await tool_registry.execute_tool("missing_value_analyzer", data=df)`
- **Score Impact**: 
  - 0% missing = 100 points
  - ≤1% missing = 95+ points  
  - ≤5% missing = 85+ points
  - ≤20% missing = 32+ points
  - >20% missing = Critical penalty

#### DuplicateRecordDetectorTool
- **Purpose**: Detect duplicate records and assess data integrity impact
- **Scoring**: Penalizes datasets with high duplication rates
- **Features**: Full-row duplicates, subset duplicates, duplicate group analysis
- **Usage**: `await tool_registry.execute_tool("duplicate_record_detector", data=df, subset_columns=["id"])`
- **Score Impact**:
  - 0% duplicates = 100 points
  - ≤1% duplicates = 93+ points
  - ≤5% duplicates = 75+ points
  - ≤20% duplicates = 15+ points
  - >20% duplicates = Severe penalty

#### DataTypeConsistencyCheckerTool
- **Purpose**: Check data type consistency and schema compliance
- **Scoring**: Validates against expected schema and detects type issues
- **Features**: Schema validation, mixed-type detection, type conversion suggestions
- **Usage**: `await tool_registry.execute_tool("data_type_consistency_checker", data=df, expected_schema=schema)`
- **Score Impact**:
  - Perfect consistency = 100 points
  - Schema mismatches = -10 points each
  - Type issues = -3 points each (capped at -15 per column)

### Statistical and Distributional Analysis Tools

#### OutlierDetectionEngineTool
- **Purpose**: Detect statistical outliers using multiple methods (Z-score, IQR, Isolation Forest)
- **Scoring**: 0-100 scale based on outlier percentage and data quality impact
- **Features**: Multi-method detection, consensus outliers, sensitivity adjustment
- **Usage**: `await tool_registry.execute_tool("outlier_detection_engine", data=df, methods=["zscore", "iqr"], sensitivity="medium")`
- **Methods Available**:
  - **Z-Score**: Detects outliers based on standard deviations from mean
  - **IQR (Interquartile Range)**: Uses quartile-based outlier detection
  - **Isolation Forest**: Machine learning approach for anomaly detection (requires scikit-learn)
- **Score Impact**:
  - ≤1% outliers = 100 points (Excellent)
  - ≤3% outliers = 90+ points (Very Good) 
  - ≤5% outliers = 80+ points (Good)
  - ≤10% outliers = 65+ points (Fair)
  - >20% outliers = Poor quality (<45 points)
- **Sensitivity Levels**:
  - **Low**: Z-score > 3.5, IQR multiplier = 2.0
  - **Medium**: Z-score > 3.0, IQR multiplier = 1.5 (default)
  - **High**: Z-score > 2.5, IQR multiplier = 1.0

#### ClassBalanceAssessorTool
- **Purpose**: Analyze class distribution and balance for classification tasks
- **Scoring**: Task-specific scoring based on class imbalance severity
- **Features**: Auto task-type detection, imbalance ratio calculation, entropy analysis
- **Usage**: `await tool_registry.execute_tool("class_balance_assessor", data=df, target_column="label", task_type="auto")`
- **Supported Task Types**:
  - **Binary Classification**: Two-class problems
  - **Multiclass Classification**: Multiple-class problems  
  - **Regression**: Continuous target variables (neutral scoring)
  - **Auto**: Automatic detection based on target characteristics
- **Binary Classification Scoring**:
  - 40-50% minority class = 100 points (Excellent)
  - 30-39% minority class = 85-95 points (Good)
  - 20-29% minority class = 55-85 points (Fair)
  - 10-19% minority class = 35-75 points (Imbalanced)
  - <10% minority class = <35 points (Severely Imbalanced)
- **Multiclass Classification Scoring**:
  - ≥15% smallest class = 95 points (Excellent)
  - 10-14% smallest class = 75-95 points (Good)
  - 5-9% smallest class = 45-85 points (Fair)
  - 2-4% smallest class = 25-70 points (Imbalanced)
  - <2% smallest class = <25 points (Severely Imbalanced)

#### FeatureCorrelationMapperTool  
- **Purpose**: Analyze feature correlations and detect multicollinearity issues
- **Scoring**: Quality score based on correlation patterns and multicollinearity risk
- **Features**: Correlation matrix generation, cluster detection, multicollinearity assessment
- **Usage**: `await tool_registry.execute_tool("feature_correlation_mapper", data=df, correlation_threshold=0.8, method="pearson")`
- **Correlation Methods**:
  - **Pearson**: Linear correlation (default)
  - **Spearman**: Rank-based correlation
  - **Kendall**: Tau correlation coefficient
- **Multicollinearity Risk Levels**:
  - **Low**: Few or no high correlations, good for most ML algorithms
  - **Medium**: Some correlations present, consider regularization
  - **High**: Many high correlations, requires dimension reduction
- **Score Impact**:
  - No high correlations = 95-100 points (Excellent)
  - Few high correlations = 80-94 points (Good)  
  - Some multicollinearity = 60-79 points (Fair)
  - High multicollinearity = <60 points (Poor)
- **Features**:
  - **Correlation Clusters**: Groups of highly correlated features
  - **Threshold Customization**: Adjustable correlation threshold
  - **Feature Recommendations**: Suggests features to remove or combine

### Machine Learning Usability Tools

#### BaselineModelPerformanceTool
- **Purpose**: Train baseline ML models to directly assess dataset predictive power and quality
- **Scoring**: Performance-based scoring using actual ML model results (accuracy, F1, R²)
- **Features**: Auto task-type detection, multiple baseline models, performance benchmarking
- **Usage**: `await tool_registry.execute_tool("baseline_model_performance", data=df, target_column="label", test_size=0.2)`
- **Supported Tasks**:
  - **Classification**: Logistic Regression, Decision Tree, Dummy Classifier
  - **Regression**: Linear Regression, Decision Tree Regressor, Dummy Regressor
  - **Auto-detection**: Based on target variable characteristics
- **Model Pipeline**:
  - Automatic feature preprocessing (imputation, scaling)
  - Train/test split with stratification
  - Multiple model training and evaluation
  - Performance comparison against baseline (dummy) models
- **Classification Scoring**:
  - ≥90% accuracy = 95 points (Excellent)
  - 80-89% accuracy = 85 points (Very Good)
  - 70-79% accuracy = 75 points (Good)
  - 60-69% accuracy = 65 points (Fair)
  - <60% accuracy = Poor quality (<65 points)
- **Regression Scoring**:
  - R² ≥ 0.9 = 95 points (Excellent)
  - R² 0.8-0.89 = 85 points (Very Good)
  - R² 0.7-0.79 = 75 points (Good)
  - R² 0.5-0.69 = 65 points (Fair)
  - R² < 0.5 = Poor quality (<65 points)

#### FeatureImportanceAnalyzerTool
- **Purpose**: Analyze feature importance distribution to assess information content and relevance
- **Scoring**: Information distribution quality based on feature importance balance and signal strength
- **Features**: Tree-based importance ranking, information concentration analysis, Gini coefficient calculation
- **Usage**: `await tool_registry.execute_tool("feature_importance_analyzer", data=df, target_column="label", importance_threshold=0.01)`
- **Analysis Methods**:
  - **Random Forest**: Primary importance calculation method
  - **Information Distribution**: Analysis of how predictive power is distributed across features
  - **Gini Coefficient**: Measure of importance inequality across features
  - **Concentration Metrics**: Top-k feature contribution analysis
- **Key Metrics**:
  - **Top 1 Feature Contribution**: Percentage of total importance from most important feature
  - **Top 3/5 Contributions**: Cumulative importance of top features
  - **Significant Features**: Count of features above importance thresholds
  - **Information Concentration**: High/Medium/Low based on distribution
- **Scoring Impact**:
  - Well-distributed importance (top feature <40%) = 85+ points (Excellent)
  - Moderate concentration (top feature 40-60%) = 70 points (Good)
  - High concentration (top feature 60-80%) = 50 points (Fair)
  - Single feature dominance (top feature >80%) = 30 points (Poor)
- **Bonuses/Penalties**:
  - Multiple useful features (>5% importance): +5-10 points
  - Good feature spread (>5 significant): +3-5 points
  - Very low max importance (<0.1): -20 points (weak signal)

#### DataSeparabilityScoreTool
- **Purpose**: Assess how well classes can be separated using dimensionality reduction techniques
- **Scoring**: Class separability quality based on PCA, LDA, and silhouette analysis
- **Features**: Multi-method separability assessment, class-wise analysis, dimensionality insights
- **Usage**: `await tool_registry.execute_tool("data_separability_scorer", data=df, target_column="label", n_components=2)`
- **Analysis Techniques**:
  - **PCA (Principal Component Analysis)**: Variance-based dimensionality reduction
  - **LDA (Linear Discriminant Analysis)**: Class-aware dimensionality reduction
  - **Silhouette Analysis**: Cluster quality assessment
  - **Class Separation Analysis**: Inter/intra-class distance calculations
- **Key Metrics**:
  - **Explained Variance**: How much information retained in reduced dimensions
  - **Silhouette Score**: Measure of cluster separation quality (-1 to 1)
  - **Separation Ratio**: Inter-class distance / intra-class scatter
  - **Components for 90/95% Variance**: Dimensionality requirements
- **Silhouette Score Interpretation**:
  - >0.7 = Excellent separation
  - 0.5-0.7 = Good separation
  - 0.3-0.5 = Fair separation
  - 0.1-0.3 = Weak separation
  - <0.1 = Poor separation
- **Scoring Breakdown**:
  - Base score: 50 points
  - PCA contribution: Up to 30 points (based on variance retention)
  - Silhouette contribution: Up to 25 points (based on separation quality)
  - LDA contribution: Up to 20 points (based on discriminative power)
  - Class separation: Up to 15 points (based on separation ratio)
- **Applications**:
  - **Classification Readiness**: How suitable for linear/simple classifiers
  - **Dimensionality Reduction**: Feasibility of dimension reduction
  - **Visualization**: Whether classes can be visualized in 2D/3D
  - **Algorithm Selection**: Guidance for choosing appropriate ML algorithms

## ETH Delhi 2025 Context

This agent demonstrates advanced capabilities for Web3 and DeFi applications:

### 🔗 **Blockchain & DeFi Use Cases**
- **Oracle Data Validation**: Validate external data feeds before blockchain integration
- **Smart Contract Data Preparation**: Ensure data quality for DeFi protocol interactions
- **Cross-Chain Data Integrity**: Validate data consistency across multiple blockchain networks
- **Tokenized Data Markets**: Assess dataset quality for data tokenization and trading

### 🤖 **AI Agent Capabilities**
- **Autonomous Data Assessment**: AI agents that can validate data quality without human intervention
- **ML-Ready Evaluation**: Direct assessment of dataset suitability for machine learning applications
- **Multi-Agent Coordination**: Tools designed for sharing between different agents in a network
- **Scalable Validation Pipeline**: Modular architecture supporting high-throughput data processing

### 📊 **Advanced Analytics Features**
- **13 Specialized Tools**: Comprehensive coverage from basic validation to advanced ML assessment
- **Quantified Quality Scoring**: 0-100 scoring systems for objective dataset evaluation
- **Predictive Power Assessment**: Direct ML model training to measure dataset utility
- **Feature Intelligence**: Automated analysis of feature importance and information distribution
- **Class Separability Analysis**: Advanced dimensionality reduction for classification readiness

## Extending the Tools System

Add new tools by creating a class that inherits from `BaseTool`:

```python
class MyCustomTool(BaseTool):
    def __init__(self):
        super().__init__("my_tool", "Description of my tool")
    
    async def execute(self, *args, **kwargs):
        # Your tool logic here
        return {"success": True, "result": "data"}

# Register your tool
tool_registry.register_tool(MyCustomTool())
```

## Project Structure

```
agents/
├── local_validation_agent.py      # Main agent implementation
├── tools.py                       # Modular tools system (13 specialized tools)
├── test_tools.py                  # Core tools testing script
├── test_integrity_tools.py        # Data integrity tools testing
├── test_statistical_tools.py      # Statistical analysis tools testing
├── test_ml_usability_tools.py     # ML usability tools testing
├── requirements.txt               # Dependencies
└── README.md                      # This comprehensive documentation
```

## Troubleshooting

### Common Issues

1. **"command not found: pip"**

   - Use `pip3` instead of `pip`
   - Ensure Python 3.8+ is installed

2. **"Import uagents could not be resolved"**

   - Install uagents: `pip3 install uagents`
   - Activate virtual environment if using one

3. **Agent connection issues**

   - Ensure agents are running on different ports
   - Check firewall settings for local ports
   - Verify agent addresses in logs

4. **Dataset loading errors**
   - Check file path is correct
   - Ensure dataset format matches `dataset_type` parameter
   - Verify file permissions

### Getting Agent Address

When you run the validation agent, look for this line in the logs:

```
INFO: [dataset_validator]: Agent address: agent1q...
```

Copy this address to use in client scripts.

## Advanced Usage

### Deploy to Agentverse

To make your agent accessible from anywhere:

1. Add `mailbox=True` to agent configuration
2. Run the agent locally
3. Connect to Agentverse via the inspector URL
4. Create a mailbox connection

### Custom Validation Logic

Extend the `DatasetValidationAgent` class to add your own validation methods:

```python
async def _check_business_rules(self, df: pd.DataFrame, params: Dict, ctx: Context) -> Dict:
    # Your custom validation logic here
    pass
```

### Integration with Other Agents

Your validation agent can communicate with other agents in the Fetch.ai ecosystem for:

- Data preprocessing
- Result storage
- Notification systems
- Automated data pipeline validation

## Support

For issues specific to Fetch.ai uAgents:

- [Documentation](https://innovationlab.fetch.ai/resources/docs/intro)
- [Discord Community](https://discord.gg/fetchai)
- [GitHub](https://github.com/fetchai)

For dataset validation logic issues:

- Review the validation parameters
- Check dataset format and content
- Examine the validation result details
