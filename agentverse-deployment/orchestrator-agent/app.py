#!/usr/bin/env python3
"""
Orchestrator Agent - Agentverse Deployment
ETH Delhi 2025 - Coordinates validation and legal compliance agents
"""

from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low
from typing import Dict, List, Any, Optional
import pandas as pd
import logging
from datetime import datetime

# Message Models
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

# Create the agent with mailbox enabled for Agentverse
agent = Agent(
    name="eth_delhi_orchestrator",
    seed="eth_delhi_2025_orchestrator_agent_unique_seed", 
    mailbox=True,  # Enable mailbox for Agentverse deployment
)

# Agent state
active_requests: Dict[str, Dict] = {}
completed_results: Dict[str, ComprehensiveValidationResult] = {}
start_time = datetime.now()

# Fund agent for testnet operations
fund_agent_if_low(agent.wallet.address())

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("orchestrator")

@agent.on_event("startup")
async def startup_handler(ctx: Context):
    ctx.logger.info("🚀 Orchestrator Agent started on Agentverse!")
    ctx.logger.info(f"Orchestrator address: {agent.address}")
    ctx.logger.info("Ready to coordinate comprehensive dataset validation!")

@agent.on_message(model=ComprehensiveValidationRequest)
async def handle_comprehensive_request(ctx: Context, sender: str, msg: ComprehensiveValidationRequest):
    """Handle comprehensive validation requests"""
    ctx.logger.info(f"📥 Received comprehensive validation request: {msg.request_id}")
    
    # Initialize request tracking
    active_requests[msg.request_id] = {
        "request": msg,
        "sender": sender,
        "start_time": datetime.now(),
        "validation_status": "pending",
        "legal_status": "pending",
        "validation_result": None,
        "legal_result": None
    }
    
    try:
        # Start comprehensive validation
        await start_comprehensive_validation(ctx, msg)
        
    except Exception as e:
        ctx.logger.error(f"❌ Failed to start validation: {e}")
        await send_error_result(ctx, sender, msg.request_id, f"Validation startup failed: {str(e)}")

@agent.on_message(model=ValidationStatusRequest)
async def handle_status_request(ctx: Context, sender: str, msg: ValidationStatusRequest):
    """Handle validation status requests"""
    if msg.request_id in active_requests:
        request_data = active_requests[msg.request_id]
        
        progress = {
            "validation": request_data["validation_status"],
            "legal": request_data["legal_status"]
        }
        
        status_response = ValidationStatusResponse(
            request_id=msg.request_id,
            status="processing" if "pending" in progress.values() or "running" in progress.values() else "completed",
            progress=progress,
            message=f"Validation: {progress['validation']}, Legal: {progress['legal']}"
        )
        
        await ctx.send(sender, status_response)
    else:
        # Check completed results
        if msg.request_id in completed_results:
            status_response = ValidationStatusResponse(
                request_id=msg.request_id,
                status="completed",
                progress={"validation": "completed", "legal": "completed"},
                message="Analysis completed successfully"
            )
        else:
            status_response = ValidationStatusResponse(
                request_id=msg.request_id,
                status="not_found",
                progress={},
                message="Request ID not found"
            )
        
        await ctx.send(sender, status_response)

async def start_comprehensive_validation(ctx: Context, request: ComprehensiveValidationRequest):
    """Start the comprehensive validation process"""
    ctx.logger.info(f"🔄 Starting comprehensive validation for: {request.dataset_name}")
    
    # For Agentverse deployment, we'll run a simplified validation
    # In a full deployment, this would coordinate with other agents
    
    try:
        # Prepare dataset
        dataset = await prepare_dataset(request)
        if dataset is None:
            raise Exception("Could not prepare dataset")
        
        # Run validation analysis
        active_requests[request.request_id]["validation_status"] = "running"
        validation_result = await run_validation_analysis(ctx, request, dataset)
        active_requests[request.request_id]["validation_result"] = validation_result
        active_requests[request.request_id]["validation_status"] = "completed" if validation_result["success"] else "failed"
        
        # Run legal analysis if requested
        legal_result = None
        if request.include_legal_analysis:
            active_requests[request.request_id]["legal_status"] = "running"
            legal_result = await run_legal_analysis(ctx, request, dataset)
            active_requests[request.request_id]["legal_result"] = legal_result
            active_requests[request.request_id]["legal_status"] = "completed" if legal_result["success"] else "failed"
        else:
            active_requests[request.request_id]["legal_status"] = "skipped"
        
        # Combine and send results
        await check_and_combine_results(ctx, request.request_id)
        
    except Exception as e:
        ctx.logger.error(f"❌ Validation process failed: {e}")
        await send_error_result(ctx, active_requests[request.request_id]["sender"], request.request_id, str(e))

