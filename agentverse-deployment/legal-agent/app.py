#!/usr/bin/env python3
"""
Legal Compliance Agent - Agentverse Deployment
ETH Delhi 2025 - Autonomous Legal Compliance Checking
"""

from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low
from typing import Dict, List, Any, Optional
import pandas as pd
import logging
import json
import hashlib
import re
from datetime import datetime

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
    """Result model for legal compliance analysis with raw tool outputs"""
    request_id: str
    success: bool
    dataset_name: str
    analysis_type: str
    
    # Raw tool outputs (no score calculations)
    raw_tool_outputs: Dict[str, Any]  # Contains all individual legal tool results as-is
    
    # Summary from agent (no combined scores)
    legal_summary: str
    requires_action: bool
    
    # Detailed results
    key_findings: List[str]
    critical_recommendations: List[str]
    
    # Error handling
    error_message: Optional[str] = None
    analysis_timestamp: str
    
    # Processing info
    timestamp: str = datetime.now().isoformat()
    processing_time_seconds: float = 0.0
    errors: List[str] = []

# Create the agent with mailbox enabled for Agentverse
agent = Agent(
    name="eth_delhi_legal_compliance",
    seed="eth_delhi_2025_legal_compliance_agent_unique_seed",
    mailbox=True,  # Enable mailbox for Agentverse deployment
)

# Agent state
active_requests = {}

# Fund agent for testnet operations
fund_agent_if_low(agent.wallet.address())

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("legal_compliance")

@agent.on_event("startup")
async def startup_handler(ctx: Context):
    """Handle agent startup"""
    ctx.logger.info("🚀 Legal Compliance Agent starting up on Agentverse...")
    ctx.logger.info(f"Agent address: {agent.address}")
    ctx.logger.info("✅ Legal Compliance Agent ready for requests")

@agent.on_message(model=LegalComplianceRequest)
async def handle_compliance_request(ctx: Context, sender: str, msg: LegalComplianceRequest):
    """Handle legal compliance analysis requests"""
    
    ctx.logger.info(f"📋 Received legal compliance request from {sender}")
    ctx.logger.info(f"Request ID: {msg.request_id}")
    ctx.logger.info(f"Dataset: {msg.dataset_name}")
    ctx.logger.info(f"Analysis type: {msg.analysis_type}")
    
    # Track the request
    active_requests[msg.request_id] = {
        "sender": sender,
        "dataset_name": msg.dataset_name,
        "analysis_type": msg.analysis_type,
        "start_time": datetime.now(),
        "status": "processing"
    }
    
    try:
        # Load or prepare dataset
        dataset = await prepare_dataset(msg)
        if dataset is None:
            raise Exception("Could not load dataset")
        
        # Perform analysis based on request type
        result = await perform_compliance_analysis(ctx, msg, dataset)
        
        # Send final result
        await ctx.send(sender, result)
        
        # Update request status
        active_requests[msg.request_id]["status"] = "completed"
        ctx.logger.info(f"✅ Completed analysis for request {msg.request_id}")
        
    except Exception as e:
        ctx.logger.error(f"❌ Analysis failed for request {msg.request_id}: {e}")
        
        # Send error result
        error_result = LegalComplianceResult(
            request_id=msg.request_id,
            success=False,
            dataset_name=msg.dataset_name,
            analysis_type=msg.analysis_type,
            raw_tool_outputs={"error": str(e)},
            legal_summary=f"Analysis failed: {str(e)}",
            requires_action=True,
            key_findings=[],
            critical_recommendations=["Resolve analysis errors before proceeding"],
            error_message=str(e),
            analysis_timestamp=datetime.now().isoformat(),
            errors=[str(e)]
        )
        await ctx.send(sender, error_result)

async def prepare_dataset(msg: LegalComplianceRequest) -> Optional[pd.DataFrame]:
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
                return pd.read_csv(msg.dataset_path)  # Try CSV as fallback
        except Exception as e:
            logger.error(f"Could not load dataset from {msg.dataset_path}: {e}")
            return None
    
    else:
        logger.error("No dataset data or path provided")
        return None

