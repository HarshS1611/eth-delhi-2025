#!/usr/bin/env python3
"""
Agent Communication Test - ETH Delhi 2025
Test the orchestrator agent communication while it's running
"""

import asyncio
import requests
import json
from typing import Dict, Any

class AgentCommunicationTester:
    """Test agent communication patterns"""
    
    def __init__(self):
        self.orchestrator_endpoint = "http://localhost:8002"
        self.validation_api_endpoint = "http://localhost:8080"
    
    async def test_orchestrator_connection(self):
        """Test if orchestrator agent is responsive"""
        print("🔍 Testing Orchestrator Agent Connection...")
        try:
            # Try to connect to the orchestrator's HTTP endpoint
            response = requests.get(f"{self.orchestrator_endpoint}/", timeout=5)
            print(f"✅ Orchestrator responding on port 8002")
            return True
        except requests.exceptions.ConnectionError:
            print(f"⚠️ Orchestrator not responding on port 8002 (normal for pure agent mode)")
            return False
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False
    
    def test_validation_api_connection(self):
        """Test if validation API is running"""
        print("🔍 Testing Validation API Connection...")
        try:
            response = requests.get(f"{self.validation_api_endpoint}/health", timeout=5)
            if response.status_code == 200:
                print(f"✅ Validation API responding on port 8080")
                return True
            else:
                print(f"⚠️ Validation API returned status {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print(f"❌ Validation API not running on port 8080")
            return False
        except Exception as e:
            print(f"❌ API connection test failed: {e}")
            return False
    
    def test_csv_upload_endpoint(self):
        """Test the CSV upload endpoint"""
        print("🔍 Testing CSV Upload Endpoint...")
        try:
            # Test with a small CSV data
            test_csv_content = """name,age,city
John,25,New York
Jane,30,London
Bob,35,Paris"""
            
            files = {'file': ('test_dataset.csv', test_csv_content, 'text/csv')}
            data = {
                'dataset_name': 'Communication Test Dataset',
                'include_legal_analysis': True,
                'analysis_depth': 'complete'
            }
            
            response = requests.post(
                f"{self.validation_api_endpoint}/validate/upload",
                files=files,
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ CSV Upload endpoint working!")
                print(f"   Request ID: {result.get('request_id')}")
                print(f"   Status URL: {result.get('status_url')}")
                return result.get('request_id')
            else:
                print(f"❌ Upload failed with status {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Upload test failed: {e}")
            return None
    
    def test_validation_status(self, request_id: str):
        """Test validation status checking"""
        if not request_id:
            print("⚠️ No request ID to check status")
            return
            
        print(f"🔍 Testing Status Check for Request: {request_id}")
        try:
            response = requests.get(
                f"{self.validation_api_endpoint}/validate/status/{request_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                status_data = response.json()
                print("✅ Status endpoint working!")
                print(f"   Status: {status_data.get('status')}")
                print(f"   Message: {status_data.get('message')}")
                return status_data
            else:
                print(f"❌ Status check failed with status {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Status check failed: {e}")
            return None
    
    def test_demo_datasets(self):
        """Test the demo dataset endpoints"""
        print("🔍 Testing Demo Dataset Endpoints...")
        
        demo_endpoints = [
            "/validate/demo/healthcare",
            "/validate/demo/air-quality"
        ]
        
        for endpoint in demo_endpoints:
            try:
                response = requests.post(
                    f"{self.validation_api_endpoint}{endpoint}",
                    json={"analysis_depth": "complete"},
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Demo endpoint {endpoint} working!")
                    print(f"   Request ID: {result.get('request_id')}")
                else:
                    print(f"⚠️ Demo endpoint {endpoint} returned {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Demo endpoint {endpoint} failed: {e}")
    
    async def run_comprehensive_test(self):
        """Run all communication tests"""
        print("🎯 ETH DELHI 2025 - AGENT COMMUNICATION TESTING")
        print("=" * 60)
        
        # Test 1: Agent Connection
        await self.test_orchestrator_connection()
        print()
        
        # Test 2: API Connection  
        api_running = self.test_validation_api_connection()
        print()
        
        if api_running:
            # Test 3: CSV Upload
            request_id = self.test_csv_upload_endpoint()
            print()
            
            # Test 4: Status Check
            if request_id:
                self.test_validation_status(request_id)
                print()
            
            # Test 5: Demo Datasets
            self.test_demo_datasets()
            print()
        
        print("🎯 Agent Communication Testing Complete!")
        print("=" * 60)
        
        if api_running:
            print("✅ System is ready for CSV file testing!")
            print("📡 Upload any CSV file to: http://localhost:8080/validate/upload")
            print("🌐 Web Dashboard: http://localhost:8080/dashboard")
        else:
            print("⚠️ Start the validation API server for full testing:")
            print("   python start_system.py")

async def main():
    """Main test function"""
    tester = AgentCommunicationTester()
    await tester.run_comprehensive_test()

if __name__ == "__main__":
    asyncio.run(main())