async def prepare_dataset(request: ComprehensiveValidationRequest) -> Optional[pd.DataFrame]:
    """Prepare dataset for analysis"""
    
    if request.dataset_data:
        try:
            return pd.DataFrame(request.dataset_data)
        except Exception as e:
            logger.error(f"Could not convert dataset_data to DataFrame: {e}")
            return None
    
    elif request.dataset_path:
        try:
            if request.dataset_path.endswith('.csv'):
                return pd.read_csv(request.dataset_path)
            elif request.dataset_path.endswith('.json'):
                return pd.read_json(request.dataset_path)
            elif request.dataset_path.endswith('.xlsx'):
                return pd.read_excel(request.dataset_path)
            else:
                return pd.read_csv(request.dataset_path)  # Try CSV as fallback
        except Exception as e:
            logger.error(f"Could not load dataset from {request.dataset_path}: {e}")
            return None
    else:
        # Create sample data for demo
        logger.info("No dataset provided, creating sample data for demo")
        return pd.DataFrame({
            'id': range(1, 101),
            'value': [i * 2 + (i % 7) for i in range(100)],
            'category': [f'cat_{i%5}' for i in range(100)],
            'flag': [i % 2 == 0 for i in range(100)]
        })

async def run_validation_analysis(ctx: Context, request: ComprehensiveValidationRequest, dataset: pd.DataFrame) -> Dict[str, Any]:
    """Run simplified validation analysis"""
    try:
        ctx.logger.info("🔍 Running validation analysis...")
        
        # Basic dataset statistics
        dataset_info = {
            "name": request.dataset_name,
            "shape": dataset.shape,
            "columns": list(dataset.columns),
            "dtypes": {col: str(dtype) for col, dtype in dataset.dtypes.items()},
            "missing_values": dataset.isnull().sum().to_dict(),
            "duplicates": int(dataset.duplicated().sum())
        }
        
        # Basic validation scores
        completeness_score = (1 - dataset.isnull().sum().sum() / (dataset.shape[0] * dataset.shape[1])) * 100
        uniqueness_score = (1 - dataset.duplicated().sum() / len(dataset)) * 100
        
        validation_tools = {
            "dataset_info": dataset_info,
            "quality_scores": {
                "completeness_score": completeness_score,
                "uniqueness_score": uniqueness_score,
                "overall_quality": (completeness_score + uniqueness_score) / 2
            },
            "analysis_summary": f"Dataset has {dataset.shape[0]} rows and {dataset.shape[1]} columns with {completeness_score:.1f}% completeness"
        }
        
        return {
            "success": True,
            "dataset_info": dataset_info,
            "raw_tool_outputs": validation_tools,
            "summary": f"Validation completed with {completeness_score:.1f}% data quality score"
        }
        
    except Exception as e:
        ctx.logger.error(f"❌ Validation analysis failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "dataset_info": {"error": str(e)},
            "raw_tool_outputs": {"error": str(e)},
            "summary": f"Validation failed: {str(e)}"
        }

