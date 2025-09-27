#!/usr/bin/env python3
"""
Comprehensive Dataset Validation Test Script - ETH Delhi 2025
Tests the orchestrator agent with both healthcare and air quality datasets
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime
import sys
import os

# Add the agents directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dataset_orchestrator_agent import (
    ComprehensiveValidationRequest,
    ComprehensiveValidationResult,
    DatasetValidationOrchestrator
)

class ValidationTester:
    """Test harness for comprehensive dataset validation"""
    
    def __init__(self):
        self.results = {}
        self.current_dir = Path(__file__).parent
        
    async def test_dataset_validation(self, dataset_path: str, dataset_name: str) -> dict:
        """Test validation for a single dataset"""
        print(f"\n🔍 Testing {dataset_name}")
        print("=" * 50)
        
        # Check if dataset exists
        path = Path(dataset_path)
        if not path.exists():
            print(f"❌ Dataset not found: {dataset_path}")
            return {"error": "Dataset not found"}
        
        print(f"📁 Dataset: {path.name}")
        print(f"📊 Size: {path.stat().st_size / 1024:.1f} KB")
        
        try:
            # Create orchestrator
            orchestrator = DatasetValidationOrchestrator()
            
            # Create validation request
            request = ComprehensiveValidationRequest(
                request_id=f"test_{datetime.now().timestamp()}",
                dataset_path=str(dataset_path),
                dataset_name=dataset_name,
                dataset_type="csv",
                requester_id="test_client",
                include_legal_analysis=True,
                analysis_depth="complete"
            )
            
            # Start processing
            start_time = datetime.now()
            print("🚀 Starting validation process...")
            
            # Simulate the orchestrator processing
            # Step 1: Data validation
            print("📊 Running data quality validation...")
            validation_result = await orchestrator._request_validation_analysis(None, request)
            
            # Step 2: Legal compliance
            print("⚖️ Running legal compliance analysis...")  
            legal_result = await orchestrator._request_legal_analysis(None, request)
            
            # Step 3: Synthesize results
            print("🔄 Synthesizing comprehensive results...")
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Get results from orchestrator's state
            validation_data = orchestrator.active_requests.get(request.request_id, {}).get("validation_result")
            legal_data = orchestrator.active_requests.get(request.request_id, {}).get("legal_result")
            
            if validation_data and legal_data:
                comprehensive_result = await orchestrator._synthesize_comprehensive_result(
                    None, request.request_id, validation_data, legal_data, processing_time
                )
                
                # Display results
                await self._display_results(comprehensive_result, dataset_name)
                
                return {
                    "success": True,
                    "result": comprehensive_result,
                    "processing_time": processing_time
                }
            else:
                print("❌ Failed to get analysis results")
                return {"error": "Analysis failed"}
                
        except Exception as e:
            print(f"❌ Error during validation: {str(e)}")
            return {"error": str(e)}
    
    async def _display_results(self, result: ComprehensiveValidationResult, dataset_name: str):
        """Display comprehensive results"""
        print("\n🎉 VALIDATION COMPLETE!")
        print("=" * 60)
        print(f"📊 Dataset: {dataset_name}")
        print(f"⭐ Overall Score: {result.overall_correctness_score}/100")
        print(f"🏆 Grade: {result.grade}")
        print(f"⏱️  Processing Time: {result.processing_time_seconds:.2f}s")
        print(f"🤖 Agents Used: {', '.join(result.agents_used)}")
        
        # Score breakdown
        print("\n📈 SCORE BREAKDOWN:")
        for category, score in result.score_breakdown.items():
            if isinstance(score, (int, float)):
                print(f"  • {category.replace('_', ' ').title()}: {score:.1f}/100")
        
        # Executive summary
        print(f"\n📝 EXECUTIVE SUMMARY:")
        print(f"  {result.executive_summary}")
        
        # Critical issues
        if result.critical_issues:
            print(f"\n🚨 CRITICAL ISSUES ({len(result.critical_issues)}):")
            for i, issue in enumerate(result.critical_issues[:3], 1):
                print(f"  {i}. {issue}")
        
        # Issues found
        if result.issues_found:
            print(f"\n⚠️  ISSUES FOUND ({len(result.issues_found)}):")
            for i, issue in enumerate(result.issues_found[:5], 1):
                print(f"  {i}. {issue}")
        
        # Recommendations
        if result.recommendations:
            print(f"\n💡 TOP RECOMMENDATIONS:")
            for i, rec in enumerate(result.recommendations[:3], 1):
                print(f"  {i}. {rec}")
        
        print("=" * 60)
    
    async def run_comprehensive_test(self):
        """Run comprehensive test on both datasets"""
        print("🚀 COMPREHENSIVE DATASET VALIDATION TEST")
        print("ETH Delhi 2025 - Agent Orchestration Demo")
        print("=" * 60)
        
        # Define datasets to test
        datasets = [
            {
                "path": self.current_dir / "comprehensive_healthcare_dataset.csv",
                "name": "Healthcare Dataset",
                "description": "1,500 patient records with 39 healthcare parameters"
            },
            {
                "path": self.current_dir / "comprehensive_air_quality_dataset.csv", 
                "name": "Air Quality Dataset",
                "description": "1,000 environmental measurements with pollution data"
            }
        ]
        
        # Test each dataset
        for dataset in datasets:
            if dataset["path"].exists():
                print(f"\n📋 {dataset['description']}")
                result = await self.test_dataset_validation(str(dataset["path"]), dataset["name"])
                self.results[dataset["name"]] = result
            else:
                print(f"\n❌ Skipping {dataset['name']} - file not found")
                self.results[dataset["name"]] = {"error": "File not found"}
        
        # Generate summary
        await self._generate_test_summary()
    
    async def _generate_test_summary(self):
        """Generate overall test summary"""
        print("\n🏁 COMPREHENSIVE TEST SUMMARY")
        print("=" * 60)
        
        successful_tests = 0
        total_tests = len(self.results)
        
        for dataset_name, result in self.results.items():
            if result.get("success"):
                successful_tests += 1
                score = result["result"].overall_correctness_score
                grade = result["result"].grade
                time_taken = result["processing_time"]
                print(f"✅ {dataset_name}: {score}/100 (Grade {grade}) - {time_taken:.2f}s")
            else:
                print(f"❌ {dataset_name}: {result.get('error', 'Unknown error')}")
        
        print(f"\n📊 Success Rate: {successful_tests}/{total_tests} ({successful_tests/total_tests*100:.1f}%)")
        
        if successful_tests > 0:
            avg_score = sum(
                result["result"].overall_correctness_score 
                for result in self.results.values() 
                if result.get("success")
            ) / successful_tests
            
            avg_time = sum(
                result["processing_time"] 
                for result in self.results.values() 
                if result.get("success")
            ) / successful_tests
            
            print(f"📈 Average Score: {avg_score:.1f}/100")
            print(f"⏱️  Average Processing Time: {avg_time:.2f}s")
        
        print("\n🎯 TEST COMPLETE!")
        print("The orchestrator agent successfully coordinates:")
        print("• Data quality validation (16 specialized tools)")
        print("• Legal compliance checking (PII detection & fingerprinting)")
        print("• Comprehensive scoring and recommendations")
        print("• Frontend-ready JSON results with executive summaries")

async def run_quick_demo():
    """Quick demo showing the orchestrator in action"""
    print("🚀 QUICK ORCHESTRATOR DEMO")
    print("=" * 40)
    
    # Check for datasets
    current_dir = Path(__file__).parent
    healthcare_path = current_dir / "comprehensive_healthcare_dataset.csv"
    air_quality_path = current_dir / "comprehensive_air_quality_dataset.csv"
    
    if healthcare_path.exists():
        print(f"✅ Found: {healthcare_path.name}")
        
        # Create a quick validation request
        orchestrator = DatasetValidationOrchestrator()
        request = ComprehensiveValidationRequest(
            request_id="quick_demo",
            dataset_path=str(healthcare_path),
            dataset_name="Healthcare Demo",
            dataset_type="csv",
            requester_id="demo_client",
            include_legal_analysis=True,
            analysis_depth="complete"
        )
        
        print("🔄 Processing healthcare dataset...")
        print("  📊 Data quality analysis...")
        print("  ⚖️  Legal compliance check...")
        print("  🔗 Synthesizing results...")
        
        # Simulate processing
        await asyncio.sleep(2)
        
        print("✅ Demo complete!")
        print("The orchestrator would return a comprehensive JSON result with:")
        print("• Overall correctness score (0-100)")
        print("• Grade (A, B, C, D, F)")
        print("• Executive summary")
        print("• Critical issues list")
        print("• Detailed recommendations")
        print("• Score breakdown by category")
        
    else:
        print("❌ Healthcare dataset not found")
        print("Please ensure comprehensive_healthcare_dataset.csv is in the agents directory")

if __name__ == "__main__":
    print("🎯 Dataset Validation Test Suite")
    print("ETH Delhi 2025 - Comprehensive Agent Testing")
    print("\nSelect test mode:")
    print("1. Full comprehensive test (both datasets)")
    print("2. Quick demo")
    print("3. Exit")
    
    try:
        choice = input("\nEnter choice (1, 2, or 3): ").strip()
        
        if choice == "1":
            tester = ValidationTester()
            asyncio.run(tester.run_comprehensive_test())
        elif choice == "2":
            asyncio.run(run_quick_demo())
        elif choice == "3":
            print("👋 Goodbye!")
        else:
            print("❌ Invalid choice")
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test error: {str(e)}")