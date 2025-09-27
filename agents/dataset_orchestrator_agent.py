#!/usr/bin/env python3
"""
Dataset Orchestrator Agent - ETH Delhi 2025
Comprehensive validation system that coordinates multiple agents for complete dataset analysis
"""

from uagents import Agent, Context, Model, Bureau
from uagents.setup import fund_agent_if_low
from typing import Dict, List, Any, Optional
import json
import asyncio
import logging
from datetime import datetime
from pathlib import Path

# Import message models from existing agents
from enhanced_validation_agent import (
    DatasetAnalysisRequest, 
    DatasetAnalysisResult,
    AgentStatusRequest,
    AgentStatusResponse
)
from legal_compliance_agent import (
    LegalComplianceRequest, 
    LegalComplianceResult,
    ComplianceStatusRequest
)

# New comprehensive message models
class ComprehensiveValidationRequest(Model):
    """Request for complete dataset validation using all agents"""
    request_id: str
    dataset_path: str
    dataset_name: str
    dataset_type: Optional[str] = None
    requester_id: str
    include_legal_analysis: bool = True
    analysis_depth: str = "complete"
    timestamp: str = datetime.now().isoformat()

class ComprehensiveValidationResult(Model):
    """Complete validation result from all agents"""
    request_id: str
    success: bool
    dataset_name: str
    timestamp: str
    
    # Overall scores
    overall_correctness_score: float  # 0-100 main score for frontend
    data_quality_score: float        # From validation agent
    legal_compliance_score: float    # From legal agent
    
    # Detailed results
    validation_analysis: Dict[str, Any]
    legal_analysis: Dict[str, Any]
    
    # Summary for frontend
    executive_summary: str
    issues_found: List[str]
    recommendations: List[str]
    critical_issues: List[str]
    warnings: List[str]
    
    # Breakdown scores
    score_breakdown: Dict[str, float]
    grade: str  # A, B, C, D, F
    
    # Processing details
    processing_time_seconds: float
    agents_used: List[str]
    errors: List[str] = []

