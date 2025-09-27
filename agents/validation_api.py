#!/usr/bin/env python3
"""
Dataset Validation API - ETH Delhi 2025
Production-ready API endpoint for frontend integration
"""

import sys
import os
from pathlib import Path

# Add current directory to Python path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from fastapi import FastAPI, HTTPException, BackgroundTasks, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import asyncio
import json
import tempfile
import shutil
from datetime import datetime
import uuid
import logging

# Try to import our orchestrator with fallback
try:
    from orchestrator_agent import run_comprehensive_validation, ComprehensiveValidationResult
    ORCHESTRATOR_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Orchestrator not available: {e}")
    ORCHESTRATOR_AVAILABLE = False
    
    # Create fallback result class
    class ComprehensiveValidationResult:
        def __init__(self):
            self.success = False
            self.dataset_name = "Unknown"
            self.timestamp = datetime.now().isoformat()
            self.overall_correctness_score = 0.0
            self.grade = "F"
            self.data_quality_score = 0.0
            self.legal_compliance_score = 0.0
            self.executive_summary = "Orchestrator agent not available"
            self.processing_time_seconds = 0.0
            self.critical_issues = ["Agent dependencies not available"]
            self.recommendations = ["Install required dependencies"]
            self.errors = ["Orchestrator agent import failed"]

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Dataset Validation API",
    description="Comprehensive dataset validation using AI agents",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global storage for validation results (use Redis/DB in production)
validation_results: Dict[str, Dict] = {}
validation_status: Dict[str, str] = {}
class ValidationRequestAPI(BaseModel):
    dataset_name: str
    dataset_type: Optional[str] = "csv"
    include_legal_analysis: bool = True
    analysis_depth: str = "complete"

class ValidationStatusResponse(BaseModel):
    request_id: str
    status: str  # "processing", "completed", "failed"
    progress: Optional[str] = None
    estimated_completion: Optional[str] = None

class ValidationResultAPI(BaseModel):
    """API response model for validation results - returns all individual tool results"""
    request_id: str
    success: bool
    dataset_name: str
    timestamp: str
    
    # Summary information
    executive_summary: str
    processing_time_seconds: float
    
    # Issues and recommendations
    critical_issues: List[str]
    issues_found: List[str]
    recommendations: List[str]
    warnings: List[str]
    
    # All individual tool results - no consolidation
    all_validation_data: Dict[str, Any]  # Complete validation agent result
    raw_validation_results: Dict[str, Any]  # Individual tool outputs
    raw_legal_results: Dict[str, Any]  # Legal analysis results
    
    # Agent tracking
    agents_used: List[str]
    
    # Error handling
    errors: List[str] = []

class HealthResponse(BaseModel):
    status: str
    version: str
    agents_available: List[str]
    uptime_seconds: float

# In-memory storage for validation results (use Redis/DB in production)
validation_results: Dict[str, Dict] = {}
validation_status: Dict[str, str] = {}

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Dataset Validation API - ETH Delhi 2025",
        "version": "1.0.0",
        "docs": "/docs",
        "dashboard": "/validation_dashboard.html",
        "health": "/health"
    }

@app.get("/validation_dashboard.html")
async def get_dashboard():
    """Serve the validation dashboard HTML"""
    dashboard_path = Path(__file__).parent / "validation_dashboard.html"
    if dashboard_path.exists():
        return FileResponse(dashboard_path, media_type="text/html")
    else:
        raise HTTPException(status_code=404, detail="Dashboard not found")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    
    # Check if orchestrator is available
    agents_status = []
    if ORCHESTRATOR_AVAILABLE:
        agents_status = ["validation_agent", "legal_compliance_agent", "orchestrator"]
        status = "healthy"
    else:
        agents_status = ["api_only"]
        status = "degraded"
    
    return HealthResponse(
        status=status,
        version="1.0.0",
        agents_available=agents_status,
        uptime_seconds=0.0  # Placeholder since we're using direct functions
    )

