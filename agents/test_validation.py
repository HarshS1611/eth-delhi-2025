#!/usr/bin/env python3
"""
Simple test script for Dataset Validation Agent
This script demonstrates how to use the validation agent without complex messaging
"""

import pandas as pd
import json
from pathlib import Path
import asyncio

# Import the validation logic (without the uAgents messaging layer)
class SimpleDatasetValidator:
    """Simplified version for testing validation logic"""
    
    def __init__(self):
        pass
    
    def validate_dataset(self, dataset_path: str, dataset_type: str, validation_parameters: dict):
        """Validate dataset without uAgents messaging"""
        
        print(f"Loading dataset: {dataset_path}")
        
        # Load dataset
        try:
            if dataset_type.lower() == 'csv':
                df = pd.read_csv(dataset_path)
            elif dataset_type.lower() == 'json':
                df = pd.read_json(dataset_path)
            else:
                return {"error": f"Unsupported dataset type: {dataset_type}"}
        except Exception as e:
            return {"error": f"Failed to load dataset: {str(e)}"}
        
        print(f"Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")
        
        # Initialize results
        errors = []
        warnings = []
        statistics = {}
        recommendations = []
        
        # Basic statistics
        statistics.update({
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "column_names": list(df.columns),
            "data_types": df.dtypes.to_dict()
        })
        
        # Run validation checks
        checks_results = []
        
        # 1. Completeness check
        completeness_result = self._check_completeness(df, validation_parameters)
        checks_results.append(completeness_result)
        print(f"✓ Completeness check: {'PASSED' if completeness_result['passed'] else 'FAILED'}")
        
        # 2. Data types check
        dtypes_result = self._check_data_types(df, validation_parameters)
        checks_results.append(dtypes_result)
        print(f"✓ Data types check: {'PASSED' if dtypes_result['passed'] else 'FAILED'}")
        
        # 3. Value ranges check
        ranges_result = self._check_value_ranges(df, validation_parameters)
        checks_results.append(ranges_result)
        print(f"✓ Value ranges check: {'PASSED' if ranges_result['passed'] else 'FAILED'}")
        
        # 4. Uniqueness check
        uniqueness_result = self._check_uniqueness(df, validation_parameters)
        checks_results.append(uniqueness_result)
        print(f"✓ Uniqueness check: {'PASSED' if uniqueness_result['passed'] else 'FAILED'}")
        
        # Aggregate results
        for result in checks_results:
            errors.extend(result.get("errors", []))
            warnings.extend(result.get("warnings", []))
            statistics.update(result.get("statistics", {}))
            recommendations.extend(result.get("recommendations", []))
        
        # Calculate overall validation score
        passed_checks = sum(1 for result in checks_results if result.get("passed", False))
        validation_score = passed_checks / len(checks_results) if checks_results else 0.0
        
        # Determine if dataset is valid
        validity_threshold = validation_parameters.get("validity_threshold", 0.8)
        is_valid = validation_score >= validity_threshold and len(errors) == 0
        
        return {
            "is_valid": is_valid,
            "validation_score": round(validation_score, 3),
            "errors": errors,
            "warnings": warnings,
            "statistics": statistics,
            "recommendations": recommendations
        }
    
    def _check_completeness(self, df: pd.DataFrame, params: dict) -> dict:
        """Check data completeness"""
        result = {"errors": [], "warnings": [], "statistics": {}, "recommendations": [], "passed": True}
        
        # Calculate missing data statistics
        missing_counts = df.isnull().sum()
        missing_percentages = (missing_counts / len(df)) * 100
        
        # Get completeness threshold from parameters
        max_missing_percentage = params.get("max_missing_percentage", 10.0)
        
        result["statistics"]["missing_data"] = {
            "columns_with_missing": {k: int(v) for k, v in missing_counts.items()},
            "missing_percentages": {k: round(float(v), 2) for k, v in missing_percentages.items()},
            "total_missing_values": int(missing_counts.sum())
        }
        
        # Check each column
        for col in df.columns:
            missing_pct = missing_percentages[col]
            if missing_pct > max_missing_percentage:
                result["errors"].append(f"Column '{col}' has {missing_pct:.1f}% missing values (threshold: {max_missing_percentage}%)")
                result["passed"] = False
            elif missing_pct > max_missing_percentage * 0.5:
                result["warnings"].append(f"Column '{col}' has {missing_pct:.1f}% missing values")
        
        if result["errors"]:
            result["recommendations"].append("Consider data imputation or removal of columns with excessive missing values")
        
        return result
    
    def _check_data_types(self, df: pd.DataFrame, params: dict) -> dict:
        """Check data types consistency"""
        result = {"errors": [], "warnings": [], "statistics": {}, "recommendations": [], "passed": True}
        
        expected_types = params.get("expected_types", {})
        result["statistics"]["actual_types"] = {k: str(v) for k, v in df.dtypes.items()}
        
        for col, expected_type in expected_types.items():
            if col in df.columns:
                actual_type = str(df[col].dtype)
                if expected_type not in actual_type:
                    result["errors"].append(f"Column '{col}' has type '{actual_type}', expected '{expected_type}'")
                    result["passed"] = False
            else:
                result["errors"].append(f"Expected column '{col}' not found in dataset")
                result["passed"] = False
        
        return result
    
    def _check_value_ranges(self, df: pd.DataFrame, params: dict) -> dict:
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
                
                result["statistics"][f"{col}_range"] = {"min": float(col_min), "max": float(col_max)}
                
                if min_val is not None and col_min < min_val:
                    result["errors"].append(f"Column '{col}' has values below minimum ({col_min} < {min_val})")
                    result["passed"] = False
                
                if max_val is not None and col_max > max_val:
                    result["errors"].append(f"Column '{col}' has values above maximum ({col_max} > {max_val})")
                    result["passed"] = False
        
        return result
    
    def _check_uniqueness(self, df: pd.DataFrame, params: dict) -> dict:
        """Check uniqueness constraints"""
        result = {"errors": [], "warnings": [], "statistics": {}, "recommendations": [], "passed": True}
        
        unique_columns = params.get("unique_columns", [])
        
        for col in unique_columns:
            if col in df.columns:
                duplicates = df[col].duplicated().sum()
                result["statistics"][f"{col}_duplicates"] = int(duplicates)
                
                if duplicates > 0:
                    result["errors"].append(f"Column '{col}' has {duplicates} duplicate values (should be unique)")
                    result["passed"] = False
        
        # Check for duplicate rows
        if params.get("check_duplicate_rows", False):
            duplicate_rows = df.duplicated().sum()
            result["statistics"]["duplicate_rows"] = int(duplicate_rows)
            
            if duplicate_rows > 0:
                result["warnings"].append(f"Dataset has {duplicate_rows} duplicate rows")
                result["recommendations"].append("Consider removing duplicate rows")
        
        return result