class DatasetValidationOrchestrator:
    """Master orchestrator that coordinates validation and legal compliance agents"""
    
    def __init__(self, name: str = "dataset_orchestrator", port: int = 8002):
        self.agent = Agent(
            name=name,
            port=port,
            seed="eth_delhi_2025_orchestrator_agent",
            endpoint=[f"http://localhost:{port}/submit"],
        )
        
        # Agent addresses (will be discovered at runtime)
        self.validation_agent_address = None
        self.legal_agent_address = None
        
        # Processing state
        self.active_requests = {}
        self.processed_requests = 0
        self.start_time = datetime.now()
        
        fund_agent_if_low(self.agent.wallet.address())
        self._setup_handlers()
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(f"orchestrator.{name}")

    def _setup_handlers(self):
        """Setup orchestrator agent handlers"""
        
        @self.agent.on_event("startup")
        async def startup_handler(ctx: Context):
            ctx.logger.info("🎯 Dataset Validation Orchestrator started!")
            ctx.logger.info(f"Orchestrator address: {ctx.address}")
            ctx.logger.info("Ready to coordinate comprehensive dataset validation!")
            
            # Discover other agents (in production, these would be registered in a service registry)
            self.validation_agent_address = "agent1qw8p4w9s6k0g3j2h8f7d6s5a4q3w2e1r9t8y7u6i5o4p3"  # Placeholder
            self.legal_agent_address = "agent1qz9p5x0s7k1g4j3h9f8d7s6a5q4w3e2r0t9y8u7i6o5p4"  # Placeholder

        @self.agent.on_message(model=ComprehensiveValidationRequest)
        async def handle_comprehensive_request(ctx: Context, sender: str, msg: ComprehensiveValidationRequest):
            """Handle comprehensive validation request"""
            ctx.logger.info(f"🚀 Received comprehensive validation request for: {msg.dataset_name}")
            start_time = datetime.now()
            
            try:
                # Store request state
                self.active_requests[msg.request_id] = {
                    "start_time": start_time,
                    "dataset_path": msg.dataset_path,
                    "validation_result": None,
                    "legal_result": None,
                    "sender": sender
                }
                
                # Step 1: Validate dataset exists
                dataset_path = Path(msg.dataset_path)
                if not dataset_path.exists():
                    error_msg = f"Dataset file not found: {msg.dataset_path}"
                    await self._send_error_result(ctx, sender, msg.request_id, [error_msg])
                    return
                
                # Step 2: Start validation agent analysis
                ctx.logger.info("📊 Starting data quality validation...")
                await self._request_validation_analysis(ctx, msg)
                
                # Step 3: Start legal compliance analysis (if requested)
                if msg.include_legal_analysis:
                    ctx.logger.info("⚖️ Starting legal compliance analysis...")
                    await self._request_legal_analysis(ctx, msg)
                else:
                    # Mark legal analysis as skipped
                    self.active_requests[msg.request_id]["legal_result"] = {"skipped": True}
                
                # The results will be processed when agents respond
                
            except Exception as e:
                ctx.logger.error(f"❌ Error processing request: {str(e)}")
                await self._send_error_result(ctx, sender, msg.request_id, [str(e)])

        @self.agent.on_message(model=DatasetAnalysisResult)
        async def handle_validation_result(ctx: Context, sender: str, msg: DatasetAnalysisResult):
            """Handle validation agent response"""
            ctx.logger.info(f"✅ Received validation result: {msg.success}")
            
            # Find the corresponding request
            request_id = msg.request_id
            if request_id in self.active_requests:
                self.active_requests[request_id]["validation_result"] = msg
                await self._check_completion_and_synthesize(ctx, request_id)

        @self.agent.on_message(model=LegalComplianceResult)
        async def handle_legal_result(ctx: Context, sender: str, msg: LegalComplianceResult):
            """Handle legal compliance agent response"""
            ctx.logger.info(f"⚖️ Received legal compliance result: {msg.success}")
            
            # Find the corresponding request
            request_id = msg.request_id
            if request_id in self.active_requests:
                self.active_requests[request_id]["legal_result"] = msg
                await self._check_completion_and_synthesize(ctx, request_id)

    async def _request_validation_analysis(self, ctx: Context, original_request: ComprehensiveValidationRequest):
        """Request analysis from validation agent"""
        validation_request = DatasetAnalysisRequest(
            dataset_path=original_request.dataset_path,
            dataset_type=original_request.dataset_type,
            analysis_depth=original_request.analysis_depth,
            requester_id=ctx.address,
            timestamp=datetime.now().isoformat()
        )
        
        # In a real implementation, we'd send to the actual validation agent address
        # For now, we'll process locally using the validation agent logic
        from enhanced_validation_agent import DatasetValidationAgent
        
        # Create validation agent instance for processing
        validator = DatasetValidationAgent("temp_validator", port=8003)
        result = await validator._perform_complete_analysis(validation_request, ctx)
        
        # Store the result
        if original_request.request_id in self.active_requests:
            self.active_requests[original_request.request_id]["validation_result"] = result

    async def _request_legal_analysis(self, ctx: Context, original_request: ComprehensiveValidationRequest):
        """Request legal compliance analysis"""
        legal_request = LegalComplianceRequest(
            request_id=original_request.request_id,
            dataset_name=original_request.dataset_name,
            dataset_path=original_request.dataset_path,
            analysis_type="full",
            include_ner=True,
            requester_address=ctx.address
        )
        
        # In a real implementation, we'd send to the actual legal agent address
        # For now, we'll process locally using the legal agent logic
        from legal_compliance_agent import LegalComplianceAgent
        
        try:
            # Create legal agent instance for processing
            legal_agent = LegalComplianceAgent("temp_legal", port=8004, seed="temp_legal_seed")
            
            # Prepare dataset for analysis
            import pandas as pd
            df = pd.read_csv(original_request.dataset_path)
            
            # Perform legal analysis
            legal_result = await legal_agent._perform_compliance_analysis(ctx, legal_request, df)
            
            # Store the result
            if original_request.request_id in self.active_requests:
                self.active_requests[original_request.request_id]["legal_result"] = legal_result
                
        except Exception as e:
            ctx.logger.error(f"Error in legal analysis: {str(e)}")
            # Create error result
            error_result = LegalComplianceResult(
                request_id=original_request.request_id,
                success=False,
                dataset_name=original_request.dataset_name,
                analysis_type="full",
                errors=[str(e)],
                warnings=["Legal analysis failed - proceeding with validation only"]
            )
            self.active_requests[original_request.request_id]["legal_result"] = error_result

    async def _check_completion_and_synthesize(self, ctx: Context, request_id: str):
        """Check if all analyses are complete and synthesize final result"""
        if request_id not in self.active_requests:
            return
            
        request_state = self.active_requests[request_id]
        validation_result = request_state.get("validation_result")
        legal_result = request_state.get("legal_result")
        
        # Check if both analyses are complete
        if validation_result is not None and legal_result is not None:
            ctx.logger.info("🔄 All analyses complete - synthesizing final result...")
            
            # Calculate processing time
            processing_time = (datetime.now() - request_state["start_time"]).total_seconds()
            
            # Synthesize comprehensive result
            comprehensive_result = await self._synthesize_comprehensive_result(
                ctx, request_id, validation_result, legal_result, processing_time
            )
            
            # Send result back to original requester
            sender = request_state["sender"]
            await ctx.send(sender, comprehensive_result)
            
            # Clean up
            del self.active_requests[request_id]
            self.processed_requests += 1
            
            ctx.logger.info(f"✅ Comprehensive validation completed in {processing_time:.2f}s")

    async def _synthesize_comprehensive_result(self, ctx: Context, request_id: str, 
                                            validation_result: DatasetAnalysisResult, 
                                            legal_result: LegalComplianceResult, 
                                            processing_time: float) -> ComprehensiveValidationResult:
        """Synthesize results from all agents into comprehensive result"""
        
        # Extract scores
        data_quality_score = validation_result.overall_utility_score if validation_result.success else 0.0
        
        # Handle legal compliance score
        if legal_result.get("skipped"):
            legal_compliance_score = 100.0  # No legal issues if not analyzed
        elif hasattr(legal_result, 'overall_compliance_score') and legal_result.success:
            legal_compliance_score = legal_result.overall_compliance_score
        else:
            legal_compliance_score = 50.0  # Neutral score if legal analysis failed
        
        # Calculate overall correctness score (weighted average)
        overall_correctness_score = (data_quality_score * 0.7) + (legal_compliance_score * 0.3)
        
        # Determine grade
        grade = self._calculate_grade(overall_correctness_score)
        
        # Collect all issues
        issues_found = []
        critical_issues = []
        warnings = []
        recommendations = []
        
        # From validation analysis
        if validation_result.success:
            issues_found.extend(validation_result.errors)
            warnings.extend(validation_result.warnings)
            recommendations.extend(validation_result.recommendations)
            
            # Extract critical issues based on scores
            if validation_result.data_integrity_score < 50:
                critical_issues.append("Severe data integrity issues detected")
            if validation_result.overall_utility_score < 40:
                critical_issues.append("Dataset quality below minimum threshold")
        else:
            critical_issues.extend(validation_result.errors)
        
        # From legal analysis
        if legal_result and not legal_result.get("skipped"):
            if hasattr(legal_result, 'errors'):
                issues_found.extend(legal_result.errors)
            if hasattr(legal_result, 'warnings'):
                warnings.extend(legal_result.warnings)
            if hasattr(legal_result, 'recommendations'):
                recommendations.extend(legal_result.recommendations)
                
            # Check for PII risks
            if hasattr(legal_result, 'pii_risk_score') and legal_result.pii_risk_score and legal_result.pii_risk_score > 70:
                critical_issues.append("High PII risk detected - dataset may contain sensitive information")
        
        # Generate executive summary
        executive_summary = self._generate_executive_summary(
            overall_correctness_score, grade, len(critical_issues), len(issues_found)
        )
        
        # Score breakdown
        score_breakdown = {
            "data_quality": data_quality_score,
            "legal_compliance": legal_compliance_score,
            "overall_correctness": overall_correctness_score
        }
        
        # Add detailed breakdown from validation
        if validation_result.success:
            score_breakdown.update({
                "data_integrity": validation_result.data_integrity_score,
                "statistical_quality": sum(validation_result.statistical_scores.values()) / len(validation_result.statistical_scores) if validation_result.statistical_scores else 0,
                "ml_usability": sum(validation_result.ml_usability_scores.values()) / len(validation_result.ml_usability_scores) if validation_result.ml_usability_scores else 0
            })
        
        return ComprehensiveValidationResult(
            request_id=request_id,
            success=True,
            dataset_name=validation_result.dataset_info.get("name", "Unknown") if validation_result.success else "Unknown",
            timestamp=datetime.now().isoformat(),
            
            # Main scores
            overall_correctness_score=round(overall_correctness_score, 1),
            data_quality_score=round(data_quality_score, 1),
            legal_compliance_score=round(legal_compliance_score, 1),
            
            # Detailed results
            validation_analysis=validation_result.dict() if validation_result.success else {"error": "Validation failed"},
            legal_analysis=legal_result.dict() if legal_result and not legal_result.get("skipped") else {"status": "skipped"},
            
            # Summary
            executive_summary=executive_summary,
            issues_found=issues_found[:10],  # Limit to top 10 issues
            recommendations=recommendations[:8],  # Limit to top 8 recommendations
            critical_issues=critical_issues,
            warnings=warnings[:5],  # Limit to top 5 warnings
            
            # Scores and grading
            score_breakdown=score_breakdown,
            grade=grade,
            
            # Processing metadata
            processing_time_seconds=round(processing_time, 2),
            agents_used=["validation_agent", "legal_compliance_agent"] if not legal_result.get("skipped") else ["validation_agent"],
            errors=[]
        )

    def _calculate_grade(self, score: float) -> str:
        """Calculate letter grade from numerical score"""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"

    def _generate_executive_summary(self, score: float, grade: str, critical_count: int, total_issues: int) -> str:
        """Generate executive summary for the validation"""
        if score >= 85:
            quality_desc = "excellent quality"
        elif score >= 70:
            quality_desc = "good quality with minor issues"
        elif score >= 55:
            quality_desc = "acceptable quality with some concerns"
        else:
            quality_desc = "poor quality requiring significant improvements"
        
        summary = f"Dataset validation completed with an overall score of {score:.1f}/100 (Grade {grade}). "
        summary += f"The dataset demonstrates {quality_desc}. "
        
        if critical_count > 0:
            summary += f"⚠️ {critical_count} critical issue{'s' if critical_count > 1 else ''} require immediate attention. "
        
        if total_issues > 0:
            summary += f"A total of {total_issues} issue{'s' if total_issues > 1 else ''} were identified across data quality and compliance checks."
        else:
            summary += "No significant issues were found."
            
        return summary

    async def _send_error_result(self, ctx: Context, sender: str, request_id: str, errors: List[str]):
        """Send error result back to requester"""
        error_result = ComprehensiveValidationResult(
            request_id=request_id,
            success=False,
            dataset_name="Unknown",
            timestamp=datetime.now().isoformat(),
            overall_correctness_score=0.0,
            data_quality_score=0.0,
            legal_compliance_score=0.0,
            validation_analysis={"error": "Analysis failed"},
            legal_analysis={"error": "Analysis failed"},
            executive_summary=f"Validation failed: {'; '.join(errors)}",
            issues_found=errors,
            recommendations=["Fix the identified errors and retry validation"],
            critical_issues=errors,
            warnings=[],
            score_breakdown={"error": True},
            grade="F",
            processing_time_seconds=0.0,
            agents_used=[],
            errors=errors
        )
        
        await ctx.send(sender, error_result)

    def run(self):
        """Run the orchestrator agent"""
        self.agent.run()

