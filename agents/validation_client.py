from uagents import Agent, Context, Model
import asyncio
import json
from dataset_validation_agent import DatasetValidationRequest, ValidationResult

class DatasetValidationClient:
    """Client to interact with Dataset Validation Agent"""
    
    def __init__(self, name: str = "validation_client", port: int = 8002):
        self.agent = Agent(
            name=name,
            port=port,
            seed="validation_client_seed_2025",
            endpoint=[f"http://localhost:{port}/submit"]
        )
        
        self.validator_address = None  # Will be set when we find the validator
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup client handlers"""
        
        @self.agent.on_event("startup")
        async def startup_handler(ctx: Context):
            ctx.logger.info(f"Dataset Validation Client {self.agent.name} started!")
            ctx.logger.info(f"Client address: {self.agent.address}")
        
        @self.agent.on_message(model=ValidationResult)
        async def handle_validation_result(ctx: Context, sender: str, msg: ValidationResult):
            ctx.logger.info("=== VALIDATION RESULT ===")
            ctx.logger.info(f"Dataset is {'VALID' if msg.is_valid else 'INVALID'}")
            ctx.logger.info(f"Validation Score: {msg.validation_score}")
            
            if msg.errors:
                ctx.logger.error("ERRORS:")
                for error in msg.errors:
                    ctx.logger.error(f"  - {error}")
            
            if msg.warnings:
                ctx.logger.warning("WARNINGS:")
                for warning in msg.warnings:
                    ctx.logger.warning(f"  - {warning}")
            
            if msg.statistics:
                ctx.logger.info("STATISTICS:")
                for key, value in msg.statistics.items():
                    ctx.logger.info(f"  {key}: {value}")
            
            if msg.recommendations:
                ctx.logger.info("RECOMMENDATIONS:")
                for rec in msg.recommendations:
                    ctx.logger.info(f"  - {rec}")
    
    async def validate_dataset(self, dataset_path: str, dataset_type: str, validation_params: dict):
        """Send validation request to the dataset validation agent"""
        
        # Validator agent address (you'll need to get this from the running validator)
        validator_address = "agent1qw8jn3nfl2fyyhe7v4x8pfmsge4hs9zqrqw9eq7h7hluzmd0da8z7j0uacx"  # Replace with actual address
        
        request = DatasetValidationRequest(
            dataset_path=dataset_path,
            validation_parameters=validation_params,
            dataset_type=dataset_type
        )
        
        # Send request to validator
        ctx = Context()  # This is simplified - in real usage, you'd get this from a handler
        await ctx.send(validator_address, request)
        print(f"Validation request sent for dataset: {dataset_path}")

def create_sample_validation_config():
    """Create a sample validation configuration"""
    return {
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

# Example usage
if __name__ == "__main__":
    # Sample usage - replace with your actual dataset path
    dataset_path = "sample_data.csv"  # Replace with your dataset path
    dataset_type = "csv"
    
    # Create validation parameters
    validation_params = create_sample_validation_config()
    
    print("Dataset Validation Client")
    print("=" * 50)
    print(f"Dataset Path: {dataset_path}")
    print(f"Dataset Type: {dataset_type}")
    print(f"Validation Parameters: {json.dumps(validation_params, indent=2)}")
    print("=" * 50)
    
    # Create and run client
    client = DatasetValidationClient()
    
    # In a real implementation, you would:
    # 1. Run this client
    # 2. Send validation request
    # 3. Receive and process results
    
    print("To use this client:")
    print("1. Run the dataset_validation_agent.py first")
    print("2. Get the validator agent's address from the logs")
    print("3. Update the validator_address in this script")
    print("4. Run this client script")
    print("5. The client will send validation requests and receive results")