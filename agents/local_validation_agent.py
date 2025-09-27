#!/usr/bin/env python3
"""
Local Dataset Validation Agent - No Internet Required
This version works entirely locally without Agentverse registration
"""

from uagents import Agent, Context, Model
from typing import Dict, List, Any, Optional
import json
import pandas as pd
import numpy as np
from pathlib import Path
import asyncio

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

class LocalDatasetValidationAgent:
    """Local Dataset Validation Agent - No external connectivity required"""
    
    def __init__(self, name: str = "local_validator", port: int = 8003):
        # Create agent with local-only configuration
        self.agent = Agent(
            name=name,
            port=port,
            seed="local_dataset_validation_seed_2025",
            endpoint=[f"http://localhost:{port}/submit"],
            # Disable external registration
            resolve=False,  # Don't resolve external agents
        )
        
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup agent event handlers"""
        
        @self.agent.on_event("startup")
        async def startup_handler(ctx: Context):
            ctx.logger.info("🚀 Local Dataset Validation Agent started!")
            ctx.logger.info(f"Agent name: {self.agent.name}")
            ctx.logger.info(f"Agent address: {self.agent.address}")
            ctx.logger.info(f"Local endpoint: http://localhost:{self.agent._port}")
            ctx.logger.info("Ready for local validation requests!")
            ctx.logger.info("Note: This agent works entirely locally - no internet required")
        
        @self.agent.on_message(model=DatasetValidationRequest)
        async def handle_validation_request(ctx: Context, sender: str, msg: DatasetValidationRequest):
            ctx.logger.info(f"📥 Received validation request")
            ctx.logger.info(f"Dataset: {msg.dataset_path}")
            
            try:
                # Perform validation
                result = await self._validate_dataset(msg, ctx)
                
                # Log result summary
                status = "✅ VALID" if result.is_valid else "❌ INVALID"
                ctx.logger.info(f"📊 Validation completed: {status} (Score: {result.validation_score:.1%})")
                
                # In local mode, we'll just log the result since we can't send back
                ctx.logger.info("📋 VALIDATION RESULT:")
                ctx.logger.info(f"  Valid: {result.is_valid}")
                ctx.logger.info(f"  Score: {result.validation_score:.1%}")
                ctx.logger.info(f"  Errors: {len(result.errors)}")
                ctx.logger.info(f"  Warnings: {len(result.warnings)}")
                
                if result.errors:
                    for error in result.errors:
                        ctx.logger.error(f"  ❌ {error}")
                
                if result.warnings:
                    for warning in result.warnings:
                        ctx.logger.warning(f"  ⚠️ {warning}")
                        
            except Exception as e:
                ctx.logger.error(f"❌ Validation failed: {e}")
    
    async def _validate_dataset(self, request: DatasetValidationRequest, ctx: Context) -> ValidationResult:
        """Core dataset validation logic"""
        
        errors = []
        warnings = []
        statistics = {}
        recommendations = []
        validation_score = 0.0
        
        try:
            # Load dataset based on type
            df = await self._load_dataset(request.dataset_path, request.dataset_type)
            
            if df is None:
                return ValidationResult(
                    is_valid=False,
                    validation_score=0.0,
                    errors=["Could not load dataset"],
                    warnings=[],
                    statistics={},
                    recommendations=["Check file path and format"]
                )
            
            ctx.logger.info(f"📊 Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")
            
            # Basic statistics
            statistics.update({
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "memory_usage_mb": df.memory_usage(deep=True).sum() / 1024**2
            })
            
            # Run validation checks
            checks_results = []
            
            # 1. Completeness check
            completeness_result = await self._check_completeness(df, request.validation_parameters, ctx)
            checks_results.append(completeness_result)
            
            # 2. Data types check
            dtypes_result = await self._check_data_types(df, request.validation_parameters, ctx)
            checks_results.append(dtypes_result)
            
            # 3. Value ranges check
            ranges_result = await self._check_value_ranges(df, request.validation_parameters, ctx)
            checks_results.append(ranges_result)
            
            # 4. Uniqueness check
            uniqueness_result = await self._check_uniqueness(df, request.validation_parameters, ctx)
            checks_results.append(uniqueness_result)
            
            # Aggregate results
            for result in checks_results:
                errors.extend(result.get("errors", []))
                warnings.extend(result.get("warnings", []))
                statistics.update(result.get("statistics", {}))
                recommendations.extend(result.get("recommendations", []))
            
            # Calculate overall validation score (0-1)
            passed_checks = sum(1 for result in checks_results if result.get("passed", False))
            validation_score = passed_checks / len(checks_results) if checks_results else 0.0
            
            # Determine if dataset is valid (threshold can be customized)
            validity_threshold = request.validation_parameters.get("validity_threshold", 0.8)
            is_valid = validation_score >= validity_threshold and len(errors) == 0
            
            return ValidationResult(
                is_valid=is_valid,
                validation_score=round(validation_score, 3),
                errors=errors,
                warnings=warnings,
                statistics=statistics,
                recommendations=recommendations
            )
            
        except Exception as e:
            ctx.logger.error(f"Validation process failed: {e}")
            return ValidationResult(
                is_valid=False,
                validation_score=0.0,
                errors=[f"Validation process failed: {str(e)}"],
                warnings=[],
                statistics=statistics,
                recommendations=["Review dataset format and validation parameters"]
            )
    
    async def _load_dataset(self, path: str, dataset_type: str) -> Optional[pd.DataFrame]:
        """Load dataset based on type"""
        try:
            if dataset_type.lower() == 'csv':
                return pd.read_csv(path)
            elif dataset_type.lower() == 'json':
                return pd.read_json(path)
            elif dataset_type.lower() == 'parquet':
                return pd.read_parquet(path)
            elif dataset_type.lower() == 'excel':
                return pd.read_excel(path)
            else:
                # Try to infer from file extension
                file_path = Path(path)
                if file_path.suffix.lower() == '.csv':
                    return pd.read_csv(path)
                elif file_path.suffix.lower() == '.json':
                    return pd.read_json(path)
                elif file_path.suffix.lower() == '.parquet':
                    return pd.read_parquet(path)
        except Exception as e:
            print(f"Error loading dataset: {e}")
            return None
    
    async def _check_completeness(self, df: pd.DataFrame, params: Dict, ctx: Context) -> Dict:
        """Check data completeness"""
        result = {"errors": [], "warnings": [], "statistics": {}, "recommendations": [], "passed": True}
        
        # Calculate missing data statistics
        missing_counts = df.isnull().sum()
        missing_percentages = (missing_counts / len(df)) * 100
        
        # Get completeness threshold from parameters
        max_missing_percentage = params.get("max_missing_percentage", 10.0)
        
        result["statistics"]["missing_data"] = {
            "columns_with_missing": missing_counts.to_dict(),
            "missing_percentages": missing_percentages.to_dict(),
            "total_missing_values": int(missing_counts.sum())
        }
        
        # Check each column
        for col in df.columns:
            missing_pct = missing_percentages[col]
            if missing_pct > max_missing_percentage:
                result["errors"].append(f"Column '{col}' has {missing_pct:.1f}% missing values (threshold: {max_missing_percentage}%)")
                result["passed"] = False
            elif missing_pct > max_missing_percentage * 0.5:  # Warning at 50% of threshold
                result["warnings"].append(f"Column '{col}' has {missing_pct:.1f}% missing values")
        
        if result["errors"]:
            result["recommendations"].append("Consider data imputation or removal of columns with excessive missing values")
        
        ctx.logger.info(f"🔍 Completeness check: {'PASSED' if result['passed'] else 'FAILED'}")
        return result
    
    async def _check_data_types(self, df: pd.DataFrame, params: Dict, ctx: Context) -> Dict:
        """Check data types consistency"""
        result = {"errors": [], "warnings": [], "statistics": {}, "recommendations": [], "passed": True}
        
        expected_types = params.get("expected_types", {})
        result["statistics"]["actual_types"] = df.dtypes.to_dict()
        
        for col, expected_type in expected_types.items():
            if col in df.columns:
                actual_type = str(df[col].dtype)
                if expected_type not in actual_type:
                    result["errors"].append(f"Column '{col}' has type '{actual_type}', expected '{expected_type}'")
                    result["passed"] = False
            else:
                result["errors"].append(f"Expected column '{col}' not found in dataset")
                result["passed"] = False
        
        ctx.logger.info(f"🔍 Data types check: {'PASSED' if result['passed'] else 'FAILED'}")
        return result
    
    async def _check_value_ranges(self, df: pd.DataFrame, params: Dict, ctx: Context) -> Dict:
        """Check if values are within expected ranges"""
        result = {"errors": [], "warnings": [], "statistics": {}, "recommendations": [], "passed": True}
        
        value_ranges = params.get("value_ranges", {})
        
        for col, range_config in value_ranges.items():
            if col not in df.columns:
                continue
                
            min_val = range_config.get("min")
            max_val = range_config.get("max")
            
            if pd.api.types.is_numeric_dtype(df[col]):
                col_min = df[col].min()
                col_max = df[col].max()
                
                result["statistics"][f"{col}_range"] = {"min": col_min, "max": col_max}
                
                if min_val is not None and col_min < min_val:
                    result["errors"].append(f"Column '{col}' has values below minimum ({col_min} < {min_val})")
                    result["passed"] = False
                
                if max_val is not None and col_max > max_val:
                    result["errors"].append(f"Column '{col}' has values above maximum ({col_max} > {max_val})")
                    result["passed"] = False
        
        ctx.logger.info(f"🔍 Value ranges check: {'PASSED' if result['passed'] else 'FAILED'}")
        return result
    
    async def _check_uniqueness(self, df: pd.DataFrame, params: Dict, ctx: Context) -> Dict:
        """Check uniqueness constraints"""
        result = {"errors": [], "warnings": [], "statistics": {}, "recommendations": [], "passed": True}
        
        unique_columns = params.get("unique_columns", [])
        
        for col in unique_columns:
            if col in df.columns:
                duplicates = df[col].duplicated().sum()
                result["statistics"][f"{col}_duplicates"] = duplicates
                
                if duplicates > 0:
                    result["errors"].append(f"Column '{col}' has {duplicates} duplicate values (should be unique)")
                    result["passed"] = False
        
        # Check for duplicate rows
        if params.get("check_duplicate_rows", False):
            duplicate_rows = df.duplicated().sum()
            result["statistics"]["duplicate_rows"] = duplicate_rows
            
            if duplicate_rows > 0:
                result["warnings"].append(f"Dataset has {duplicate_rows} duplicate rows")
                result["recommendations"].append("Consider removing duplicate rows")
        
        ctx.logger.info(f"🔍 Uniqueness check: {'PASSED' if result['passed'] else 'FAILED'}")
        return result
    
    def run(self):
        """Run the agent locally"""
        print("🏠 Starting Local Dataset Validation Agent")
        print("=" * 50)
        print(f"Agent Name: {self.agent.name}")
        print(f"Port: {self.agent._port}")
        print("Mode: Local only (no internet required)")
        print("=" * 50)
        
        try:
            self.agent.run()
        except KeyboardInterrupt:
            print("\n👋 Local agent stopped by user")

# Example usage and test function
async def test_local_validation():
    """Test the local validation directly"""
    print("🧪 Testing Local Validation Directly")
    print("=" * 40)
    
    # Create agent instance (but don't run the server)
    agent = LocalDatasetValidationAgent()
    
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
    
    # Create request
    request = DatasetValidationRequest(
        dataset_path="sample_dataset.csv",
        validation_parameters=validation_config,
        dataset_type="csv"
    )
    
    # Mock context
    class MockContext:
        def info(self, msg): print(f"INFO: {msg}")
        def error(self, msg): print(f"ERROR: {msg}")
        def warning(self, msg): print(f"WARNING: {msg}")
        logger = type('Logger', (), {'info': info, 'error': error, 'warning': warning})()
    
    ctx = MockContext()
    
    # Run validation
    print(f"📁 Validating: {request.dataset_path}")
    result = await agent._validate_dataset(request, ctx)
    
    # Display results
    print("\n📊 VALIDATION RESULTS:")
    print("-" * 30)
    print(f"Valid: {'✅ YES' if result.is_valid else '❌ NO'}")
    print(f"Score: {result.validation_score:.1%}")
    print(f"Errors: {len(result.errors)}")
    print(f"Warnings: {len(result.warnings)}")
    
    if result.errors:
        print("\n🔴 Errors:")
        for error in result.errors:
            print(f"  - {error}")
    
    if result.warnings:
        print("\n🟡 Warnings:")
        for warning in result.warnings:
            print(f"  - {warning}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Run direct test
        asyncio.run(test_local_validation())
    else:
        # Run the agent server
        validator_agent = LocalDatasetValidationAgent()
        validator_agent.run()