class ValidationClient:
    """Client for requesting comprehensive validation"""
    
    def __init__(self, name: str = "validation_client", port: int = 8005):
        self.agent = Agent(
            name=name,
            port=port,
            seed="validation_client_seed",
            endpoint=[f"http://localhost:{port}/submit"],
        )
        
        fund_agent_if_low(self.agent.wallet.address())
        self._setup_handlers()

    def _setup_handlers(self):
        """Setup client handlers"""
        
        @self.agent.on_event("startup")
        async def startup_handler(ctx: Context):
            ctx.logger.info("📱 Validation Client started!")
            ctx.logger.info(f"Client address: {ctx.address}")

        @self.agent.on_message(model=ComprehensiveValidationResult)
        async def handle_comprehensive_result(ctx: Context, sender: str, msg: ComprehensiveValidationResult):
            """Handle comprehensive validation result"""
            ctx.logger.info("🎉 COMPREHENSIVE VALIDATION COMPLETE")
            ctx.logger.info("=" * 60)
            ctx.logger.info(f"📊 Overall Correctness Score: {msg.overall_correctness_score}/100")
            ctx.logger.info(f"🏆 Grade: {msg.grade}")
            ctx.logger.info(f"⏱️  Processing Time: {msg.processing_time_seconds}s")
            ctx.logger.info(f"🤖 Agents Used: {', '.join(msg.agents_used)}")
            ctx.logger.info("")
            ctx.logger.info("📋 SCORE BREAKDOWN:")
            for category, score in msg.score_breakdown.items():
                ctx.logger.info(f"  • {category.replace('_', ' ').title()}: {score:.1f}/100")
            ctx.logger.info("")
            ctx.logger.info(f"📝 Executive Summary: {msg.executive_summary}")
            
            if msg.critical_issues:
                ctx.logger.info("")
                ctx.logger.info("🚨 CRITICAL ISSUES:")
                for issue in msg.critical_issues:
                    ctx.logger.info(f"  ❌ {issue}")
            
            if msg.issues_found:
                ctx.logger.info("")
                ctx.logger.info("⚠️  ISSUES FOUND:")
                for issue in msg.issues_found[:5]:  # Show top 5
                    ctx.logger.info(f"  • {issue}")
            
            if msg.recommendations:
                ctx.logger.info("")
                ctx.logger.info("💡 RECOMMENDATIONS:")
                for rec in msg.recommendations[:3]:  # Show top 3
                    ctx.logger.info(f"  • {rec}")
            
            ctx.logger.info("=" * 60)

    async def request_validation(self, orchestrator_address: str, dataset_path: str, dataset_name: str):
        """Request comprehensive validation"""
        request = ComprehensiveValidationRequest(
            request_id=f"req_{datetime.now().timestamp()}",
            dataset_path=dataset_path,
            dataset_name=dataset_name,
            dataset_type="csv",
            requester_id=self.agent.address,
            include_legal_analysis=True,
            analysis_depth="complete"
        )
        
        await self.agent._send(orchestrator_address, request)

    def run(self):
        """Run the client"""
        self.agent.run()

