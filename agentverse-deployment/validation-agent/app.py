#!/usr/bin/env python3
"""
Dataset Validation Agent - Agentverse Deployment
ETH Delhi 2025 - Fetch.ai uAgents Integration
"""

from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
import logging
import json
import uuid
from datetime import datetime

# Import our comprehensive tool registry
from tools import tool_registry

# Enhanced Message Models following uAgents patterns
class DatasetAnalysisRequest(Model):
    """Comprehensive dataset analysis request"""
    request_id: str
    dataset_path: str
    dataset_type: Optional[str] = None  # Auto-detect if not provided
    analysis_depth: str = "complete"  # "basic", "standard", "complete"
    custom_parameters: Optional[Dict[str, Any]] = {}
    requester_id: Optional[str] = None
    timestamp: str = datetime.now().isoformat()

class DatasetAnalysisResult(Model):
    """Complete dataset analysis result with raw tool outputs"""
    success: bool
    request_id: str
    timestamp: str
    
    # Basic dataset info
    dataset_info: Dict[str, Any]
    
    # Raw tool outputs (no score calculations)
    raw_tool_outputs: Dict[str, Any]  # Contains all individual tool results as-is
    
    # High-level analysis results
    persona_tags: List[str]
    primary_persona: str
    
    # Summary from agent (no combined scores)
    executive_summary: str
    
    # Actionable insights
    recommendations: List[str]
    next_steps: List[str]
    
    # Error handling
    errors: List[str] = []
    warnings: List[str] = []

class AgentStatusRequest(Model):
    """Request for agent status and capabilities"""
    requester_id: str

class AgentStatusResponse(Model):
    """Agent status and capabilities response"""
    agent_name: str
    agent_address: str
    status: str
    available_tools: Dict[str, str]
    analysis_modes: List[str]
    uptime: str
    processed_requests: int

# Create the agent with mailbox enabled for Agentverse
agent = Agent(
    name="eth_delhi_dataset_validator",
    seed="eth_delhi_2025_dataset_validation_agent_unique_seed",
    mailbox=True,  # Enable mailbox for Agentverse deployment
)

# Agent state
processed_requests = 0
start_time = datetime.now()

# Fund agent for testnet operations
fund_agent_if_low(agent.wallet.address())

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dataset_validator")

@agent.on_event("startup")
async def startup_handler(ctx: Context):
    ctx.logger.info("🚀 Enhanced Dataset Validation Agent started on Agentverse!")
    ctx.logger.info(f"Agent name: {agent.name}")
    ctx.logger.info(f"Agent address: {agent.address}")

@agent.on_message(model=DatasetAnalysisRequest)
async def handle_analysis_request(ctx: Context, sender: str, msg: DatasetAnalysisRequest):
    """Handle dataset analysis requests"""
    global processed_requests
    
    ctx.logger.info(f"📥 Received analysis request from {sender}")
    ctx.logger.info(f"Dataset: {msg.dataset_path}")
    
    try:
        # Perform complete analysis
        result = await perform_complete_analysis(msg, ctx)
        
        # Send result back
        await ctx.send(sender, result)
        
        processed_requests += 1
        ctx.logger.info(f"✅ Analysis completed for request {msg.request_id}")
        
    except Exception as e:
        ctx.logger.error(f"❌ Analysis failed: {e}")
        error_result = DatasetAnalysisResult(
            success=False,
            request_id=msg.request_id,
            timestamp=datetime.now().isoformat(),
            dataset_info={"error": str(e)},
            raw_tool_outputs={"error": str(e)},
            persona_tags=[],
            primary_persona="unknown",
            executive_summary=f"Analysis failed: {str(e)}",
            recommendations=[],
            next_steps=[],
            errors=[str(e)]
        )
        await ctx.send(sender, error_result)

@agent.on_message(model=AgentStatusRequest)
async def handle_status_request(ctx: Context, sender: str, msg: AgentStatusRequest):
    """Handle agent status requests"""
    global processed_requests, start_time
    
    uptime = str(datetime.now() - start_time)
    
    # Get available tools
    available_tools = {}
    try:
        all_tools = tool_registry.list_tools()
        available_tools = {name: desc[:100] for name, desc in all_tools.items()}  # Truncate descriptions
    except:
        available_tools = {"error": "Could not load tools"}
    
    status_response = AgentStatusResponse(
        agent_name=agent.name,
        agent_address=agent.address,
        status="active",
        available_tools=available_tools,
        analysis_modes=["basic", "standard", "complete"],
        uptime=uptime,
        processed_requests=processed_requests
    )
    
    await ctx.send(sender, status_response)

