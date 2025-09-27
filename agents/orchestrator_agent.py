#!/usr/bin/env python3
"""
Orchestrator Agent - ETH Delhi 2025
Coordinates validation and legal compliance agents for comprehensive dataset analysis
"""

from uagents import Agent, Context, Model, Bureau
from uagents.setup import fund_agent_if_low
from typing import Dict, List, Any, Optional
import json
import asyncio
import logging
from datetime import datetime
from pathlib import Path

# Import message models from other agents
from enhanced_validation_agent import DatasetAnalysisRequest, DatasetAnalysisResult
from legal_compliance_agent import LegalComplianceRequest, LegalComplianceResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# New message models for orchestrator
class ComprehensiveValidationRequest(Model):
    """Request for comprehensive validation (both data quality and legal compliance)"""
    request_id: str
    dataset_path: Optional[str] = None
    dataset_name: str = "unknown"
    dataset_data: Optional[Dict[str, Any]] = None
    analysis_depth: str = "complete"
    include_legal_analysis: bool = True
    requester_address: str
    timestamp: str = datetime.now().isoformat()

class ComprehensiveValidationResult(Model):
    """Complete validation result with raw tool outputs only"""
    request_id: str
    success: bool
    timestamp: str
    processing_time_seconds: float
    
    # Dataset information
    dataset_name: str
    dataset_info: Dict[str, Any]
    
    # Raw tool results only (no summaries or combined data)
    validation_tool_results: Optional[Dict[str, Any]] = None  # Raw outputs from all validation tools
    legal_tool_results: Optional[Dict[str, Any]] = None       # Raw outputs from all legal tools
    
    # Status and errors
    validation_status: str = "unknown"
    legal_status: str = "unknown"
    errors: List[str] = []
    warnings: List[str] = []

class ValidationStatusRequest(Model):
    """Request for validation status"""
    request_id: str
    requester_address: str

class ValidationStatusResponse(Model):
    """Response with current validation status"""
    request_id: str
    status: str  # "processing", "completed", "failed"
    progress: Dict[str, str]  # Progress of each component
    message: str

