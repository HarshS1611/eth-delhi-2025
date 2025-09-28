#!/usr/bin/env python3
"""
Complete Air Quality Dataset Validation + LLM Analysis Test
Single test script for the entire workflow
"""

import requests
import json
import time
from pathlib import Path

def test_complete_workflow():
    """Test the complete validation + LLM analysis workflow"""
    
    print("🌬️ COMPLETE AIR QUALITY DATASET ANALYSIS")
    print("=" * 60)
    
    # Configuration
    BASE_URL = "http://localhost:8000"
    DATASET_FILE = "comprehensive_air_quality_dataset.csv"
    DATASET_NAME = "Comprehensive Air Quality Dataset"
    ASI_ONE_API_KEY = "sk_0665376abf204d5197802bf566d03b40c16ec82816974ba6b288566977fb179d"
    
    # Check prerequisites
    print("🔍 Step 1: Checking prerequisites...")
    if not Path(DATASET_FILE).exists():
        print(f"❌ Dataset file not found: {DATASET_FILE}")
        return
    
    # Test API health
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print(f"✅ API is healthy")
            print(f"   Status: {health.get('status')}")
            print(f"   Agents: {health.get('agents_available', [])}")
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to API: {str(e)}")
        print("   Make sure validation_api.py is running on localhost:8000")
        return
    
    # Step 2: Upload dataset for validation
    print(f"\n📤 Step 2: Uploading dataset for validation...")
    try:
        with open(DATASET_FILE, 'rb') as f:
            files = {'file': (DATASET_FILE, f, 'text/csv')}
            data = {
                'dataset_name': DATASET_NAME,
                'include_legal_analysis': 'true',
                'analysis_depth': 'complete'
            }
            
            response = requests.post(f"{BASE_URL}/validate/upload", files=files, data=data, timeout=30)
            
            if response.status_code != 200:
                print(f"❌ Upload failed: {response.status_code} - {response.text}")
                return
            
            upload_result = response.json()
            request_id = upload_result['request_id']
            print(f"✅ Dataset uploaded successfully!")
            print(f"   Request ID: {request_id}")
    
    except Exception as e:
        print(f"❌ Upload error: {str(e)}")
        return
    
    # Step 3: Wait for validation to complete
    print(f"\n⏳ Step 3: Waiting for validation to complete...")
    validation_completed = False
    max_attempts = 60  # 5 minutes timeout
    
    for attempt in range(1, max_attempts + 1):
        try:
            response = requests.get(f"{BASE_URL}/validate/status/{request_id}", timeout=10)
            
            if response.status_code == 200:
                status_data = response.json()
                status = status_data['status']
                progress = status_data.get('progress', '')
                
                print(f"   Attempt {attempt}/60: {status} - {progress}")
                
                if status == 'completed':
                    validation_completed = True
                    break
                elif status == 'failed':
                    print("❌ Validation failed!")
                    return
            else:
                print(f"   Status check failed: {response.status_code}")
            
            time.sleep(5)  # Wait 5 seconds between checks
            
        except Exception as e:
            print(f"   Status check error: {str(e)}")
            time.sleep(5)
    
    if not validation_completed:
        print("❌ Validation timeout after 5 minutes!")
        return
    
    print("✅ Validation completed successfully!")
    
    # Step 4: Get validation results
    print(f"\n📊 Step 4: Retrieving validation results...")
    try:
        response = requests.get(f"{BASE_URL}/validate/result/{request_id}", timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Failed to get validation results: {response.status_code} - {response.text}")
            return
        
        validation_results = response.json()
        print("✅ Validation results retrieved!")
        
        # Display validation summary
        print(f"\n📋 VALIDATION SUMMARY:")
        print(f"   Dataset: {validation_results.get('dataset_name')}")
        print(f"   Success: {validation_results.get('success')}")
        print(f"   Processing Time: {validation_results.get('processing_time_seconds', 0):.2f}s")
        print(f"   Critical Issues: {len(validation_results.get('critical_issues', []))}")
        
        # Show top issues
        critical_issues = validation_results.get('critical_issues', [])
        if critical_issues:
            print(f"\n⚠️  TOP CRITICAL ISSUES:")
            for i, issue in enumerate(critical_issues[:3], 1):
                print(f"   {i}. {issue}")
    
    except Exception as e:
        print(f"❌ Error getting validation results: {str(e)}")
        return
    
    # Step 5: Get ASI:One LLM analysis
    print(f"\n🤖 Step 5: Getting ASI:One LLM expert analysis...")
    try:
        llm_payload = {
            "request_id": request_id,
            "asi_one_api_key": ASI_ONE_API_KEY,
            "dataset_name": DATASET_NAME
        }
        
        response = requests.post(f"{BASE_URL}/analyze/asi-one", json=llm_payload, timeout=120)
        
        if response.status_code != 200:
            print(f"❌ LLM analysis failed: {response.status_code} - {response.text}")
            return
        
        llm_results = response.json()
        print("✅ ASI:One LLM analysis completed!")
        
        # Print the complete LLM results JSON object
        print(f"\n🎯 COMPLETE LLM RESULTS JSON:")
        print("=" * 50)
        print(json.dumps(llm_results, indent=2, ensure_ascii=False, default=str))
        print("=" * 50)
    
    except Exception as e:
        print(f"❌ LLM analysis error: {str(e)}")
        return
    
    # Step 6: Save complete results
    print(f"\n💾 Step 6: Saving complete results...")
    try:
        complete_results = {
            "test_info": {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "dataset_file": DATASET_FILE,
                "request_id": request_id
            },
            "validation_results": validation_results,
            "llm_analysis": llm_results,
            "summary": {
                "validation_success": validation_results.get('success'),
                "llm_success": llm_results.get('success'),
                "quality_score": llm_results.get('quality_score'),
                "critical_issues_count": len(validation_results.get('critical_issues', [])),
                "processing_time_seconds": validation_results.get('processing_time_seconds', 0)
            }
        }
        
        output_file = "complete_air_quality_analysis.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(complete_results, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"✅ Complete results saved to: {output_file}")
    
    except Exception as e:
        print(f"❌ Error saving results: {str(e)}")
        return
    
    # Final summary
    print(f"\n🎉 COMPLETE WORKFLOW SUCCESSFUL!")
    print("=" * 50)
    print(f"✅ Dataset validated: {DATASET_NAME}")
    print(f"✅ Quality score: {llm_results.get('quality_score', 'N/A')}/100")
    print(f"✅ Processing time: {validation_results.get('processing_time_seconds', 0):.2f}s")
    print(f"✅ Critical issues found: {len(validation_results.get('critical_issues', []))}")
    print(f"✅ LLM analysis tokens: {llm_results.get('token_usage', {}).get('total_tokens', 'N/A')}")
    print(f"✅ Results saved: {output_file}")
    print(f"\n🔍 Check {output_file} for complete detailed analysis!")

if __name__ == "__main__":
    test_complete_workflow()