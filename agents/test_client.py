#!/usr/bin/env python3
"""
Simple client to test the Dataset Validation Agent
"""

from uagents import Agent, Context, Model
import asyncio
from typing import Dict, List, Any
import json

# Data models (copy from the main agent)
class DatasetValidationRequest(Model):
    """Model for dataset validation requests"""
    dataset_path: str
    validation_parameters: Dict[str, Any]
    dataset_type: str  # 'csv', 'json', 'parquet', etc.

class ValidationResult(Model):
    """Model for validation results"""
    is_valid: bool
    validation_score: float  # 0-1 score
    errors: List[str]
    warnings: List[str]
    statistics: Dict[str, Any]
    recommendations: List[str]

class ValidationTestClient:
    """Test client for the dataset validation agent"""
    
    def __init__(self):
        # The validator agent address from the console output
        self.validator_address = "agent1qw4nawu4stvqqmghjp2glxl00prtdu9te9g02dmdwknn60a0wtw75rgsa7w"
        
        # Create client agent
        self.agent = Agent(
            name="validation_test_client",
            port=8002,
            seed="validation_test_client_seed_2025",
            endpoint=["http://localhost:8002/submit"]
        )
        
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup client handlers"""
        
        @self.agent.on_event("startup")
        async def startup_handler(ctx: Context):
            ctx.logger.info(f"🚀 Test Client started!")
            ctx.logger.info(f"Client address: {self.agent.address}")
            ctx.logger.info(f"Will send validation request to: {self.validator_address}")
            
            # Wait a moment for the agent to fully start
            await asyncio.sleep(2)
            
            # Send test validation request
            await self.send_test_request(ctx)
        
        @self.agent.on_message(model=ValidationResult)
        async def handle_validation_result(ctx: Context, sender: str, msg: ValidationResult):
            ctx.logger.info("=" * 60)
            ctx.logger.info("📊 VALIDATION RESULT RECEIVED")
            ctx.logger.info("=" * 60)
            
            status_emoji = "✅" if msg.is_valid else "❌"
            ctx.logger.info(f"{status_emoji} Dataset Status: {'VALID' if msg.is_valid else 'INVALID'}")
            ctx.logger.info(f"📈 Validation Score: {msg.validation_score:.1%}")
            
            if msg.errors:
                ctx.logger.info(f"🔴 ERRORS ({len(msg.errors)}):")
                for i, error in enumerate(msg.errors, 1):
                    ctx.logger.info(f"  {i}. {error}")
            
            if msg.warnings:
                ctx.logger.info(f"🟡 WARNINGS ({len(msg.warnings)}):")
                for i, warning in enumerate(msg.warnings, 1):
                    ctx.logger.info(f"  {i}. {warning}")
            
            if msg.statistics:
                ctx.logger.info("📊 KEY STATISTICS:")
                for key, value in list(msg.statistics.items())[:5]:  # Show first 5
                    ctx.logger.info(f"  {key}: {value}")
            
            if msg.recommendations:
                ctx.logger.info(f"💡 RECOMMENDATIONS:")
                for i, rec in enumerate(msg.recommendations, 1):
                    ctx.logger.info(f"  {i}. {rec}")
            
            ctx.logger.info("=" * 60)
            ctx.logger.info("✅ Test completed successfully!")
            
            # Stop the client after receiving the result
            await asyncio.sleep(1)
            ctx.logger.info("Shutting down test client...")
    
    async def send_test_request(self, ctx: Context):
        """Send a test validation request"""
        
        # Test configuration
        validation_config = {
            "max_missing_percentage": 5.0,
            "validity_threshold": 0.8,
            "expected_types": {
                "id": "int64",
                "name": "object", 
                "age": "int64",
                "salary": "int64"
            },
            "value_ranges": {
                "age": {"min": 18, "max": 120},
                "salary": {"min": 0, "max": 100000}
            },
            "unique_columns": ["id"],
            "check_duplicate_rows": True
        }
        
        # Create validation request
        request = DatasetValidationRequest(
            dataset_path="sample_dataset.csv",
            validation_parameters=validation_config,
            dataset_type="csv"
        )
        
        ctx.logger.info("📤 Sending validation request...")
        ctx.logger.info(f"📁 Dataset: {request.dataset_path}")
        ctx.logger.info(f"📋 Config: {len(validation_config)} validation parameters")
        
        try:
            # Send request to the validation agent
            await ctx.send(self.validator_address, request)
            ctx.logger.info("✅ Request sent successfully!")
        except Exception as e:
            ctx.logger.error(f"❌ Failed to send request: {e}")
    
    def run(self):
        """Run the test client"""
        print("🧪 Starting Dataset Validation Test Client")
        print("=" * 50)
        print(f"Target Validator: {self.validator_address}")
        print("=" * 50)
        
        try:
            self.agent.run()
        except KeyboardInterrupt:
            print("\n👋 Test client stopped by user")
        except Exception as e:
            print(f"❌ Client error: {e}")

if __name__ == "__main__":
    client = ValidationTestClient()
    client.run()