async def perform_complete_analysis(request: DatasetAnalysisRequest, ctx: Context) -> DatasetAnalysisResult:
    """Perform complete dataset analysis using all available tools"""
    
    try:
        # Step 1: Load dataset
        ctx.logger.info("📊 Step 1: Loading dataset...")
        load_result = await tool_registry.execute_tool(
            "data_loader",
            file_path=request.dataset_path,
            format_type=request.dataset_type
        )
        
        if not load_result["success"]:
            raise Exception(f"Failed to load dataset: {load_result.get('error', 'Unknown error')}")
        
        df = load_result["data"]
        dataset_info = load_result["metadata"]
        ctx.logger.info(f"✅ Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")
        
        # Step 2: Run foundational analysis tools
        ctx.logger.info("🔍 Step 2: Running foundational analysis...")
        analysis_results = await run_foundational_analysis(df, ctx)
        
        # Check for critical failures
        failed_tools = [name for name, result in analysis_results.items() if not result.get("success", False)]
        if len(failed_tools) > len(analysis_results) // 2:
            raise Exception(f"Too many tools failed: {failed_tools}")
        
        # Step 3: Extract scores from foundational tools
        ctx.logger.info("📊 Step 3: Extracting scores...")
        integrity_scores = extract_integrity_scores(analysis_results)
        statistical_scores = extract_statistical_scores(analysis_results)
        ml_usability_scores = extract_ml_scores(analysis_results)
        
        # Step 4: Run high-level analysis
        ctx.logger.info("🎯 Step 4: Running high-level analysis...")
        
        # Persona tagging
        persona_result = await tool_registry.execute_tool("dataset_persona_tagger", analysis_results=analysis_results)
        persona_tags = persona_result.get("persona_tags", []) if persona_result["success"] else []
        primary_persona = persona_result.get("primary_persona", "#Unknown") if persona_result["success"] else "#Unknown"
        
        # Contextual scoring
        scoring_result = await tool_registry.execute_tool("contextual_scoring_engine", analysis_results=analysis_results, persona_tags=persona_tags)
        contextual_scores = scoring_result.get("contextual_scores", {}) if scoring_result["success"] else {}
        
        # Final synthesis
        synthesis_result = await tool_registry.execute_tool("utility_score_synthesizer", analysis_results=analysis_results, persona_tags=persona_tags, contextual_scores=contextual_scores)
        
        if not synthesis_result["success"]:
            raise Exception("Synthesis failed")
        
        ctx.logger.info("✅ Step 4: High-level analysis completed")
        
        # Step 5: Compile comprehensive result with raw tool outputs
        raw_tool_outputs = {
            "integrity_tools": integrity_scores,
            "statistical_tools": statistical_scores, 
            "ml_tools": ml_usability_scores,
            "contextual_tools": contextual_scores,
            "synthesis_result": synthesis_result,
            "analysis_results": analysis_results
        }
        
        result = DatasetAnalysisResult(
            success=True,
            request_id=request.request_id or request.requester_id,
            timestamp=datetime.now().isoformat(),
            dataset_info=dataset_info,
            raw_tool_outputs=raw_tool_outputs,
            persona_tags=persona_tags,
            primary_persona=primary_persona,
            executive_summary=synthesis_result["executive_summary"],
            recommendations=synthesis_result["recommendations"],
            next_steps=synthesis_result["next_steps"]
        )
        
        # Collect any warnings from tools
        warnings = []
        for tool_result in analysis_results.values():
            if tool_result.get("warnings"):
                warnings.extend(tool_result["warnings"])
        result.warnings = warnings
        
        return result
        
    except Exception as e:
        ctx.logger.error(f"Analysis pipeline error: {e}")
        return create_error_result(request, [str(e)], "Pipeline execution failed")