def create_validation_bureau():
    """Create a bureau with orchestrator and client"""
    bureau = Bureau(endpoint="http://127.0.0.1:8000/submit", port=8000)
    
    orchestrator = DatasetValidationOrchestrator()
    client = ValidationClient()
    
    bureau.add(orchestrator.agent)
    bureau.add(client.agent)
    
    return bureau

async def demo_comprehensive_validation():
    """Demo function to test comprehensive validation"""
    import os
    
    # Get current directory and dataset paths
    current_dir = Path(__file__).parent
    
    datasets = [
        {
            "path": current_dir / "comprehensive_healthcare_dataset.csv",
            "name": "Healthcare Dataset"
        },
        {
            "path": current_dir / "comprehensive_air_quality_dataset.csv", 
            "name": "Air Quality Dataset"
        }
    ]
    
    print("🚀 Starting Comprehensive Dataset Validation Demo")
    print("=" * 50)
    
    orchestrator = DatasetValidationOrchestrator()
    
    for dataset in datasets:
        if dataset["path"].exists():
            print(f"\n📊 Validating: {dataset['name']}")
            print(f"📁 Path: {dataset['path']}")
            
            # Create a mock request
            request = ComprehensiveValidationRequest(
                request_id=f"demo_{datetime.now().timestamp()}",
                dataset_path=str(dataset["path"]),
                dataset_name=dataset["name"],
                dataset_type="csv",
                requester_id="demo_client",
                include_legal_analysis=True,
                analysis_depth="complete"
            )
            
            # Process the request (simplified for demo)
            print(f"✅ Demo setup complete for {dataset['name']}")
        else:
            print(f"❌ Dataset not found: {dataset['path']}")

if __name__ == "__main__":
    print("🎯 Dataset Validation Orchestrator")
    print("Select mode:")
    print("1. Run orchestrator agent")
    print("2. Run demo")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        orchestrator = DatasetValidationOrchestrator()
        orchestrator.run()
    elif choice == "2":
        asyncio.run(demo_comprehensive_validation())
    else:
        print("Invalid choice")