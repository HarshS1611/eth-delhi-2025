#!/usr/bin/env python3
"""
CSV File Upload Test Script - ETH Delhi 2025
Test the upload endpoint with any CSV file
"""

import requests
import json
import time
from pathlib import Path
import sys

def test_upload_endpoint(csv_file_path: str, api_base_url: str = "http://localhost:8080"):
    """Test the upload endpoint with a CSV file"""
    
    # Check if file exists
    file_path = Path(csv_file_path)
    if not file_path.exists():
        print(f"❌ File not found: {csv_file_path}")
        return
    
    if not file_path.suffix.lower() == '.csv':
        print(f"❌ File must be a CSV file: {csv_file_path}")
        return
    
    print("🚀 ETH Delhi 2025 - CSV Upload Test")
    print("=" * 50)
    print(f"📁 File: {file_path.name}")
    print(f"🌐 API: {api_base_url}")
    print()
    
    try:
        # Step 1: Upload the file
        print("📤 Uploading file...")
        with open(file_path, 'rb') as f:
            files = {'file': (file_path.name, f, 'text/csv')}
            data = {
                'dataset_name': file_path.stem,
                'include_legal_analysis': True,
                'analysis_depth': 'complete'
            }
            
            response = requests.post(
                f"{api_base_url}/validate/upload",
                files=files,
                data=data,
                timeout=30
            )
        
        if response.status_code != 200:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"Response: {response.text}")
            return
        
        upload_result = response.json()
        request_id = upload_result['request_id']
        
        print(f"✅ Upload successful!")
        print(f"📋 Request ID: {request_id}")
        print(f"📊 Dataset: {upload_result['dataset_name']}")
        print()
        
        # Step 2: Monitor progress
        print("⏳ Monitoring validation progress...")
        max_attempts = 60  # 5 minutes timeout
        attempt = 0
        
        while attempt < max_attempts:
            try:
                status_response = requests.get(
                    f"{api_base_url}/validate/status/{request_id}",
                    timeout=10
                )
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data.get('status', 'unknown')
                    
                    print(f"🔄 Status: {status}")
                    
                    if status == 'completed':
                        print("✅ Validation completed!")
                        break
                    elif status == 'failed':
                        print("❌ Validation failed!")
                        error = status_data.get('error', 'Unknown error')
                        print(f"Error: {error}")
                        return
                
                time.sleep(5)  # Wait 5 seconds
                attempt += 1
                
            except requests.RequestException as e:
                print(f"⚠️ Status check failed: {e}")
                time.sleep(5)
                attempt += 1
        
        if attempt >= max_attempts:
            print("⏰ Timeout waiting for validation to complete")
            return
        
        # Step 3: Get results
        print("📊 Fetching validation results...")
        result_response = requests.get(
            f"{api_base_url}/validate/result/{request_id}",
            timeout=30
        )
        
        if result_response.status_code == 200:
            result_data = result_response.json()
            
            print("🎯 VALIDATION RESULTS")
            print("=" * 50)
            print(f"📈 Overall Score: {result_data.get('overall_correctness_score', 0):.1f}/100")
            print(f"🏆 Grade: {result_data.get('grade', 'N/A')}")
            print(f"📊 Data Quality: {result_data.get('data_quality_score', 0):.1f}/100")
            print(f"⚖️ Legal Compliance: {result_data.get('legal_compliance_score', 0):.1f}/100")
            print()
            
            print("📝 Executive Summary:")
            print(result_data.get('executive_summary', 'No summary available'))
            print()
            
            if result_data.get('recommendations'):
                print("💡 Recommendations:")
                for i, rec in enumerate(result_data['recommendations'][:5], 1):
                    print(f"  {i}. {rec}")
                print()
            
            if result_data.get('critical_issues'):
                print("⚠️ Critical Issues:")
                for i, issue in enumerate(result_data['critical_issues'][:3], 1):
                    print(f"  {i}. {issue}")
            
        else:
            print(f"❌ Failed to get results: {result_response.status_code}")
            print(f"Response: {result_response.text}")
    
    except requests.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python test_upload.py <path_to_csv_file> [api_url]")
        print("Example: python test_upload.py my_dataset.csv")
        print("Example: python test_upload.py my_dataset.csv http://localhost:8080")
        return
    
    csv_file = sys.argv[1]
    api_url = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:8080"
    
    test_upload_endpoint(csv_file, api_url)

if __name__ == "__main__":
    main()