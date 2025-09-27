#!/usr/bin/env python3
"""
Direct HTTP API test for the Dataset Validation Agent
This bypasses agent messaging and tests the HTTP endpoint directly
"""

import requests
import json
import time

def test_validation_via_http():
    """Test the validation agent via HTTP API"""
    
    print("🧪 Testing Dataset Validation Agent via HTTP")
    print("=" * 50)
    
    # Agent endpoint (from the running agent logs)
    agent_url = "http://127.0.0.1:8001/submit"
    
    # Test validation configuration
    validation_request = {
        "dataset_path": "sample_dataset.csv",
        "validation_parameters": {
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
        },
        "dataset_type": "csv"
    }
    
    print(f"🎯 Target URL: {agent_url}")
    print(f"📁 Dataset: {validation_request['dataset_path']}")
    print(f"📋 Validation parameters: {len(validation_request['validation_parameters'])} checks")
    print()
    
    try:
        print("📤 Sending HTTP request...")
        
        response = requests.post(
            agent_url,
            json=validation_request,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"📨 Response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Request successful!")
            try:
                result = response.json()
                print("\n📊 VALIDATION RESULT:")
                print("-" * 30)
                print(json.dumps(result, indent=2))
            except json.JSONDecodeError:
                print("📝 Response content:", response.text)
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print("📝 Response:", response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed!")
        print("💡 Make sure the dataset_validation_agent.py is running")
        print("   Run: python3 dataset_validation_agent.py")
        
    except requests.exceptions.Timeout:
        print("⏰ Request timed out")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def check_agent_status():
    """Check if the agent is running"""
    print("🔍 Checking if validation agent is running...")
    
    try:
        response = requests.get("http://127.0.0.1:8001", timeout=5)
        print("✅ Agent is running!")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Agent is not running")
        return False
    except Exception as e:
        print(f"❓ Could not determine agent status: {e}")
        return False

def main():
    """Main test function"""
    print("Dataset Validation Agent - HTTP Test")
    print("=" * 50)
    
    # Check if agent is running
    if not check_agent_status():
        print("\n🚀 To start the agent, run:")
        print("   python3 dataset_validation_agent.py")
        print("\nThen run this test again.")
        return
    
    print()
    
    # Wait a moment
    time.sleep(1)
    
    # Run the test
    test_validation_via_http()
    
    print("\n" + "=" * 50)
    print("🏁 Test completed!")

if __name__ == "__main__":
    main()