async def perform_compliance_analysis(ctx: Context, msg: LegalComplianceRequest, 
                                     dataset: pd.DataFrame) -> LegalComplianceResult:
    """Perform the requested compliance analysis"""
    
    fingerprint_result = None
    pii_result = None
    
    # Perform fingerprinting analysis
    if msg.analysis_type in ["full", "fingerprinting"]:
        ctx.logger.info("🔍 Running dataset fingerprinting...")
        fingerprint_result = await run_dataset_fingerprinting(dataset, msg.dataset_name)
    
    # Perform PII scanning
    if msg.analysis_type in ["full", "pii_scan"]:
        ctx.logger.info("🕵️ Running PII scanning...")
        pii_result = await run_pii_scanning(dataset, msg.include_ner)
    
    # Combine results and generate final assessment
    ctx.logger.info("📊 Generating compliance assessment...")
    return combine_analysis_results(msg, fingerprint_result, pii_result)

async def run_dataset_fingerprinting(dataset: pd.DataFrame, dataset_name: str) -> Dict[str, Any]:
    """Run dataset fingerprinting analysis"""
    try:
        # Create a simple dataset fingerprint using column names, types, and basic stats
        column_info = []
        for col in dataset.columns:
            col_info = {
                "name": col,
                "type": str(dataset[col].dtype),
                "null_count": int(dataset[col].isnull().sum()),
                "unique_count": int(dataset[col].nunique())
            }
            column_info.append(col_info)
        
        # Create fingerprint hash
        fingerprint_data = {
            "dataset_name": dataset_name,
            "shape": dataset.shape,
            "columns": sorted(dataset.columns.tolist()),
            "dtypes": {col: str(dtype) for col, dtype in dataset.dtypes.items()}
        }
        
        fingerprint_str = json.dumps(fingerprint_data, sort_keys=True)
        dataset_fingerprint = hashlib.sha256(fingerprint_str.encode()).hexdigest()
        
        # Simple originality scoring based on column names and structure
        common_patterns = ['id', 'name', 'date', 'time', 'value', 'amount', 'price', 'count']
        common_count = sum(1 for col in dataset.columns if any(pattern in col.lower() for pattern in common_patterns))
        originality_score = max(20, 100 - (common_count * 10))  # Simple heuristic
        
        # Determine verification status
        if dataset_name.lower() in ['iris', 'titanic', 'boston', 'diabetes', 'wine']:
            verification_status = "Known Public Dataset"
        else:
            verification_status = "Original"
        
        return {
            "success": True,
            "dataset_fingerprint": dataset_fingerprint,
            "verification_status": verification_status,
            "originality_score": originality_score,
            "column_info": column_info,
            "recommendations": [
                "Consider dataset licensing if sharing publicly",
                "Document data sources and collection methods",
                "Review data usage permissions"
            ]
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "dataset_fingerprint": None,
            "verification_status": "Unknown",
            "originality_score": 0
        }