async def run_legal_analysis(ctx: Context, request: ComprehensiveValidationRequest, dataset: pd.DataFrame) -> Dict[str, Any]:
    """Run simplified legal analysis"""
    try:
        ctx.logger.info("⚖️ Running legal compliance analysis...")
        
        # Basic PII detection
        pii_indicators = 0
        pii_columns = []
        
        for col in dataset.columns:
            col_lower = col.lower()
            if any(pii_term in col_lower for pii_term in ['email', 'phone', 'name', 'address', 'ssn', 'id']):
                pii_indicators += 1
                pii_columns.append(col)
        
        # Calculate risk score
        pii_risk_score = min(100, (pii_indicators / len(dataset.columns)) * 100) if len(dataset.columns) > 0 else 0
        
        if pii_risk_score >= 50:
            risk_level = "High"
        elif pii_risk_score >= 25:
            risk_level = "Medium"
        else:
            risk_level = "Low"
        
        legal_tools = {
            "pii_analysis": {
                "pii_risk_score": pii_risk_score,
                "risk_level": risk_level,
                "pii_columns": pii_columns,
                "columns_analyzed": len(dataset.columns)
            },
            "compliance_summary": {
                "overall_risk": risk_level,
                "requires_action": pii_risk_score >= 25,
                "recommendations": [
                    "Review data usage policies" if pii_risk_score >= 25 else "No immediate action required",
                    "Consider data anonymization" if len(pii_columns) > 0 else "PII risk appears minimal"
                ]
            }
        }
        
        return {
            "success": True,
            "raw_tool_outputs": legal_tools,
            "risk_level": risk_level,
            "requires_action": pii_risk_score >= 25,
            "summary": f"Legal analysis completed - {risk_level} risk level detected"
        }
        
    except Exception as e:
        ctx.logger.error(f"❌ Legal analysis failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "raw_tool_outputs": {"error": str(e)},
            "risk_level": "Unknown",
            "requires_action": True,
            "summary": f"Legal analysis failed: {str(e)}"
        }

async def check_and_combine_results(ctx: Context, request_id: str):
    """Check if both analyses are complete and combine results"""
    if request_id not in active_requests:
        return
    
    request_data = active_requests[request_id]
    validation_done = request_data["validation_status"] in ["completed", "failed"]
    legal_done = request_data["legal_status"] in ["completed", "failed", "skipped"]
    
    if validation_done and legal_done:
        ctx.logger.info(f"🔄 Combining results for: {request_id}")
        
        try:
            combined_result = await combine_validation_results(request_data)
            completed_results[request_id] = combined_result
            
            # Send result to requester
            await ctx.send(request_data["sender"], combined_result)
            
            # Clean up active request
            del active_requests[request_id]
            
            ctx.logger.info(f"✅ Combined results sent for: {request_id}")
            
        except Exception as e:
            ctx.logger.error(f"❌ Failed to combine results for {request_id}: {e}")
            await send_error_result(ctx, request_data["sender"], request_id, f"Failed to combine results: {str(e)}")

async def combine_validation_results(request_data: Dict) -> ComprehensiveValidationResult:
    """Combine validation and legal compliance results - pass through raw results without score calculations"""
    validation_result = request_data["validation_result"]
    legal_result = request_data["legal_result"]
    original_request = request_data["request"]
    processing_time = (datetime.now() - request_data["start_time"]).total_seconds()
    
    # Extract raw tool outputs (no score calculations)
    validation_tool_results = None
    if validation_result and validation_result.get("success"):
        validation_tool_results = validation_result.get("raw_tool_outputs")
    
    legal_tool_results = None
    if legal_result and legal_result.get("success"):
        legal_tool_results = legal_result.get("raw_tool_outputs")
    
    return ComprehensiveValidationResult(
        request_id=original_request.request_id,
        success=True,
        timestamp=datetime.now().isoformat(),
        processing_time_seconds=round(processing_time, 2),
        dataset_name=original_request.dataset_name,
        dataset_info=validation_result.get("dataset_info", {"name": original_request.dataset_name}) if validation_result else {"name": original_request.dataset_name},
        validation_tool_results=validation_tool_results,
        legal_tool_results=legal_tool_results,
        validation_status=request_data["validation_status"],
        legal_status=request_data["legal_status"]
    )

async def send_error_result(ctx: Context, requester: str, request_id: str, error_message: str):
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
    if request_id in active_requests:
        del active_requests[request_id]

if __name__ == "__main__":
    logger.info("🚀 Starting Orchestrator Agent for Agentverse...")
    logger.info(f"Agent address: {agent.address}")
    agent.run()