async def run_foundational_analysis(df: pd.DataFrame, ctx: Context) -> Dict[str, Any]:
    """Run optimized foundational analysis tools"""
    analysis_results = {}
    
    # Core analysis tools (always run these)
    core_tools = [
        ("missing_value_analyzer", {"data": df}),
        ("duplicate_record_detector", {"data": df}),
        ("data_type_consistency_checker", {"data": df}),
    ]
    
    # Smart selection based on dataset characteristics
    dataset_size = df.shape[0]
    num_features = df.shape[1]
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    categorical_cols = df.select_dtypes(include=['object']).columns
    
    # Conditional tools based on dataset characteristics
    if len(numeric_cols) > 0:
        core_tools.append(("outlier_detection_engine", {"data": df}))
    
    if len(numeric_cols) >= 2:
        core_tools.append(("feature_correlation_mapper", {"data": df}))
    
    # Execute tools
    for tool_name, params in core_tools:
        try:
            ctx.logger.info(f"🔧 Running {tool_name}...")
            result = await tool_registry.execute_tool(tool_name, **params)
            analysis_results[f"{tool_name}_analysis"] = result
            if result["success"]:
                ctx.logger.info(f"✅ {tool_name} completed")
            else:
                ctx.logger.warning(f"⚠️ {tool_name} failed: {result.get('error', 'Unknown error')}")
        except Exception as e:
            ctx.logger.error(f"❌ {tool_name} crashed: {e}")
            analysis_results[f"{tool_name}_analysis"] = {"success": False, "error": str(e)}
    
    return analysis_results

def extract_integrity_scores(analysis_results: Dict) -> Dict[str, float]:
    """Extract integrity-related scores"""
    scores = {}
    
    if "missing_value_analyzer_analysis" in analysis_results:
        result = analysis_results["missing_value_analyzer_analysis"]
        if result["success"]:
            scores["missing_value_score"] = result.get("completeness_score", 0.0)
    
    if "duplicate_record_detector_analysis" in analysis_results:
        result = analysis_results["duplicate_record_detector_analysis"]
        if result["success"]:
            scores["duplicate_score"] = result.get("uniqueness_score", 0.0)
    
    if "data_type_consistency_checker_analysis" in analysis_results:
        result = analysis_results["data_type_consistency_checker_analysis"]
        if result["success"]:
            scores["consistency_score"] = result.get("consistency_score", 0.0)
    
    return scores

def extract_statistical_scores(analysis_results: Dict) -> Dict[str, float]:
    """Extract statistical analysis scores"""
    scores = {}
    
    if "outlier_detection_engine_analysis" in analysis_results:
        result = analysis_results["outlier_detection_engine_analysis"]
        if result["success"]:
            scores["outlier_score"] = result.get("outlier_score", 0.0)
    
    if "feature_correlation_mapper_analysis" in analysis_results:
        result = analysis_results["feature_correlation_mapper_analysis"]
        if result["success"]:
            scores["correlation_score"] = result.get("correlation_score", 0.0)
    
    return scores

def extract_ml_scores(analysis_results: Dict) -> Dict[str, float]:
    """Extract ML usability scores"""
    scores = {}
    
    if "baseline_model_performance_analysis" in analysis_results:
        result = analysis_results["baseline_model_performance_analysis"]
        if result["success"]:
            scores["ml_performance_score"] = result.get("baseline_score", 0.0)
    
    if "feature_importance_analyzer_analysis" in analysis_results:
        result = analysis_results["feature_importance_analyzer_analysis"]
        if result["success"]:
            scores["feature_importance_score"] = result.get("importance_score", 0.0)
    
    return scores

def create_error_result(request: DatasetAnalysisRequest, errors: List[str], summary: str) -> DatasetAnalysisResult:
    """Create an error result"""
    return DatasetAnalysisResult(
        success=False,
        request_id=request.request_id or request.requester_id,
        timestamp=datetime.now().isoformat(),
        dataset_info={},
        raw_tool_outputs={"error": {"summary": summary, "errors": errors}},
        persona_tags=[],
        primary_persona="#Unknown",
        executive_summary=summary,
        recommendations=[],
        next_steps=[],
        errors=errors
    )

if __name__ == "__main__":
    logger.info("🚀 Starting Dataset Validation Agent for Agentverse...")
    logger.info(f"Agent address: {agent.address}")
    agent.run()