async def run_pii_scanning(dataset: pd.DataFrame, include_ner: bool = True) -> Dict[str, Any]:
    """Run PII scanning analysis"""
    try:
        pii_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b',
            'ssn': r'\b\d{3}-?\d{2}-?\d{4}\b',
            'credit_card': r'\b(?:\d{4}[-\s]?){3}\d{4}\b'
        }
        
        pii_columns = []
        pii_counts = {}
        column_risks = {}
        
        for col in dataset.columns:
            col_pii_count = 0
            col_pii_types = []
            
            # Check column name for PII indicators
            pii_keywords = ['email', 'phone', 'ssn', 'social', 'name', 'address', 'zip', 'postal']
            if any(keyword in col.lower() for keyword in pii_keywords):
                col_pii_types.append('column_name_indicator')
                col_pii_count += 10
            
            # Sample check for PII patterns in actual data
            if dataset[col].dtype == 'object':
                sample_data = dataset[col].dropna().astype(str).head(100)
                
                for pii_type, pattern in pii_patterns.items():
                    matches = sample_data.str.contains(pattern, regex=True, na=False).sum()
                    if matches > 0:
                        col_pii_types.append(pii_type)
                        col_pii_count += matches
            
            if col_pii_count > 0:
                pii_columns.append(col)
                pii_counts[col] = col_pii_count
                
                # Risk assessment
                if col_pii_count >= 20:
                    column_risks[col] = "High"
                elif col_pii_count >= 5:
                    column_risks[col] = "Medium" 
                else:
                    column_risks[col] = "Low"
        
        # Calculate overall PII risk score
        total_pii_indicators = sum(pii_counts.values())
        total_columns = len(dataset.columns)
        pii_risk_score = min(100, (total_pii_indicators / total_columns) * 20)
        
        # Determine risk level
        if pii_risk_score >= 70:
            risk_level = "High"
        elif pii_risk_score >= 40:
            risk_level = "Medium"
        elif pii_risk_score >= 20:
            risk_level = "Low"
        else:
            risk_level = "Minimal"
        
        recommendations = []
        if len(pii_columns) > 0:
            recommendations.extend([
                f"Review {len(pii_columns)} columns with potential PII data",
                "Consider data anonymization or pseudonymization",
                "Implement data access controls",
                "Review GDPR/privacy compliance requirements"
            ])
        else:
            recommendations.append("No obvious PII detected - dataset appears privacy-safe")
        
        return {
            "success": True,
            "pii_risk_score": pii_risk_score,
            "risk_level": risk_level,
            "risk_assessment": {
                "columns_with_pii": len(pii_columns),
                "pii_columns": pii_columns,
                "column_risks": column_risks,
                "total_pii_indicators": total_pii_indicators
            },
            "detailed_findings": pii_counts,
            "recommendations": recommendations
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "pii_risk_score": 100,  # Assume worst case on error
            "risk_level": "High",
            "risk_assessment": {
                "columns_with_pii": 0,
                "pii_columns": [],
                "column_risks": {},
                "total_pii_indicators": 0
            }
        }

def combine_analysis_results(msg: LegalComplianceRequest, 
                           fingerprint_result: Optional[Dict], 
                           pii_result: Optional[Dict]) -> LegalComplianceResult:
    """Combine analysis results into a comprehensive compliance assessment"""
    
    # Extract key metrics
    dataset_fingerprint = None
    verification_status = None
    originality_score = None
    pii_risk_score = None
    pii_risk_level = None
    columns_with_pii = 0
    
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
        
        key_findings.append(f"PII risk score: {pii_risk_score:.1f}/100")
        key_findings.append(f"PII risk level: {pii_risk_level}")
        key_findings.append(f"Columns with PII: {columns_with_pii}")
        
        # Add top PII recommendations
        pii_recs = pii_result.get('recommendations', [])
        critical_recommendations.extend(pii_recs[:2])
    
    # Determine overall risk and legal status
    overall_risk_level, legal_status, requires_action = calculate_overall_compliance(
        fingerprint_result, pii_result
    )
    
    # Calculate overall compliance score (0-100)
    compliance_score = calculate_compliance_score(
        originality_score, pii_risk_score, overall_risk_level
    )
    
    # Compile raw tool outputs
    raw_tool_outputs = {}
    if fingerprint_result:
        raw_tool_outputs["dataset_fingerprinting"] = fingerprint_result
    if pii_result:
        raw_tool_outputs["pii_scanner"] = pii_result
    
    # Generate legal summary
    legal_summary = f"Legal Analysis Complete - Risk Level: {overall_risk_level}, Compliance Score: {compliance_score:.1f}/100"
    if requires_action:
        legal_summary += f", Action Required: {len(critical_recommendations)} recommendations"
    
    return LegalComplianceResult(
        request_id=msg.request_id,
        success=True,
        dataset_name=msg.dataset_name,
        analysis_type=msg.analysis_type,
        key_findings=key_findings,
        raw_tool_outputs=raw_tool_outputs,
        legal_summary=legal_summary,
        requires_action=requires_action,
        critical_recommendations=critical_recommendations[:5],  # Limit for message size
        analysis_timestamp=datetime.now().isoformat()
    )

def calculate_overall_compliance(fingerprint_result: Optional[Dict], 
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

def calculate_compliance_score(originality_score: Optional[float], 
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

if __name__ == "__main__":
    logger.info("🚀 Starting Legal Compliance Agent for Agentverse...")
    logger.info(f"Agent address: {agent.address}")
    agent.run()