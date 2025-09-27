#!/usr/bin/env python3
"""
Standardized Message Models - ETH Delhi 2025
Following Fetch.ai Innovation Labs documentation patterns for consistent message types
"""

from uagents import Model
from typing import Dict, List, Any, Optional
from datetime import datetime
from pydantic import Field, validator

# Base message models following uAgents patterns
class BaseRequest(Model):
    """Base request model with common fields"""
    request_id: str = Field(..., description="Unique identifier for the request")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Request timestamp")
    requester_address: str = Field(..., description="Address of the requesting agent")

class BaseResponse(Model):
    """Base response model with common fields"""
    request_id: str = Field(..., description="Request identifier this response corresponds to")
    success: bool = Field(..., description="Whether the operation was successful")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Response timestamp")
    processing_time_seconds: Optional[float] = Field(None, description="Time taken to process the request")
    errors: List[str] = Field(default_factory=list, description="List of error messages if any")
    warnings: List[str] = Field(default_factory=list, description="List of warning messages if any")

# Dataset Analysis Messages
class DatasetAnalysisRequest(BaseRequest):
    """Comprehensive dataset analysis request following uAgents message patterns"""
    dataset_path: Optional[str] = Field(None, description="Path to the dataset file")
    dataset_name: str = Field("unknown", description="Name of the dataset")
    dataset_data: Optional[Dict[str, Any]] = Field(None, description="Dataset data if provided inline")
    analysis_depth: str = Field("complete", description="Analysis depth: basic, standard, complete")
    custom_parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Custom analysis parameters")
    
    @validator('analysis_depth')
    def validate_analysis_depth(cls, v):
        allowed_depths = ['basic', 'standard', 'complete']
        if v not in allowed_depths:
            raise ValueError(f'analysis_depth must be one of {allowed_depths}')
        return v

class DatasetAnalysisResult(BaseResponse):
    """Complete dataset analysis result with standardized structure"""
    # Basic dataset information
    dataset_info: Dict[str, Any] = Field(..., description="Basic dataset metadata")
    
    # Scoring components (0-100 scale)
    integrity_scores: Dict[str, float] = Field(default_factory=dict, description="Data integrity scores by tool")
    statistical_scores: Dict[str, float] = Field(default_factory=dict, description="Statistical analysis scores")
    ml_usability_scores: Dict[str, float] = Field(default_factory=dict, description="ML usability scores")
    
    # High-level analysis
    persona_tags: List[str] = Field(default_factory=list, description="Dataset persona classifications")
    primary_persona: str = Field("", description="Primary dataset persona")
    contextual_scores: Dict[str, float] = Field(default_factory=dict, description="Context-specific scores")
    
    # Final synthesis
    overall_utility_score: float = Field(0.0, description="Overall utility score (0-100)")
    utility_grade: Dict[str, Any] = Field(default_factory=dict, description="Grade information")
    data_integrity_score: float = Field(0.0, description="Data integrity score (0-100)")
    executive_summary: str = Field("", description="Executive summary of analysis")
    
    # Actionable insights
    recommendations: List[str] = Field(default_factory=list, description="Improvement recommendations")
    publication_readiness: Dict[str, Any] = Field(default_factory=dict, description="Publication readiness assessment")
    next_steps: List[str] = Field(default_factory=list, description="Recommended next steps")

# Legal Compliance Messages
class LegalComplianceRequest(BaseRequest):
    """Legal compliance analysis request with standardized validation"""
    dataset_path: Optional[str] = Field(None, description="Path to dataset for compliance analysis")
    dataset_name: str = Field("unknown", description="Name of the dataset")
    compliance_frameworks: List[str] = Field(default_factory=lambda: ["GDPR", "CCPA", "HIPAA"], description="Compliance frameworks to check")
    include_pii_scan: bool = Field(True, description="Whether to include PII scanning")
    include_fingerprinting: bool = Field(True, description="Whether to include dataset fingerprinting")

