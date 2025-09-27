#!/usr/bin/env python3
"""
Enhanced Dataset Validation Agent with Complete Analysis Pipeline
ETH Delhi 2025 - Fetch.ai uAgents Integration
"""

from uagents import Agent, Context, Model, Bureau
from uagents.setup import fund_agent_if_low
from typing import Dict, List, Any, Optional
import json
import pandas as pd
import numpy as np
from pathlib import Path
import asyncio
import logging
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

class DatasetValidationAgent:
    """Enhanced Dataset Validation Agent with complete analysis pipeline"""
    
    def __init__(self, name: str = "dataset_validator", port: int = 8000, mailbox: bool = False):
        # Agent configuration with optional mailbox support
        agent_config = {
            "name": name,
            "port": port,
            "seed": "eth_delhi_2025_dataset_validation_agent",
            "endpoint": [f"http://localhost:{port}/submit"],
        }
        
        # Add mailbox configuration if requested
        if mailbox:
            agent_config["mailbox"] = True
            
        self.agent = Agent(**agent_config)
        
        # Agent state
        self.processed_requests = 0
        self.start_time = datetime.now()
        
        # Fund agent for testnet operations (following uAgents guidelines)
        fund_agent_if_low(self.agent.wallet.address())
        
        self._setup_handlers()
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(f"agent.{name}")
    
    def _setup_handlers(self):
        """Setup all agent event handlers following uAgents patterns"""
        
        @self.agent.on_event("startup")
        async def startup_handler(ctx: Context):
            ctx.logger.info("🚀 Enhanced Dataset Validation Agent started!")
            ctx.logger.info(f"Agent name: {self.agent.name}")
            ctx.logger.info(f"Agent address: {self.agent.address}")
            ctx.logger.info(f"Wallet address: {self.agent.wallet.address()}")
            ctx.logger.info(f"Total analysis tools available: {len(tool_registry.tools)}")
            
            # Log available tool categories
            tools_by_category = self._categorize_tools()
            for category, tools in tools_by_category.items():
                ctx.logger.info(f"  {category}: {len(tools)} tools")
            
            ctx.logger.info("✅ Ready for dataset analysis requests!")
        
        @self.agent.on_message(model=DatasetAnalysisRequest)
        async def handle_analysis_request(ctx: Context, sender: str, msg: DatasetAnalysisRequest):
            """Handle comprehensive dataset analysis requests"""
            ctx.logger.info(f"📥 Received analysis request from {sender}")
            ctx.logger.info(f"Dataset: {msg.dataset_path}")
            ctx.logger.info(f"Analysis depth: {msg.analysis_depth}")
            
            try:
                # Perform complete analysis pipeline
                result = await self._perform_complete_analysis(msg, ctx)
                
                # Update processed requests counter
                self.processed_requests += 1
                
                # Log summary
                if result.success:
                    ctx.logger.info(f"✅ Analysis completed successfully")
                    ctx.logger.info(f"Overall Utility Score: {result.overall_utility_score:.1f}/100")
                    ctx.logger.info(f"Primary Persona: {result.primary_persona}")
                    ctx.logger.info(f"Utility Grade: {result.utility_grade['grade']}")
                else:
                    ctx.logger.error(f"❌ Analysis failed: {len(result.errors)} errors")
                
                # Send result back to requester
                await ctx.send(sender, result)
                
            except Exception as e:
                ctx.logger.error(f"❌ Analysis pipeline failed: {e}")
                
                # Send error result
                error_result = DatasetAnalysisResult(
                    success=False,
                    request_id=msg.requester_id,
                    timestamp=datetime.now().isoformat(),
                    dataset_info={},
                    integrity_scores={},
                    statistical_scores={},
                    ml_usability_scores={},
                    persona_tags=[],
                    primary_persona="#Unknown",
                    contextual_scores={},
                    overall_utility_score=0.0,
                    utility_grade={"grade": "F", "description": "Failed"},
                    data_integrity_score=0.0,
                    executive_summary=f"Analysis failed: {str(e)}",
                    recommendations=[],
                    publication_readiness={"status": "failed"},
                    next_steps=[],
                    errors=[str(e)]
                )
                
                await ctx.send(sender, error_result)
        
        @self.agent.on_message(model=AgentStatusRequest)
        async def handle_status_request(ctx: Context, sender: str, msg: AgentStatusRequest):
            """Handle agent status requests"""
            ctx.logger.info(f"📊 Status request from {sender}")
            
            uptime = datetime.now() - self.start_time
            
            response = AgentStatusResponse(
                agent_name=ctx.name,
                agent_address=ctx.address,
                status="active",
                available_tools=tool_registry.list_tools(),
                analysis_modes=["basic", "standard", "complete"],
                uptime=str(uptime),
                processed_requests=self.processed_requests
            )
            
            await ctx.send(sender, response)
            ctx.logger.info(f"📤 Status sent to {sender}")
    
    async def _perform_complete_analysis(self, request: DatasetAnalysisRequest, ctx: Context) -> DatasetAnalysisResult:
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
                return self._create_error_result(request, [load_result["error"]], "Dataset loading failed")
            
            df = load_result["data"]
            dataset_info = load_result["metadata"]
            ctx.logger.info(f"✅ Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")
            
            # Step 2: Run foundational analysis tools
            ctx.logger.info("🔍 Step 2: Running foundational analysis...")
            analysis_results = await self._run_foundational_analysis(df, ctx)
            
            # Check for critical failures
            failed_tools = [name for name, result in analysis_results.items() if not result.get("success", False)]
            if len(failed_tools) > len(analysis_results) // 2:
                return self._create_error_result(
                    request, 
                    [f"Too many analysis tools failed: {failed_tools}"],
                    "Critical analysis failure"
                )
            
            # Step 3: Extract scores from foundational tools
            ctx.logger.info("📊 Step 3: Extracting scores...")
            integrity_scores = self._extract_integrity_scores(analysis_results)
            statistical_scores = self._extract_statistical_scores(analysis_results)
            ml_usability_scores = self._extract_ml_scores(analysis_results)
            
            # Step 4: Run high-level analysis
            ctx.logger.info("🎯 Step 4: Running high-level analysis...")
            
            # Persona tagging
            persona_result = await tool_registry.execute_tool("dataset_persona_tagger", analysis_results=analysis_results)
            persona_tags = persona_result.get("persona_tags", []) if persona_result["success"] else []
            primary_persona = persona_result.get("primary_persona", "#Unknown") if persona_result["success"] else "#Unknown"
            
            # Contextual scoring
            scoring_result = await tool_registry.execute_tool("contextual_scoring_engine", analysis_results=analysis_results, persona_tags=persona_tags)
            contextual_scores = scoring_result.get("contextual_scores", {}) if scoring_result["success"] else {}
            
            # DEBUG: Log contextual scoring results
            print("\n=== CONTEXTUAL SCORING RESULTS ===")
            print(f"Scoring result success: {scoring_result['success']}")
            print(f"Full scoring result: {scoring_result}")
            print(f"Extracted contextual scores: {contextual_scores}")
            print("=================================\n")
            
            # Final synthesis
            synthesis_result = await tool_registry.execute_tool("utility_score_synthesizer", analysis_results=analysis_results, persona_tags=persona_tags, contextual_scores=contextual_scores)
            
            # DEBUG: Log synthesis results
            print("\n=== SYNTHESIS RESULTS ===")
            print(f"Synthesis result success: {synthesis_result['success']}")
            print(f"Full synthesis result: {synthesis_result}")
            print("========================\n")
            
            if not synthesis_result["success"]:
                return self._create_error_result(request, [synthesis_result["error"]], "Final synthesis failed")
            
            ctx.logger.info("✅ Step 4: High-level analysis completed")
            
            # Step 5: Compile comprehensive result with raw tool outputs
            raw_tool_outputs = {
                "integrity_tools": integrity_scores,
                "statistical_tools": statistical_scores, 
                "ml_tools": ml_usability_scores,
                "contextual_tools": contextual_scores,
                "synthesis_result": synthesis_result,
                "analysis_results": analysis_results  # All raw tool results
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
                if "warnings" in tool_result:
                    warnings.extend(tool_result["warnings"])
            result.warnings = warnings
            
            return result
            
        except Exception as e:
            ctx.logger.error(f"Analysis pipeline error: {e}")
            return self._create_error_result(request, [str(e)], "Pipeline execution failed")
    
    async def _run_foundational_analysis(self, df: pd.DataFrame, ctx: Context) -> Dict[str, Any]:
        """Run optimized foundational analysis tools based on dataset characteristics"""
        analysis_results = {}
        
        # First, run data profiler to understand dataset characteristics
        ctx.logger.info("🔍 Running data profiler for smart tool selection...")
        profile_result = await tool_registry.execute_tool("data_profiler", data=df)
        analysis_results["data_profiler"] = profile_result
        
        if not profile_result.get("success", False):
            ctx.logger.error("❌ Data profiler failed - using default tool set")
            
        # Extract dataset characteristics for smart tool selection
        dataset_size = df.shape[0]
        num_features = df.shape[1]
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        categorical_cols = df.select_dtypes(include=['object']).columns
        
        ctx.logger.info(f"📊 Dataset characteristics: {dataset_size} rows, {num_features} features")
        ctx.logger.info(f"   📈 Numeric columns: {len(numeric_cols)}")
        ctx.logger.info(f"   📝 Categorical columns: {len(categorical_cols)}")
        
        # Smart tool selection based on dataset characteristics
        tools_to_run = self._select_optimal_tools(df, dataset_size, num_features, len(numeric_cols), len(categorical_cols))
        
        ctx.logger.info(f"🎯 Selected {len(tools_to_run)} optimal tools for analysis")
        
        # Execute tools
        for tool_name, params in tools_to_run:
            try:
                ctx.logger.info(f"  Running {tool_name}...")
                result = await tool_registry.execute_tool(tool_name, **params)
                analysis_results[f"{tool_name}_analysis"] = result
                
                if result["success"]:
                    ctx.logger.info(f"  ✅ {tool_name} completed")
                else:
                    ctx.logger.warning(f"  ⚠️ {tool_name} failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                ctx.logger.error(f"  ❌ {tool_name} error: {e}")
                analysis_results[f"{tool_name}_analysis"] = {"success": False, "error": str(e)}
        
        return analysis_results
    
    def _select_optimal_tools(self, df: pd.DataFrame, dataset_size: int, num_features: int, 
                            num_numeric: int, num_categorical: int) -> List[tuple]:
        """Select optimal analysis tools based on dataset characteristics"""
        tools_to_run = []
        
        # Core analysis tools (always run these - essential for any dataset)
        core_tools = [
            ("missing_value_analyzer", {"data": df}),
            ("duplicate_record_detector", {"data": df}),
            ("data_type_consistency_checker", {"data": df}),
        ]
        tools_to_run.extend(core_tools)
        
        # Conditional tools based on dataset characteristics
        
        # 1. Outlier detection - only if we have numeric columns
        if num_numeric > 0:
            tools_to_run.append(("outlier_detection_engine", {"data": df}))
        
        # 2. Correlation analysis - only if multiple numeric columns
        if num_numeric >= 2:
            tools_to_run.append(("feature_correlation_mapper", {"data": df}))
        
        # 3. ML analysis tools - run for datasets with sufficient complexity
        target_column = self._identify_target_column(df)
        
        # Run ML tools even without explicit target - they can provide general ML usability insights
        if dataset_size >= 20 and num_features >= 2:  # Very relaxed conditions
            
            # Always try feature importance (can work without explicit target)
            if num_features >= 2:
                tools_to_run.append(("feature_importance_analyzer", {"data": df, "target_column": target_column}))
            
            # Baseline model performance (can auto-detect target or use last column)
            if dataset_size >= 50:
                tools_to_run.append(("baseline_model_performance", {"data": df, "target_column": target_column}))
            
            # Data separability (can work with auto-detected or assumed target)
            if target_column or num_features >= 2:  # Either explicit target or try last column
                actual_target = target_column or df.columns[-1]  # Fallback to last column
                tools_to_run.append(("data_separability_scorer", {"data": df, "target_column": actual_target}))
                
                # Class balance if the target looks categorical
                if df[actual_target].nunique() <= min(50, len(df) // 5):  # More relaxed
                    tools_to_run.append(("class_balance_assessor", {"data": df, "target_column": actual_target}))
        
        # 4. Skip expensive tools for very large datasets
        if dataset_size > 10000:
            # Remove computationally expensive tools for large datasets
            expensive_tools = ["baseline_model_performance", "data_separability_scorer"]
            tools_to_run = [(name, params) for name, params in tools_to_run 
                          if name not in expensive_tools]
        
        return tools_to_run
    
    def _identify_target_column(self, df: pd.DataFrame) -> str:
        """Smart target column identification"""
        # Look for common target column names
        potential_targets = ['target', 'label', 'class', 'y', 'outcome', 'result', 
                           'prediction', 'response', 'dependent', 'output']
        
        for col in df.columns:
            if col.lower() in potential_targets:
                return col
        
        # If no obvious target, use heuristics
        if len(df.columns) > 1:
            # Check last column - often the target in ML datasets
            last_col = df.columns[-1]
            
            # For classification: low cardinality
            if df[last_col].nunique() <= min(20, len(df) // 10):
                return last_col
            
            # For regression: numeric with reasonable range
            if pd.api.types.is_numeric_dtype(df[last_col]):
                return last_col
        
        return None

    def _extract_integrity_scores(self, analysis_results: Dict) -> Dict[str, float]:
        """Extract integrity-related scores"""
        scores = {}
        
        print("\n=== INTEGRITY SCORES EXTRACTION ===")
        
        if "missing_value_analyzer_analysis" in analysis_results:
            result = analysis_results["missing_value_analyzer_analysis"]
            print(f"Missing Value Analyzer: success={result['success']}, full_result={result}")
            if result["success"]:
                # Try both top-level and nested approach
                integrity_score = result.get("integrity_score", 0)
                if integrity_score == 0 and "analysis" in result:
                    analysis_data = result.get("analysis", {})
                    integrity_score = analysis_data.get("integrity_score", 0)
                    print(f"  -> Found nested integrity_score: {integrity_score}")
                scores["completeness"] = integrity_score
                print(f"  -> Final completeness score: {integrity_score}")
                print(f"  -> Available keys: {list(result.keys())}")
        
        if "duplicate_record_detector_analysis" in analysis_results:
            result = analysis_results["duplicate_record_detector_analysis"]
            print(f"Duplicate Detector: success={result['success']}, full_result={result}")
            if result["success"]:
                # Try both top-level and nested approach
                integrity_score = result.get("integrity_score", 0)
                if integrity_score == 0 and "analysis" in result:
                    analysis_data = result.get("analysis", {})
                    integrity_score = analysis_data.get("integrity_score", 0)
                    print(f"  -> Found nested integrity_score: {integrity_score}")
                scores["duplicates"] = integrity_score
                print(f"  -> Final duplicates score: {integrity_score}")
                print(f"  -> Available keys: {list(result.keys())}")
        
        if "data_type_consistency_checker_analysis" in analysis_results:
            result = analysis_results["data_type_consistency_checker_analysis"]
            print(f"Data Type Checker: success={result['success']}, full_result={result}")
            if result["success"]:
                # Try both top-level and nested approach
                consistency_score = result.get("consistency_score", 0)
                if consistency_score == 0 and "analysis" in result:
                    analysis_data = result.get("analysis", {})
                    consistency_score = analysis_data.get("consistency_score", 0)
                    print(f"  -> Found nested consistency_score: {consistency_score}")
                scores["consistency"] = consistency_score
                print(f"  -> Final consistency score: {consistency_score}")
                print(f"  -> Available keys: {list(result.keys())}")
        
        print(f"Final integrity scores: {scores}")
        print("================================\n")
        
        return scores
    
    def _extract_statistical_scores(self, analysis_results: Dict) -> Dict[str, float]:
        """Extract statistical analysis scores"""
        scores = {}
        
        print("\n=== STATISTICAL SCORES EXTRACTION ===")
        
        if "outlier_detection_engine_analysis" in analysis_results:
            result = analysis_results["outlier_detection_engine_analysis"]
            print(f"Outlier Detection: success={result['success']}, full_result={result}")
            if result["success"]:
                # Try both top-level and nested approach
                outlier_score = result.get("outlier_score", 0)
                if outlier_score == 0 and "analysis" in result:
                    analysis_data = result.get("analysis", {})
                    outlier_score = analysis_data.get("outlier_score", 0)
                    print(f"  -> Found nested outlier_score: {outlier_score}")
                scores["outliers"] = outlier_score
                print(f"  -> Final outliers score: {outlier_score}")
                print(f"  -> Available keys: {list(result.keys())}")
        
        if "class_balance_assessor_analysis" in analysis_results:
            result = analysis_results["class_balance_assessor_analysis"]
            print(f"Class Balance: success={result['success']}, full_result={result}")
            if result["success"]:
                balance_score = result.get("balance_score", 0)
                scores["class_balance"] = balance_score
                print(f"  -> Class balance score: {balance_score}")
        
        if "feature_correlation_mapper_analysis" in analysis_results:
            result = analysis_results["feature_correlation_mapper_analysis"]
            print(f"Correlation Mapper: success={result['success']}, full_result={result}")
            if result["success"]:
                # The score is nested in the 'analysis' field
                analysis_data = result.get("analysis", {})
                correlation_score = analysis_data.get("multicollinearity_score", 0)
                scores["correlations"] = correlation_score
                print(f"  -> Correlations score: {correlation_score}")
                print(f"  -> Available keys in result: {list(result.keys())}")
                print(f"  -> Available keys in analysis: {list(analysis_data.keys()) if analysis_data else 'No analysis data'}")
        
        print(f"Final statistical scores: {scores}")
        print("==================================\n")
        
        return scores
    
    def _extract_ml_scores(self, analysis_results: Dict) -> Dict[str, float]:
        """Extract ML usability scores"""
        scores = {}
        
        print("\n=== ML USABILITY SCORES EXTRACTION ===")
        
        if "baseline_model_performance_analysis" in analysis_results:
            result = analysis_results["baseline_model_performance_analysis"]
            print(f"Baseline ML Performance: success={result['success']}, full_result={result}")
            if result["success"]:
                ml_score = result.get("ml_usability_score", 0)
                scores["ml_performance"] = ml_score
                print(f"  -> ML performance score: {ml_score}")
        
        if "feature_importance_analyzer_analysis" in analysis_results:
            result = analysis_results["feature_importance_analyzer_analysis"]
            print(f"Feature Importance: success={result['success']}, full_result={result}")
            if result["success"]:
                importance_score = result.get("information_score", 0)
                scores["feature_importance"] = importance_score
                print(f"  -> Feature importance score: {importance_score}")
        
        if "data_separability_scorer_analysis" in analysis_results:
            result = analysis_results["data_separability_scorer_analysis"]
            print(f"Data Separability: success={result['success']}, full_result={result}")
            if result["success"]:
                separability_score = result.get("separability_score", 0)
                scores["separability"] = separability_score
                print(f"  -> Separability score: {separability_score}")
        
        print(f"Final ML scores: {scores}")
        print("===================================\n")
        
        return scores
    
    def _create_error_result(self, request: DatasetAnalysisRequest, errors: List[str], summary: str) -> DatasetAnalysisResult:
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
    
    def _categorize_tools(self) -> Dict[str, List[str]]:
        """Categorize available tools for status reporting"""
        all_tools = tool_registry.list_tools()
        
        categories = {
            "Core Processing": [],
            "Data Integrity": [],
            "Statistical Analysis": [],
            "ML Usability": [],
            "High-Level Analysis": []
        }
        
        for tool_name in all_tools.keys():
            if tool_name in ["data_loader", "data_profiler", "validation_rules", "report_generator"]:
                categories["Core Processing"].append(tool_name)
            elif tool_name in ["missing_value_analyzer", "duplicate_record_detector", "data_type_consistency_checker"]:
                categories["Data Integrity"].append(tool_name)
            elif tool_name in ["outlier_detection_engine", "class_balance_assessor", "feature_correlation_mapper"]:
                categories["Statistical Analysis"].append(tool_name)
            elif tool_name in ["baseline_model_performance", "feature_importance_analyzer", "data_separability_scorer"]:
                categories["ML Usability"].append(tool_name)
            elif tool_name in ["dataset_persona_tagger", "contextual_scoring_engine", "utility_score_synthesizer"]:
                categories["High-Level Analysis"].append(tool_name)
        
        return categories

# Bureau setup for multi-agent coordination (following uAgents guidelines)
def create_validation_bureau():
    """Create a bureau with multiple validation agents for distributed processing"""
    bureau = Bureau()
    
    # Primary validation agent
    primary_agent = DatasetValidationAgent("primary_validator", 8000)
    bureau.add(primary_agent.agent)
    
    # Secondary agent for load balancing (if needed)
    # secondary_agent = DatasetValidationAgent("secondary_validator", 8001)
    # bureau.add(secondary_agent.agent)
    
    return bureau

# Example client code for testing
async def test_validation_agent():
    """Test the validation agent with a sample request"""
    print("🧪 Testing Enhanced Dataset Validation Agent")
    print("=" * 50)
    
    # Create a test request
    request = DatasetAnalysisRequest(
        dataset_path="sample_dataset.csv",
        dataset_type="csv",
        analysis_depth="complete",
        requester_id="test_client_001"
    )
    
    print(f"📝 Test request created:")
    print(f"  Dataset: {request.dataset_path}")
    print(f"  Analysis depth: {request.analysis_depth}")
    print(f"  Requester: {request.requester_id}")
    
    # Note: In actual usage, this would be sent via the uAgents network
    # For testing, we would need to set up a client agent to send the message

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "bureau":
        # Run as bureau (multiple agents)
        print("🏢 Starting Dataset Validation Bureau")
        validation_bureau = create_validation_bureau()
        validation_bureau.run()
    elif len(sys.argv) > 1 and sys.argv[1] == "test":
        # Run test
        asyncio.run(test_validation_agent())
    else:
        # Run single agent
        print("🤖 Starting Single Dataset Validation Agent")
        validator = DatasetValidationAgent()
        validator.agent.run()