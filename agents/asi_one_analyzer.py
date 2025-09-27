#!/usr/bin/env python3
"""
ASI:One Extended model integration for dataset quality analysis - Final corrected version
Properly handles dataset size context without confusion
"""

import json
import httpx
import asyncio
import pandas as pd
import re
from typing import Dict, Any, Optional
from datetime import datetime

class ASIOneAnalyzer:
    """ASI:One Extended model analyzer for dataset quality assessment"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = "https://api.asi1.ai/v1/chat/completions"
        self.model = "asi1-extended"
        
    async def analyze_dataset_quality(
        self, 
        tool_results: Dict[str, Any], 
        dataset_sample: pd.DataFrame,
        dataset_name: str = "Dataset"
    ) -> Dict[str, Any]:
        """
        Analyze dataset quality using ASI:One Extended model
        
        Args:
            tool_results: Validation and legal compliance results
            dataset_sample: Sample of the dataset (for column context only)
            dataset_name: Name/description of the dataset
            
        Returns:
            Dictionary containing analysis results and metadata
        """
        try:
            # Extract actual dataset dimensions from validation results
            actual_dimensions = self._extract_dataset_dimensions(tool_results)
            
            # Create analysis prompt with correct dataset size
            prompt = self._create_analysis_prompt(tool_results, dataset_sample, dataset_name, actual_dimensions)
            
            # Call ASI:One API
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.api_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a Senior Data Scientist and ML Engineer with 15+ years of experience in healthcare data analysis. Provide direct, technical analysis without casual language or pleasantries. Focus on actionable insights and quantitative assessments."
                            },
                            {
                                "role": "user", 
                                "content": prompt
                            }
                        ],
                        "temperature": 0.3,
                        "max_tokens": 4096
                    }
                )
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"API request failed: {response.status_code} - {response.text}"
                }
            
            result = response.json()
            
            # Parse response and extract insights
            analysis_text = self._parse_response(result)
            quality_score = self._extract_quality_score(analysis_text)
            
            return {
                "success": True,
                "timestamp": datetime.now().isoformat(),
                "model_used": self.model,
                "analysis": {
                    "expert_analysis": analysis_text,
                    "quality_score": quality_score,
                    "token_usage": result.get("usage", {}),
                    "model_info": {
                        "model": result.get("model", self.model),
                        "response_id": result.get("id", "unknown")
                    }
                },
                "source_data": {
                    "validation_tools_count": len(tool_results.get("validation_tool_results", {})),
                    "legal_tools_count": len(tool_results.get("legal_tool_results", {})),
                    "analysis_completeness": "full",
                    "actual_dataset_size": actual_dimensions
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Analysis failed: {str(e)}"
            }
    
    def _extract_dataset_dimensions(self, tool_results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract actual dataset dimensions from validation results"""
        dimensions = {"rows": None, "columns": None, "cells": None}
        
        # Get total cells from integrity results
        integrity_results = tool_results.get("validation_tool_results", {}).get("integrity_tools", {})
        missing_analysis = integrity_results.get("missing_value_analyzer", {}).get("analysis", {})
        overall_stats = missing_analysis.get("overall_stats", {})
        dimensions["cells"] = overall_stats.get("total_cells")
        
        # Get total rows from duplicate results
        duplicate_analysis = integrity_results.get("duplicate_record_detector", {}).get("analysis", {})
        duplicate_stats = duplicate_analysis.get("overall_stats", {})
        dimensions["rows"] = duplicate_stats.get("total_rows")
        
        # Calculate columns
        if dimensions["cells"] and dimensions["rows"]:
            dimensions["columns"] = dimensions["cells"] // dimensions["rows"]
        
        # Get numeric columns count from statistical results
        statistical_results = tool_results.get("validation_tool_results", {}).get("statistical_tools", {})
        outlier_analysis = statistical_results.get("outlier_detection_engine", {}).get("analysis", {})
        outlier_stats = outlier_analysis.get("overall_stats", {})
        dimensions["numeric_columns"] = outlier_stats.get("total_numeric_columns", 0)
        
        return dimensions
    
    def _create_analysis_prompt(
        self, 
        tool_results: Dict[str, Any], 
        dataset_sample: pd.DataFrame, 
        dataset_name: str,
        actual_dimensions: Dict[str, Any]
    ) -> str:
        """Create comprehensive analysis prompt with correct dataset context"""
        
        # Format actual dataset size
        rows = actual_dimensions.get("rows", "unknown")
        cols = actual_dimensions.get("columns", "unknown") 
        cells = actual_dimensions.get("cells", "unknown")
        numeric_cols = actual_dimensions.get("numeric_columns", "unknown")
        
        dataset_size_info = f"""ACTUAL DATASET DIMENSIONS (from validation metrics):
- Total Rows: {rows:,}
- Total Columns: {cols}
- Total Cells: {cells:,}
- Numeric Columns: {numeric_cols}"""
        
        # Format sample context
        sample_info = f"""COLUMN STRUCTURE (sample for context only):
- Sample shows {dataset_sample.shape[0]} rows × {dataset_sample.shape[1]} columns
- Column names: {', '.join(dataset_sample.columns.tolist())}
- Data types: {dict(dataset_sample.dtypes)}"""
        
        # Format validation results
        validation_summary = self._format_validation_results(tool_results)
        
        prompt = f"""Analyze the dataset quality for: {dataset_name}

{dataset_size_info}

{sample_info}

VALIDATION RESULTS:
{validation_summary}

ANALYSIS REQUIREMENTS:
Provide a comprehensive dataset quality assessment covering:

1. DATA INTEGRITY ANALYSIS
- Missing value patterns and impact
- Duplicate record assessment  
- Data type consistency evaluation

2. STATISTICAL PROPERTIES
- Outlier distribution and severity
- Data distribution characteristics
- Feature correlation implications

3. ML READINESS ASSESSMENT
- Feature quality for predictive modeling
- Bias and fairness considerations
- Preprocessing requirements

4. LEGAL & COMPLIANCE REVIEW
- PII exposure risks
- Regulatory compliance status
- Data governance recommendations

5. OVERALL QUALITY SCORE
Provide a numerical score (0-100) with detailed justification.

6. ACTIONABLE RECOMMENDATIONS
Specific steps to improve dataset quality.

Focus on the ACTUAL dataset dimensions provided above. The sample data is only for column context."""

        return prompt
    
    def _format_validation_results(self, tool_results: Dict[str, Any]) -> str:
        """Format validation results into readable text"""
        formatted = []
        
        # Validation tools
        validation_tools = tool_results.get("validation_tool_results", {})
        for category, tools in validation_tools.items():
            formatted.append(f"\n{category.upper().replace('_', ' ')}:")
            for tool_name, results in tools.items():
                if results.get("success"):
                    analysis = results.get("analysis", {})
                    formatted.append(f"  {tool_name}: {json.dumps(analysis, indent=4)}")
                else:
                    formatted.append(f"  {tool_name}: FAILED")
        
        # Legal tools
        legal_tools = tool_results.get("legal_tool_results", {})
        if legal_tools:
            formatted.append(f"\nLEGAL COMPLIANCE:")
            for tool_name, results in legal_tools.items():
                if results.get("success"):
                    analysis = results.get("analysis", {})
                    formatted.append(f"  {tool_name}: {json.dumps(analysis, indent=4)}")
                else:
                    formatted.append(f"  {tool_name}: FAILED")
        
        return "\n".join(formatted)
    
    def _parse_response(self, api_response: Dict[str, Any]) -> str:
        """Parse ASI:One Extended response - handles both content and reasoning fields"""
        try:
            choices = api_response.get("choices", [])
            if not choices:
                return "No response content available"
            
            message = choices[0].get("message", {})
            
            # ASI:One Extended may use 'reasoning' field for detailed analysis
            if "reasoning" in message:
                return message["reasoning"]
            elif "content" in message:
                return message["content"]
            else:
                return str(message)
                
        except Exception as e:
            return f"Error parsing response: {str(e)}"
    
    def _extract_quality_score(self, analysis_text: str) -> Optional[float]:
        """Extract numerical quality score from analysis text"""
        try:
            # Look for various score patterns
            patterns = [
                r"Overall Quality Score:\s*([0-9]+\.?[0-9]*)",
                r"Quality Score:\s*([0-9]+\.?[0-9]*)",
                r"Score:\s*([0-9]+\.?[0-9]*)/100",
                r"([0-9]+\.?[0-9]*)/100",
                r"score.*?([0-9]+\.?[0-9]*)"
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, analysis_text, re.IGNORECASE)
                if matches:
                    score = float(matches[0])
                    if 0 <= score <= 100:
                        return score
            
            return None
            
        except Exception:
            return None

# Convenience function for direct usage
async def analyze_with_asi_one(
    api_key: str,
    tool_results: Dict[str, Any],
    dataset_sample: pd.DataFrame,
    dataset_name: str = "Dataset"
) -> Dict[str, Any]:
    """
    Convenience function to analyze dataset quality with ASI:One
    
    Args:
        api_key: ASI:One API key
        tool_results: Validation and legal compliance results
        dataset_sample: Sample of the dataset for column context
        dataset_name: Name/description of the dataset
        
    Returns:
        Analysis results dictionary
    """
    analyzer = ASIOneAnalyzer(api_key)
    return await analyzer.analyze_dataset_quality(tool_results, dataset_sample, dataset_name)