def create_test_validation_config():
    """Create test validation configuration"""
    return {
        "max_missing_percentage": 5.0,  # Max 5% missing values per column
        "validity_threshold": 0.8,      # 80% of checks must pass
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
        "unique_columns": ["id"],       # ID should be unique
        "check_duplicate_rows": True,   # Check for duplicate rows
    }

def print_validation_results(results):
    """Pretty print validation results"""
    print("\n" + "="*60)
    print("DATASET VALIDATION RESULTS")
    print("="*60)
    
    print(f"Overall Status: {'✅ VALID' if results['is_valid'] else '❌ INVALID'}")
    print(f"Validation Score: {results['validation_score']:.1%}")
    
    if results.get("errors"):
        print(f"\n🔴 ERRORS ({len(results['errors'])}):")
        for i, error in enumerate(results["errors"], 1):
            print(f"  {i}. {error}")
    
    if results.get("warnings"):
        print(f"\n🟡 WARNINGS ({len(results['warnings'])}):")
        for i, warning in enumerate(results["warnings"], 1):
            print(f"  {i}. {warning}")
    
    if results.get("statistics"):
        print(f"\n📊 STATISTICS:")
        for key, value in results["statistics"].items():
            if isinstance(value, dict):
                print(f"  {key}:")
                for sub_key, sub_value in value.items():
                    print(f"    {sub_key}: {sub_value}")
            else:
                print(f"  {key}: {value}")
    
    if results.get("recommendations"):
        print(f"\n💡 RECOMMENDATIONS:")
        for i, rec in enumerate(results["recommendations"], 1):
            print(f"  {i}. {rec}")
    
    print("="*60)

def main():
    """Main test function"""
    print("Dataset Validation Agent - Test Script")
    print("="*50)
    
    # Configuration
    dataset_path = "sample_dataset.csv"
    dataset_type = "csv"
    validation_config = create_test_validation_config()
    
    print(f"Dataset: {dataset_path}")
    print(f"Type: {dataset_type}")
    print(f"Validation Config: {json.dumps(validation_config, indent=2)}")
    
    # Check if sample dataset exists
    if not Path(dataset_path).exists():
        print(f"\n❌ Error: Sample dataset '{dataset_path}' not found!")
        print("Please ensure the sample_dataset.csv file is in the same directory.")
        return
    
    # Create validator and run test
    validator = SimpleDatasetValidator()
    
    print(f"\n🔍 Running validation...")
    results = validator.validate_dataset(dataset_path, dataset_type, validation_config)
    
    if "error" in results:
        print(f"❌ Validation failed: {results['error']}")
        return
    
    # Print results
    print_validation_results(results)
    
    print(f"\n✅ Test completed successfully!")
    print(f"Next steps:")
    print(f"1. Install uagents: pip3 install uagents pandas")
    print(f"2. Run the full agent: python3 dataset_validation_agent.py")
    print(f"3. Use the validation client to send requests")

if __name__ == "__main__":
    main()