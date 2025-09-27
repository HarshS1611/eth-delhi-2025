# Dataset Validation Agent

A Fetch.ai uAgent that validates datasets based on configurable parameters.

## Features

- **Data Completeness**: Check for missing values and data gaps
- **Data Types Validation**: Ensure columns have expected data types
- **Value Range Validation**: Verify values are within acceptable ranges
- **Uniqueness Constraints**: Check for duplicate values where required
- **Custom Validation Rules**: Define custom business logic validation
- **Comprehensive Reporting**: Get detailed validation results with scores and recommendations

## Installation

1. **Install Python 3.8+** (if not already installed)

2. **Install required packages**:

   ```bash
   # If pip doesn't work, use pip3
   pip3 install -r requirements.txt
   ```

   Or install packages individually:

   ```bash
   pip3 install uagents pandas numpy jsonschema
   ```

## Usage

### Step 1: Run the Validation Agent

```bash
cd /Users/sahasvivek/Desktop/eth\ delhi/eth-delhi-2025/agents
python3 dataset_validation_agent.py
```

The agent will start and display:

- Agent name and address
- Available validation capabilities
- Server endpoint

### Step 2: Configure Validation Parameters

Create validation parameters based on your dataset requirements:

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