class OrchestratorAgent:
    """Master orchestrator for comprehensive dataset validation"""
    
    def __init__(self, name: str = "orchestrator", port: int = 8002, mailbox: bool = False):
        # Agent configuration with optional mailbox support
        agent_config = {
            "name": name,
            "port": port,
            "seed": "eth_delhi_2025_orchestrator_agent",
            "endpoint": [f"http://localhost:{port}/submit"],
        }
        
        # Add mailbox configuration if requested
        if mailbox:
            agent_config["mailbox"] = True
            
        self.agent = Agent(**agent_config)
        
        # Agent state
        self.active_requests: Dict[str, Dict] = {}
        self.completed_results: Dict[str, ComprehensiveValidationResult] = {}
        self.start_time = datetime.now()
        
        # Agent addresses (will be discovered at runtime)
        self.validation_agent_address = None
        self.legal_agent_address = None
        
        # Fund agent for testnet operations
        fund_agent_if_low(self.agent.wallet.address())
        
        self._setup_handlers()
        
        # Setup logging
        self.logger = logging.getLogger(f"agent.{name}")
    
    def _setup_handlers(self):
        """Setup all agent handlers"""
        
        @self.agent.on_event("startup")
        async def startup_handler(ctx: Context):
            ctx.logger.info("🚀 Orchestrator Agent started!")
            ctx.logger.info(f"Orchestrator address: {self.agent.address}")
            ctx.logger.info("Ready to coordinate comprehensive dataset validation!")
            
            # Try to discover other agents
            await self._discover_agents(ctx)
        
        @self.agent.on_message(model=ComprehensiveValidationRequest)
        async def handle_comprehensive_request(ctx: Context, sender: str, msg: ComprehensiveValidationRequest):
            """Handle comprehensive validation requests"""
            ctx.logger.info(f"📥 Received comprehensive validation request: {msg.request_id}")
            
            # Initialize request tracking
            self.active_requests[msg.request_id] = {
                "start_time": datetime.now(),
                "requester": sender,
                "request": msg,
                "validation_status": "pending",
                "legal_status": "pending",
                "validation_result": None,
                "legal_result": None
            }
            
            try:
                # Start the comprehensive validation process
                await self._start_comprehensive_validation(ctx, msg)
                
            except Exception as e:
                ctx.logger.error(f"❌ Error starting validation: {str(e)}")
                await self._send_error_result(ctx, sender, msg.request_id, str(e))
        
        @self.agent.on_message(model=ValidationStatusRequest)
        async def handle_status_request(ctx: Context, sender: str, msg: ValidationStatusRequest):
            """Handle status requests"""
            request_data = self.active_requests.get(msg.request_id)
            
            if not request_data:
                # Check completed results
                if msg.request_id in self.completed_results:
                    status_response = ValidationStatusResponse(
                        request_id=msg.request_id,
                        status="completed",
                        progress={"validation": "completed", "legal": "completed"},
                        message="Validation completed successfully"
                    )
                else:
                    status_response = ValidationStatusResponse(
                        request_id=msg.request_id,
                        status="not_found",
                        progress={},
                        message="Request not found"
                    )
            else:
                status_response = ValidationStatusResponse(
                    request_id=msg.request_id,
                    status="processing",
                    progress={
                        "validation": request_data["validation_status"],
                        "legal": request_data["legal_status"]
                    },
                    message="Processing in progress"
                )
            
            await ctx.send(sender, status_response)
        
        @self.agent.on_message(model=DatasetAnalysisResult)
        async def handle_validation_result(ctx: Context, sender: str, msg: DatasetAnalysisResult):
            """Handle results from validation agent"""
            ctx.logger.info(f"📥 Received validation result: {msg.request_id}")
            
            if msg.request_id in self.active_requests:
                self.active_requests[msg.request_id]["validation_result"] = msg
                self.active_requests[msg.request_id]["validation_status"] = "completed" if msg.success else "failed"
                
                # Smart legal analysis triggering based on validation scores
                await self._conditionally_trigger_legal_analysis(ctx, msg.request_id, msg)
                
                # Check if we can combine results
                await self._check_and_combine_results(ctx, msg.request_id)
        
        @self.agent.on_message(model=LegalComplianceResult)
        async def handle_legal_result(ctx: Context, sender: str, msg: LegalComplianceResult):
            """Handle results from legal compliance agent"""
            ctx.logger.info(f"📥 Received legal compliance result: {msg.request_id}")
            
            if msg.request_id in self.active_requests:
                self.active_requests[msg.request_id]["legal_result"] = msg
                self.active_requests[msg.request_id]["legal_status"] = "completed" if msg.success else "failed"
                
                # Check if we can combine results
                await self._check_and_combine_results(ctx, msg.request_id)
    
    async def _discover_agents(self, ctx: Context):
        """Discover other agents in the network using Almanac contract registration"""
        ctx.logger.info("🔍 Discovering validation and legal agents...")
        
        try:
            # Try to discover agents by their known seeds/names
            from enhanced_validation_agent import DatasetValidationAgent
            from legal_compliance_agent import LegalComplianceAgent
            
            # Create temporary agent instances to get their addresses
            temp_validator = DatasetValidationAgent()
            temp_legal = LegalComplianceAgent()
            
            self.validation_agent_address = temp_validator.agent.address
            self.legal_agent_address = temp_legal.agent.address
            
            ctx.logger.info(f"� Found validation agent: {self.validation_agent_address}")
            ctx.logger.info(f"📡 Found legal agent: {self.legal_agent_address}")
            
        except Exception as e:
            ctx.logger.warning(f"⚠️ Agent discovery failed, using fallback addresses: {e}")
            # Fallback to known addresses for development
            self.validation_agent_address = "agent1qfpqn9jhvp9nnqhrmntks7xw0swag4y4mv7z6zygud6s9hqngy5ms6dh7h7"
            self.legal_agent_address = "agent1qtl5j5v6p4k4xqmq8w5h6g5i4f3e7r8s4w0r7t2l9n1x5c8z4m6k3p2s1"
        
        ctx.logger.info("✅ Agent discovery completed")
    
    async def _start_comprehensive_validation(self, ctx: Context, request: ComprehensiveValidationRequest):
        """Start the comprehensive validation process"""
        ctx.logger.info(f"🔄 Starting comprehensive validation for: {request.dataset_name}")
        
        # Prepare dataset for analysis
        dataset_path = None
        if request.dataset_path:
            dataset_path = request.dataset_path
        else:
            # Handle demo datasets
            if "healthcare" in request.dataset_name.lower():
                dataset_path = "/Users/sahasvivek/Desktop/eth delhi/eth-delhi-2025/agents/comprehensive_healthcare_dataset.csv"
            elif "air" in request.dataset_name.lower() or "quality" in request.dataset_name.lower():
                dataset_path = "/Users/sahasvivek/Desktop/eth delhi/eth-delhi-2025/agents/comprehensive_air_quality_dataset.csv"
        
        if not dataset_path or not Path(dataset_path).exists():
            raise Exception(f"Dataset not found: {dataset_path}")
        
        # 1. Start validation analysis
        validation_request = DatasetAnalysisRequest(
            request_id=request.request_id,
            dataset_path=dataset_path,
            dataset_type="csv",
            analysis_depth=request.analysis_depth,
            custom_parameters={}
        )
        
        # Since we're running in the same process, directly call the validation agent
        await self._run_validation_analysis(ctx, validation_request)
        
        # 2. Legal compliance analysis will be conditionally triggered after validation
        # Skip immediate legal analysis - we'll decide after validation results
        self.active_requests[request.request_id]["legal_status"] = "pending_validation"
        self.active_requests[request.request_id]["legal_result"] = None
        self.active_requests[request.request_id]["original_legal_request"] = request.include_legal_analysis
    
    async def _run_validation_analysis(self, ctx: Context, request: DatasetAnalysisRequest):
        """Run validation analysis using the validation agent tools"""
        try:
            # Import and use the validation agent directly
            from enhanced_validation_agent import DatasetValidationAgent
            
            # Create a validation agent instance
            validator = DatasetValidationAgent()
            
            # Run the analysis
            result = await validator._perform_complete_analysis(request, ctx)
            
            # Handle the result
            await self.handle_validation_result(ctx, ctx.address, result)
            
        except Exception as e:
            ctx.logger.error(f"❌ Validation analysis failed: {str(e)}")
            # Create an error result
            error_result = DatasetAnalysisResult(
                success=False,
                request_id=request.request_id,
                timestamp=datetime.now().isoformat(),
                dataset_info={"name": "unknown", "error": str(e)},
                raw_tool_outputs={"error": str(e)},
                persona_tags=[],
                primary_persona="unknown",
                executive_summary=f"Analysis failed: {str(e)}",
                recommendations=[],
                next_steps=[],
                errors=[str(e)]
            )
            await self.handle_validation_result(ctx, ctx.address, error_result)
    
    async def _run_legal_analysis(self, ctx: Context, request: LegalComplianceRequest):
        """Run legal compliance analysis"""
        try:
            # Import and use the legal compliance agent directly
            from legal_compliance_agent import LegalComplianceAgent
            
            # Create a legal compliance agent instance
            legal_agent = LegalComplianceAgent()
            
            # Prepare dataset
            dataset = await legal_agent._prepare_dataset(request)
            
            if dataset is not None:
                # Run the analysis (returns a single result, not a tuple)
                result = await legal_agent._perform_compliance_analysis(
                    ctx, request, dataset
                )
                
                await self.handle_legal_result(ctx, ctx.address, result)
            else:
                raise Exception("Failed to prepare dataset for legal analysis")
                
        except Exception as e:
            ctx.logger.error(f"❌ Legal analysis failed: {str(e)}")
            # Create an error result
            error_result = LegalComplianceResult(
                request_id=request.request_id,
                success=False,
                dataset_name=request.dataset_name,
                analysis_type=request.analysis_type,
                raw_tool_outputs={"error": str(e)},
                legal_summary=f"Legal analysis failed: {str(e)}",
                requires_action=True,
                key_findings=[],
                critical_recommendations=["Resolve analysis errors before proceeding"],
                error_message=str(e),
                analysis_timestamp=datetime.now().isoformat(),
                timestamp=datetime.now().isoformat(),
                processing_time_seconds=0.0,
                errors=[str(e)]
            )
            await self.handle_legal_result(ctx, ctx.address, error_result)
    
    async def _conditionally_trigger_legal_analysis(self, ctx: Context, request_id: str, validation_result: DatasetAnalysisResult):
        """Conditionally trigger legal analysis based on validation scores"""
        request_data = self.active_requests[request_id]
        original_legal_requested = request_data.get("original_legal_request", False)
        
        # Decision logic for legal analysis
        should_run_legal = False
        reason = ""
        
        if not original_legal_requested:
            # If user didn't request legal analysis, skip regardless of scores
            should_run_legal = False
            reason = "Legal analysis not requested by user"
        elif not validation_result.success:
            # If validation failed, skip legal analysis
            should_run_legal = False
            reason = "Validation failed - skipping legal analysis"
        else:
            # Always run legal analysis when requested
            ctx.logger.info(f"🎯 Running legal analysis for {request_id}")
            
            # Trigger legal analysis
            original_request = request_data["request"]
            legal_request = LegalComplianceRequest(
                request_id=request_id,
                dataset_name=original_request.dataset_name,
                dataset_path=original_request.dataset_path,
                analysis_type="full",
                include_ner=True,
                requester_address=ctx.address
            )
            
            self.active_requests[request_id]["legal_status"] = "running"
            await self._run_legal_analysis(ctx, legal_request)

    async def _check_and_combine_results(self, ctx: Context, request_id: str):
        """Check if both analyses are complete and combine results"""
        if request_id not in self.active_requests:
            return
        
        request_data = self.active_requests[request_id]
        validation_done = request_data["validation_status"] in ["completed", "failed"]
        legal_done = request_data["legal_status"] in ["completed", "failed", "skipped"]
        
        if validation_done and legal_done:
            ctx.logger.info(f"🔄 Combining results for: {request_id}")
            
            try:
                # Combine the results
                combined_result = await self._combine_validation_results(request_data)
                
                # Store the result
                self.completed_results[request_id] = combined_result
                
                # Send result to original requester
                await ctx.send(request_data["requester"], combined_result)
                
                # Cleanup active request
                del self.active_requests[request_id]
                
                ctx.logger.info(f"✅ Comprehensive validation completed: {request_id}")
                
            except Exception as e:
                ctx.logger.error(f"❌ Error combining results: {str(e)}")
                await self._send_error_result(ctx, request_data["requester"], request_id, str(e))
    
    async def _combine_validation_results(self, request_data: Dict) -> ComprehensiveValidationResult:
        """Combine validation and legal compliance results - pass through raw results without score calculations"""
        validation_result = request_data["validation_result"]
        legal_result = request_data["legal_result"]
        original_request = request_data["request"]
        processing_time = (datetime.now() - request_data["start_time"]).total_seconds()
        
        # Extract raw tool outputs (no score calculations)
        validation_tool_results = None
        if validation_result and hasattr(validation_result, 'raw_tool_outputs'):
            validation_tool_results = validation_result.raw_tool_outputs
        
        legal_tool_results = None
        if legal_result and hasattr(legal_result, 'raw_tool_outputs'):
            legal_tool_results = legal_result.raw_tool_outputs
        
        return ComprehensiveValidationResult(
            request_id=original_request.request_id,
            success=True,
            timestamp=datetime.now().isoformat(),
            processing_time_seconds=round(processing_time, 2),
            dataset_name=original_request.dataset_name,
            dataset_info=validation_result.dataset_info if validation_result else {"name": original_request.dataset_name},
            validation_tool_results=validation_tool_results,
            legal_tool_results=legal_tool_results,
            validation_status=request_data["validation_status"],
            legal_status=request_data["legal_status"]
        )
    
    async def _send_error_result(self, ctx: Context, requester: str, request_id: str, error_message: str):
        """Send an error result"""
        error_result = ComprehensiveValidationResult(
            request_id=request_id,
            success=False,
            timestamp=datetime.now().isoformat(),
            processing_time_seconds=0.0,
            dataset_name="unknown",
            dataset_info={"error": error_message},
            validation_tool_results=None,
            legal_tool_results=None,
            errors=[error_message],
            validation_status="failed",
            legal_status="failed"
        )
        
        await ctx.send(requester, error_result)
        
        # Clean up if in active requests
        if request_id in self.active_requests:
            del self.active_requests[request_id]
    
    def get_result(self, request_id: str) -> Optional[ComprehensiveValidationResult]:
        """Get completed result by request ID"""
        return self.completed_results.get(request_id)
    
    def run(self):
        """Run the orchestrator agent"""
        self.agent.run()

