#!/usr/bin/env python3
"""
Manual validation demonstration
Shows exactly how the validation agent works step by step
"""

import pandas as pd
import json
from pathlib import Path

def demonstrate_validation():
    """Demonstrate the validation process step by step"""
    
    print("🧪 Dataset Validation Demonstration")
    print("=" * 60)
    
    # Load and display the sample dataset
    dataset_path = "sample_dataset.csv"
    
    if not Path(dataset_path).exists():
        print(f"❌ Sample dataset '{dataset_path}' not found!")
        return
    
    print("📊 Loading sample dataset...")
    df = pd.read_csv(dataset_path)
    
    print(f"Dataset shape: {df.shape[0]} rows × {df.shape[1]} columns")
    print("\n📋 Dataset preview:")
    print(df.head())
    
    print(f"\n📈 Data types:")
    print(df.dtypes.to_dict())
    
    print(f"\n❓ Missing values per column:")
    missing_data = df.isnull().sum()
    missing_percentages = (missing_data / len(df)) * 100
    for col in df.columns:
        if missing_data[col] > 0:
            print(f"  {col}: {missing_data[col]} ({missing_percentages[col]:.1f}%)")
        else:
            print(f"  {col}: 0 (0.0%)")
    
    print("\n" + "="*60)
    print("🔍 VALIDATION CHECKS")
    print("="*60)
    
    # Validation configuration
    config = {
        "max_missing_percentage": 5.0,
        "expected_types": {
            "id": "int64",
            "name": "object", 
            "age": "int64",  # This will fail - it's float64 due to missing value
            "salary": "int64"
        },
        "value_ranges": {
            "age": {"min": 18, "max": 120},
            "salary": {"min": 0, "max": 100000}
        },
        "unique_columns": ["id"]
    }
    
    print("📝 Validation Configuration:")
    print(json.dumps(config, indent=2))
    
    # Check 1: Completeness
    print(f"\n✅ Check 1: Data Completeness (max {config['max_missing_percentage']}% missing)")
    completeness_passed = True
    for col in df.columns:
        missing_pct = missing_percentages[col]
        if missing_pct > config['max_missing_percentage']:
            print(f"  ❌ {col}: {missing_pct:.1f}% missing (exceeds {config['max_missing_percentage']}% threshold)")
            completeness_passed = False
        elif missing_pct > 0:
            print(f"  ⚠️  {col}: {missing_pct:.1f}% missing (within threshold)")
        else:
            print(f"  ✅ {col}: No missing values")
    
    # Check 2: Data types
    print(f"\n✅ Check 2: Data Types")
    types_passed = True
    actual_types = df.dtypes.to_dict()
    
    for col, expected_type in config['expected_types'].items():
        if col in actual_types:
            actual_type = str(actual_types[col])
            if expected_type in actual_type:
                print(f"  ✅ {col}: {actual_type} (matches {expected_type})")
            else:
                print(f"  ❌ {col}: {actual_type} (expected {expected_type})")
                types_passed = False
        else:
            print(f"  ❌ {col}: Column not found")
            types_passed = False
    
    # Check 3: Value ranges
    print(f"\n✅ Check 3: Value Ranges")
    ranges_passed = True
    
    for col, range_config in config['value_ranges'].items():
        if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
            col_min = df[col].min()
            col_max = df[col].max()
            range_min = range_config.get('min')
            range_max = range_config.get('max')
            
            print(f"  📊 {col}: range {col_min} to {col_max}")
            
            if range_min is not None and col_min < range_min:
                print(f"    ❌ Minimum {col_min} < required {range_min}")
                ranges_passed = False
            elif range_min is not None:
                print(f"    ✅ Minimum {col_min} >= required {range_min}")
                
            if range_max is not None and col_max > range_max:
                print(f"    ❌ Maximum {col_max} > allowed {range_max}")
                ranges_passed = False
            elif range_max is not None:
                print(f"    ✅ Maximum {col_max} <= allowed {range_max}")
    
    # Check 4: Uniqueness
    print(f"\n✅ Check 4: Uniqueness Constraints")
    uniqueness_passed = True
    
    for col in config['unique_columns']:
        if col in df.columns:
            duplicates = df[col].duplicated().sum()
            if duplicates > 0:
                print(f"  ❌ {col}: {duplicates} duplicate values (should be unique)")
                uniqueness_passed = False
            else:
                print(f"  ✅ {col}: All values are unique")
        else:
            print(f"  ❌ {col}: Column not found")
            uniqueness_passed = False
    
    # Final result
    print("\n" + "="*60)
    print("📋 VALIDATION SUMMARY")
    print("="*60)
    
    checks = [
        ("Completeness", completeness_passed),
        ("Data Types", types_passed),
        ("Value Ranges", ranges_passed),
        ("Uniqueness", uniqueness_passed)
    ]
    
    passed_checks = sum(1 for _, passed in checks if passed)
    total_checks = len(checks)
    score = passed_checks / total_checks
    
    for check_name, passed in checks:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {check_name}: {status}")
    
    print(f"\nOverall Score: {score:.1%} ({passed_checks}/{total_checks})")
    
    validity_threshold = 0.8
    is_valid = score >= validity_threshold and all(passed for _, passed in checks)
    
    final_status = "✅ VALID" if is_valid else "❌ INVALID"
    print(f"Final Status: {final_status}")
    
    if not is_valid:
        print("\n💡 To make this dataset valid:")
        if not completeness_passed:
            print("  - Fix missing values in age column (fill or remove rows)")
        if not types_passed:
            print("  - Ensure age column contains only integers (no missing values)")
        if not ranges_passed:
            print("  - Check value ranges are within acceptable limits")
        if not uniqueness_passed:
            print("  - Remove or fix duplicate values in unique columns")
    
    print("\n" + "="*60)
    print("🎯 This is exactly what the uAgent does automatically!")
    print("The agent receives validation requests and returns these results.")
    print("="*60)

if __name__ == "__main__":
    demonstrate_validation()