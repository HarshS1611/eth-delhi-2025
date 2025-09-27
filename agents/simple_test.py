#!/usr/bin/env python3
"""
Simple Validation Test - ETH Delhi 2025
Quick test to verify the validation system works
"""

import asyncio
import sys
from pathlib import Path

# Add the agents directory to Python path
sys.path.append(str(Path(__file__).parent))

from tools import tool_registry

async def test_basic_tools():
    """Test basic tools functionality"""
    print("🔧 Testing Basic Tools Functionality")
    print("=" * 50)
    
    # Test if we can load the healthcare dataset
    try:
        dataset_path = Path(__file__).parent / "comprehensive_healthcare_dataset.csv"
        
        if not dataset_path.exists():
            print(f"❌ Healthcare dataset not found: {dataset_path}")
            return False
        
        print(f"📊 Loading dataset: {dataset_path.name}")
        
        # Test data loader
        result = await tool_registry.execute_tool(
            "data_loader", 
            file_path=str(dataset_path),
            format_type="csv"
        )
        
        if result["success"]:
            df = result["data"]
            metadata = result["metadata"]
            print(f"✅ Data loaded successfully:")
            print(f"   📏 Shape: {metadata['shape']}")
            print(f"   📊 Columns: {len(metadata['columns'])}")
            print(f"   💾 Size: {metadata['size_mb']:.1f} MB")
            
            # Test data profiler
            print("🔍 Running data profiler...")
            profile_result = await tool_registry.execute_tool(
                "data_profiler",
                data=df
            )
            
            if profile_result["success"]:
                profile = profile_result["profile"]
                print(f"✅ Data profiling completed:")
                print(f"   📊 Quality Score: {profile['quality_score']:.1f}/100")
                print(f"   🔢 Numeric Columns: {len(profile.get('numeric_columns', []))}")
                print(f"   📝 Text Columns: {len(profile.get('categorical_columns', []))}")
                return True
            else:
                print(f"❌ Data profiling failed: {profile_result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Data loading failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_legal_tools():
    """Test legal compliance tools"""
    print("\n⚖️ Testing Legal Compliance Tools")
    print("=" * 50)
    
    try:
        from legal_tools import legal_tool_registry
        import pandas as pd
        
        # Create a simple test dataset
        test_data = pd.DataFrame({
            'name': ['John Doe', 'Jane Smith', 'Bob Johnson'],
            'email': ['john@example.com', 'jane@test.com', 'bob@sample.org'],
            'phone': ['555-1234', '555-5678', '555-9999'],
            'score': [85, 92, 78]
        })
        
        print("🔍 Testing PII scanner...")
        pii_result = await legal_tool_registry.execute_tool(
            'pii_scanner',
            data=test_data,
            include_ner=False  # Skip NER since we don't have spaCy
        )
        
        if pii_result["success"]:
            print("✅ PII scanning completed:")
            print(f"   🔢 Risk Score: {pii_result['pii_risk_score']:.1f}/100")
            print(f"   📊 Entities Found: {len(pii_result.get('detected_entities', []))}")
            
            # Test fingerprinting
            print("🔍 Testing dataset fingerprinting...")
            fingerprint_result = await legal_tool_registry.execute_tool(
                'dataset_fingerprinting',
                data=test_data,
                dataset_name="Test Dataset"
            )
            
            if fingerprint_result["success"]:
                print("✅ Dataset fingerprinting completed:")
                print(f"   🔒 Originality Score: {fingerprint_result['originality_score']:.1f}/100")
                print(f"   ✨ Status: {fingerprint_result['verification_status']}")
                return True
            else:
                print(f"❌ Fingerprinting failed: {fingerprint_result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ PII scanning failed: {pii_result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Legal tools test failed: {str(e)}")
        return False

async def main():
    """Run the simple validation test"""
    print("🚀 ETH DELHI 2025 - SIMPLE VALIDATION TEST")
    print("=" * 60)
    
    # Test basic tools
    basic_success = await test_basic_tools()
    
    # Test legal tools
    legal_success = await test_legal_tools()
    
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"🔧 Basic Tools: {'✅ PASSED' if basic_success else '❌ FAILED'}")
    print(f"⚖️ Legal Tools: {'✅ PASSED' if legal_success else '❌ FAILED'}")
    
    if basic_success and legal_success:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Core validation tools are working")
        print("✅ Legal compliance tools are working")
        print("✅ System is functional for basic operations")
        print("\n🌐 You can now start the API server:")
        print("   python validation_api.py")
        print("🎯 And access the dashboard at: http://localhost:8080")
        return True
    else:
        print("\n⚠️ SOME TESTS FAILED")
        print("🔧 Please check the errors above")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 Test interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)