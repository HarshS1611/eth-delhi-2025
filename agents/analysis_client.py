#!/usr/bin/env python3
"""
Dataset Analysis Client Agent - ETH Delhi 2025
Demonstrates proper uAgents communication patterns
"""

from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low
from enhanced_validation_agent import DatasetAnalysisRequest, DatasetAnalysisResult, AgentStatusRequest, AgentStatusResponse
import asyncio
from datetime import datetime
from pathlib import Path

class DatasetAnalysisClient:
    """Client agent for requesting dataset analysis"""
    
    def __init__(self, name: str = "analysis_client", port: int = 8001):
        self.agent = Agent(
            name=name,
            port=port,
            seed="eth_delhi_2025_analysis_client",
            endpoint=[f"http://localhost:{port}/submit"],
        )
        
        # Fund agent for testnet operations
        fund_agent_if_low(self.agent.wallet.address())
        
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup client agent handlers"""
        
        @self.agent.on_event("startup")
        async def startup_handler(ctx: Context):
            ctx.logger.info("🚀 Dataset Analysis Client started!")
            ctx.logger.info(f"Client address: {ctx.address}")
            ctx.logger.info("Ready to request dataset analysis!")
        
        @self.agent.on_message(model=DatasetAnalysisResult)
        async def handle_analysis_result(ctx: Context, sender: str, msg: DatasetAnalysisResult):
            """Handle analysis results from validation agent"""
            ctx.logger.info(f"📥 Received analysis result from {sender}")
            
            if msg.success:
                ctx.logger.info("✅ ANALYSIS SUCCESSFUL")
                ctx.logger.info(f"Overall Utility Score: {msg.overall_utility_score:.1f}/100")
                ctx.logger.info(f"Primary Persona: {msg.primary_persona}")
                ctx.logger.info(f"Grade: {msg.utility_grade['grade']} ({msg.utility_grade['description']})")
                ctx.logger.info(f"Executive Summary: {msg.executive_summary}")
                
                # Log detailed scores
                ctx.logger.info("\n📊 DETAILED SCORES:")
                if msg.integrity_scores:
                    ctx.logger.info(f"  Data Integrity: {msg.integrity_scores}")
                if msg.statistical_scores:
                    ctx.logger.info(f"  Statistical: {msg.statistical_scores}")
                if msg.ml_usability_scores:
                    ctx.logger.info(f"  ML Usability: {msg.ml_usability_scores}")
                if msg.contextual_scores:
                    ctx.logger.info(f"  Contextual: {msg.contextual_scores}")
                
                # Log recommendations
                if msg.recommendations:
                    ctx.logger.info("\n💡 RECOMMENDATIONS:")
                    for i, rec in enumerate(msg.recommendations[:5], 1):
                        ctx.logger.info(f"  {i}. {rec}")
                
                # Log publication readiness
                pub_status = msg.publication_readiness.get("status", "unknown")
                ctx.logger.info(f"\n📋 Publication Status: {pub_status.upper()}")
                
            else:
                ctx.logger.error("❌ ANALYSIS FAILED")
                ctx.logger.error(f"Errors: {msg.errors}")
                if msg.warnings:
                    ctx.logger.warning(f"Warnings: {msg.warnings}")
        
        @self.agent.on_message(model=AgentStatusResponse)
        async def handle_status_response(ctx: Context, sender: str, msg: AgentStatusResponse):
            """Handle status responses"""
            ctx.logger.info(f"📊 Status response from {msg.agent_name}:")
            ctx.logger.info(f"  Status: {msg.status}")
            ctx.logger.info(f"  Uptime: {msg.uptime}")
            ctx.logger.info(f"  Processed requests: {msg.processed_requests}")
            ctx.logger.info(f"  Available tools: {len(msg.available_tools)}")
    
    async def request_analysis(self, dataset_path: str, validator_address: str, 
                             analysis_depth: str = "complete", dataset_type: str = None):
        """Request dataset analysis from validation agent"""
        
        # Create analysis request
        request = DatasetAnalysisRequest(
            dataset_path=dataset_path,
            dataset_type=dataset_type,
            analysis_depth=analysis_depth,
            requester_id=f"client_{self.agent.address[:8]}"
        )
        
        # Send request to validator
        await self.agent._ctx.send(validator_address, request)
        self.agent._ctx.logger.info(f"📤 Analysis request sent to {validator_address}")
        self.agent._ctx.logger.info(f"Dataset: {dataset_path}")
    
    async def request_status(self, validator_address: str):
        """Request status from validation agent"""
        
        status_request = AgentStatusRequest(
            requester_id=f"client_{self.agent.address[:8]}"
        )
        
        await self.agent._ctx.send(validator_address, status_request)
        self.agent._ctx.logger.info(f"📤 Status request sent to {validator_address}")

# Demo function showing complete workflow
async def demo_analysis_workflow():
    """Demonstrate the complete analysis workflow"""
    print("🎬 ETH Delhi 2025 - Dataset Analysis Demo")
    print("=" * 60)
    
    # This would typically involve:
    # 1. Starting the validation agent
    # 2. Starting the client agent
    # 3. Client discovers validator via Almanac
    # 4. Client sends analysis request
    # 5. Validator processes dataset
    # 6. Client receives comprehensive results
    
    print("📋 Workflow Steps:")
    print("1. ✅ Enhanced validation agent with 16 specialized tools")
    print("2. ✅ Proper uAgents message patterns (Model classes)")
    print("3. ✅ Comprehensive analysis pipeline")
    print("4. ✅ Context-aware scoring and persona tagging")
    print("5. ✅ Executive summaries and actionable recommendations")
    
    print("\n🔧 uAgents Integration Features:")
    print("- ✅ Proper Agent initialization with funding")
    print("- ✅ Message models extending uAgents.Model")
    print("- ✅ Event handlers (@agent.on_event, @agent.on_message)")
    print("- ✅ Context-aware logging")
    print("- ✅ Bureau support for multi-agent coordination")
    print("- ✅ Almanac integration ready")
    
    print("\n📊 Analysis Capabilities:")
    print("- ✅ 16 specialized analysis tools")
    print("- ✅ 10 research domain personas")
    print("- ✅ 6 contextual scoring lenses")
    print("- ✅ Overall Utility Score (0-100)")
    print("- ✅ Publication readiness assessment")
    print("- ✅ Executive summaries and recommendations")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        # Run demo
        asyncio.run(demo_analysis_workflow())
    else:
        # Run client agent
        client = DatasetAnalysisClient()
        client.agent.run()