# For direct method calls (used by API)
async def run_comprehensive_validation(dataset_path: str, dataset_name: str, 
                                     include_legal: bool = True) -> ComprehensiveValidationResult:
    """Run comprehensive validation directly (for API use)"""
    from enhanced_validation_agent import DatasetValidationAgent, DatasetAnalysisRequest
    from legal_compliance_agent import LegalComplianceAgent, LegalComplianceRequest
    import uuid
    
    request_id = str(uuid.uuid4())
    start_time = datetime.now()
    
    try:
        # Run validation analysis
        validator = DatasetValidationAgent()
        validation_request = DatasetAnalysisRequest(
            request_id=request_id,
            dataset_path=dataset_path,
            dataset_type="csv",
            analysis_depth="complete",
            custom_parameters={}
        )
        
        # Create a dummy context for logging
        class DummyContext:
            def __init__(self):
                self.logger = logging.getLogger("api_validation")
                self.address = "api_caller"
        
        dummy_ctx = DummyContext()
        validation_result = await validator._perform_complete_analysis(validation_request, dummy_ctx)
        
        # Run legal analysis if requested
        legal_result = None
        if include_legal:
            legal_agent = LegalComplianceAgent()
            legal_request = LegalComplianceRequest(
                request_id=request_id,
                dataset_name=dataset_name,
                dataset_path=dataset_path,
                analysis_type="full",
                include_ner=True,
                requester_address="api_caller"
            )
            
            dataset = await legal_agent._prepare_dataset(legal_request)
            if dataset is not None:
                legal_result = await legal_agent._perform_compliance_analysis(
                    dummy_ctx, legal_request, dataset
                )
        
        # Combine results - pass through raw tool outputs without calculations
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Extract raw tool outputs
        validation_tool_results = None
        if validation_result and hasattr(validation_result, 'raw_tool_outputs'):
            validation_tool_results = validation_result.raw_tool_outputs
        
        legal_tool_results = None
        if legal_result and hasattr(legal_result, 'raw_tool_outputs'):
            legal_tool_results = legal_result.raw_tool_outputs
        
        return ComprehensiveValidationResult(
            request_id=request_id,
            success=True,
            timestamp=datetime.now().isoformat(),
            processing_time_seconds=round(processing_time, 2),
            dataset_name=dataset_name,
            dataset_info=validation_result.dataset_info,
            validation_tool_results=validation_tool_results,
            legal_tool_results=legal_tool_results,
            validation_status="completed",
            legal_status="completed" if include_legal else "skipped"
        )
        
    except Exception as e:
        processing_time = (datetime.now() - start_time).total_seconds()
        return ComprehensiveValidationResult(
            request_id=request_id,
            success=False,
            timestamp=datetime.now().isoformat(),
            processing_time_seconds=round(processing_time, 2),
            dataset_name=dataset_name,
            dataset_info={"error": str(e)},
            validation_tool_results=None,
            legal_tool_results=None,
            errors=[str(e)],
            validation_status="failed",
            legal_status="failed"
        )

