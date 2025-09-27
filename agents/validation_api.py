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
    """API response model for validation results"""
    request_id: str
    success: bool
    dataset_name: str
    timestamp: str
    
    # Main scores for frontend display
    overall_correctness_score: float
    grade: str
    data_quality_score: float
    legal_compliance_score: float
    
    # Summary information
    executive_summary: str
    processing_time_seconds: float
    
    # Issues and recommendations
    critical_issues: List[str]
    issues_found: List[str]
    recommendations: List[str]
    warnings: List[str]
    
    # Detailed breakdown
    score_breakdown: Dict[str, float]
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
            # Convert to API format
            api_result = {
                "request_id": request_id,
                "success": True,
                "dataset_name": result.dataset_name,
                "timestamp": result.timestamp,
                "overall_correctness_score": result.overall_correctness_score,
                "grade": result.grade,
                "data_quality_score": result.data_quality_score,
                "legal_compliance_score": result.legal_compliance_score,
                "executive_summary": result.executive_summary,
                "processing_time_seconds": result.processing_time_seconds,
                "critical_issues": result.critical_issues,
                "issues_found": result.critical_issues,  # For API compatibility
                "recommendations": result.recommendations,
                "warnings": [],
                "score_breakdown": {
                    "data_quality": result.data_quality_score,
                    "legal_compliance": result.legal_compliance_score,
                    "overall": result.overall_correctness_score
                },
                "agents_used": ["validation_agent", "legal_compliance_agent"] if ORCHESTRATOR_AVAILABLE else [],
                "errors": result.errors
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
            "overall_correctness_score": 0.0,
            "grade": "F",
            "data_quality_score": 0.0,
            "legal_compliance_score": 0.0,
            "executive_summary": f"Validation failed: {str(e)}",
            "processing_time_seconds": 0.0,
            "critical_issues": [str(e)],
            "issues_found": [str(e)],
            "recommendations": ["Fix validation errors before proceeding"],
            "warnings": [],
            "score_breakdown": {"data_quality": 0.0, "legal_compliance": 0.0, "overall": 0.0},
            "agents_used": [],
            "errors": [str(e)]
        }

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
    print("  • GET  /docs                - Interactive API documentation")
    print("=" * 50)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        log_level="info"
    )