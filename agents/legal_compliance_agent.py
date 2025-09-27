#!/usr/bin/env python3
"""
Legal Compliance Agent - Fetch.ai uAgents Integration
ETH Delhi 2025 - Autonomous Legal Compliance Checking

This agent provides autonomous legal compliance checking for datasets using
Dataset Fingerprinting and PII Scanning capabilities within the uAgents framework.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
import pandas as pd
from datetime import datetime

# uAgents framework imports
from uagents import Agent, Context, Model, Bureau
from uagents.setup import fund_agent_if_low

# Import our legal tools
from legal_tools import legal_tool_registry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Message Models for uAgents communication
class LegalComplianceRequest(Model):
    """Request model for legal compliance analysis"""
    request_id: str
    dataset_name: str
    dataset_path: Optional[str] = None
    dataset_data: Optional[Dict[str, Any]] = None  # For passing small datasets directly
    analysis_type: str = "full"  # Options: "full", "fingerprinting", "pii_scan"
    include_ner: bool = True
    requester_address: str

class LegalComplianceResult(Model):
    """Result model for legal compliance analysis"""
    request_id: str
    success: bool
    dataset_name: str
    analysis_type: str
    
    # Fingerprinting results
    dataset_fingerprint: Optional[str] = None
    verification_status: Optional[str] = None
    originality_score: Optional[float] = None
    
    # PII scanning results
    pii_risk_score: Optional[float] = None
    pii_risk_level: Optional[str] = None
    columns_with_pii: Optional[int] = None
    
    # Overall compliance
    overall_risk_level: str
    legal_status: str
    requires_action: bool
    overall_compliance_score: float = 50.0  # 0-100 score for overall compliance
    
    # Detailed results (truncated for message size)
    key_findings: List[str]
    critical_recommendations: List[str]
    
    # Error handling
    error_message: Optional[str] = None
    analysis_timestamp: str

class ComplianceStatusRequest(Model):
    """Request model for compliance status updates"""
    request_id: str
    requester_address: str

class ComplianceStatusUpdate(Model):
    """Model for compliance status updates"""
    request_id: str
    status: str  # "processing", "completed", "error"
    progress_percentage: float
    current_step: str
    estimated_completion: Optional[str] = None

# Legal Compliance Agent
class LegalComplianceAgent:
    """Autonomous legal compliance agent using Fetch.ai uAgents framework"""
    
    def __init__(self, name: str = "legal_compliance_agent", port: int = 8001, seed: str = "legal_compliance_seed"):
        """Initialize the legal compliance agent"""
        
        # Create the uAgent
        self.agent = Agent(
            name=name,
            port=port,
            seed=seed,
            endpoint=[f"http://localhost:{port}/submit"],
        )
        
        # Fund agent for testnet operations
        fund_agent_if_low(self.agent.wallet.address())
        
        # Agent state
        self.active_requests = {}  # Track active analysis requests
        
        # Register event handlers
        self._register_handlers()
        
        logger.info(f"Legal Compliance Agent initialized: {self.agent.address}")
    
    def _register_handlers(self):
        """Register all message and event handlers"""
        
        @self.agent.on_event("startup")
        async def startup_handler(ctx: Context):
            """Handle agent startup"""
            ctx.logger.info("🚀 Legal Compliance Agent starting up...")
            ctx.logger.info(f"Agent address: {self.agent.address}")
            ctx.logger.info("Available legal tools:")
            
            tools = legal_tool_registry.list_tools()
            for name, description in tools.items():
                ctx.logger.info(f"  • {name}: {description}")
            
            ctx.logger.info("✅ Legal Compliance Agent ready for requests")
        
        @self.agent.on_message(model=LegalComplianceRequest)
        async def handle_compliance_request(ctx: Context, sender: str, msg: LegalComplianceRequest):
            """Handle legal compliance analysis requests"""
            
            ctx.logger.info(f"📋 Received legal compliance request from {sender}")
            ctx.logger.info(f"Request ID: {msg.request_id}")
            ctx.logger.info(f"Dataset: {msg.dataset_name}")
            ctx.logger.info(f"Analysis type: {msg.analysis_type}")
            
            # Track the request
            self.active_requests[msg.request_id] = {
                "sender": sender,
                "dataset_name": msg.dataset_name,
                "analysis_type": msg.analysis_type,
                "start_time": datetime.now(),
                "status": "processing"
            }
            
            try:
                # Send status update
                await self._send_status_update(ctx, sender, msg.request_id, 
                                             "processing", 10.0, "Loading dataset...")
                
                # Load or prepare dataset
                dataset = await self._prepare_dataset(msg)
                if dataset is None:
                    raise ValueError("Could not load or prepare dataset")
                
                # Perform analysis based on request type
                result = await self._perform_compliance_analysis(
                    ctx, msg, dataset
                )
                
                # Send final result
                await ctx.send(sender, result)
                
                # Update request status
                self.active_requests[msg.request_id]["status"] = "completed"
                ctx.logger.info(f"✅ Completed analysis for request {msg.request_id}")
                
            except Exception as e:
                ctx.logger.error(f"❌ Analysis failed for request {msg.request_id}: {e}")
                
                # Send error result
                error_result = LegalComplianceResult(
                    request_id=msg.request_id,
                    success=False,
                    dataset_name=msg.dataset_name,
                    analysis_type=msg.analysis_type,
                    overall_risk_level="Unknown",
                    legal_status="Analysis Failed",
                    requires_action=True,
                    overall_compliance_score=0.0,  # Failed analysis gets 0 score
                    key_findings=[],
                    critical_recommendations=[f"Analysis failed: {str(e)}"],
                    error_message=str(e),
                    analysis_timestamp=datetime.now().isoformat()
                )
                
                await ctx.send(sender, error_result)
                self.active_requests[msg.request_id]["status"] = "error"
        
        @self.agent.on_message(model=ComplianceStatusRequest)
        async def handle_status_request(ctx: Context, sender: str, msg: ComplianceStatusRequest):
            """Handle status update requests"""
            
            if msg.request_id in self.active_requests:
                request_info = self.active_requests[msg.request_id]
                
                status_update = ComplianceStatusUpdate(
                    request_id=msg.request_id,
                    status=request_info["status"],
                    progress_percentage=100.0 if request_info["status"] == "completed" else 50.0,
                    current_step=f"Analyzing {request_info['dataset_name']}"
                )
                
                await ctx.send(sender, status_update)
            else:
                # Request not found
                status_update = ComplianceStatusUpdate(
                    request_id=msg.request_id,
                    status="not_found",
                    progress_percentage=0.0,
                    current_step="Request not found"
                )
                
                await ctx.send(sender, status_update)
    
    async def _send_status_update(self, ctx: Context, sender: str, request_id: str, 
                                 status: str, progress: float, step: str):
        """Send status update to requester"""
        
        update = ComplianceStatusUpdate(
            request_id=request_id,
            status=status,
            progress_percentage=progress,
            current_step=step
        )
        
        try:
            await ctx.send(sender, update)
        except Exception as e:
            ctx.logger.warning(f"Could not send status update: {e}")
    
    async def _prepare_dataset(self, msg: LegalComplianceRequest) -> Optional[pd.DataFrame]:
        """Prepare dataset for analysis"""
        
        if msg.dataset_data:
            # Convert dictionary data to DataFrame
            try:
                return pd.DataFrame(msg.dataset_data)
            except Exception as e:
                logger.error(f"Could not convert dataset_data to DataFrame: {e}")
                return None
        
        elif msg.dataset_path:
            # Load dataset from file path
            try:
                if msg.dataset_path.endswith('.csv'):
                    return pd.read_csv(msg.dataset_path)
                elif msg.dataset_path.endswith('.json'):
                    return pd.read_json(msg.dataset_path)
                elif msg.dataset_path.endswith('.xlsx'):
                    return pd.read_excel(msg.dataset_path)
                else:
                    logger.error(f"Unsupported file format: {msg.dataset_path}")
                    return None
            except Exception as e:
                logger.error(f"Could not load dataset from {msg.dataset_path}: {e}")
                return None
        
        else:
            logger.error("No dataset data or path provided")
            return None
    
    async def _perform_compliance_analysis(self, ctx: Context, msg: LegalComplianceRequest, 
                                         dataset: pd.DataFrame) -> LegalComplianceResult:
        """Perform the requested compliance analysis"""
        
        fingerprint_result = None
        pii_result = None
        
        # Perform fingerprinting analysis
        if msg.analysis_type in ["full", "fingerprinting"]:
            ctx.logger.info("🔍 Running dataset fingerprinting...")
            await self._send_status_update(ctx, msg.requester_address, msg.request_id, 
                                         "processing", 30.0, "Running fingerprinting analysis...")
            
            fingerprint_result = await legal_tool_registry.execute_tool(
                'dataset_fingerprinting',
                data=dataset,
                dataset_name=msg.dataset_name
            )
        
        # Perform PII scanning
        if msg.analysis_type in ["full", "pii_scan"]:
            ctx.logger.info("🕵️ Running PII scanning...")
            await self._send_status_update(ctx, msg.requester_address, msg.request_id, 
                                         "processing", 70.0, "Running PII analysis...")
            
            pii_result = await legal_tool_registry.execute_tool(
                'pii_scanner',
                data=dataset,
                include_ner=msg.include_ner
            )
        
        # Combine results and generate final assessment
        ctx.logger.info("📊 Generating compliance assessment...")
        await self._send_status_update(ctx, msg.requester_address, msg.request_id, 
                                      "processing", 90.0, "Generating final report...")
        
        return self._combine_analysis_results(msg, fingerprint_result, pii_result)
    
    def _combine_analysis_results(self, msg: LegalComplianceRequest, 
                                fingerprint_result: Optional[Dict], 
                                pii_result: Optional[Dict]) -> LegalComplianceResult:
        """Combine analysis results into a comprehensive compliance assessment"""
        
        # Extract key metrics
        dataset_fingerprint = None
        verification_status = None
        originality_score = None
        pii_risk_score = None
        pii_risk_level = None
        columns_with_pii = None
        
        key_findings = []
        critical_recommendations = []
        
        # Process fingerprinting results
        if fingerprint_result and fingerprint_result.get('success'):
            dataset_fingerprint = fingerprint_result['dataset_fingerprint']
            verification_status = fingerprint_result['verification_status']
            originality_score = fingerprint_result['originality_score']
            
            key_findings.append(f"Dataset fingerprint: {dataset_fingerprint[:16]}...")
            key_findings.append(f"Verification status: {verification_status}")
            key_findings.append(f"Originality score: {originality_score}/100")
            
            # Add top recommendations
            fingerprint_recs = fingerprint_result.get('recommendations', [])
            critical_recommendations.extend(fingerprint_recs[:2])
        
        # Process PII results
        if pii_result and pii_result.get('success'):
            pii_risk_score = pii_result['pii_risk_score']
            pii_risk_level = pii_result['risk_level']
            columns_with_pii = pii_result['risk_assessment']['columns_with_pii']
            
            key_findings.append(f"PII risk score: {pii_risk_score}/100")
            key_findings.append(f"PII risk level: {pii_risk_level}")
            key_findings.append(f"Columns with PII: {columns_with_pii}")
            
            # Add top PII recommendations
            pii_recs = pii_result.get('recommendations', [])
            critical_recommendations.extend(pii_recs[:2])
        
        # Determine overall risk and legal status
        overall_risk_level, legal_status, requires_action = self._calculate_overall_compliance(
            fingerprint_result, pii_result
        )
        
        # Calculate overall compliance score (0-100)
        compliance_score = self._calculate_compliance_score(
            originality_score, pii_risk_score, overall_risk_level
        )
        
        return LegalComplianceResult(
            request_id=msg.request_id,
            success=True,
            dataset_name=msg.dataset_name,
            analysis_type=msg.analysis_type,
            dataset_fingerprint=dataset_fingerprint,
            verification_status=verification_status,
            originality_score=originality_score,
            pii_risk_score=pii_risk_score,
            pii_risk_level=pii_risk_level,
            columns_with_pii=columns_with_pii,
            overall_risk_level=overall_risk_level,
            legal_status=legal_status,
            requires_action=requires_action,
            overall_compliance_score=compliance_score,
            key_findings=key_findings[:10],  # Limit for message size
            critical_recommendations=critical_recommendations[:5],  # Limit for message size
            analysis_timestamp=datetime.now().isoformat()
        )
    
    def _calculate_overall_compliance(self, fingerprint_result: Optional[Dict], 
                                    pii_result: Optional[Dict]) -> tuple:
        """Calculate overall compliance assessment"""
        
        risk_levels = []
        requires_action = False
        legal_issues = []
        
        # Assess fingerprinting risks
        if fingerprint_result and fingerprint_result.get('success'):
            originality_score = fingerprint_result.get('originality_score', 100)
            verification_status = fingerprint_result.get('verification_status', 'Original')
            
            if verification_status == "Known Public Dataset":
                legal_issues.append("Known public dataset - check licensing")
                requires_action = True
                risk_levels.append("Medium")
            elif originality_score < 60:
                legal_issues.append("Low originality score")
                requires_action = True
                risk_levels.append("Medium")
            else:
                risk_levels.append("Low")
        
        # Assess PII risks
        if pii_result and pii_result.get('success'):
            pii_risk_level = pii_result.get('risk_level', 'Minimal')
            columns_with_pii = pii_result.get('risk_assessment', {}).get('columns_with_pii', 0)
            
            if pii_risk_level == "High":
                legal_issues.append("High PII risk detected")
                requires_action = True
                risk_levels.append("High")
            elif pii_risk_level == "Medium":
                legal_issues.append("Medium PII risk detected")
                requires_action = True
                risk_levels.append("Medium")
            elif columns_with_pii > 0:
                legal_issues.append("Some PII detected")
                risk_levels.append("Low")
            else:
                risk_levels.append("Minimal")
        
        # Determine overall risk
        if "High" in risk_levels:
            overall_risk = "High"
        elif "Medium" in risk_levels:
            overall_risk = "Medium"
        elif "Low" in risk_levels:
            overall_risk = "Low"
        else:
            overall_risk = "Minimal"
        
        # Determine legal status
        if requires_action:
            legal_status = f"Action Required: {'; '.join(legal_issues)}"
        else:
            legal_status = "Compliant"
        
        return overall_risk, legal_status, requires_action
    
    def _calculate_compliance_score(self, originality_score: Optional[float], 
                                   pii_risk_score: Optional[float], 
                                   overall_risk_level: str) -> float:
        """Calculate overall compliance score (0-100)"""
        
        score = 100.0
        
        # Deduct based on originality
        if originality_score is not None:
            if originality_score < 60:
                score -= 30  # Major deduction for low originality
            elif originality_score < 80:
                score -= 15  # Moderate deduction
        
        # Deduct based on PII risk
        if pii_risk_score is not None:
            if pii_risk_score > 70:
                score -= 25  # High PII risk
            elif pii_risk_score > 40:
                score -= 15  # Medium PII risk
            elif pii_risk_score > 20:
                score -= 5   # Low PII risk
        
        # Deduct based on overall risk level
        if overall_risk_level == "High":
            score -= 20
        elif overall_risk_level == "Medium":
            score -= 10
        elif overall_risk_level == "Low":
            score -= 5
        
        return max(0.0, min(100.0, score))
    
    def run(self):
        """Run the legal compliance agent"""
        self.agent.run()

# Client Agent for Testing
class LegalComplianceClient:
    """Client agent for testing legal compliance requests"""
    
    def __init__(self, name: str = "legal_client", port: int = 8002, seed: str = "legal_client_seed"):
        """Initialize client agent"""
        
        self.agent = Agent(
            name=name,
            port=port,
            seed=seed,
            endpoint=[f"http://localhost:{port}/submit"],
        )
        
        fund_agent_if_low(self.agent.wallet.address())
        
        self.received_results = {}
        self._register_handlers()
        
        logger.info(f"Legal Compliance Client initialized: {self.agent.address}")
    
    def _register_handlers(self):
        """Register message handlers for client"""
        
        @self.agent.on_message(model=LegalComplianceResult)
        async def handle_compliance_result(ctx: Context, sender: str, msg: LegalComplianceResult):
            """Handle compliance analysis results"""
            
            ctx.logger.info(f"📋 Received compliance result for request {msg.request_id}")
            ctx.logger.info(f"Success: {msg.success}")
            ctx.logger.info(f"Overall risk: {msg.overall_risk_level}")
            ctx.logger.info(f"Legal status: {msg.legal_status}")
            
            # Store result
            self.received_results[msg.request_id] = msg
            
            # Print key findings
            if msg.key_findings:
                ctx.logger.info("Key findings:")
                for finding in msg.key_findings:
                    ctx.logger.info(f"  • {finding}")
            
            if msg.critical_recommendations:
                ctx.logger.info("Critical recommendations:")
                for rec in msg.critical_recommendations:
                    ctx.logger.info(f"  • {rec}")
        
        @self.agent.on_message(model=ComplianceStatusUpdate)
        async def handle_status_update(ctx: Context, sender: str, msg: ComplianceStatusUpdate):
            """Handle status updates"""
            
            ctx.logger.info(f"📊 Status update for {msg.request_id}: {msg.status} ({msg.progress_percentage}%)")
            ctx.logger.info(f"Current step: {msg.current_step}")
    
    async def request_compliance_analysis(self, compliance_agent_address: str, 
                                        dataset_name: str, dataset_data: Dict, 
                                        analysis_type: str = "full") -> str:
        """Request compliance analysis from legal agent"""
        
        request_id = f"req_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        request = LegalComplianceRequest(
            request_id=request_id,
            dataset_name=dataset_name,
            dataset_data=dataset_data,
            analysis_type=analysis_type,
            include_ner=True,
            requester_address=self.agent.address
        )
        
        # Send request
        ctx = Context(self.agent.address, logger)
        await ctx.send(compliance_agent_address, request)
        
        logger.info(f"Sent compliance request {request_id} for dataset '{dataset_name}'")
        return request_id
    
    def run(self):
        """Run the client agent"""
        self.agent.run()

# Bureau for running multiple agents
def create_legal_compliance_bureau():
    """Create a bureau with legal compliance agent and client"""
    
    bureau = Bureau()
    
    # Add legal compliance agent
    legal_agent = LegalComplianceAgent()
    bureau.add(legal_agent.agent)
    
    # Add client agent for testing
    client_agent = LegalComplianceClient()
    bureau.add(client_agent.agent)
    
    return bureau, legal_agent, client_agent

if __name__ == "__main__":
    # Create and run the legal compliance bureau
    bureau, legal_agent, client_agent = create_legal_compliance_bureau()
    
    logger.info("🚀 Starting Legal Compliance Bureau...")
    logger.info(f"Legal Agent: {legal_agent.agent.address}")
    logger.info(f"Client Agent: {client_agent.agent.address}")
    
    bureau.run()