@app.post("/validate/upload", response_model=Dict[str, str])
async def upload_and_validate(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    dataset_name: Optional[str] = None,
    include_legal_analysis: bool = True,
    analysis_depth: str = "complete"
):
    """Upload dataset file and start validation"""
    
    # Generate unique request ID
    request_id = str(uuid.uuid4())
    
    try:
        # Validate file type
        if not file.filename.endswith(('.csv', '.json', '.xlsx', '.parquet')):
            raise HTTPException(status_code=400, detail="Unsupported file format")
        
        # Create temporary file
        temp_dir = Path(tempfile.gettempdir()) / "dataset_validation"
        temp_dir.mkdir(exist_ok=True)
        
        temp_file = temp_dir / f"{request_id}_{file.filename}"
        
        # Save uploaded file
        with open(temp_file, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Set validation status
        validation_status[request_id] = "processing"
        
        # Start validation in background
        background_tasks.add_task(
            process_validation_task,
            request_id,
            str(temp_file),
            dataset_name or file.filename,
            file.filename.split('.')[-1],
            include_legal_analysis,
            analysis_depth
        )
        
        logger.info(f"Started validation for {file.filename} with request_id: {request_id}")
        
        return {
            "request_id": request_id,
            "message": "Validation started",
            "dataset_name": dataset_name or file.filename,
            "status_url": f"/validate/status/{request_id}",
            "result_url": f"/validate/result/{request_id}"
        }
        
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/validate/path", response_model=Dict[str, str])
async def validate_by_path(
    request: ValidationRequestAPI,
    background_tasks: BackgroundTasks,
    dataset_path: str
):
    """Validate dataset by file path (for local files)"""
    
    # Generate unique request ID
    request_id = str(uuid.uuid4())
    
    try:
        # Check if file exists
        file_path = Path(dataset_path)
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Dataset file not found")
        
        # Set validation status
        validation_status[request_id] = "processing"
        
        # Start validation in background
        background_tasks.add_task(
            process_validation_task,
            request_id,
            dataset_path,
            request.dataset_name,
            request.dataset_type,
            request.include_legal_analysis,
            request.analysis_depth
        )
        
        logger.info(f"Started validation for {dataset_path} with request_id: {request_id}")
        
        return {
            "request_id": request_id,
            "message": "Validation started",
            "dataset_name": request.dataset_name,
            "status_url": f"/validate/status/{request_id}",
            "result_url": f"/validate/result/{request_id}"
        }
        
    except Exception as e:
        logger.error(f"Path validation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/validate/status/{request_id}", response_model=ValidationStatusResponse)
async def get_validation_status(request_id: str):
    """Get validation status"""
    
    if request_id not in validation_status:
        raise HTTPException(status_code=404, detail="Request ID not found")
    
    status = validation_status[request_id]
    
    # Provide progress information
    progress_info = {
        "processing": "Running comprehensive validation analysis...",
        "completed": "Validation completed successfully",
        "failed": "Validation failed"
    }
    
    return ValidationStatusResponse(
        request_id=request_id,
        status=status,
        progress=progress_info.get(status, "Unknown status"),
        estimated_completion="2-5 minutes" if status == "processing" else None
    )

@app.get("/validate/result/{request_id}", response_model=ValidationResultAPI)
async def get_validation_result(request_id: str):
    """Get validation result"""
    
    if request_id not in validation_results:
        if request_id in validation_status:
            if validation_status[request_id] == "processing":
                raise HTTPException(status_code=202, detail="Validation still in progress")
            else:
                raise HTTPException(status_code=500, detail="Validation failed")
        else:
            raise HTTPException(status_code=404, detail="Request ID not found")
    
    result = validation_results[request_id]
    
    # Convert to API response format
    return ValidationResultAPI(**result)

@app.delete("/validate/result/{request_id}")
async def delete_validation_result(request_id: str):
    """Delete validation result and cleanup"""
    
    # Remove from storage
    validation_results.pop(request_id, None)
    validation_status.pop(request_id, None)
    
    # Cleanup temporary files
    temp_dir = Path(tempfile.gettempdir()) / "dataset_validation"
    for file_path in temp_dir.glob(f"{request_id}_*"):
        try:
            file_path.unlink()
        except Exception as e:
            logger.warning(f"Failed to cleanup {file_path}: {e}")
    
    return {"message": "Validation result deleted"}

@app.get("/validate/demo/healthcare")
async def demo_healthcare_validation(background_tasks: BackgroundTasks):
    """Demo endpoint for healthcare dataset validation"""
    
    # Check if demo dataset exists
    demo_path = Path(__file__).parent / "comprehensive_healthcare_dataset.csv"
    if not demo_path.exists():
        raise HTTPException(status_code=404, detail="Demo healthcare dataset not found")
    
    # Generate request ID
    request_id = str(uuid.uuid4())
    
    # Set status and start processing
    validation_status[request_id] = "processing"
    background_tasks.add_task(
        process_validation_task,
        request_id,
        str(demo_path),
        "Healthcare Demo Dataset",
        "csv",
        True,  # include_legal_analysis
        "complete"
    )
    
    return {
        "request_id": request_id,
        "message": "Demo healthcare validation started",
        "dataset_info": "1,500 patient records with 39 healthcare parameters",
        "status_url": f"/validate/status/{request_id}",
        "result_url": f"/validate/result/{request_id}"
    }

@app.get("/validate/demo/airquality")
async def demo_airquality_validation(background_tasks: BackgroundTasks):
    """Demo endpoint for air quality dataset validation"""
    
    # Check if demo dataset exists
    demo_path = Path(__file__).parent / "comprehensive_air_quality_dataset.csv"
    if not demo_path.exists():
        raise HTTPException(status_code=404, detail="Demo air quality dataset not found")
    
    # Generate request ID
    request_id = str(uuid.uuid4())
    
    # Set status and start processing
    validation_status[request_id] = "processing"
    background_tasks.add_task(
        process_validation_task,
        request_id,
        str(demo_path),
        "Air Quality Demo Dataset",
        "csv",
        True,  # include_legal_analysis
        "complete"
    )
    
    return {
        "request_id": request_id,
        "message": "Demo air quality validation started",
        "dataset_info": "1,000 environmental measurements with pollution data",
        "status_url": f"/validate/status/{request_id}",
        "result_url": f"/validate/result/{request_id}"
    }

async def process_validation_task(
    request_id: str,
    dataset_path: str,
    dataset_name: str,
    dataset_type: str,
    include_legal_analysis: bool,
    analysis_depth: str
):
    """Background task to process validation"""
    
    try:
        logger.info(f"Processing validation for request {request_id}")
        
        if ORCHESTRATOR_AVAILABLE:
            # Run comprehensive validation using our orchestrator function
            result = await run_comprehensive_validation(
                dataset_path=dataset_path,
                dataset_name=dataset_name,
                include_legal=include_legal_analysis
            )
        else:
            # Fallback when orchestrator is not available
            result = ComprehensiveValidationResult()
            result.success = False
            result.dataset_name = dataset_name
            result.errors = ["Validation agents not available - dependencies missing"]
            result.critical_issues = ["Please ensure all agent dependencies are installed"]
            result.recommendations = ["Run: pip install -r requirements.txt"]
        
        if result.success:
            # Extract all individual tool results from validation and legal agents
            validation_data = result.validation_results if hasattr(result, 'validation_results') else {}
            legal_data = result.legal_results if hasattr(result, 'legal_results') else {}
            
            # Build API result with ALL individual tool results - NO CONSOLIDATION
            api_result = {
                "request_id": request_id,
                "success": True,
                "dataset_name": result.dataset_name,
                "timestamp": result.timestamp,
                "executive_summary": result.executive_summary,
                "processing_time_seconds": result.processing_time_seconds,
                "critical_issues": result.critical_issues,
                "issues_found": result.critical_issues,  # For API compatibility
                "recommendations": result.recommendations,
                "warnings": [],
                "agents_used": ["validation_agent", "legal_compliance_agent"] if ORCHESTRATOR_AVAILABLE else [],
                "errors": result.errors,
                
                # RETURN ALL RAW DATA - EVERY INDIVIDUAL TOOL RESULT
                "all_validation_data": result.dict() if hasattr(result, 'dict') else {},
                "raw_validation_results": validation_data,
                "raw_legal_results": legal_data
            }
            
            validation_results[request_id] = api_result
            validation_status[request_id] = "completed"
            
            logger.info(f"Validation completed for request {request_id}")
        else:
            raise Exception(f"Validation failed: {result.errors[0] if result.errors else 'Unknown error'}")
            
    except Exception as e:
        logger.error(f"Validation error for request {request_id}: {str(e)}")
        validation_status[request_id] = "failed"
        validation_results[request_id] = {
            "request_id": request_id,
            "success": False,
            "dataset_name": dataset_name,
            "timestamp": datetime.now().isoformat(),
            "executive_summary": f"Validation failed: {str(e)}",
            "processing_time_seconds": 0.0,
            "critical_issues": [str(e)],
            "issues_found": [str(e)],
            "recommendations": ["Fix validation errors before proceeding"],
            "warnings": [],
            "agents_used": [],
            "errors": [str(e)],
            "all_validation_data": {},
            "raw_validation_results": {},
            "raw_legal_results": {}
        }


# ASI:One LLM Analysis Endpoint
# ==============================

class ASIOneAnalysisRequest(BaseModel):
    """Request model for ASI:One LLM analysis"""
    request_id: str  # ID from previous validation
    asi_one_api_key: str
    dataset_name: Optional[str] = "Dataset"

class ASIOneAnalysisResponse(BaseModel):
    """Response model for ASI:One LLM analysis"""
    success: bool
    timestamp: str
    analysis_id: str
    expert_analysis: str
    quality_score: Optional[float]
    model_used: str
    token_usage: Dict[str, Any]
    validation_source: str
    errors: List[str] = []

@app.post("/analyze/asi-one", response_model=ASIOneAnalysisResponse)
async def analyze_with_asi_one_llm(request: ASIOneAnalysisRequest):
    """
    Analyze dataset quality using ASI:One Extended LLM
    
    This endpoint takes the raw tool results from a previous validation
    and sends them to ASI:One Extended model for expert analysis.
    """
    
    try:
        # Import ASI:One analyzer
        from asi_one_analyzer import analyze_with_asi_one
        import pandas as pd
        
        # Check if validation results exist
        if request.request_id not in validation_results:
            raise HTTPException(
                status_code=404, 
                detail=f"Validation results not found for request_id: {request.request_id}"
            )
        
        validation_data = validation_results[request.request_id]
        
        # Check if validation was successful
        if not validation_data.get("success", False):
            raise HTTPException(
                status_code=400,
                detail="Cannot analyze failed validation. Please ensure validation completed successfully."
            )
        
        # Prepare tool results for ASI:One
        tool_results = {
            "validation_tool_results": validation_data.get("raw_validation_results", {}),
            "legal_tool_results": validation_data.get("raw_legal_results", {}),
            "dataset_info": {
                "name": validation_data.get("dataset_name", "Unknown"),
                "timestamp": validation_data.get("timestamp"),
                "processing_time": validation_data.get("processing_time_seconds", 0)
            }
        }
        
        # Create sample dataset context (we'll use mock data since we may not have the original file)
        # In production, you might want to store a sample of the original dataset
        dataset_sample = pd.DataFrame({
            "sample_note": ["Original dataset sample would be provided here for better context"],
            "columns_analyzed": [f"Dataset had multiple columns - see tool results for details"],
            "note": ["This is a placeholder - ideally store dataset sample during validation"]
        })
        
        # If we have dataset info from validation, create a better sample
        all_validation_data = validation_data.get("all_validation_data", {})
        if "dataset_info" in all_validation_data:
            dataset_info = all_validation_data["dataset_info"]
            # Create a mock sample based on column names and types
            if "columns" in dataset_info and "dtypes" in dataset_info:
                sample_data = {}
                for col in dataset_info["columns"][:10]:  # Limit to first 10 columns
                    dtype = dataset_info["dtypes"].get(col, "object")
                    if "int" in str(dtype):
                        sample_data[col] = [1, 2, 3, 4, 5]
                    elif "float" in str(dtype):
                        sample_data[col] = [1.1, 2.2, 3.3, 4.4, 5.5]
                    else:
                        sample_data[col] = ["sample", "data", "for", "context", "analysis"]
                
                dataset_sample = pd.DataFrame(sample_data)
        
        # Call ASI:One analyzer
        logger.info(f"Starting ASI:One analysis for request {request.request_id}")
        
        analysis_result = await analyze_with_asi_one(
            api_key=request.asi_one_api_key,
            tool_results=tool_results,
            dataset_sample=dataset_sample,
            dataset_name=request.dataset_name or validation_data.get("dataset_name", "Dataset")
        )
        
        if not analysis_result.get("success", False):
            raise Exception(analysis_result.get("error", "ASI:One analysis failed"))
        
        # Generate analysis ID
        analysis_id = str(uuid.uuid4())
        
        # Extract analysis details
        analysis_data = analysis_result.get("analysis", {})
        
        logger.info(f"ASI:One analysis completed for request {request.request_id}")
        
        return ASIOneAnalysisResponse(
            success=True,
            timestamp=analysis_result.get("timestamp", datetime.now().isoformat()),
            analysis_id=analysis_id,
            expert_analysis=analysis_data.get("expert_analysis", ""),
            quality_score=analysis_data.get("quality_score"),
            model_used=analysis_result.get("model_used", "asi1-extended"),
            token_usage=analysis_data.get("token_usage", {}),
            validation_source=request.request_id,
            errors=[]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ASI:One analysis error: {str(e)}")
        return ASIOneAnalysisResponse(
            success=False,
            timestamp=datetime.now().isoformat(),
            analysis_id="",
            expert_analysis="",
            quality_score=None,
            model_used="asi1-extended",
            token_usage={},
            validation_source=request.request_id,
            errors=[str(e)]
        )


@app.get("/analyze/demo/{dataset_type}")
async def demo_asi_one_analysis(
    dataset_type: str,
    asi_one_api_key: str,
    background_tasks: BackgroundTasks
):
    """
    Demo endpoint: Run full validation + ASI:One analysis
    
    This endpoint demonstrates the complete workflow:
    1. Run validation on demo dataset
    2. Automatically analyze results with ASI:One LLM
    """
    
    if dataset_type not in ["healthcare", "airquality"]:
        raise HTTPException(status_code=400, detail="Invalid dataset type. Use 'healthcare' or 'airquality'")
    
    try:
        # First, run the demo validation
        if dataset_type == "healthcare":
            validation_response = await demo_healthcare_validation(background_tasks)
        else:
            validation_response = await demo_airquality_validation(background_tasks)
        
        request_id = validation_response["request_id"]
        
        # Wait a moment for validation to complete (in production, you'd poll the status)
        await asyncio.sleep(2)
        
        # Check if validation completed
        if validation_status.get(request_id) != "completed":
            return {
                "message": "Validation started. Please wait for completion before ASI:One analysis.",
                "validation_request_id": request_id,
                "next_steps": [
                    f"1. Check validation status: GET /validate/status/{request_id}",
                    f"2. When completed, run ASI:One analysis: POST /analyze/asi-one",
                    "3. Use the validation request_id and your ASI:One API key"
                ]
            }
        
        # Run ASI:One analysis
        analysis_request = ASIOneAnalysisRequest(
            request_id=request_id,
            asi_one_api_key=asi_one_api_key,
            dataset_name=f"Demo {dataset_type.title()} Dataset"
        )
        
        analysis_result = await analyze_with_asi_one_llm(analysis_request)
        
        return {
            "validation_completed": True,
            "validation_request_id": request_id,
            "asi_one_analysis": analysis_result,
            "demo_workflow": "completed"
        }
        
    except Exception as e:
        logger.error(f"Demo ASI:One analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Demo analysis failed: {str(e)}")


# Development server
if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting Dataset Validation API Server")
    print("ETH Delhi 2025 - Production Ready API")
    print("=" * 50)
    print("📊 Endpoints available:")
    print("  • GET  /                    - API information")
    print("  • GET  /health              - Health check")  
    print("  • POST /validate/upload     - Upload & validate dataset")
    print("  • POST /validate/path       - Validate by file path")
    print("  • GET  /validate/status/{id} - Check validation status")
    print("  • GET  /validate/result/{id} - Get validation results")
    print("  • GET  /validate/demo/healthcare - Demo healthcare validation")
    print("  • GET  /validate/demo/airquality - Demo air quality validation")
    print("  🤖 ASI:One LLM Analysis:")
    print("  • POST /analyze/asi-one     - Analyze with ASI:One Extended LLM")
    print("  • GET  /analyze/demo/{type}?asi_one_api_key=KEY - Full demo workflow")
    print("  • GET  /docs                - Interactive API documentation")
    print("=" * 50)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        log_level="info"
    )