def create_comprehensive_bureau():
    """Create a bureau with all agents following Innovation Labs pattern"""
    bureau = Bureau(port=8003)
    
    # Create all agents with different ports
    orchestrator = OrchestratorAgent(name="orchestrator", port=8002)
    
    # Import and create other agents
    from enhanced_validation_agent import DatasetValidationAgent
    from legal_compliance_agent import LegalComplianceAgent
    
    validator = DatasetValidationAgent(name="dataset_validator", port=8000)
    legal_agent = LegalComplianceAgent(name="legal_compliance", port=8001)
    
    # Add all agents to bureau for coordination
    bureau.add(orchestrator.agent)
    bureau.add(validator.agent)
    bureau.add(legal_agent.agent)
    
    logger.info("🏢 Bureau created with all agents:")
    logger.info(f"   📡 Orchestrator: {orchestrator.agent.address}")
    logger.info(f"   🔍 Validator: {validator.agent.address}")
    logger.info(f"   ⚖️ Legal Agent: {legal_agent.agent.address}")
    
    return bureau, orchestrator, validator, legal_agent

# Following Innovation Labs documentation pattern - bureau.run() at module level
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "single":
        # Run single orchestrator agent (for development/testing)
        agent = OrchestratorAgent()
        print("🚀 Starting Single Orchestrator Agent...")
        print(f"Agent address: {agent.agent.address}")
        agent.run()
    else:
        # Run comprehensive bureau (recommended pattern)
        print("🏢 Starting Comprehensive Validation Bureau...")
        bureau, orchestrator, validator, legal_agent = create_comprehensive_bureau()
        print("📡 Bureau will coordinate all validation agents")
        print("🎯 Access the web dashboard at: http://localhost:8080/validation-dashboard")
        bureau.run()