class LegalComplianceResult(BaseResponse):
    """Legal compliance analysis result with standardized structure"""
    # Compliance assessment
    compliance_score: float = Field(0.0, description="Overall compliance score (0-100)")
    framework_scores: Dict[str, float] = Field(default_factory=dict, description="Scores by compliance framework")
    
    # Detailed findings
    key_findings: List[str] = Field(default_factory=list, description="Key compliance findings summary")
    pii_findings: Dict[str, Any] = Field(default_factory=dict, description="PII scanning results")
    fingerprint_results: Dict[str, Any] = Field(default_factory=dict, description="Dataset fingerprinting results")
    risk_assessment: Dict[str, Any] = Field(default_factory=dict, description="Risk assessment details")
    
    # Compliance recommendations
    compliance_recommendations: List[str] = Field(default_factory=list, description="Compliance improvement recommendations")
    required_actions: List[str] = Field(default_factory=list, description="Required actions for compliance")
    optional_improvements: List[str] = Field(default_factory=list, description="Optional improvements")

# Orchestrator Messages
class ComprehensiveValidationRequest(BaseRequest):
    """Request for comprehensive validation combining data quality and legal compliance"""
    dataset_path: Optional[str] = Field(None, description="Path to the dataset")
    dataset_name: str = Field("unknown", description="Dataset name")
    dataset_data: Optional[Dict[str, Any]] = Field(None, description="Dataset data if provided inline")
    analysis_depth: str = Field("complete", description="Analysis depth")
    include_legal_analysis: bool = Field(True, description="Whether to include legal compliance analysis")
    
    @validator('analysis_depth')
    def validate_analysis_depth(cls, v):
        allowed_depths = ['basic', 'standard', 'complete']
        if v not in allowed_depths:
            raise ValueError(f'analysis_depth must be one of {allowed_depths}')
        return v

class ComprehensiveValidationResult(BaseResponse):
    """Complete validation result combining data quality and legal compliance"""
    # Dataset information
    dataset_name: str = Field(..., description="Name of the analyzed dataset")
    dataset_info: Dict[str, Any] = Field(..., description="Dataset metadata")
    
    # Overall scores (0-100 scale)
    overall_correctness_score: float = Field(..., description="Combined correctness score")
    data_quality_score: float = Field(..., description="Data quality score from validation agent")
    legal_compliance_score: float = Field(..., description="Legal compliance score")
    grade: str = Field(..., description="Overall grade (A, B, C, D, F)")
    
    # Analysis results
    validation_results: Optional[Dict[str, Any]] = Field(None, description="Detailed validation results")
    legal_results: Optional[Dict[str, Any]] = Field(None, description="Detailed legal compliance results")
    
    # Summary and recommendations
    executive_summary: str = Field(..., description="Executive summary")
    critical_issues: List[str] = Field(default_factory=list, description="Critical issues found")
    recommendations: List[str] = Field(default_factory=list, description="Improvement recommendations")
    
    # Status tracking
    validation_status: str = Field("unknown", description="Validation process status")
    legal_status: str = Field("unknown", description="Legal analysis process status")

# Status and Control Messages
class ValidationStatusRequest(BaseRequest):
    """Request for validation status"""
    pass  # Inherits all fields from BaseRequest

class ValidationStatusResponse(BaseResponse):
    """Response with current validation status"""
    status: str = Field(..., description="Current status: processing, completed, failed")
    progress: Dict[str, str] = Field(..., description="Progress of each component")
    message: str = Field(..., description="Status message")

class AgentStatusRequest(BaseRequest):
    """Request for agent status and capabilities"""
    pass  # Inherits all fields from BaseRequest

class AgentStatusResponse(BaseResponse):
    """Agent status and capabilities response"""
    agent_name: str = Field(..., description="Name of the agent")
    agent_address: str = Field(..., description="Agent's network address")
    status: str = Field(..., description="Agent status")
    available_tools: Dict[str, str] = Field(..., description="Available tools and their descriptions")
    analysis_modes: List[str] = Field(..., description="Supported analysis modes")
    uptime: str = Field(..., description="Agent uptime")
    processed_requests: int = Field(..., description="Number of processed requests")

# Health Check Messages
class HealthCheckRequest(BaseRequest):
    """Health check request for system monitoring"""
    check_dependencies: bool = Field(True, description="Whether to check dependencies")

class HealthCheckResponse(BaseResponse):
    """Health check response with system status"""
    status: str = Field(..., description="System status: healthy, degraded, unhealthy")
    components: Dict[str, str] = Field(..., description="Status of individual components")
    dependencies: Dict[str, bool] = Field(default_factory=dict, description="Dependency availability")
    version: str = Field("1.0.0", description="System version")