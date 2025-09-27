#!/usr/bin/env python3
"""
Agent Tools - Reusable tools for Fetch.ai agents
ETH Delhi 2025 - Dataset Validation Agent Tools
"""

from typing import Dict, List, Any, Optional, Union
import pandas as pd
import numpy as np
from pathlib import Path
import json
import logging
from datetime import datetime
from abc import ABC, abstractmethod

class BaseTool(ABC):
    """Base class for all agent tools"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"tool.{name}")
    
    @abstractmethod
    async def execute(self, *args, **kwargs) -> Dict[str, Any]:
        """Execute the tool with given parameters"""
        pass
    
    def log_execution(self, params: Dict[str, Any], result: Dict[str, Any]):
        """Log tool execution for debugging"""
        self.logger.info(f"Tool '{self.name}' executed with params: {params}")
        self.logger.debug(f"Tool result: {result}")

class DataLoaderTool(BaseTool):
    """Tool for loading various data formats"""
    
    def __init__(self):
        super().__init__(
            name="data_loader",
            description="Load datasets from various formats (CSV, JSON, Parquet, Excel)"
        )
        self.supported_formats = ['csv', 'json', 'parquet', 'xlsx', 'xls']
    
    async def execute(self, file_path: str, format_type: str = None, **kwargs) -> Dict[str, Any]:
        """Load dataset from file"""
        try:
            path = Path(file_path)
            
            # Auto-detect format if not provided
            if format_type is None:
                format_type = path.suffix.lower().lstrip('.')
            
            # Validate format
            if format_type not in self.supported_formats:
                return {
                    "success": False,
                    "error": f"Unsupported format: {format_type}. Supported: {self.supported_formats}",
                    "data": None
                }
            
            # Check if file exists
            if not path.exists():
                return {
                    "success": False,
                    "error": f"File not found: {file_path}",
                    "data": None
                }
            
            # Load data based on format
            if format_type == 'csv':
                df = pd.read_csv(file_path, **kwargs)
            elif format_type == 'json':
                df = pd.read_json(file_path, **kwargs)
            elif format_type == 'parquet':
                df = pd.read_parquet(file_path, **kwargs)
            elif format_type in ['xlsx', 'xls']:
                df = pd.read_excel(file_path, **kwargs)
            else:
                return {
                    "success": False,
                    "error": f"Format {format_type} not implemented",
                    "data": None
                }
            
            result = {
                "success": True,
                "data": df,
                "metadata": {
                    "file_path": str(path),
                    "format": format_type,
                    "shape": df.shape,
                    "columns": list(df.columns),
                    "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
                    "size_mb": path.stat().st_size / (1024 * 1024),
                    "loaded_at": datetime.now().isoformat()
                }
            }
            
            self.log_execution({"file_path": file_path, "format_type": format_type}, 
                             {"success": True, "shape": df.shape})
            return result
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": f"Failed to load data: {str(e)}",
                "data": None
            }
            self.log_execution({"file_path": file_path, "format_type": format_type}, error_result)
            return error_result

class DataProfilerTool(BaseTool):
    """Tool for generating comprehensive data profiles"""
    
    def __init__(self):
        super().__init__(
            name="data_profiler", 
            description="Generate comprehensive data quality and statistical profiles"
        )
    
    async def execute(self, data: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """Generate data profile"""
        try:
            profile = {
                "basic_info": self._get_basic_info(data),
                "data_quality": self._assess_data_quality(data),
                "statistical_summary": self._get_statistical_summary(data),
                "column_analysis": self._analyze_columns(data),
                "correlations": self._get_correlations(data),
                "generated_at": datetime.now().isoformat()
            }
            
            result = {
                "success": True,
                "profile": profile,
                "summary": self._generate_summary(profile)
            }
            
            self.log_execution({"data_shape": data.shape}, {"success": True})
            return result
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": f"Data profiling failed: {str(e)}",
                "profile": None
            }
            self.log_execution({"data_shape": data.shape}, error_result)
            return error_result
    
    def _get_basic_info(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get basic dataset information"""
        return {
            "total_rows": int(df.shape[0]),
            "total_columns": int(df.shape[1]),
            "column_names": list(df.columns),
            "data_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "memory_usage_mb": float(df.memory_usage(deep=True).sum() / (1024 * 1024))
        }
    
    def _assess_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Assess overall data quality"""
        total_cells = df.shape[0] * df.shape[1]
        missing_cells = df.isnull().sum().sum()
        
        return {
            "total_cells": int(total_cells),
            "missing_cells": int(missing_cells),
            "missing_percentage": float((missing_cells / total_cells) * 100),
            "duplicate_rows": int(df.duplicated().sum()),
            "columns_with_missing": {col: int(count) for col, count in df.isnull().sum().items() if count > 0},
            "completeness_score": float(((total_cells - missing_cells) / total_cells) * 100)
        }
    
    def _get_statistical_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get statistical summary for numeric columns"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) == 0:
            return {"message": "No numeric columns found"}
        
        stats = df[numeric_cols].describe()
        return {
            "numeric_columns": list(numeric_cols),
            "summary_statistics": {
                col: {
                    "count": float(stats.loc['count', col]),
                    "mean": float(stats.loc['mean', col]),
                    "std": float(stats.loc['std', col]),
                    "min": float(stats.loc['min', col]),
                    "25%": float(stats.loc['25%', col]),
                    "50%": float(stats.loc['50%', col]),
                    "75%": float(stats.loc['75%', col]),
                    "max": float(stats.loc['max', col])
                } for col in numeric_cols
            }
        }
    
    def _analyze_columns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze individual columns"""
        column_analysis = {}
        
        for col in df.columns:
            analysis = {
                "data_type": str(df[col].dtype),
                "missing_count": int(df[col].isnull().sum()),
                "missing_percentage": float((df[col].isnull().sum() / len(df)) * 100),
                "unique_count": int(df[col].nunique()),
                "unique_percentage": float((df[col].nunique() / len(df)) * 100)
            }
            
            # Add type-specific analysis
            if pd.api.types.is_numeric_dtype(df[col]):
                analysis.update({
                    "min_value": float(df[col].min()) if pd.notna(df[col].min()) else None,
                    "max_value": float(df[col].max()) if pd.notna(df[col].max()) else None,
                    "mean_value": float(df[col].mean()) if pd.notna(df[col].mean()) else None,
                    "zero_count": int((df[col] == 0).sum()),
                    "negative_count": int((df[col] < 0).sum()) if df[col].dtype in ['int64', 'float64'] else 0
                })
            elif pd.api.types.is_string_dtype(df[col]) or df[col].dtype == 'object':
                analysis.update({
                    "max_length": int(df[col].astype(str).str.len().max()) if not df[col].empty else 0,
                    "min_length": int(df[col].astype(str).str.len().min()) if not df[col].empty else 0,
                    "avg_length": float(df[col].astype(str).str.len().mean()) if not df[col].empty else 0,
                    "empty_strings": int((df[col] == '').sum())
                })
            
            column_analysis[col] = analysis
        
        return column_analysis
    
    def _get_correlations(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate correlations for numeric columns"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) < 2:
            return {"message": "Need at least 2 numeric columns for correlation analysis"}
        
        corr_matrix = df[numeric_cols].corr()
        
        # Find high correlations (> 0.7 or < -0.7)
        high_correlations = []
        for i in range(len(numeric_cols)):
            for j in range(i+1, len(numeric_cols)):
                corr_value = corr_matrix.iloc[i, j]
                if abs(corr_value) > 0.7:
                    high_correlations.append({
                        "column1": numeric_cols[i],
                        "column2": numeric_cols[j],
                        "correlation": float(corr_value)
                    })
        
        return {
            "correlation_matrix": {
                col1: {col2: float(corr_matrix.loc[col1, col2]) 
                       for col2 in numeric_cols}
                for col1 in numeric_cols
            },
            "high_correlations": high_correlations
        }
    
    def _generate_summary(self, profile: Dict[str, Any]) -> str:
        """Generate a human-readable summary"""
        basic = profile["basic_info"]
        quality = profile["data_quality"]
        
        summary = f"Dataset contains {basic['total_rows']} rows and {basic['total_columns']} columns. "
        summary += f"Data completeness: {quality['completeness_score']:.1f}%. "
        
        if quality["duplicate_rows"] > 0:
            summary += f"Found {quality['duplicate_rows']} duplicate rows. "
        
        if quality["missing_percentage"] > 10:
            summary += "High missing data detected - requires attention. "
        elif quality["missing_percentage"] > 5:
            summary += "Moderate missing data - monitor quality. "
        else:
            summary += "Good data quality overall. "
        
        return summary

class ValidationRulesTool(BaseTool):
    """Tool for defining and executing validation rules"""
    
    def __init__(self):
        super().__init__(
            name="validation_rules",
            description="Define and execute custom validation rules on datasets"
        )
        self.built_in_rules = {
            "completeness": self._check_completeness,
            "data_types": self._check_data_types,
            "value_ranges": self._check_value_ranges,
            "uniqueness": self._check_uniqueness,
            "patterns": self._check_patterns,
            "custom_logic": self._check_custom_logic
        }
    
    async def execute(self, data: pd.DataFrame, rules: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Execute validation rules on dataset"""
        try:
            validation_results = {
                "overall_valid": True,
                "validation_score": 0.0,
                "rules_executed": 0,
                "rules_passed": 0,
                "errors": [],
                "warnings": [],
                "rule_results": {},
                "executed_at": datetime.now().isoformat()
            }
            
            # Execute each rule
            for rule_name, rule_config in rules.items():
                if rule_name in self.built_in_rules:
                    rule_result = await self.built_in_rules[rule_name](data, rule_config)
                    validation_results["rule_results"][rule_name] = rule_result
                    validation_results["rules_executed"] += 1
                    
                    if rule_result["passed"]:
                        validation_results["rules_passed"] += 1
                    else:
                        validation_results["overall_valid"] = False
                        validation_results["errors"].extend(rule_result.get("errors", []))
                    
                    validation_results["warnings"].extend(rule_result.get("warnings", []))
                else:
                    validation_results["warnings"].append(f"Unknown rule: {rule_name}")
            
            # Calculate overall score
            if validation_results["rules_executed"] > 0:
                validation_results["validation_score"] = (
                    validation_results["rules_passed"] / validation_results["rules_executed"]
                )
            
            result = {
                "success": True,
                "validation_results": validation_results
            }
            
            self.log_execution({"rules_count": len(rules)}, {"success": True, "overall_valid": validation_results["overall_valid"]})
            return result
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": f"Validation failed: {str(e)}",
                "validation_results": None
            }
            self.log_execution({"rules_count": len(rules)}, error_result)
            return error_result
    
    async def _check_completeness(self, df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """Check data completeness"""
        max_missing_pct = config.get("max_missing_percentage", 5.0)
        errors = []
        warnings = []
        
        for col in df.columns:
            missing_pct = (df[col].isnull().sum() / len(df)) * 100
            if missing_pct > max_missing_pct:
                errors.append(f"Column '{col}' has {missing_pct:.1f}% missing values (threshold: {max_missing_pct}%)")
            elif missing_pct > max_missing_pct * 0.5:  # Warning at 50% of threshold
                warnings.append(f"Column '{col}' has {missing_pct:.1f}% missing values (approaching threshold)")
        
        return {
            "passed": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "details": {
                "threshold": max_missing_pct,
                "columns_checked": len(df.columns)
            }
        }
    
    async def _check_data_types(self, df: pd.DataFrame, config: Dict[str, str]) -> Dict[str, Any]:
        """Check data types match expectations"""
        expected_types = config.get("expected_types", {})
        errors = []
        warnings = []
        
        for col, expected_type in expected_types.items():
            if col in df.columns:
                actual_type = str(df[col].dtype)
                if actual_type != expected_type:
                    errors.append(f"Column '{col}' has type '{actual_type}', expected '{expected_type}'")
            else:
                warnings.append(f"Expected column '{col}' not found in dataset")
        
        return {
            "passed": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "details": {
                "expected_types": expected_types,
                "columns_checked": len(expected_types)
            }
        }
    
    async def _check_value_ranges(self, df: pd.DataFrame, config: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """Check value ranges"""
        value_ranges = config.get("value_ranges", {})
        errors = []
        warnings = []
        
        for col, range_config in value_ranges.items():
            if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
                col_min = df[col].min()
                col_max = df[col].max()
                expected_min = range_config.get("min")
                expected_max = range_config.get("max")
                
                if expected_min is not None and col_min < expected_min:
                    errors.append(f"Column '{col}' minimum value {col_min} below expected {expected_min}")
                
                if expected_max is not None and col_max > expected_max:
                    errors.append(f"Column '{col}' maximum value {col_max} above expected {expected_max}")
            elif col not in df.columns:
                warnings.append(f"Range check column '{col}' not found in dataset")
            else:
                warnings.append(f"Column '{col}' is not numeric, skipping range check")
        
        return {
            "passed": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "details": {
                "ranges_checked": len(value_ranges)
            }
        }
    
    async def _check_uniqueness(self, df: pd.DataFrame, config: List[str]) -> Dict[str, Any]:
        """Check uniqueness constraints"""
        unique_columns = config.get("unique_columns", [])
        errors = []
        warnings = []
        
        for col in unique_columns:
            if col in df.columns:
                duplicates = df[col].duplicated().sum()
                if duplicates > 0:
                    errors.append(f"Column '{col}' has {duplicates} duplicate values")
            else:
                warnings.append(f"Uniqueness check column '{col}' not found in dataset")
        
        return {
            "passed": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "details": {
                "unique_columns": unique_columns
            }
        }
    
    async def _check_patterns(self, df: pd.DataFrame, config: Dict[str, str]) -> Dict[str, Any]:
        """Check regex patterns"""
        patterns = config.get("patterns", {})
        errors = []
        warnings = []
        
        for col, pattern in patterns.items():
            if col in df.columns:
                try:
                    matches = df[col].astype(str).str.match(pattern, na=False)
                    non_matches = (~matches).sum()
                    if non_matches > 0:
                        errors.append(f"Column '{col}' has {non_matches} values not matching pattern '{pattern}'")
                except Exception as e:
                    warnings.append(f"Pattern check failed for column '{col}': {str(e)}")
            else:
                warnings.append(f"Pattern check column '{col}' not found in dataset")
        
        return {
            "passed": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "details": {
                "patterns_checked": len(patterns)
            }
        }
    
    async def _check_custom_logic(self, df: pd.DataFrame, config: List[Dict[str, str]]) -> Dict[str, Any]:
        """Execute custom validation logic"""
        custom_rules = config.get("custom_rules", [])
        errors = []
        warnings = []
        
        for rule in custom_rules:
            rule_name = rule.get("name", "Unknown Rule")
            condition = rule.get("condition", "")
            
            try:
                # Evaluate condition (be careful with eval in production!)
                result = eval(condition, {"df": df, "pd": pd, "np": np})
                violations = (~result).sum() if hasattr(result, 'sum') else (not result)
                
                if violations > 0:
                    errors.append(f"Custom rule '{rule_name}' failed: {violations} violations")
            except Exception as e:
                warnings.append(f"Custom rule '{rule_name}' execution failed: {str(e)}")
        
        return {
            "passed": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "details": {
                "custom_rules_count": len(custom_rules)
            }
        }

class ReportGeneratorTool(BaseTool):
    """Tool for generating validation reports"""
    
    def __init__(self):
        super().__init__(
            name="report_generator",
            description="Generate comprehensive validation and data quality reports"
        )
    
    async def execute(self, validation_results: Dict[str, Any], data_profile: Dict[str, Any] = None, 
                     format_type: str = "json", **kwargs) -> Dict[str, Any]:
        """Generate validation report"""
        try:
            report = {
                "report_metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "report_version": "1.0",
                    "format": format_type
                },
                "executive_summary": self._generate_executive_summary(validation_results, data_profile),
                "validation_results": validation_results,
                "recommendations": self._generate_recommendations(validation_results, data_profile)
            }
            
            if data_profile:
                report["data_profile"] = data_profile
            
            # Format report based on requested format
            if format_type == "json":
                formatted_report = json.dumps(report, indent=2, default=str)
            elif format_type == "markdown":
                formatted_report = self._generate_markdown_report(report)
            else:
                formatted_report = str(report)
            
            result = {
                "success": True,
                "report": report,
                "formatted_report": formatted_report,
                "format": format_type
            }
            
            self.log_execution({"format": format_type}, {"success": True})
            return result
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": f"Report generation failed: {str(e)}",
                "report": None
            }
            self.log_execution({"format": format_type}, error_result)
            return error_result
    
    def _generate_executive_summary(self, validation_results: Dict[str, Any], 
                                  data_profile: Dict[str, Any] = None) -> str:
        """Generate executive summary"""
        summary = []
        
        if validation_results:
            overall_valid = validation_results.get("overall_valid", False)
            score = validation_results.get("validation_score", 0.0) * 100
            
            summary.append(f"Dataset validation {'PASSED' if overall_valid else 'FAILED'} with {score:.1f}% score.")
            
            errors_count = len(validation_results.get("errors", []))
            warnings_count = len(validation_results.get("warnings", []))
            
            if errors_count > 0:
                summary.append(f"Found {errors_count} critical issues that require attention.")
            
            if warnings_count > 0:
                summary.append(f"Found {warnings_count} warnings to review.")
        
        if data_profile and "data_quality" in data_profile:
            quality = data_profile["data_quality"]
            completeness = quality.get("completeness_score", 0)
            summary.append(f"Data completeness: {completeness:.1f}%.")
        
        return " ".join(summary) if summary else "No validation results available."
    
    def _generate_recommendations(self, validation_results: Dict[str, Any], 
                                data_profile: Dict[str, Any] = None) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if validation_results:
            errors = validation_results.get("errors", [])
            warnings = validation_results.get("warnings", [])
            
            if errors:
                recommendations.append("🔴 Critical: Address all validation errors before proceeding")
                
                # Specific recommendations based on error types
                for error in errors:
                    if "missing values" in error.lower():
                        recommendations.append("💡 Consider data imputation or removal strategies for missing values")
                    elif "data type" in error.lower() or "type" in error.lower():
                        recommendations.append("💡 Review and correct data type mismatches")
                    elif "duplicate" in error.lower():
                        recommendations.append("💡 Investigate and resolve duplicate data entries")
                    elif "range" in error.lower() or "value" in error.lower():
                        recommendations.append("💡 Validate data collection process for out-of-range values")
            
            if warnings:
                recommendations.append("⚠️ Review warnings and consider addressing them for better data quality")
        
        if data_profile and "data_quality" in data_profile:
            quality = data_profile["data_quality"]
            
            if quality.get("missing_percentage", 0) > 10:
                recommendations.append("📊 High missing data detected - implement data collection improvements")
            
            if quality.get("duplicate_rows", 0) > 0:
                recommendations.append("🔄 Remove duplicate rows to improve data integrity")
        
        if not recommendations:
            recommendations.append("✅ Data quality appears good - continue with analysis")
        
        return recommendations
    
    def _generate_markdown_report(self, report: Dict[str, Any]) -> str:
        """Generate markdown formatted report"""
        md = []
        md.append("# Dataset Validation Report")
        md.append("")
        md.append(f"**Generated:** {report['report_metadata']['generated_at']}")
        md.append("")
        
        md.append("## Executive Summary")
        md.append(report['executive_summary'])
        md.append("")
        
        if 'validation_results' in report:
            vr = report['validation_results']
            md.append("## Validation Results")
            md.append(f"- **Overall Status:** {'✅ VALID' if vr.get('overall_valid') else '❌ INVALID'}")
            md.append(f"- **Validation Score:** {vr.get('validation_score', 0) * 100:.1f}%")
            md.append(f"- **Rules Executed:** {vr.get('rules_executed', 0)}")
            md.append(f"- **Rules Passed:** {vr.get('rules_passed', 0)}")
            md.append("")
            
            if vr.get('errors'):
                md.append("### Errors")
                for error in vr['errors']:
                    md.append(f"- ❌ {error}")
                md.append("")
            
            if vr.get('warnings'):
                md.append("### Warnings")
                for warning in vr['warnings']:
                    md.append(f"- ⚠️ {warning}")
                md.append("")
        
        if 'recommendations' in report:
            md.append("## Recommendations")
            for rec in report['recommendations']:
                md.append(f"- {rec}")
            md.append("")
        
        return "\n".join(md)

# Tool Registry
class ToolRegistry:
    """Registry for managing all available tools"""
    
    def __init__(self):
        self.tools = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register all default tools"""
        self.register_tool(DataLoaderTool())
        self.register_tool(DataProfilerTool())
        self.register_tool(ValidationRulesTool())
        self.register_tool(ReportGeneratorTool())
    
    def register_tool(self, tool: BaseTool):
        """Register a new tool"""
        self.tools[tool.name] = tool
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name"""
        return self.tools.get(name)
    
    def list_tools(self) -> Dict[str, str]:
        """List all available tools"""
        return {name: tool.description for name, tool in self.tools.items()}
    
    async def execute_tool(self, tool_name: str, *args, **kwargs) -> Dict[str, Any]:
        """Execute a tool by name"""
        tool = self.get_tool(tool_name)
        if not tool:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found. Available tools: {list(self.tools.keys())}"
            }
        
        return await tool.execute(*args, **kwargs)

class MissingValueAnalyzerTool(BaseTool):
    """Tool for comprehensive missing value analysis and scoring"""
    
    def __init__(self):
        super().__init__(
            name="missing_value_analyzer",
            description="Analyze missing values and calculate data integrity scores"
        )
    
    async def execute(self, data: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """Analyze missing values in dataset"""
        try:
            # Basic missing value statistics
            total_cells = data.shape[0] * data.shape[1]
            missing_counts = data.isnull().sum()
            missing_percentages = (missing_counts / len(data)) * 100
            total_missing = missing_counts.sum()
            overall_missing_pct = (total_missing / total_cells) * 100
            
            # Column-level analysis
            column_analysis = {}
            for col in data.columns:
                missing_count = int(missing_counts[col])
                missing_pct = float(missing_percentages[col])
                
                # Assign severity level
                if missing_pct == 0:
                    severity = "none"
                    impact = "no_impact"
                elif missing_pct <= 1:
                    severity = "minimal"
                    impact = "low"
                elif missing_pct <= 5:
                    severity = "low"
                    impact = "moderate"
                elif missing_pct <= 20:
                    severity = "moderate"
                    impact = "high"
                else:
                    severity = "high"
                    impact = "critical"
                
                column_analysis[col] = {
                    "missing_count": missing_count,
                    "missing_percentage": missing_pct,
                    "severity": severity,
                    "impact": impact,
                    "total_values": len(data),
                    "valid_values": len(data) - missing_count
                }
            
            # Calculate integrity score (0-100)
            # Score decreases exponentially with missing data percentage
            if overall_missing_pct == 0:
                integrity_score = 100.0
            elif overall_missing_pct <= 1:
                integrity_score = 95.0
            elif overall_missing_pct <= 5:
                integrity_score = 85.0 - (overall_missing_pct - 1) * 2
            elif overall_missing_pct <= 20:
                integrity_score = 77.0 - (overall_missing_pct - 5) * 3
            else:
                integrity_score = max(20.0, 32.0 - (overall_missing_pct - 20) * 0.6)
            
            # Pattern analysis
            patterns = self._analyze_missing_patterns(data)
            
            # Recommendations
            recommendations = self._generate_missing_value_recommendations(column_analysis, overall_missing_pct)
            
            result = {
                "success": True,
                "analysis": {
                    "overall_stats": {
                        "total_cells": int(total_cells),
                        "total_missing": int(total_missing),
                        "missing_percentage": round(overall_missing_pct, 2),
                        "integrity_score": round(integrity_score, 1),
                        "columns_affected": len([col for col in column_analysis.values() if col["missing_count"] > 0])
                    },
                    "column_analysis": column_analysis,
                    "missing_patterns": patterns,
                    "recommendations": recommendations,
                    "score_breakdown": {
                        "excellent": "0% missing (Score: 100)",
                        "very_good": "≤1% missing (Score: 95+)",
                        "good": "≤5% missing (Score: 85+)",
                        "fair": "≤20% missing (Score: 32+)",
                        "poor": ">20% missing (Score: <32)"
                    }
                }
            }
            
            self.log_execution({"data_shape": data.shape}, 
                             {"success": True, "integrity_score": integrity_score})
            return result
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": f"Missing value analysis failed: {str(e)}",
                "analysis": None
            }
            self.log_execution({"data_shape": data.shape}, error_result)
            return error_result
    
    def _analyze_missing_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze patterns in missing data"""
        patterns = {
            "completely_missing_columns": [],
            "mostly_complete_columns": [],
            "problematic_columns": [],
            "missing_combinations": []
        }
        
        for col in df.columns:
            missing_pct = (df[col].isnull().sum() / len(df)) * 100
            
            if missing_pct == 100:
                patterns["completely_missing_columns"].append(col)
            elif missing_pct >= 50:
                patterns["problematic_columns"].append({
                    "column": col,
                    "missing_percentage": round(missing_pct, 1)
                })
            elif missing_pct <= 5:
                patterns["mostly_complete_columns"].append({
                    "column": col,
                    "missing_percentage": round(missing_pct, 1)
                })
        
        # Check for rows with multiple missing values
        row_missing_counts = df.isnull().sum(axis=1)
        high_missing_rows = (row_missing_counts > df.shape[1] * 0.5).sum()
        
        patterns["high_missing_rows"] = {
            "count": int(high_missing_rows),
            "percentage": round((high_missing_rows / len(df)) * 100, 2)
        }
        
        return patterns
    
    def _generate_missing_value_recommendations(self, column_analysis: Dict, overall_pct: float) -> List[str]:
        """Generate actionable recommendations for missing values"""
        recommendations = []
        
        if overall_pct == 0:
            recommendations.append("✅ Excellent data completeness - no missing values detected")
        elif overall_pct <= 1:
            recommendations.append("✅ Very good data quality with minimal missing values")
        elif overall_pct <= 5:
            recommendations.append("⚠️ Good data quality but monitor missing value trends")
        elif overall_pct <= 20:
            recommendations.append("🔶 Moderate missing data - consider imputation strategies")
        else:
            recommendations.append("🔴 High missing data requires immediate attention")
        
        # Column-specific recommendations
        critical_columns = [col for col, analysis in column_analysis.items() 
                          if analysis["impact"] == "critical"]
        if critical_columns:
            recommendations.append(f"🚨 Critical: Columns {critical_columns} have >20% missing values")
            recommendations.append("💡 Consider: data collection review, column removal, or advanced imputation")
        
        high_impact_columns = [col for col, analysis in column_analysis.items() 
                             if analysis["impact"] == "high"]
        if high_impact_columns:
            recommendations.append(f"⚠️ Moderate: Columns {high_impact_columns} need attention")
            recommendations.append("💡 Consider: mean/median imputation, forward/backward fill, or domain expertise")
        
        return recommendations

class DuplicateRecordDetectorTool(BaseTool):
    """Tool for detecting and analyzing duplicate records"""
    
    def __init__(self):
        super().__init__(
            name="duplicate_record_detector",
            description="Detect duplicate records and calculate data integrity impact"
        )
    
    async def execute(self, data: pd.DataFrame, subset_columns: List[str] = None, **kwargs) -> Dict[str, Any]:
        """Detect and analyze duplicate records"""
        try:
            total_rows = len(data)
            
            # Full row duplicates
            full_duplicates = data.duplicated()
            full_duplicate_count = full_duplicates.sum()
            full_duplicate_pct = (full_duplicate_count / total_rows) * 100
            
            # Subset duplicates (if specified)
            subset_analysis = {}
            if subset_columns:
                valid_columns = [col for col in subset_columns if col in data.columns]
                if valid_columns:
                    subset_duplicates = data.duplicated(subset=valid_columns)
                    subset_duplicate_count = subset_duplicates.sum()
                    subset_duplicate_pct = (subset_duplicate_count / total_rows) * 100
                    
                    subset_analysis = {
                        "columns_checked": valid_columns,
                        "duplicate_count": int(subset_duplicate_count),
                        "duplicate_percentage": round(subset_duplicate_pct, 2),
                        "unique_combinations": int(data[valid_columns].drop_duplicates().shape[0])
                    }
            
            # Calculate integrity score based on duplication
            # Score decreases as duplication increases
            if full_duplicate_pct == 0:
                integrity_score = 100.0
            elif full_duplicate_pct <= 1:
                integrity_score = 95.0 - full_duplicate_pct * 2
            elif full_duplicate_pct <= 5:
                integrity_score = 90.0 - full_duplicate_pct * 3
            elif full_duplicate_pct <= 20:
                integrity_score = 75.0 - (full_duplicate_pct - 5) * 2
            else:
                integrity_score = max(10.0, 45.0 - (full_duplicate_pct - 20) * 1.5)
            
            # Identify duplicate groups
            duplicate_groups = self._analyze_duplicate_groups(data)
            
            # Generate recommendations
            recommendations = self._generate_duplicate_recommendations(
                full_duplicate_pct, full_duplicate_count, subset_analysis
            )
            
            result = {
                "success": True,
                "analysis": {
                    "overall_stats": {
                        "total_rows": total_rows,
                        "unique_rows": total_rows - full_duplicate_count,
                        "duplicate_rows": int(full_duplicate_count),
                        "duplication_percentage": round(full_duplicate_pct, 2),
                        "integrity_score": round(integrity_score, 1)
                    },
                    "full_row_analysis": {
                        "duplicate_count": int(full_duplicate_count),
                        "duplicate_percentage": round(full_duplicate_pct, 2),
                        "first_occurrences": total_rows - full_duplicate_count,
                        "data_reduction_potential": f"{full_duplicate_count} rows ({full_duplicate_pct:.1f}%)"
                    },
                    "subset_analysis": subset_analysis,
                    "duplicate_groups": duplicate_groups,
                    "recommendations": recommendations,
                    "score_breakdown": {
                        "excellent": "0% duplicates (Score: 100)",
                        "very_good": "≤1% duplicates (Score: 93+)",
                        "good": "≤5% duplicates (Score: 75+)",
                        "fair": "≤20% duplicates (Score: 15+)",
                        "poor": ">20% duplicates (Score: <15)"
                    }
                }
            }
            
            self.log_execution({"data_shape": data.shape}, 
                             {"success": True, "duplicate_percentage": full_duplicate_pct})
            return result
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": f"Duplicate detection failed: {str(e)}",
                "analysis": None
            }
            self.log_execution({"data_shape": data.shape}, error_result)
            return error_result
    
    def _analyze_duplicate_groups(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze groups of duplicate records"""
        # Find rows that appear more than once
        value_counts = df.value_counts()
        duplicated_groups = value_counts[value_counts > 1]
        
        groups_info = {
            "total_duplicate_groups": len(duplicated_groups),
            "largest_group_size": int(duplicated_groups.max()) if len(duplicated_groups) > 0 else 0,
            "average_group_size": round(duplicated_groups.mean(), 1) if len(duplicated_groups) > 0 else 0,
            "groups_by_size": {}
        }
        
        if len(duplicated_groups) > 0:
            # Group by frequency
            for size in sorted(duplicated_groups.unique()):
                count = (duplicated_groups == size).sum()
                groups_info["groups_by_size"][f"{size}_duplicates"] = int(count)
        
        return groups_info
    
    def _generate_duplicate_recommendations(self, duplicate_pct: float, 
                                          duplicate_count: int, subset_analysis: Dict) -> List[str]:
        """Generate recommendations for handling duplicates"""
        recommendations = []
        
        if duplicate_pct == 0:
            recommendations.append("✅ Excellent - no duplicate records found")
        elif duplicate_pct <= 1:
            recommendations.append("✅ Very good data quality with minimal duplication")
            recommendations.append("💡 Consider: Review duplicates to ensure they're not legitimate repeated events")
        elif duplicate_pct <= 5:
            recommendations.append("⚠️ Low duplication detected - investigate data collection process")
            recommendations.append("💡 Consider: Automated deduplication with manual review")
        elif duplicate_pct <= 20:
            recommendations.append("🔶 Moderate duplication suggests data collection issues")
            recommendations.append("💡 Consider: Implementing unique constraints, reviewing ETL processes")
        else:
            recommendations.append("🔴 High duplication indicates serious data quality problems")
            recommendations.append("💡 Urgent: Review data sources, implement deduplication pipeline")
        
        if duplicate_count > 0:
            recommendations.append(f"📊 Potential storage savings: {duplicate_count} rows can be removed")
        
        if subset_analysis and subset_analysis.get("duplicate_percentage", 0) > duplicate_pct:
            recommendations.append("🔍 Partial duplicates detected - may indicate related records or data entry errors")
        
        return recommendations

class DataTypeConsistencyCheckerTool(BaseTool):
    """Tool for checking data type consistency and integrity"""
    
    def __init__(self):
        super().__init__(
            name="data_type_consistency_checker",
            description="Check data type consistency and identify type-related quality issues"
        )
    
    async def execute(self, data: pd.DataFrame, expected_schema: Dict[str, str] = None, **kwargs) -> Dict[str, Any]:
        """Check data type consistency"""
        try:
            column_analysis = {}
            type_issues = []
            consistency_score = 100.0
            
            for col in data.columns:
                series = data[col]
                analysis = {
                    "current_dtype": str(series.dtype),
                    "non_null_count": int(series.count()),
                    "null_count": int(series.isnull().sum()),
                    "unique_count": int(series.nunique()),
                    "consistency_issues": []
                }
                
                # Analyze type consistency issues
                issues = self._check_column_type_issues(series, col)
                analysis["consistency_issues"] = issues
                
                # Check against expected schema if provided
                if expected_schema and col in expected_schema:
                    expected_type = expected_schema[col]
                    current_type = str(series.dtype)
                    
                    analysis["expected_dtype"] = expected_type
                    analysis["schema_match"] = current_type == expected_type
                    
                    if not analysis["schema_match"]:
                        type_issues.append({
                            "column": col,
                            "expected": expected_type,
                            "actual": current_type,
                            "severity": "high"
                        })
                        consistency_score -= 10  # Penalize schema mismatches heavily
                
                # Penalize based on consistency issues
                if issues:
                    penalty = min(15, len(issues) * 3)  # Cap penalty per column
                    consistency_score -= penalty
                
                column_analysis[col] = analysis
            
            # Ensure score doesn't go below 0
            consistency_score = max(0.0, consistency_score)
            
            # Generate type recommendations
            type_recommendations = self._generate_type_recommendations(column_analysis, type_issues)
            
            # Overall assessment
            if consistency_score >= 95:
                quality_level = "excellent"
            elif consistency_score >= 80:
                quality_level = "good"
            elif consistency_score >= 60:
                quality_level = "fair"
            else:
                quality_level = "poor"
            
            result = {
                "success": True,
                "analysis": {
                    "overall_stats": {
                        "total_columns": len(data.columns),
                        "columns_with_issues": len([col for col, analysis in column_analysis.items() 
                                                  if analysis["consistency_issues"]]),
                        "schema_mismatches": len(type_issues),
                        "consistency_score": round(consistency_score, 1),
                        "quality_level": quality_level
                    },
                    "column_analysis": column_analysis,
                    "schema_issues": type_issues,
                    "recommendations": type_recommendations,
                    "type_summary": self._generate_type_summary(data),
                    "score_breakdown": {
                        "excellent": "95-100: All types consistent",
                        "good": "80-94: Minor type issues",
                        "fair": "60-79: Some type problems",
                        "poor": "<60: Major type inconsistencies"
                    }
                }
            }
            
            self.log_execution({"data_shape": data.shape}, 
                             {"success": True, "consistency_score": consistency_score})
            return result
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": f"Data type consistency check failed: {str(e)}",
                "analysis": None
            }
            self.log_execution({"data_shape": data.shape}, error_result)
            return error_result
    
    def _check_column_type_issues(self, series: pd.Series, col_name: str) -> List[Dict[str, Any]]:
        """Check for type consistency issues in a column"""
        issues = []
        
        # Skip if all values are null
        if series.isnull().all():
            issues.append({
                "issue": "all_null",
                "description": "Column contains only null values",
                "severity": "high",
                "count": len(series)
            })
            return issues
        
        # Check for mixed types in object columns
        if series.dtype == 'object':
            non_null_series = series.dropna()
            if len(non_null_series) > 0:
                # Check for mixed numeric and string
                numeric_count = 0
                string_count = 0
                other_count = 0
                
                for value in non_null_series.head(min(1000, len(non_null_series))):  # Sample for performance
                    try:
                        float(value)
                        numeric_count += 1
                    except (ValueError, TypeError):
                        if isinstance(value, str):
                            string_count += 1
                        else:
                            other_count += 1
                
                total_sampled = numeric_count + string_count + other_count
                if total_sampled > 0:
                    if numeric_count > 0 and string_count > 0:
                        issues.append({
                            "issue": "mixed_numeric_string",
                            "description": f"Column contains both numeric ({numeric_count}) and string ({string_count}) values",
                            "severity": "medium",
                            "numeric_percentage": round((numeric_count / total_sampled) * 100, 1),
                            "string_percentage": round((string_count / total_sampled) * 100, 1)
                        })
                    
                    if other_count > 0:
                        issues.append({
                            "issue": "unexpected_types",
                            "description": f"Column contains {other_count} values of unexpected types",
                            "severity": "medium",
                            "count": other_count
                        })
        
        # Check for potential numeric columns stored as strings
        elif series.dtype == 'object':
            non_null_series = series.dropna()
            if len(non_null_series) > 0:
                # Check if most values can be converted to numbers
                convertible_count = 0
                for value in non_null_series.head(min(100, len(non_null_series))):
                    try:
                        float(str(value).replace(',', '').replace('$', '').replace('%', ''))
                        convertible_count += 1
                    except (ValueError, TypeError):
                        pass
                
                if convertible_count / min(100, len(non_null_series)) > 0.8:
                    issues.append({
                        "issue": "numeric_stored_as_string",
                        "description": "Column appears to contain numeric data stored as strings",
                        "severity": "medium",
                        "convertible_percentage": round((convertible_count / min(100, len(non_null_series))) * 100, 1)
                    })
        
        # Check for outliers in numeric columns that might indicate type issues
        elif pd.api.types.is_numeric_dtype(series):
            non_null_series = series.dropna()
            if len(non_null_series) > 0:
                # Check for extreme outliers (might be data entry errors)
                Q1 = non_null_series.quantile(0.25)
                Q3 = non_null_series.quantile(0.75)
                IQR = Q3 - Q1
                
                if IQR > 0:  # Avoid division by zero
                    lower_bound = Q1 - 3 * IQR
                    upper_bound = Q3 + 3 * IQR
                    
                    outliers = non_null_series[(non_null_series < lower_bound) | (non_null_series > upper_bound)]
                    if len(outliers) > 0:
                        outlier_pct = (len(outliers) / len(non_null_series)) * 100
                        if outlier_pct > 5:  # Only flag if >5% are outliers
                            issues.append({
                                "issue": "extreme_outliers",
                                "description": f"Column has {len(outliers)} extreme outliers ({outlier_pct:.1f}%)",
                                "severity": "low",
                                "outlier_count": len(outliers),
                                "outlier_percentage": round(outlier_pct, 1)
                            })
        
        return issues
    
    def _generate_type_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate summary of data types in the dataset"""
        type_counts = df.dtypes.value_counts()
        
        summary = {
            "type_distribution": {str(dtype): int(count) for dtype, count in type_counts.items()},
            "column_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "inferred_improvements": []
        }
        
        # Suggest type improvements
        for col in df.columns:
            series = df[col]
            if series.dtype == 'object' and not series.isnull().all():
                # Check if it could be converted to a more specific type
                non_null_series = series.dropna()
                if len(non_null_series) > 0:
                    # Try datetime conversion
                    try:
                        pd.to_datetime(non_null_series.head(10))
                        summary["inferred_improvements"].append({
                            "column": col,
                            "current_type": "object",
                            "suggested_type": "datetime",
                            "confidence": "medium"
                        })
                        continue
                    except:
                        pass
                    
                    # Try numeric conversion
                    try:
                        pd.to_numeric(non_null_series.head(10))
                        summary["inferred_improvements"].append({
                            "column": col,
                            "current_type": "object",
                            "suggested_type": "numeric",
                            "confidence": "high"
                        })
                    except:
                        pass
        
        return summary
    
    def _generate_type_recommendations(self, column_analysis: Dict, type_issues: List) -> List[str]:
        """Generate recommendations for type consistency improvements"""
        recommendations = []
        
        total_issues = sum(len(analysis["consistency_issues"]) for analysis in column_analysis.values())
        
        if total_issues == 0 and len(type_issues) == 0:
            recommendations.append("✅ Excellent type consistency - no issues detected")
        else:
            if type_issues:
                recommendations.append(f"🔴 Schema Mismatches: {len(type_issues)} columns don't match expected types")
                recommendations.append("💡 Consider: Type conversion or schema update")
            
            issue_columns = [col for col, analysis in column_analysis.items() 
                           if analysis["consistency_issues"]]
            
            if issue_columns:
                recommendations.append(f"⚠️ Type Issues: {len(issue_columns)} columns have consistency problems")
                
                # Specific recommendations based on issue types
                mixed_type_columns = []
                numeric_string_columns = []
                
                for col, analysis in column_analysis.items():
                    for issue in analysis["consistency_issues"]:
                        if issue["issue"] == "mixed_numeric_string":
                            mixed_type_columns.append(col)
                        elif issue["issue"] == "numeric_stored_as_string":
                            numeric_string_columns.append(col)
                
                if mixed_type_columns:
                    recommendations.append(f"🔧 Mixed Types: Clean data in columns {mixed_type_columns}")
                
                if numeric_string_columns:
                    recommendations.append(f"🔄 Type Conversion: Convert {numeric_string_columns} to numeric")
        
        return recommendations

class OutlierDetectionEngineTool(BaseTool):
    """Tool for detecting outliers using multiple statistical methods"""
    
    def __init__(self):
        super().__init__(
            name="outlier_detection_engine",
            description="Detect outliers using Z-score, IQR, and Isolation Forest methods"
        )
    
    async def execute(self, data: pd.DataFrame, methods: List[str] = None, 
                     sensitivity: str = "medium", **kwargs) -> Dict[str, Any]:
        """Detect outliers using multiple methods"""
        try:
            if methods is None:
                methods = ["zscore", "iqr", "isolation_forest"]
            
            # Set sensitivity thresholds
            sensitivity_config = {
                "low": {"zscore_threshold": 3.5, "iqr_multiplier": 2.0},
                "medium": {"zscore_threshold": 3.0, "iqr_multiplier": 1.5},
                "high": {"zscore_threshold": 2.5, "iqr_multiplier": 1.0}
            }
            
            config = sensitivity_config.get(sensitivity, sensitivity_config["medium"])
            
            # Get numeric columns only
            numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
            if not numeric_cols:
                return {
                    "success": False,
                    "error": "No numeric columns found for outlier detection",
                    "analysis": None
                }
            
            # Analyze outliers for each numeric column
            column_analysis = {}
            overall_outliers = set()
            method_results = {}
            
            for col in numeric_cols:
                series = data[col].dropna()
                if len(series) == 0:
                    continue
                
                col_outliers = {}
                col_outlier_indices = set()
                
                # Z-Score method
                if "zscore" in methods:
                    z_scores = np.abs((series - series.mean()) / series.std())
                    zscore_outliers = series.index[z_scores > config["zscore_threshold"]].tolist()
                    col_outliers["zscore"] = {
                        "count": len(zscore_outliers),
                        "percentage": round((len(zscore_outliers) / len(series)) * 100, 2),
                        "indices": zscore_outliers
                    }
                    col_outlier_indices.update(zscore_outliers)
                
                # IQR method
                if "iqr" in methods:
                    Q1 = series.quantile(0.25)
                    Q3 = series.quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - config["iqr_multiplier"] * IQR
                    upper_bound = Q3 + config["iqr_multiplier"] * IQR
                    
                    iqr_outliers = series.index[(series < lower_bound) | (series > upper_bound)].tolist()
                    col_outliers["iqr"] = {
                        "count": len(iqr_outliers),
                        "percentage": round((len(iqr_outliers) / len(series)) * 100, 2),
                        "indices": iqr_outliers,
                        "bounds": {"lower": float(lower_bound), "upper": float(upper_bound)}
                    }
                    col_outlier_indices.update(iqr_outliers)
                
                # Isolation Forest method
                if "isolation_forest" in methods and len(series) > 10:
                    try:
                        from sklearn.ensemble import IsolationForest
                        
                        iso_forest = IsolationForest(contamination=0.05, random_state=42)
                        outlier_labels = iso_forest.fit_predict(series.values.reshape(-1, 1))
                        isolation_outliers = series.index[outlier_labels == -1].tolist()
                        
                        col_outliers["isolation_forest"] = {
                            "count": len(isolation_outliers),
                            "percentage": round((len(isolation_outliers) / len(series)) * 100, 2),
                            "indices": isolation_outliers
                        }
                        col_outlier_indices.update(isolation_outliers)
                    except ImportError:
                        col_outliers["isolation_forest"] = {
                            "error": "sklearn not available - install scikit-learn for Isolation Forest"
                        }
                
                # Consensus outliers (detected by multiple methods)
                method_counts = {}
                for method, result in col_outliers.items():
                    if "indices" in result:
                        for idx in result["indices"]:
                            method_counts[idx] = method_counts.get(idx, 0) + 1
                
                consensus_outliers = [idx for idx, count in method_counts.items() if count >= 2]
                
                column_analysis[col] = {
                    "method_results": col_outliers,
                    "consensus_outliers": {
                        "count": len(consensus_outliers),
                        "percentage": round((len(consensus_outliers) / len(series)) * 100, 2),
                        "indices": consensus_outliers
                    },
                    "total_unique_outliers": len(col_outlier_indices),
                    "outlier_percentage": round((len(col_outlier_indices) / len(series)) * 100, 2)
                }
                
                overall_outliers.update(col_outlier_indices)
            
            # Calculate overall outlier statistics
            total_data_points = len(data) * len(numeric_cols)
            overall_outlier_pct = (len(overall_outliers) / len(data)) * 100 if len(data) > 0 else 0
            
            # Calculate quality score based on outlier percentage
            # Score decreases as outlier percentage increases
            if overall_outlier_pct <= 1:
                quality_score = 100.0
            elif overall_outlier_pct <= 3:
                quality_score = 95.0 - (overall_outlier_pct - 1) * 2.5
            elif overall_outlier_pct <= 5:
                quality_score = 90.0 - (overall_outlier_pct - 3) * 5
            elif overall_outlier_pct <= 10:
                quality_score = 80.0 - (overall_outlier_pct - 5) * 3
            elif overall_outlier_pct <= 20:
                quality_score = 65.0 - (overall_outlier_pct - 10) * 2
            else:
                quality_score = max(25.0, 45.0 - (overall_outlier_pct - 20) * 1)
            
            # Generate recommendations
            recommendations = self._generate_outlier_recommendations(overall_outlier_pct, column_analysis)
            
            result = {
                "success": True,
                "analysis": {
                    "overall_stats": {
                        "total_numeric_columns": len(numeric_cols),
                        "total_data_points": len(data),
                        "outlier_rows": len(overall_outliers),
                        "outlier_percentage": round(overall_outlier_pct, 2),
                        "quality_score": round(quality_score, 1),
                        "sensitivity_level": sensitivity,
                        "methods_used": methods
                    },
                    "column_analysis": column_analysis,
                    "recommendations": recommendations,
                    "score_breakdown": {
                        "excellent": "≤1% outliers (Score: 100)",
                        "very_good": "≤3% outliers (Score: 90+)",
                        "good": "≤5% outliers (Score: 80+)",
                        "fair": "≤10% outliers (Score: 65+)",
                        "poor": ">20% outliers (Score: <45)"
                    }
                }
            }
            
            self.log_execution({"data_shape": data.shape, "methods": methods}, 
                             {"success": True, "outlier_percentage": overall_outlier_pct})
            return result
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": f"Outlier detection failed: {str(e)}",
                "analysis": None
            }
            self.log_execution({"data_shape": data.shape}, error_result)
            return error_result
    
    def _generate_outlier_recommendations(self, outlier_pct: float, column_analysis: Dict) -> List[str]:
        """Generate recommendations for handling outliers"""
        recommendations = []
        
        if outlier_pct <= 1:
            recommendations.append("✅ Excellent - very few outliers detected")
        elif outlier_pct <= 3:
            recommendations.append("✅ Good data quality with minimal outliers")
            recommendations.append("💡 Consider: Review outliers to ensure they're not data entry errors")
        elif outlier_pct <= 5:
            recommendations.append("⚠️ Moderate outliers detected - investigate patterns")
            recommendations.append("💡 Consider: Statistical methods for outlier treatment (winsorizing, capping)")
        elif outlier_pct <= 10:
            recommendations.append("🔶 High outlier count suggests data quality issues")
            recommendations.append("💡 Consider: Domain expert review, robust statistical methods")
        else:
            recommendations.append("🔴 Very high outlier percentage indicates serious data issues")
            recommendations.append("💡 Urgent: Review data collection process, consider data filtering")
        
        # Column-specific recommendations
        problematic_columns = [col for col, analysis in column_analysis.items() 
                             if analysis["outlier_percentage"] > 10]
        if problematic_columns:
            recommendations.append(f"🎯 Focus on columns: {problematic_columns[:3]}{'...' if len(problematic_columns) > 3 else ''}")
        
        # Method consensus recommendations
        consensus_columns = [col for col, analysis in column_analysis.items() 
                           if analysis["consensus_outliers"]["count"] > 0]
        if consensus_columns:
            recommendations.append(f"🔍 High-confidence outliers found in: {consensus_columns[:3]}{'...' if len(consensus_columns) > 3 else ''}")
        
        return recommendations

class ClassBalanceAssessorTool(BaseTool):
    """Tool for analyzing class balance in classification datasets"""
    
    def __init__(self):
        super().__init__(
            name="class_balance_assessor",
            description="Analyze class distribution and balance for classification tasks"
        )
    
    async def execute(self, data: pd.DataFrame, target_column: str = None, 
                     task_type: str = "auto", **kwargs) -> Dict[str, Any]:
        """Analyze class balance in the dataset"""
        try:
            # Auto-detect target column if not provided
            if target_column is None:
                # Look for common target column names
                common_targets = ['target', 'label', 'class', 'y', 'outcome', 'prediction']
                for col in common_targets:
                    if col in data.columns:
                        target_column = col
                        break
                
                if target_column is None:
                    # Use the last column as target
                    target_column = data.columns[-1]
            
            if target_column not in data.columns:
                return {
                    "success": False,
                    "error": f"Target column '{target_column}' not found in dataset",
                    "analysis": None
                }
            
            target_series = data[target_column].dropna()
            if len(target_series) == 0:
                return {
                    "success": False,
                    "error": f"Target column '{target_column}' contains no valid values",
                    "analysis": None
                }
            
            # Auto-detect task type if not specified
            unique_values = target_series.nunique()
            if task_type == "auto":
                if unique_values == 2:
                    task_type = "binary_classification"
                elif unique_values <= 20 and not pd.api.types.is_numeric_dtype(target_series):
                    task_type = "multiclass_classification"
                elif unique_values <= 20 and pd.api.types.is_numeric_dtype(target_series):
                    task_type = "multiclass_classification"
                else:
                    task_type = "regression"
            
            # Analyze class distribution
            class_counts = target_series.value_counts()
            class_percentages = target_series.value_counts(normalize=True) * 100
            
            # Calculate balance metrics
            balance_analysis = self._analyze_class_balance(class_counts, class_percentages, task_type)
            
            # Calculate balance score
            balance_score = self._calculate_balance_score(balance_analysis, task_type)
            
            # Generate recommendations
            recommendations = self._generate_balance_recommendations(balance_analysis, task_type)
            
            result = {
                "success": True,
                "analysis": {
                    "target_info": {
                        "column_name": target_column,
                        "task_type": task_type,
                        "total_samples": len(target_series),
                        "unique_classes": unique_values,
                        "missing_values": int(data[target_column].isnull().sum())
                    },
                    "class_distribution": {
                        "counts": {str(k): int(v) for k, v in class_counts.items()},
                        "percentages": {str(k): round(float(v), 2) for k, v in class_percentages.items()}
                    },
                    "balance_metrics": balance_analysis,
                    "balance_score": round(balance_score, 1),
                    "recommendations": recommendations,
                    "score_breakdown": self._get_score_breakdown(task_type)
                }
            }
            
            self.log_execution({"target_column": target_column, "task_type": task_type}, 
                             {"success": True, "balance_score": balance_score})
            return result
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": f"Class balance analysis failed: {str(e)}",
                "analysis": None
            }
            self.log_execution({"target_column": target_column}, error_result)
            return error_result
    
    def _analyze_class_balance(self, class_counts: pd.Series, class_percentages: pd.Series, 
                              task_type: str) -> Dict[str, Any]:
        """Analyze class balance metrics"""
        analysis = {
            "majority_class": {
                "label": str(class_counts.index[0]),
                "count": int(class_counts.iloc[0]),
                "percentage": round(float(class_percentages.iloc[0]), 2)
            },
            "minority_class": {
                "label": str(class_counts.index[-1]),
                "count": int(class_counts.iloc[-1]),
                "percentage": round(float(class_percentages.iloc[-1]), 2)
            }
        }
        
        if task_type in ["binary_classification", "multiclass_classification"]:
            # Calculate imbalance ratio
            imbalance_ratio = class_counts.iloc[0] / class_counts.iloc[-1]
            analysis["imbalance_ratio"] = round(float(imbalance_ratio), 2)
            
            # Gini impurity (measure of class mixing)
            gini = 1 - sum((class_percentages / 100) ** 2)
            analysis["gini_impurity"] = round(float(gini), 3)
            
            # Entropy (information content)
            probs = class_percentages / 100
            entropy = -sum(probs * np.log2(probs + 1e-10))  # Add small value to avoid log(0)
            analysis["entropy"] = round(float(entropy), 3)
            
            # Balance assessment
            min_pct = class_percentages.min()
            max_pct = class_percentages.max()
            
            if task_type == "binary_classification":
                if min_pct >= 40:
                    balance_level = "excellent"
                elif min_pct >= 30:
                    balance_level = "good"
                elif min_pct >= 20:
                    balance_level = "fair"
                elif min_pct >= 10:
                    balance_level = "imbalanced"
                else:
                    balance_level = "severely_imbalanced"
            else:  # multiclass
                if min_pct >= 15:
                    balance_level = "excellent"
                elif min_pct >= 10:
                    balance_level = "good"
                elif min_pct >= 5:
                    balance_level = "fair"
                elif min_pct >= 2:
                    balance_level = "imbalanced"
                else:
                    balance_level = "severely_imbalanced"
            
            analysis["balance_level"] = balance_level
        
        return analysis
    
    def _calculate_balance_score(self, balance_analysis: Dict, task_type: str) -> float:
        """Calculate balance score based on task type and distribution"""
        if task_type == "regression":
            # For regression, we focus on distribution shape
            return 85.0  # Neutral score since balance is less critical
        
        balance_level = balance_analysis.get("balance_level", "unknown")
        minority_pct = balance_analysis["minority_class"]["percentage"]
        imbalance_ratio = balance_analysis.get("imbalance_ratio", 1)
        
        if task_type == "binary_classification":
            if balance_level == "excellent":
                score = 100.0
            elif balance_level == "good":
                score = 90.0 - (40 - minority_pct) * 1.5
            elif balance_level == "fair":
                score = 75.0 - (30 - minority_pct) * 2
            elif balance_level == "imbalanced":
                score = 60.0 - (20 - minority_pct) * 2.5
            else:  # severely_imbalanced
                score = max(20.0, 35.0 - (10 - minority_pct) * 1.5)
        else:  # multiclass
            if balance_level == "excellent":
                score = 95.0
            elif balance_level == "good":
                score = 85.0 - (15 - minority_pct) * 2
            elif balance_level == "fair":
                score = 70.0 - (10 - minority_pct) * 2.5
            elif balance_level == "imbalanced":
                score = 55.0 - (5 - minority_pct) * 3
            else:  # severely_imbalanced
                score = max(15.0, 25.0 - (2 - minority_pct) * 5)
        
        return max(0.0, score)
    
    def _generate_balance_recommendations(self, balance_analysis: Dict, task_type: str) -> List[str]:
        """Generate recommendations for handling class imbalance"""
        recommendations = []
        
        if task_type == "regression":
            recommendations.append("📊 Regression task - class balance less critical")
            recommendations.append("💡 Consider: Distribution analysis, outlier detection")
            return recommendations
        
        balance_level = balance_analysis.get("balance_level", "unknown")
        minority_pct = balance_analysis["minority_class"]["percentage"]
        imbalance_ratio = balance_analysis.get("imbalance_ratio", 1)
        
        if balance_level == "excellent":
            recommendations.append("✅ Excellent class balance - proceed with standard algorithms")
        elif balance_level == "good":
            recommendations.append("✅ Good class balance - minor adjustments may help")
            recommendations.append("💡 Consider: Stratified sampling, balanced accuracy metrics")
        elif balance_level == "fair":
            recommendations.append("⚠️ Moderate imbalance - implement balancing strategies")
            recommendations.append("💡 Consider: SMOTE, class weights, threshold tuning")
        elif balance_level == "imbalanced":
            recommendations.append("🔶 Significant imbalance detected")
            recommendations.append("💡 Consider: Advanced sampling (ADASYN), ensemble methods")
            recommendations.append("📊 Use: Precision, Recall, F1-score instead of accuracy")
        else:  # severely_imbalanced
            recommendations.append("🔴 Severe class imbalance requires careful handling")
            recommendations.append("💡 Consider: Anomaly detection approaches, cost-sensitive learning")
            recommendations.append("⚠️ Warning: Standard accuracy metrics will be misleading")
        
        if imbalance_ratio > 10:
            recommendations.append(f"📈 Imbalance ratio: {imbalance_ratio:.1f}:1 - consider data collection review")
        
        return recommendations
    
    def _get_score_breakdown(self, task_type: str) -> Dict[str, str]:
        """Get score breakdown explanation"""
        if task_type == "binary_classification":
            return {
                "excellent": "40-50% minority class (Score: 100)",
                "good": "30-39% minority class (Score: 85-95)",
                "fair": "20-29% minority class (Score: 55-85)",
                "imbalanced": "10-19% minority class (Score: 35-75)",
                "severe": "<10% minority class (Score: <35)"
            }
        else:  # multiclass
            return {
                "excellent": "≥15% smallest class (Score: 95)",
                "good": "10-14% smallest class (Score: 75-95)",
                "fair": "5-9% smallest class (Score: 45-85)",
                "imbalanced": "2-4% smallest class (Score: 25-70)",
                "severe": "<2% smallest class (Score: <25)"
            }

class FeatureCorrelationMapperTool(BaseTool):
    """Tool for analyzing feature correlations and multicollinearity"""
    
    def __init__(self):
        super().__init__(
            name="feature_correlation_mapper",
            description="Analyze feature correlations and detect multicollinearity issues"
        )
    
    async def execute(self, data: pd.DataFrame, correlation_threshold: float = 0.8, 
                     method: str = "pearson", **kwargs) -> Dict[str, Any]:
        """Analyze feature correlations"""
        try:
            # Get numeric columns for correlation analysis
            numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
            if len(numeric_cols) < 2:
                return {
                    "success": False,
                    "error": "Need at least 2 numeric columns for correlation analysis",
                    "analysis": None
                }
            
            # Calculate correlation matrix
            numeric_data = data[numeric_cols].dropna()
            if len(numeric_data) == 0:
                return {
                    "success": False,
                    "error": "No valid data remaining after removing missing values",
                    "analysis": None
                }
            
            corr_matrix = numeric_data.corr(method=method)
            
            # Analyze correlation patterns
            correlation_analysis = self._analyze_correlations(corr_matrix, correlation_threshold)
            
            # Calculate multicollinearity score
            multicollinearity_score = self._calculate_multicollinearity_score(correlation_analysis)
            
            # Generate recommendations
            recommendations = self._generate_correlation_recommendations(correlation_analysis)
            
            result = {
                "success": True,
                "analysis": {
                    "matrix_info": {
                        "features_analyzed": len(numeric_cols),
                        "correlation_method": method,
                        "threshold_used": correlation_threshold,
                        "matrix_shape": corr_matrix.shape
                    },
                    "correlation_matrix": {
                        col1: {col2: round(float(corr_matrix.loc[col1, col2]), 3) 
                               for col2 in numeric_cols}
                        for col1 in numeric_cols
                    },
                    "correlation_summary": correlation_analysis,
                    "multicollinearity_score": round(multicollinearity_score, 1),
                    "recommendations": recommendations,
                    "score_breakdown": {
                        "excellent": "No high correlations (Score: 95-100)",
                        "good": "Few high correlations (Score: 80-94)",
                        "fair": "Some multicollinearity (Score: 60-79)",
                        "poor": "High multicollinearity (Score: <60)"
                    }
                }
            }
            
            self.log_execution({"features_count": len(numeric_cols), "method": method}, 
                             {"success": True, "multicollinearity_score": multicollinearity_score})
            return result
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": f"Correlation analysis failed: {str(e)}",
                "analysis": None
            }
            self.log_execution({"method": method}, error_result)
            return error_result
    
    def _analyze_correlations(self, corr_matrix: pd.DataFrame, threshold: float) -> Dict[str, Any]:
        """Analyze correlation patterns and identify issues"""
        n_features = len(corr_matrix)
        
        # Find high correlations (excluding diagonal)
        high_correlations = []
        correlation_counts = {"very_high": 0, "high": 0, "moderate": 0}
        
        for i in range(n_features):
            for j in range(i + 1, n_features):
                corr_value = corr_matrix.iloc[i, j]
                col1, col2 = corr_matrix.index[i], corr_matrix.index[j]
                
                abs_corr = abs(corr_value)
                
                if abs_corr >= threshold:
                    severity = "very_high" if abs_corr >= 0.95 else "high"
                    correlation_counts[severity] += 1
                    
                    high_correlations.append({
                        "feature1": col1,
                        "feature2": col2,
                        "correlation": round(float(corr_value), 3),
                        "abs_correlation": round(abs_corr, 3),
                        "severity": severity
                    })
                elif abs_corr >= 0.6:
                    correlation_counts["moderate"] += 1
        
        # Sort by absolute correlation (highest first)
        high_correlations.sort(key=lambda x: x["abs_correlation"], reverse=True)
        
        # Identify feature groups with high internal correlations
        feature_groups = self._identify_correlation_clusters(corr_matrix, threshold)
        
        # Calculate correlation statistics
        corr_values = []
        for i in range(n_features):
            for j in range(i + 1, n_features):
                corr_values.append(abs(corr_matrix.iloc[i, j]))
        
        corr_stats = {
            "mean_abs_correlation": round(np.mean(corr_values), 3),
            "max_abs_correlation": round(np.max(corr_values), 3),
            "correlations_above_threshold": len(high_correlations),
            "total_feature_pairs": len(corr_values)
        }
        
        return {
            "high_correlations": high_correlations[:10],  # Top 10 for brevity
            "correlation_counts": correlation_counts,
            "correlation_statistics": corr_stats,
            "feature_groups": feature_groups,
            "multicollinearity_risk": self._assess_multicollinearity_risk(correlation_counts, n_features)
        }
    
    def _identify_correlation_clusters(self, corr_matrix: pd.DataFrame, threshold: float) -> List[Dict]:
        """Identify clusters of highly correlated features"""
        clusters = []
        visited = set()
        
        for i, feature in enumerate(corr_matrix.index):
            if feature in visited:
                continue
            
            # Find all features highly correlated with this one
            cluster = [feature]
            correlated_features = []
            
            for j, other_feature in enumerate(corr_matrix.index):
                if i != j and abs(corr_matrix.iloc[i, j]) >= threshold:
                    correlated_features.append({
                        "feature": other_feature,
                        "correlation": round(float(corr_matrix.iloc[i, j]), 3)
                    })
                    cluster.append(other_feature)
            
            if len(cluster) > 1:  # Only include clusters with multiple features
                clusters.append({
                    "primary_feature": feature,
                    "cluster_size": len(cluster),
                    "features": cluster,
                    "correlations": correlated_features
                })
                visited.update(cluster)
        
        return clusters
    
    def _assess_multicollinearity_risk(self, correlation_counts: Dict, n_features: int) -> str:
        """Assess overall multicollinearity risk"""
        very_high = correlation_counts["very_high"]
        high = correlation_counts["high"]
        
        # Calculate risk based on proportion of high correlations
        total_pairs = (n_features * (n_features - 1)) // 2
        high_corr_ratio = (very_high + high) / total_pairs if total_pairs > 0 else 0
        
        if very_high > 0 or high_corr_ratio > 0.3:
            return "high"
        elif high > 0 or high_corr_ratio > 0.1:
            return "medium"
        else:
            return "low"
    
    def _calculate_multicollinearity_score(self, correlation_analysis: Dict) -> float:
        """Calculate multicollinearity quality score"""
        risk = correlation_analysis["multicollinearity_risk"]
        high_correlations = len(correlation_analysis["high_correlations"])
        very_high_count = correlation_analysis["correlation_counts"]["very_high"]
        high_count = correlation_analysis["correlation_counts"]["high"]
        
        # Start with perfect score
        score = 100.0
        
        # Penalize based on risk level
        if risk == "high":
            score -= 25
        elif risk == "medium":
            score -= 15
        
        # Additional penalties for specific correlation counts
        score -= very_high_count * 10  # 10 points per very high correlation
        score -= high_count * 5       # 5 points per high correlation
        
        # Bonus for low multicollinearity
        if risk == "low" and high_correlations == 0:
            score = 100.0
        
        return max(0.0, score)
    
    def _generate_correlation_recommendations(self, correlation_analysis: Dict) -> List[str]:
        """Generate recommendations for handling correlations"""
        recommendations = []
        
        risk = correlation_analysis["multicollinearity_risk"]
        high_correlations = correlation_analysis["high_correlations"]
        feature_groups = correlation_analysis["feature_groups"]
        
        if risk == "low" and len(high_correlations) == 0:
            recommendations.append("✅ Excellent - no significant multicollinearity detected")
            recommendations.append("💡 Features are appropriately independent for most ML algorithms")
        elif risk == "low":
            recommendations.append("✅ Good correlation structure with minimal multicollinearity")
            recommendations.append("💡 Consider monitoring correlation trends as data grows")
        elif risk == "medium":
            recommendations.append("⚠️ Moderate multicollinearity detected")
            recommendations.append("💡 Consider: PCA, Ridge regression, or feature selection")
            
            if high_correlations:
                top_pairs = high_correlations[:3]
                pair_names = [f"{pair['feature1']}-{pair['feature2']}" for pair in top_pairs]
                recommendations.append(f"🎯 Focus on: {', '.join(pair_names)}")
        else:  # high risk
            recommendations.append("🔴 High multicollinearity requires immediate attention")
            recommendations.append("💡 Consider: Dimensionality reduction, regularization, feature removal")
            recommendations.append("⚠️ Warning: May cause unstable model coefficients")
        
        # Feature group recommendations
        if feature_groups:
            large_groups = [group for group in feature_groups if group["cluster_size"] > 2]
            if large_groups:
                group_names = [group["primary_feature"] for group in large_groups[:2]]
                recommendations.append(f"🔗 Large correlation clusters found: {', '.join(group_names)}")
                recommendations.append("💡 Consider: Keep one representative feature per cluster")
        
        return recommendations

class BaselineModelPerformanceTool(BaseTool):
    """Tool for measuring dataset quality through baseline ML model performance"""
    
    def __init__(self):
        super().__init__(
            name="baseline_model_performance",
            description="Train baseline ML models to assess dataset quality and predictive power"
        )
    
    async def execute(self, data: pd.DataFrame, target_column: str = None, 
                     test_size: float = 0.2, random_state: int = 42, **kwargs) -> Dict[str, Any]:
        """Train baseline models and assess performance"""
        try:
            # Auto-detect target column if not provided
            if target_column is None:
                common_targets = ['target', 'label', 'class', 'y', 'outcome', 'prediction']
                for col in common_targets:
                    if col in data.columns:
                        target_column = col
                        break
                
                if target_column is None:
                    target_column = data.columns[-1]
            
            if target_column not in data.columns:
                return {
                    "success": False,
                    "error": f"Target column '{target_column}' not found in dataset",
                    "analysis": None
                }
            
            # Prepare features and target
            features = data.drop(columns=[target_column])
            target = data[target_column]
            
            # Remove non-numeric columns for baseline models
            numeric_features = features.select_dtypes(include=[np.number])
            if len(numeric_features.columns) == 0:
                return {
                    "success": False,
                    "error": "No numeric features found for ML modeling",
                    "analysis": None
                }
            
            # Handle missing values (simple imputation)
            from sklearn.impute import SimpleImputer
            imputer = SimpleImputer(strategy='mean')
            X_imputed = pd.DataFrame(
                imputer.fit_transform(numeric_features),
                columns=numeric_features.columns,
                index=numeric_features.index
            )
            
            # Remove rows with missing target values
            valid_indices = target.dropna().index
            X_clean = X_imputed.loc[valid_indices]
            y_clean = target.loc[valid_indices]
            
            if len(X_clean) < 10:
                return {
                    "success": False,
                    "error": "Insufficient clean data for ML modeling (need at least 10 samples)",
                    "analysis": None
                }
            
            # Determine task type and train appropriate models
            task_type = self._determine_task_type(y_clean)
            model_results = await self._train_baseline_models(X_clean, y_clean, task_type, test_size, random_state)
            
            # Calculate ML usability score
            ml_score = self._calculate_ml_usability_score(model_results, task_type)
            
            # Generate recommendations
            recommendations = self._generate_ml_recommendations(model_results, task_type, ml_score)
            
            result = {
                "success": True,
                "analysis": {
                    "dataset_info": {
                        "target_column": target_column,
                        "task_type": task_type,
                        "features_used": len(X_clean.columns),
                        "samples_used": len(X_clean),
                        "test_size": test_size
                    },
                    "model_performance": model_results,
                    "ml_usability_score": round(ml_score, 1),
                    "recommendations": recommendations,
                    "score_breakdown": self._get_ml_score_breakdown(task_type)
                }
            }
            
            self.log_execution({"target_column": target_column, "task_type": task_type}, 
                             {"success": True, "ml_score": ml_score})
            return result
            
        except ImportError as e:
            return {
                "success": False,
                "error": f"Required ML library not available: {str(e)}. Install scikit-learn for ML functionality.",
                "analysis": None
            }
        except Exception as e:
            error_result = {
                "success": False,
                "error": f"ML performance analysis failed: {str(e)}",
                "analysis": None
            }
            self.log_execution({"target_column": target_column}, error_result)
            return error_result
    
    def _determine_task_type(self, target: pd.Series) -> str:
        """Determine if this is classification or regression"""
        unique_values = target.nunique()
        
        if unique_values <= 10 and not pd.api.types.is_numeric_dtype(target):
            return "classification"
        elif unique_values <= 10 and pd.api.types.is_numeric_dtype(target):
            return "classification"
        else:
            return "regression"
    
    async def _train_baseline_models(self, X, y, task_type: str, test_size: float, random_state: int) -> Dict:
        """Train baseline models appropriate for the task"""
        from sklearn.model_selection import train_test_split
        from sklearn.preprocessing import StandardScaler
        from sklearn.metrics import accuracy_score, f1_score, r2_score, mean_squared_error
        
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y if task_type == "classification" else None
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        results = {}
        
        if task_type == "classification":
            # Train classification models
            models = self._get_classification_models()
            
            for name, model in models.items():
                try:
                    model.fit(X_train_scaled, y_train)
                    y_pred = model.predict(X_test_scaled)
                    
                    accuracy = accuracy_score(y_test, y_pred)
                    f1 = f1_score(y_test, y_pred, average='weighted')
                    
                    results[name] = {
                        "accuracy": round(float(accuracy), 4),
                        "f1_score": round(float(f1), 4),
                        "primary_metric": accuracy,
                        "samples_train": len(X_train),
                        "samples_test": len(X_test)
                    }
                except Exception as e:
                    results[name] = {"error": str(e)}
        
        else:  # regression
            # Train regression models
            models = self._get_regression_models()
            
            for name, model in models.items():
                try:
                    model.fit(X_train_scaled, y_train)
                    y_pred = model.predict(X_test_scaled)
                    
                    r2 = r2_score(y_test, y_pred)
                    mse = mean_squared_error(y_test, y_pred)
                    
                    results[name] = {
                        "r2_score": round(float(r2), 4),
                        "mse": round(float(mse), 4),
                        "primary_metric": r2,
                        "samples_train": len(X_train),
                        "samples_test": len(X_test)
                    }
                except Exception as e:
                    results[name] = {"error": str(e)}
        
        return results
    
    def _get_classification_models(self):
        """Get baseline classification models"""
        from sklearn.linear_model import LogisticRegression
        from sklearn.tree import DecisionTreeClassifier
        from sklearn.dummy import DummyClassifier
        
        return {
            "logistic_regression": LogisticRegression(random_state=42, max_iter=1000),
            "decision_tree": DecisionTreeClassifier(random_state=42, max_depth=5),
            "dummy_classifier": DummyClassifier(strategy="most_frequent")
        }
    
    def _get_regression_models(self):
        """Get baseline regression models"""
        from sklearn.linear_model import LinearRegression
        from sklearn.tree import DecisionTreeRegressor
        from sklearn.dummy import DummyRegressor
        
        return {
            "linear_regression": LinearRegression(),
            "decision_tree": DecisionTreeRegressor(random_state=42, max_depth=5),
            "dummy_regressor": DummyRegressor(strategy="mean")
        }
    
    def _calculate_ml_usability_score(self, model_results: Dict, task_type: str) -> float:
        """Calculate ML usability score based on model performance"""
        if not model_results:
            return 0.0
        
        valid_results = {name: result for name, result in model_results.items() if "error" not in result}
        if not valid_results:
            return 0.0
        
        if task_type == "classification":
            # Use accuracy as primary metric
            best_accuracy = max(result["primary_metric"] for result in valid_results.values())
            dummy_accuracy = model_results.get("dummy_classifier", {}).get("primary_metric", 0)
            
            # Score based on accuracy and improvement over dummy
            if best_accuracy >= 0.9:
                base_score = 95
            elif best_accuracy >= 0.8:
                base_score = 85
            elif best_accuracy >= 0.7:
                base_score = 75
            elif best_accuracy >= 0.6:
                base_score = 65
            else:
                base_score = 40
            
            # Bonus for beating dummy classifier significantly
            if best_accuracy > dummy_accuracy + 0.1:
                base_score += 5
            
            return min(100.0, base_score)
        
        else:  # regression
            # Use R² as primary metric
            best_r2 = max(result["primary_metric"] for result in valid_results.values())
            
            # Score based on R² value
            if best_r2 >= 0.9:
                return 95.0
            elif best_r2 >= 0.8:
                return 85.0
            elif best_r2 >= 0.7:
                return 75.0
            elif best_r2 >= 0.5:
                return 65.0
            elif best_r2 >= 0.3:
                return 50.0
            elif best_r2 >= 0.1:
                return 35.0
            else:
                return max(0.0, 20.0 + best_r2 * 50)  # Some credit for positive R²
    
    def _generate_ml_recommendations(self, model_results: Dict, task_type: str, ml_score: float) -> List[str]:
        """Generate ML-focused recommendations"""
        recommendations = []
        
        if ml_score >= 85:
            recommendations.append("🎯 Excellent ML performance - dataset is highly predictive")
            recommendations.append("✅ Ready for advanced modeling techniques")
        elif ml_score >= 70:
            recommendations.append("✅ Good ML performance - dataset shows strong predictive power")
            recommendations.append("💡 Consider feature engineering for better results")
        elif ml_score >= 50:
            recommendations.append("⚠️ Moderate ML performance - dataset has some predictive value")
            recommendations.append("💡 Consider: Feature selection, data cleaning, more sophisticated models")
        else:
            recommendations.append("🔴 Poor ML performance - dataset shows limited predictive power")
            recommendations.append("💡 Consider: Data quality issues, feature relevance, problem formulation")
        
        # Model-specific recommendations
        valid_results = {name: result for name, result in model_results.items() if "error" not in result}
        if valid_results:
            best_model = max(valid_results.items(), key=lambda x: x[1]["primary_metric"])
            recommendations.append(f"🏆 Best baseline model: {best_model[0]} ({best_model[1]['primary_metric']:.3f})")
        
        # Task-specific advice
        if task_type == "classification":
            dummy_result = model_results.get("dummy_classifier", {})
            if "primary_metric" in dummy_result:
                dummy_acc = dummy_result["primary_metric"]
                if dummy_acc > 0.7:
                    recommendations.append("⚠️ High dummy classifier accuracy suggests class imbalance")
        
        return recommendations
    
    def _get_ml_score_breakdown(self, task_type: str) -> Dict[str, str]:
        """Get score breakdown explanation"""
        if task_type == "classification":
            return {
                "excellent": "≥90% accuracy (Score: 95-100)",
                "very_good": "80-89% accuracy (Score: 85-94)",
                "good": "70-79% accuracy (Score: 75-84)",
                "fair": "60-69% accuracy (Score: 65-74)",
                "poor": "<60% accuracy (Score: <65)"
            }
        else:  # regression
            return {
                "excellent": "R² ≥ 0.9 (Score: 95)",
                "very_good": "R² 0.8-0.89 (Score: 85)",
                "good": "R² 0.7-0.79 (Score: 75)",
                "fair": "R² 0.5-0.69 (Score: 65)",
                "poor": "R² < 0.5 (Score: <65)"
            }

class FeatureImportanceAnalyzerTool(BaseTool):
    """Tool for analyzing feature importance and information distribution"""
    
    def __init__(self):
        super().__init__(
            name="feature_importance_analyzer",
            description="Analyze feature importance using tree-based models and assess information distribution"
        )
    
    async def execute(self, data: pd.DataFrame, target_column: str = None, 
                     importance_threshold: float = 0.01, **kwargs) -> Dict[str, Any]:
        """Analyze feature importance and information distribution"""
        try:
            # Auto-detect target column if not provided
            if target_column is None:
                common_targets = ['target', 'label', 'class', 'y', 'outcome', 'prediction']
                for col in common_targets:
                    if col in data.columns:
                        target_column = col
                        break
                
                if target_column is None:
                    target_column = data.columns[-1]
            
            if target_column not in data.columns:
                return {
                    "success": False,
                    "error": f"Target column '{target_column}' not found in dataset",
                    "analysis": None
                }
            
            # Prepare features and target
            features = data.drop(columns=[target_column])
            target = data[target_column]
            
            # Get numeric features
            numeric_features = features.select_dtypes(include=[np.number])
            if len(numeric_features.columns) == 0:
                return {
                    "success": False,
                    "error": "No numeric features found for importance analysis",
                    "analysis": None
                }
            
            # Handle missing values
            from sklearn.impute import SimpleImputer
            imputer = SimpleImputer(strategy='mean')
            X_imputed = pd.DataFrame(
                imputer.fit_transform(numeric_features),
                columns=numeric_features.columns,
                index=numeric_features.index
            )
            
            # Remove rows with missing target values
            valid_indices = target.dropna().index
            X_clean = X_imputed.loc[valid_indices]
            y_clean = target.loc[valid_indices]
            
            if len(X_clean) < 10:
                return {
                    "success": False,
                    "error": "Insufficient clean data for importance analysis",
                    "analysis": None
                }
            
            # Determine task type and analyze importance
            task_type = self._determine_task_type(y_clean)
            importance_results = await self._analyze_feature_importance(X_clean, y_clean, task_type)
            
            # Calculate information distribution score
            info_score = self._calculate_information_score(importance_results, importance_threshold)
            
            # Generate recommendations
            recommendations = self._generate_importance_recommendations(importance_results, info_score)
            
            result = {
                "success": True,
                "analysis": {
                    "dataset_info": {
                        "target_column": target_column,
                        "task_type": task_type,
                        "features_analyzed": len(X_clean.columns),
                        "samples_used": len(X_clean),
                        "importance_threshold": importance_threshold
                    },
                    "feature_importance": importance_results,
                    "information_score": round(info_score, 1),
                    "recommendations": recommendations,
                    "score_breakdown": {
                        "excellent": "Many important features, good distribution (Score: 85-100)",
                        "good": "Several important features (Score: 70-84)",
                        "fair": "Few important features (Score: 50-69)",
                        "poor": "Single dominant feature or no importance (Score: <50)"
                    }
                }
            }
            
            self.log_execution({"target_column": target_column, "task_type": task_type}, 
                             {"success": True, "info_score": info_score})
            return result
            
        except ImportError as e:
            return {
                "success": False,
                "error": f"Required ML library not available: {str(e)}",
                "analysis": None
            }
        except Exception as e:
            error_result = {
                "success": False,
                "error": f"Feature importance analysis failed: {str(e)}",
                "analysis": None
            }
            self.log_execution({"target_column": target_column}, error_result)
            return error_result
    
    def _determine_task_type(self, target: pd.Series) -> str:
        """Determine if this is classification or regression"""
        unique_values = target.nunique()
        return "classification" if unique_values <= 10 else "regression"
    
    async def _analyze_feature_importance(self, X, y, task_type: str) -> Dict:
        """Analyze feature importance using tree-based models"""
        from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
        
        # Train appropriate model
        if task_type == "classification":
            model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
        else:
            model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
        
        model.fit(X, y)
        
        # Get feature importances
        importances = model.feature_importances_
        feature_names = X.columns
        
        # Create feature importance analysis
        feature_importance_data = []
        for i, (feature, importance) in enumerate(zip(feature_names, importances)):
            feature_importance_data.append({
                "feature": feature,
                "importance": round(float(importance), 4),
                "rank": i + 1
            })
        
        # Sort by importance (descending)
        feature_importance_data.sort(key=lambda x: x["importance"], reverse=True)
        
        # Update ranks
        for i, item in enumerate(feature_importance_data):
            item["rank"] = i + 1
        
        # Calculate statistics
        importances_array = np.array([item["importance"] for item in feature_importance_data])
        
        return {
            "feature_rankings": feature_importance_data,
            "importance_statistics": {
                "max_importance": round(float(np.max(importances_array)), 4),
                "min_importance": round(float(np.min(importances_array)), 4),
                "mean_importance": round(float(np.mean(importances_array)), 4),
                "std_importance": round(float(np.std(importances_array)), 4),
                "gini_coefficient": round(float(self._calculate_gini_coefficient(importances_array)), 4)
            },
            "information_distribution": self._analyze_information_distribution(importances_array)
        }
    
    def _calculate_gini_coefficient(self, importances: np.ndarray) -> float:
        """Calculate Gini coefficient for importance distribution"""
        sorted_importances = np.sort(importances)
        n = len(importances)
        index = np.arange(1, n + 1)
        return (2 * np.sum(index * sorted_importances)) / (n * np.sum(sorted_importances)) - (n + 1) / n
    
    def _analyze_information_distribution(self, importances: np.ndarray) -> Dict:
        """Analyze how information is distributed across features"""
        total_importance = np.sum(importances)
        
        # Calculate cumulative importance
        sorted_importances = np.sort(importances)[::-1]  # Descending order
        cumulative_importance = np.cumsum(sorted_importances)
        cumulative_pct = cumulative_importance / total_importance
        
        # Find key thresholds
        top_1_pct = cumulative_pct[0] if len(cumulative_pct) > 0 else 0
        top_3_pct = cumulative_pct[min(2, len(cumulative_pct) - 1)] if len(cumulative_pct) > 2 else cumulative_pct[-1]
        top_5_pct = cumulative_pct[min(4, len(cumulative_pct) - 1)] if len(cumulative_pct) > 4 else cumulative_pct[-1]
        
        # Count significant features
        significant_features = np.sum(importances > 0.01)
        useful_features = np.sum(importances > 0.05)
        
        return {
            "top_1_feature_contribution": round(float(top_1_pct), 3),
            "top_3_features_contribution": round(float(top_3_pct), 3),
            "top_5_features_contribution": round(float(top_5_pct), 3),
            "features_above_1pct": int(significant_features),
            "features_above_5pct": int(useful_features),
            "information_concentration": "high" if top_1_pct > 0.7 else "medium" if top_1_pct > 0.4 else "low"
        }
    
    def _calculate_information_score(self, importance_results: Dict, threshold: float) -> float:
        """Calculate information distribution quality score"""
        stats = importance_results["importance_statistics"]
        distribution = importance_results["information_distribution"]
        
        # Base score from information distribution
        top_1_contrib = distribution["top_1_feature_contribution"]
        significant_features = distribution["features_above_1pct"]
        useful_features = distribution["features_above_5pct"]
        
        # Start with distribution quality
        if top_1_contrib > 0.8:
            # Single feature dominance - poor
            base_score = 30
        elif top_1_contrib > 0.6:
            # High concentration - fair
            base_score = 50
        elif top_1_contrib > 0.4:
            # Moderate concentration - good
            base_score = 70
        else:
            # Well distributed - excellent
            base_score = 85
        
        # Bonus for multiple useful features
        if useful_features >= 5:
            base_score += 10
        elif useful_features >= 3:
            base_score += 5
        
        # Bonus for good spread
        if significant_features >= 10:
            base_score += 5
        elif significant_features >= 5:
            base_score += 3
        
        # Penalty for very low max importance (suggests weak signal)
        max_importance = stats["max_importance"]
        if max_importance < 0.1:
            base_score -= 20
        elif max_importance < 0.2:
            base_score -= 10
        
        return max(0.0, min(100.0, base_score))
    
    def _generate_importance_recommendations(self, importance_results: Dict, info_score: float) -> List[str]:
        """Generate feature importance recommendations"""
        recommendations = []
        
        distribution = importance_results["information_distribution"]
        stats = importance_results["importance_statistics"]
        
        # Overall assessment
        if info_score >= 80:
            recommendations.append("🎯 Excellent feature information distribution")
            recommendations.append("✅ Multiple informative features with good balance")
        elif info_score >= 65:
            recommendations.append("✅ Good feature importance distribution")
            recommendations.append("💡 Consider feature engineering to improve balance")
        elif info_score >= 45:
            recommendations.append("⚠️ Moderate feature importance distribution")
            recommendations.append("💡 Consider feature selection and engineering")
        else:
            recommendations.append("🔴 Poor feature importance distribution")
            recommendations.append("💡 Critical: Review feature relevance and data quality")
        
        # Specific recommendations
        top_1_contrib = distribution["top_1_feature_contribution"]
        if top_1_contrib > 0.7:
            recommendations.append(f"⚠️ Single feature dominates ({top_1_contrib:.1%}) - check for data leakage")
        
        useful_features = distribution["features_above_5pct"]
        if useful_features < 3:
            recommendations.append("📊 Few highly important features - consider feature engineering")
        
        if stats["max_importance"] < 0.1:
            recommendations.append("🔍 Low maximum importance suggests weak predictive signal")
        
        # Top features recommendation
        top_features = importance_results["feature_rankings"][:3]
        top_names = [f["feature"] for f in top_features]
        recommendations.append(f"🔝 Focus on top features: {', '.join(top_names)}")
        
        return recommendations

class DataSeparabilityScoreTool(BaseTool):
    """Tool for assessing class separability using dimensionality reduction"""
    
    def __init__(self):
        super().__init__(
            name="data_separability_scorer",
            description="Assess class separability using PCA and dimensionality reduction techniques"
        )
    
    async def execute(self, data: pd.DataFrame, target_column: str = None, 
                     n_components: int = 2, **kwargs) -> Dict[str, Any]:
        """Assess data separability for classification tasks"""
        try:
            # Auto-detect target column if not provided
            if target_column is None:
                common_targets = ['target', 'label', 'class', 'y', 'outcome', 'prediction']
                for col in common_targets:
                    if col in data.columns:
                        target_column = col
                        break
                
                if target_column is None:
                    target_column = data.columns[-1]
            
            if target_column not in data.columns:
                return {
                    "success": False,
                    "error": f"Target column '{target_column}' not found in dataset",
                    "analysis": None
                }
            
            # Prepare features and target
            features = data.drop(columns=[target_column])
            target = data[target_column]
            
            # Check if this is a classification task
            if target.nunique() > 20:
                return {
                    "success": False,
                    "error": "Separability analysis is only applicable to classification tasks (≤20 classes)",
                    "analysis": None
                }
            
            # Get numeric features
            numeric_features = features.select_dtypes(include=[np.number])
            if len(numeric_features.columns) < 2:
                return {
                    "success": False,
                    "error": "Need at least 2 numeric features for separability analysis",
                    "analysis": None
                }
            
            # Handle missing values
            from sklearn.impute import SimpleImputer
            imputer = SimpleImputer(strategy='mean')
            X_imputed = pd.DataFrame(
                imputer.fit_transform(numeric_features),
                columns=numeric_features.columns,
                index=numeric_features.index
            )
            
            # Remove rows with missing target values
            valid_indices = target.dropna().index
            X_clean = X_imputed.loc[valid_indices]
            y_clean = target.loc[valid_indices]
            
            if len(X_clean) < 20:
                return {
                    "success": False,
                    "error": "Insufficient clean data for separability analysis (need at least 20 samples)",
                    "analysis": None
                }
            
            # Perform separability analysis
            separability_results = await self._analyze_separability(X_clean, y_clean, n_components)
            
            # Calculate separability score
            separability_score = self._calculate_separability_score(separability_results)
            
            # Generate recommendations
            recommendations = self._generate_separability_recommendations(separability_results, separability_score)
            
            result = {
                "success": True,
                "analysis": {
                    "dataset_info": {
                        "target_column": target_column,
                        "n_classes": int(y_clean.nunique()),
                        "features_used": len(X_clean.columns),
                        "samples_used": len(X_clean),
                        "pca_components": n_components
                    },
                    "separability_metrics": separability_results,
                    "separability_score": round(separability_score, 1),
                    "recommendations": recommendations,
                    "score_breakdown": {
                        "excellent": "Classes well separated in low dimensions (Score: 85-100)",
                        "good": "Moderate class separation achievable (Score: 70-84)",
                        "fair": "Some separability with dimensionality reduction (Score: 50-69)",
                        "poor": "Classes heavily overlap, difficult to separate (Score: <50)"
                    }
                }
            }
            
            self.log_execution({"target_column": target_column, "n_classes": y_clean.nunique()}, 
                             {"success": True, "separability_score": separability_score})
            return result
            
        except ImportError as e:
            return {
                "success": False,
                "error": f"Required ML library not available: {str(e)}",
                "analysis": None
            }
        except Exception as e:
            error_result = {
                "success": False,
                "error": f"Separability analysis failed: {str(e)}",
                "analysis": None
            }
            self.log_execution({"target_column": target_column}, error_result)
            return error_result
    
    async def _analyze_separability(self, X, y, n_components: int) -> Dict:
        """Analyze class separability using multiple techniques"""
        from sklearn.decomposition import PCA
        from sklearn.preprocessing import StandardScaler
        from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
        from sklearn.metrics import silhouette_score
        
        # Standardize features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        results = {}
        
        # PCA Analysis
        pca = PCA(n_components=min(n_components, X.shape[1], len(X) - 1))
        X_pca = pca.fit_transform(X_scaled)
        
        results["pca_analysis"] = {
            "explained_variance_ratio": [round(float(x), 4) for x in pca.explained_variance_ratio_],
            "cumulative_variance": round(float(np.sum(pca.explained_variance_ratio_)), 4),
            "n_components_90": int(np.argmax(np.cumsum(pca.explained_variance_ratio_) >= 0.9) + 1),
            "n_components_95": int(np.argmax(np.cumsum(pca.explained_variance_ratio_) >= 0.95) + 1)
        }
        
        # Linear Discriminant Analysis (if applicable)
        try:
            n_classes = len(np.unique(y))
            lda_components = min(n_classes - 1, X.shape[1])
            if lda_components > 0:
                lda = LinearDiscriminantAnalysis(n_components=lda_components)
                X_lda = lda.fit_transform(X_scaled, y)
                
                results["lda_analysis"] = {
                    "explained_variance_ratio": [round(float(x), 4) for x in lda.explained_variance_ratio_],
                    "n_components": lda_components,
                    "separability_power": round(float(np.sum(lda.explained_variance_ratio_)), 4)
                }
        except Exception:
            results["lda_analysis"] = {"error": "LDA analysis failed"}
        
        # Silhouette Analysis
        try:
            # Use PCA components for silhouette analysis
            silhouette_avg = silhouette_score(X_pca, y)
            results["silhouette_analysis"] = {
                "silhouette_score": round(float(silhouette_avg), 4),
                "interpretation": self._interpret_silhouette_score(silhouette_avg)
            }
        except Exception:
            results["silhouette_analysis"] = {"error": "Silhouette analysis failed"}
        
        # Class-wise separation analysis
        results["class_separation"] = self._analyze_class_separation(X_pca, y)
        
        return results
    
    def _interpret_silhouette_score(self, score: float) -> str:
        """Interpret silhouette score"""
        if score > 0.7:
            return "excellent_separation"
        elif score > 0.5:
            return "good_separation"
        elif score > 0.3:
            return "fair_separation"
        elif score > 0.1:
            return "weak_separation"
        else:
            return "poor_separation"
    
    def _analyze_class_separation(self, X_reduced, y) -> Dict:
        """Analyze separation between classes"""
        from scipy.spatial.distance import cdist
        
        classes = np.unique(y)
        n_classes = len(classes)
        
        # Calculate class centroids
        centroids = {}
        for cls in classes:
            class_data = X_reduced[y == cls]
            centroids[str(cls)] = np.mean(class_data, axis=0)
        
        # Calculate inter-class distances
        centroid_matrix = np.array(list(centroids.values()))
        inter_class_distances = cdist(centroid_matrix, centroid_matrix)
        
        # Calculate intra-class scatter
        intra_class_scatter = {}
        for cls in classes:
            class_data = X_reduced[y == cls]
            if len(class_data) > 1:
                centroid = centroids[str(cls)]
                scatter = np.mean([np.linalg.norm(point - centroid) for point in class_data])
                intra_class_scatter[str(cls)] = round(float(scatter), 4)
        
        return {
            "n_classes": int(n_classes),
            "class_centroids": {k: [round(float(x), 4) for x in v] for k, v in centroids.items()},
            "mean_inter_class_distance": round(float(np.mean(inter_class_distances[inter_class_distances > 0])), 4),
            "min_inter_class_distance": round(float(np.min(inter_class_distances[inter_class_distances > 0])), 4),
            "mean_intra_class_scatter": round(float(np.mean(list(intra_class_scatter.values()))), 4),
            "separation_ratio": round(float(np.mean(inter_class_distances[inter_class_distances > 0]) / 
                                          (np.mean(list(intra_class_scatter.values())) + 1e-10)), 4)
        }
    
    def _calculate_separability_score(self, separability_results: Dict) -> float:
        """Calculate overall separability score"""
        score = 50.0  # Base score
        
        # PCA contribution
        pca = separability_results.get("pca_analysis", {})
        if "cumulative_variance" in pca:
            variance_score = pca["cumulative_variance"] * 30  # Up to 30 points
            score += variance_score
        
        # Silhouette contribution
        silhouette = separability_results.get("silhouette_analysis", {})
        if "silhouette_score" in silhouette:
            sil_score = silhouette["silhouette_score"]
            if sil_score > 0:
                sil_points = min(25, sil_score * 35)  # Up to 25 points
                score += sil_points
        
        # LDA contribution
        lda = separability_results.get("lda_analysis", {})
        if "separability_power" in lda:
            lda_points = lda["separability_power"] * 20  # Up to 20 points
            score += lda_points
        
        # Class separation contribution
        separation = separability_results.get("class_separation", {})
        if "separation_ratio" in separation:
            sep_ratio = separation["separation_ratio"]
            if sep_ratio > 1:
                sep_points = min(15, np.log(sep_ratio) * 5)  # Up to 15 points
                score += sep_points
        
        return max(0.0, min(100.0, score))
    
    def _generate_separability_recommendations(self, separability_results: Dict, separability_score: float) -> List[str]:
        """Generate separability-focused recommendations"""
        recommendations = []
        
        # Overall assessment
        if separability_score >= 85:
            recommendations.append("🎯 Excellent class separability - ideal for classification")
            recommendations.append("✅ Classes are well-separated in reduced dimensions")
        elif separability_score >= 70:
            recommendations.append("✅ Good class separability with some dimensionality reduction")
            recommendations.append("💡 Consider linear classifiers or SVM")
        elif separability_score >= 50:
            recommendations.append("⚠️ Moderate separability - may need advanced techniques")
            recommendations.append("💡 Consider: kernel methods, ensemble models, feature engineering")
        else:
            recommendations.append("🔴 Poor class separability - challenging classification task")
            recommendations.append("💡 Consider: feature engineering, anomaly detection, problem reformulation")
        
        # Silhouette-based recommendations
        silhouette = separability_results.get("silhouette_analysis", {})
        if "silhouette_score" in silhouette:
            sil_score = silhouette["silhouette_score"]
            if sil_score < 0.3:
                recommendations.append("📊 Low silhouette score suggests overlapping classes")
        
        # PCA-based recommendations
        pca = separability_results.get("pca_analysis", {})
        if "n_components_90" in pca:
            n_comp = pca["n_components_90"]
            if n_comp <= 3:
                recommendations.append(f"✨ Good: {n_comp} components capture 90% variance - efficient representation")
            elif n_comp > 10:
                recommendations.append("📈 High dimensionality needed for 90% variance - consider feature selection")
        
        # Class separation recommendations
        separation = separability_results.get("class_separation", {})
        if "separation_ratio" in separation:
            ratio = separation["separation_ratio"]
            if ratio < 1.5:
                recommendations.append("🔄 Classes are close together - consider data augmentation or feature engineering")
        
        return recommendations

class DatasetPersonaTaggerTool(BaseTool):
    """Tool for identifying dataset personas based on characteristics from foundational analysis tools"""
    
    def __init__(self):
        super().__init__(
            name="dataset_persona_tagger",
            description="Analyze dataset characteristics to identify optimal research domains and use cases"
        )
        self.persona_rules = self._define_persona_rules()
    
    async def execute(self, analysis_results: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Tag dataset with appropriate personas based on analysis results"""
        try:
            # Extract key characteristics from all foundational tools
            characteristics = self._extract_characteristics(analysis_results)
            
            # Apply persona tagging rules
            persona_tags = []
            tag_reasoning = {}
            
            for persona, rules in self.persona_rules.items():
                should_tag, confidence, reasons = self._evaluate_persona_rules(characteristics, rules)
                if should_tag:
                    persona_tags.append(persona)
                    tag_reasoning[persona] = {
                        "confidence": confidence,
                        "reasons": reasons
                    }
            
            # If no specific personas match, assign general purpose
            if not persona_tags:
                persona_tags.append("#GeneralPurposeML")
                tag_reasoning["#GeneralPurposeML"] = {
                    "confidence": 0.7,
                    "reasons": ["No specific use case patterns detected - suitable for general ML tasks"]
                }
            
            # Sort personas by confidence
            sorted_personas = sorted(tag_reasoning.items(), key=lambda x: x[1]["confidence"], reverse=True)
            
            result = {
                "success": True,
                "persona_tags": persona_tags,
                "primary_persona": sorted_personas[0][0] if sorted_personas else "#GeneralPurposeML",
                "tag_reasoning": tag_reasoning,
                "confidence_scores": {tag: info["confidence"] for tag, info in tag_reasoning.items()},
                "characteristics_used": characteristics,
                "analysis_summary": self._generate_persona_summary(persona_tags, sorted_personas)
            }
            
            self.log_execution({"personas_found": len(persona_tags)}, {"success": True})
            return result
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": f"Persona tagging failed: {str(e)}",
                "persona_tags": [],
                "primary_persona": "#Unknown"
            }
            self.log_execution({}, error_result)
            return error_result
    
    def _define_persona_rules(self) -> Dict[str, Dict]:
        """Define heuristic rules for persona identification"""
        return {
            "#AnomalyDetection": {
                "class_imbalance_ratio": {"min": 10.0, "weight": 0.4},
                "minority_class_percentage": {"max": 5.0, "weight": 0.3},
                "outlier_percentage": {"min": 3.0, "weight": 0.2},
                "data_completeness": {"min": 80.0, "weight": 0.1},
                "threshold": 0.6
            },
            "#FraudResearch": {
                "class_imbalance_ratio": {"min": 20.0, "weight": 0.5},
                "minority_class_percentage": {"max": 2.0, "weight": 0.3},
                "data_completeness": {"min": 85.0, "weight": 0.2},
                "threshold": 0.7
            },
            "#FairnessAudit": {
                "has_demographic_features": {"value": True, "weight": 0.4},
                "class_balance_level": {"values": ["imbalanced", "severely_imbalanced"], "weight": 0.3},
                "data_completeness": {"min": 70.0, "weight": 0.2},
                "feature_correlation_issues": {"min": 1, "weight": 0.1},
                "threshold": 0.5
            },
            "#GeneralPurposeML": {
                "data_completeness": {"min": 90.0, "weight": 0.3},
                "class_balance_level": {"values": ["excellent", "good", "fair"], "weight": 0.3},
                "duplicate_percentage": {"max": 2.0, "weight": 0.2},
                "outlier_percentage": {"max": 5.0, "weight": 0.2},
                "threshold": 0.7
            },
            "#PredictiveModeling": {
                "ml_usability_score": {"min": 70.0, "weight": 0.4},
                "feature_importance_distribution": {"values": ["medium", "low"], "weight": 0.3},
                "data_separability_score": {"min": 60.0, "weight": 0.2},
                "data_completeness": {"min": 85.0, "weight": 0.1},
                "threshold": 0.65
            },
            "#ImbalancedLearning": {
                "class_imbalance_ratio": {"min": 5.0, "weight": 0.4},
                "minority_class_percentage": {"max": 10.0, "weight": 0.3},
                "data_completeness": {"min": 75.0, "weight": 0.2},
                "ml_usability_score": {"min": 50.0, "weight": 0.1},
                "threshold": 0.6
            },
            "#ModelRobustnessTesting": {
                "outlier_percentage": {"min": 10.0, "weight": 0.4},
                "missing_percentage": {"min": 5.0, "weight": 0.3},
                "type_consistency_issues": {"min": 2, "weight": 0.2},
                "duplicate_percentage": {"min": 1.0, "weight": 0.1},
                "threshold": 0.5
            },
            "#AdversarialTraining": {
                "outlier_percentage": {"min": 15.0, "weight": 0.5},
                "feature_correlation_issues": {"min": 3, "weight": 0.3},
                "data_separability_score": {"max": 40.0, "weight": 0.2},
                "threshold": 0.6
            },
            "#SociologicalAnalysis": {
                "has_demographic_features": {"value": True, "weight": 0.5},
                "class_balance_level": {"values": ["imbalanced", "severely_imbalanced"], "weight": 0.2},
                "data_completeness": {"min": 60.0, "weight": 0.2},
                "feature_count": {"min": 10, "weight": 0.1},
                "threshold": 0.4
            },
            "#DataQualityBenchmark": {
                "missing_percentage": {"min": 20.0, "weight": 0.4},
                "duplicate_percentage": {"min": 5.0, "weight": 0.3},
                "type_consistency_issues": {"min": 5, "weight": 0.2},
                "outlier_percentage": {"min": 8.0, "weight": 0.1},
                "threshold": 0.5
            }
        }
    
    def _extract_characteristics(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key characteristics from foundational tool results"""
        characteristics = {}
        
        # From missing value analyzer
        if "missing_value_analysis" in analysis_results:
            missing_data = analysis_results["missing_value_analysis"]
            characteristics["missing_percentage"] = missing_data.get("overall_missing_percentage", 0)
            characteristics["data_completeness"] = missing_data.get("integrity_score", 100)
        
        # From duplicate detector
        if "duplicate_analysis" in analysis_results:
            dup_data = analysis_results["duplicate_analysis"]
            characteristics["duplicate_percentage"] = dup_data.get("duplicate_percentage", 0)
        
        # From data type consistency checker
        if "type_consistency_analysis" in analysis_results:
            type_data = analysis_results["type_consistency_analysis"]
            characteristics["type_consistency_issues"] = len(type_data.get("type_issues", []))
        
        # From outlier detection
        if "outlier_analysis" in analysis_results:
            outlier_data = analysis_results["outlier_analysis"]
            characteristics["outlier_percentage"] = outlier_data.get("overall_outlier_percentage", 0)
        
        # From class balance assessor
        if "class_balance_analysis" in analysis_results:
            balance_data = analysis_results["class_balance_analysis"]
            characteristics["class_balance_level"] = balance_data.get("balance_level", "unknown")
            characteristics["class_imbalance_ratio"] = balance_data.get("imbalance_ratio", 1.0)
            characteristics["minority_class_percentage"] = balance_data.get("minority_class", {}).get("percentage", 50.0)
        
        # From feature correlation mapper
        if "correlation_analysis" in analysis_results:
            corr_data = analysis_results["correlation_analysis"]
            characteristics["feature_correlation_issues"] = len(corr_data.get("high_correlations", []))
            characteristics["multicollinearity_risk"] = corr_data.get("multicollinearity_risk", "low")
        
        # From baseline model performance
        if "ml_performance_analysis" in analysis_results:
            ml_data = analysis_results["ml_performance_analysis"]
            characteristics["ml_usability_score"] = ml_data.get("ml_usability_score", 0)
        
        # From feature importance analyzer
        if "feature_importance_analysis" in analysis_results:
            importance_data = analysis_results["feature_importance_analysis"]
            info_dist = importance_data.get("information_distribution", {})
            characteristics["feature_importance_distribution"] = info_dist.get("information_concentration", "medium")
        
        # From data separability scorer
        if "separability_analysis" in analysis_results:
            sep_data = analysis_results["separability_analysis"]
            characteristics["data_separability_score"] = sep_data.get("separability_score", 50)
        
        # General characteristics
        if "data_profile" in analysis_results:
            profile = analysis_results["data_profile"]
            basic_info = profile.get("basic_info", {})
            characteristics["feature_count"] = basic_info.get("total_columns", 0)
            characteristics["sample_count"] = basic_info.get("total_rows", 0)
            
            # Check for potential demographic features
            columns = basic_info.get("column_names", [])
            demographic_keywords = ["age", "gender", "race", "ethnicity", "income", "education", "location", "zip", "postal"]
            characteristics["has_demographic_features"] = any(
                any(keyword in col.lower() for keyword in demographic_keywords) for col in columns
            )
        
        return characteristics
    
    def _evaluate_persona_rules(self, characteristics: Dict, rules: Dict) -> tuple:
        """Evaluate if characteristics match persona rules"""
        total_weight = 0
        matched_weight = 0
        reasons = []
        
        threshold = rules.get("threshold", 0.5)
        
        for rule_name, rule_config in rules.items():
            if rule_name == "threshold":
                continue
                
            weight = rule_config.get("weight", 0.1)
            total_weight += weight
            
            if rule_name not in characteristics:
                continue
            
            char_value = characteristics[rule_name]
            rule_matched = False
            reason = ""
            
            # Check different rule types
            if "min" in rule_config:
                if char_value >= rule_config["min"]:
                    rule_matched = True
                    reason = f"{rule_name} ({char_value}) meets minimum threshold ({rule_config['min']})"
            
            if "max" in rule_config:
                if char_value <= rule_config["max"]:
                    rule_matched = True
                    reason = f"{rule_name} ({char_value}) is below maximum threshold ({rule_config['max']})"
            
            if "value" in rule_config:
                if char_value == rule_config["value"]:
                    rule_matched = True
                    reason = f"{rule_name} matches expected value ({rule_config['value']})"
            
            if "values" in rule_config:
                if char_value in rule_config["values"]:
                    rule_matched = True
                    reason = f"{rule_name} ({char_value}) is in expected values ({rule_config['values']})"
            
            if rule_matched:
                matched_weight += weight
                reasons.append(reason)
        
        confidence = matched_weight / total_weight if total_weight > 0 else 0
        should_tag = confidence >= threshold
        
        return should_tag, round(confidence, 3), reasons
    
    def _generate_persona_summary(self, persona_tags: List[str], sorted_personas: List) -> str:
        """Generate human-readable summary of persona analysis"""
        if not persona_tags:
            return "No specific research personas identified - dataset suitable for general purposes."
        
        primary = sorted_personas[0][0] if sorted_personas else persona_tags[0]
        confidence = sorted_personas[0][1]["confidence"] if sorted_personas else 0.7
        
        summary = f"Primary persona: {primary} (confidence: {confidence:.2f}). "
        
        if len(persona_tags) > 1:
            other_personas = [p for p in persona_tags if p != primary]
            summary += f"Also suitable for: {', '.join(other_personas)}. "
        
        # Add contextual advice
        persona_advice = {
            "#AnomalyDetection": "Excellent for detecting rare events and outliers",
            "#FraudResearch": "Ideal for fraud detection and financial security research",
            "#FairnessAudit": "Valuable for bias detection and algorithmic fairness studies",
            "#GeneralPurposeML": "Well-balanced dataset suitable for standard ML tasks",
            "#PredictiveModeling": "Strong predictive signals for forecasting applications",
            "#ImbalancedLearning": "Perfect for testing imbalanced learning techniques",
            "#ModelRobustnessTesting": "Useful for testing model resilience to noisy data",
            "#AdversarialTraining": "Challenging dataset for adversarial ML research",
            "#SociologicalAnalysis": "Rich in demographic patterns for social science research",
            "#DataQualityBenchmark": "Contains quality issues useful for data cleaning research"
        }
        
        if primary in persona_advice:
            summary += persona_advice[primary]
        
        return summary

class ContextualScoringEngineTool(BaseTool):
    """Tool for generating multiple purpose-driven scores based on different research contexts"""
    
    def __init__(self):
        super().__init__(
            name="contextual_scoring_engine",
            description="Generate purpose-driven quality scores for different research contexts and use cases"
        )
        self.scoring_lenses = self._define_scoring_lenses()
    
    async def execute(self, analysis_results: Dict[str, Any], persona_tags: List[str] = None, **kwargs) -> Dict[str, Any]:
        """Generate contextual scores for different research purposes"""
        try:
            # Extract metrics from foundational tools
            metrics = self._extract_metrics(analysis_results)
            
            # Calculate scores for all relevant lenses
            contextual_scores = {}
            score_explanations = {}
            
            # Determine which lenses to calculate based on persona tags
            relevant_lenses = self._determine_relevant_lenses(persona_tags) if persona_tags else list(self.scoring_lenses.keys())
            
            for lens_name in relevant_lenses:
                if lens_name in self.scoring_lenses:
                    score, explanation = self._calculate_lens_score(metrics, self.scoring_lenses[lens_name])
                    contextual_scores[lens_name] = score
                    score_explanations[lens_name] = explanation
            
            # Find the highest scoring context
            best_context = max(contextual_scores.items(), key=lambda x: x[1]) if contextual_scores else ("general_purpose_score", 50)
            
            # Generate comparative analysis
            comparative_analysis = self._generate_comparative_analysis(contextual_scores, score_explanations)
            
            result = {
                "success": True,
                "contextual_scores": contextual_scores,
                "score_explanations": score_explanations,
                "best_context": {
                    "name": best_context[0],
                    "score": best_context[1],
                    "explanation": score_explanations.get(best_context[0], "")
                },
                "comparative_analysis": comparative_analysis,
                "metrics_used": metrics,
                "scoring_summary": self._generate_scoring_summary(contextual_scores, best_context)
            }
            
            self.log_execution({"lenses_calculated": len(contextual_scores)}, {"success": True})
            return result
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": f"Contextual scoring failed: {str(e)}",
                "contextual_scores": {},
                "best_context": {"name": "unknown", "score": 0}
            }
            self.log_execution({}, error_result)
            return error_result
    
    def _define_scoring_lenses(self) -> Dict[str, Dict]:
        """Define scoring formulas for different research contexts"""
        return {
            "general_purpose_score": {
                "description": "Overall dataset quality for standard ML tasks",
                "weights": {
                    "completeness": 0.30,      # Increased weight for completeness
                    "consistency": 0.25,       # Increased weight for consistency  
                    "balance": 0.15,           # Reduced weight for balance (not all datasets need perfect balance)
                    "cleanliness": 0.15,       # Maintained
                    "ml_readiness": 0.15       # Reduced but maintained
                },
                "penalties": {
                    "high_missing": {"threshold": 20, "penalty": 15},      # More lenient threshold and penalty
                    "severe_imbalance": {"threshold": 50, "penalty": 10},  # Much more lenient on imbalance
                    "many_duplicates": {"threshold": 10, "penalty": 8}     # More lenient on duplicates
                }
            },
            "anomaly_research_score": {
                "description": "Quality for anomaly detection and rare event research",
                "weights": {
                    "imbalance_presence": 0.35,  # Higher imbalance is better
                    "minority_completeness": 0.25,
                    "overall_completeness": 0.15,
                    "separability": 0.15,
                    "cleanliness": 0.10
                },
                "bonuses": {
                    "high_imbalance": {"threshold": 10, "bonus": 25},
                    "extreme_imbalance": {"threshold": 50, "bonus": 40}
                }
            },
            "fairness_audit_score": {
                "description": "Quality for bias detection and fairness research",
                "weights": {
                    "demographic_presence": 0.30,
                    "bias_detectability": 0.25,
                    "completeness": 0.20,
                    "sample_diversity": 0.15,
                    "feature_richness": 0.10
                },
                "bonuses": {
                    "has_demographics": {"condition": True, "bonus": 30},
                    "imbalance_present": {"threshold": 2, "bonus": 20}
                }
            },
            "predictive_modeling_score": {
                "description": "Quality for forecasting and predictive analytics",
                "weights": {
                    "ml_performance": 0.30,
                    "feature_importance": 0.25,
                    "separability": 0.20,
                    "completeness": 0.15,
                    "consistency": 0.10
                },
                "penalties": {
                    "weak_signals": {"threshold": 50, "penalty": 25},
                    "poor_separability": {"threshold": 40, "penalty": 20}
                }
            },
            "robustness_testing_score": {
                "description": "Quality for testing model robustness and resilience",
                "weights": {
                    "noise_presence": 0.30,  # Higher noise is better for robustness testing
                    "outlier_presence": 0.25,
                    "missing_patterns": 0.20,
                    "type_inconsistencies": 0.15,
                    "completeness": 0.10
                },
                "bonuses": {
                    "high_outliers": {"threshold": 10, "bonus": 20},
                    "missing_data": {"threshold": 5, "bonus": 15},
                    "type_issues": {"threshold": 2, "bonus": 10}
                }
            },
            "research_benchmark_score": {
                "description": "Quality as a research benchmark dataset",
                "weights": {
                    "completeness": 0.20,
                    "documentation": 0.20,  # Inferred from consistency
                    "balance": 0.15,
                    "size_adequacy": 0.15,
                    "feature_diversity": 0.15,
                    "reproducibility": 0.15
                },
                "bonuses": {
                    "large_sample": {"threshold": 10000, "bonus": 15},
                    "balanced_classes": {"condition": "excellent", "bonus": 20}
                }
            }
        }
    
    def _extract_metrics(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract numerical metrics from all foundational tool results"""
        metrics = {}
        
        # Completeness metrics
        if "missing_value_analysis" in analysis_results:
            missing_data = analysis_results["missing_value_analysis"]
            metrics["completeness"] = missing_data.get("integrity_score", 100)
            metrics["missing_percentage"] = missing_data.get("overall_missing_percentage", 0)
        
        # Consistency metrics
        if "type_consistency_analysis" in analysis_results:
            type_data = analysis_results["type_consistency_analysis"]
            metrics["consistency"] = type_data.get("consistency_score", 100)
            metrics["type_issues_count"] = len(type_data.get("type_issues", []))
        
        # Duplicate metrics
        if "duplicate_analysis" in analysis_results:
            dup_data = analysis_results["duplicate_analysis"]
            metrics["duplicate_percentage"] = dup_data.get("duplicate_percentage", 0)
            metrics["duplicate_score"] = dup_data.get("integrity_score", 100)
        
        # Class balance metrics
        if "class_balance_analysis" in analysis_results:
            balance_data = analysis_results["class_balance_analysis"]
            metrics["balance_score"] = balance_data.get("balance_score", 100)
            metrics["imbalance_ratio"] = balance_data.get("imbalance_ratio", 1.0)
            metrics["minority_class_pct"] = balance_data.get("minority_class", {}).get("percentage", 50.0)
            metrics["balance_level"] = balance_data.get("balance_level", "unknown")
        
        # Outlier metrics
        if "outlier_analysis" in analysis_results:
            outlier_data = analysis_results["outlier_analysis"]
            metrics["outlier_percentage"] = outlier_data.get("overall_outlier_percentage", 0)
            metrics["outlier_score"] = outlier_data.get("outlier_score", 100)
        
        # Correlation metrics
        if "correlation_analysis" in analysis_results:
            corr_data = analysis_results["correlation_analysis"]
            metrics["correlation_score"] = corr_data.get("multicollinearity_score", 100)
            metrics["high_correlations_count"] = len(corr_data.get("high_correlations", []))
        
        # ML performance metrics
        if "ml_performance_analysis" in analysis_results:
            ml_data = analysis_results["ml_performance_analysis"]
            metrics["ml_usability_score"] = ml_data.get("ml_usability_score", 0)
        
        # Feature importance metrics
        if "feature_importance_analysis" in analysis_results:
            importance_data = analysis_results["feature_importance_analysis"]
            metrics["information_score"] = importance_data.get("information_score", 50)
            info_dist = importance_data.get("information_distribution", {})
            metrics["top_feature_contribution"] = info_dist.get("top_1_feature_contribution", 0.3)
            metrics["useful_features_count"] = info_dist.get("features_above_5pct", 0)
        
        # Separability metrics
        if "separability_analysis" in analysis_results:
            sep_data = analysis_results["separability_analysis"]
            metrics["separability_score"] = sep_data.get("separability_score", 50)
        
        # Dataset characteristics
        if "data_profile" in analysis_results:
            profile = analysis_results["data_profile"]
            basic_info = profile.get("basic_info", {})
            metrics["sample_count"] = basic_info.get("total_rows", 0)
            metrics["feature_count"] = basic_info.get("total_columns", 0)
            
            # Check for demographic features
            columns = basic_info.get("column_names", [])
            demographic_keywords = ["age", "gender", "race", "ethnicity", "income", "education"]
            metrics["has_demographic_features"] = any(
                any(keyword in col.lower() for keyword in demographic_keywords) for col in columns
            )
        
        # Derived metrics
        metrics["cleanliness"] = (
            metrics.get("completeness", 100) * 0.4 +
            metrics.get("consistency", 100) * 0.3 +
            metrics.get("duplicate_score", 100) * 0.3
        )
        
        metrics["ml_readiness"] = (
            metrics.get("ml_usability_score", 0) * 0.5 +
            metrics.get("separability_score", 50) * 0.3 +
            metrics.get("information_score", 50) * 0.2
        )
        
        return metrics
    
    def _determine_relevant_lenses(self, persona_tags: List[str]) -> List[str]:
        """Determine which scoring lenses are relevant based on persona tags"""
        lens_mapping = {
            "#AnomalyDetection": ["anomaly_research_score", "general_purpose_score"],
            "#FraudResearch": ["anomaly_research_score", "general_purpose_score"],
            "#FairnessAudit": ["fairness_audit_score", "research_benchmark_score"],
            "#GeneralPurposeML": ["general_purpose_score", "predictive_modeling_score"],
            "#PredictiveModeling": ["predictive_modeling_score", "general_purpose_score"],
            "#ImbalancedLearning": ["anomaly_research_score", "general_purpose_score"],
            "#ModelRobustnessTesting": ["robustness_testing_score", "general_purpose_score"],
            "#AdversarialTraining": ["robustness_testing_score", "research_benchmark_score"],
            "#SociologicalAnalysis": ["fairness_audit_score", "research_benchmark_score"],
            "#DataQualityBenchmark": ["research_benchmark_score", "robustness_testing_score"]
        }
        
        relevant_lenses = set()
        for tag in persona_tags:
            if tag in lens_mapping:
                relevant_lenses.update(lens_mapping[tag])
        
        # Always include general purpose as baseline
        relevant_lenses.add("general_purpose_score")
        
        return list(relevant_lenses)
    
    def _calculate_lens_score(self, metrics: Dict[str, Any], lens_config: Dict) -> tuple:
        """Calculate score for a specific lens"""
        weights = lens_config.get("weights", {})
        penalties = lens_config.get("penalties", {})
        bonuses = lens_config.get("bonuses", {})
        
        # Start with a baseline score of 60 for datasets that have basic structure
        base_score = 60.0
        max_weight = sum(weights.values())
        
        explanation_parts = []
        
        # Calculate weighted additions to base score
        for metric_name, weight in weights.items():
            metric_value = self._get_metric_value(metrics, metric_name)
            if metric_value is not None:
                # Convert metric to contribution (-20 to +20 range)
                contribution = ((metric_value - 50) / 50) * weight * 20  
                base_score += contribution
                explanation_parts.append(f"{metric_name}: {metric_value:.1f} (contrib: {contribution:+.1f})")
        
        # Apply penalties
        for penalty_name, penalty_config in penalties.items():
            penalty_value = self._evaluate_penalty(metrics, penalty_name, penalty_config)
            if penalty_value > 0:
                base_score -= penalty_value
                explanation_parts.append(f"Penalty ({penalty_name}): -{penalty_value:.1f}")
        
        # Apply bonuses
        for bonus_name, bonus_config in bonuses.items():
            bonus_value = self._evaluate_bonus(metrics, bonus_name, bonus_config)
            if bonus_value > 0:
                base_score += bonus_value
                explanation_parts.append(f"Bonus ({bonus_name}): +{bonus_value:.1f}")
        
        # Ensure score is within bounds
        final_score = max(0.0, min(100.0, base_score))
        
        explanation = f"Score {final_score:.1f}/100. " + "; ".join(explanation_parts[:5])
        
        return round(final_score, 1), explanation
    
    def _get_metric_value(self, metrics: Dict, metric_name: str) -> Optional[float]:
        """Get metric value with special handling for different metric types"""
        special_metrics = {
            "imbalance_presence": lambda m: min(100, (m.get("imbalance_ratio", 1) - 1) * 10),
            "minority_completeness": lambda m: max(0, 100 - m.get("minority_class_pct", 50) * 2),
            "demographic_presence": lambda m: 100 if m.get("has_demographic_features", False) else 0,
            "bias_detectability": lambda m: min(100, (m.get("imbalance_ratio", 1) - 1) * 15),
            "sample_diversity": lambda m: min(100, m.get("feature_count", 0) * 5),
            "feature_richness": lambda m: min(100, m.get("useful_features_count", 0) * 10),
            "ml_performance": lambda m: m.get("ml_usability_score", 0),
            "feature_importance": lambda m: m.get("information_score", 50),
            "noise_presence": lambda m: min(100, m.get("outlier_percentage", 0) * 5),
            "outlier_presence": lambda m: min(100, m.get("outlier_percentage", 0) * 3),
            "missing_patterns": lambda m: min(100, m.get("missing_percentage", 0) * 4),
            "type_inconsistencies": lambda m: min(100, m.get("type_issues_count", 0) * 15),
            "documentation": lambda m: m.get("consistency", 100),
            "size_adequacy": lambda m: min(100, max(0, (m.get("sample_count", 0) / 1000) * 10)),
            "feature_diversity": lambda m: min(100, m.get("feature_count", 0) * 3),
            "reproducibility": lambda m: m.get("consistency", 100),
            "balance": lambda m: m.get("balance_score", 100)
        }
        
        if metric_name in special_metrics:
            return special_metrics[metric_name](metrics)
        else:
            return metrics.get(metric_name)
    
    def _evaluate_penalty(self, metrics: Dict, penalty_name: str, penalty_config: Dict) -> float:
        """Evaluate penalty conditions"""
        penalty_checks = {
            "high_missing": lambda m: penalty_config["penalty"] if m.get("missing_percentage", 0) > penalty_config["threshold"] else 0,
            "severe_imbalance": lambda m: penalty_config["penalty"] if m.get("imbalance_ratio", 1) > penalty_config["threshold"] else 0,
            "many_duplicates": lambda m: penalty_config["penalty"] if m.get("duplicate_percentage", 0) > penalty_config["threshold"] else 0,
            "weak_signals": lambda m: penalty_config["penalty"] if m.get("ml_usability_score", 100) < penalty_config["threshold"] else 0,
            "poor_separability": lambda m: penalty_config["penalty"] if m.get("separability_score", 100) < penalty_config["threshold"] else 0
        }
        
        if penalty_name in penalty_checks:
            return penalty_checks[penalty_name](metrics)
        return 0
    
    def _evaluate_bonus(self, metrics: Dict, bonus_name: str, bonus_config: Dict) -> float:
        """Evaluate bonus conditions"""
        bonus_checks = {
            "high_imbalance": lambda m: bonus_config["bonus"] if m.get("imbalance_ratio", 1) > bonus_config["threshold"] else 0,
            "extreme_imbalance": lambda m: bonus_config["bonus"] if m.get("imbalance_ratio", 1) > bonus_config["threshold"] else 0,
            "has_demographics": lambda m: bonus_config["bonus"] if m.get("has_demographic_features", False) == bonus_config["condition"] else 0,
            "imbalance_present": lambda m: bonus_config["bonus"] if m.get("imbalance_ratio", 1) > bonus_config["threshold"] else 0,
            "high_outliers": lambda m: bonus_config["bonus"] if m.get("outlier_percentage", 0) > bonus_config["threshold"] else 0,
            "missing_data": lambda m: bonus_config["bonus"] if m.get("missing_percentage", 0) > bonus_config["threshold"] else 0,
            "type_issues": lambda m: bonus_config["bonus"] if m.get("type_issues_count", 0) > bonus_config["threshold"] else 0,
            "large_sample": lambda m: bonus_config["bonus"] if m.get("sample_count", 0) > bonus_config["threshold"] else 0,
            "balanced_classes": lambda m: bonus_config["bonus"] if m.get("balance_level", "") == bonus_config["condition"] else 0
        }
        
        if bonus_name in bonus_checks:
            return bonus_checks[bonus_name](metrics)
        return 0
    
    def _generate_comparative_analysis(self, contextual_scores: Dict, score_explanations: Dict) -> Dict[str, Any]:
        """Generate comparative analysis across different contexts"""
        if not contextual_scores:
            return {"message": "No contextual scores available for comparison"}
        
        sorted_scores = sorted(contextual_scores.items(), key=lambda x: x[1], reverse=True)
        
        analysis = {
            "ranking": [{"context": name, "score": score} for name, score in sorted_scores],
            "score_spread": round(sorted_scores[0][1] - sorted_scores[-1][1], 1) if len(sorted_scores) > 1 else 0,
            "average_score": round(sum(contextual_scores.values()) / len(contextual_scores), 1),
            "performance_tier": self._determine_performance_tier(sorted_scores[0][1])
        }
        
        # Generate insights
        insights = []
        best_score = sorted_scores[0][1]
        
        if best_score >= 80:
            insights.append("Excellent dataset quality across evaluated contexts")
        elif best_score >= 65:
            insights.append("Good dataset quality with strong potential for specific use cases")
        elif best_score >= 45:
            insights.append("Moderate quality - may require preprocessing for optimal results")
        else:
            insights.append("Low quality - significant issues need addressing before use")
        
        if analysis["score_spread"] > 30:
            insights.append("Highly context-dependent quality - some use cases much better than others")
        elif analysis["score_spread"] > 15:
            insights.append("Moderately context-dependent - performance varies by use case")
        else:
            insights.append("Consistent quality across different contexts")
        
        analysis["insights"] = insights
        
        return analysis
    
    def _determine_performance_tier(self, best_score: float) -> str:
        """Determine performance tier based on best score"""
        if best_score >= 85:
            return "Excellent"
        elif best_score >= 70:
            return "Good"
        elif best_score >= 55:
            return "Fair"
        elif best_score >= 35:
            return "Poor"
        else:
            return "Unacceptable"
    
    def _generate_scoring_summary(self, contextual_scores: Dict, best_context: tuple) -> str:
        """Generate human-readable scoring summary"""
        if not contextual_scores:
            return "No contextual scores calculated."
        
        best_name, best_score = best_context
        
        summary = f"Best use case: {best_name.replace('_', ' ').title()} ({best_score:.1f}/100). "
        
        if best_score >= 80:
            summary += "Excellent quality for this specific application. "
        elif best_score >= 65:
            summary += "Good quality with strong potential. "
        elif best_score >= 45:
            summary += "Moderate quality - some preprocessing recommended. "
        else:
            summary += "Poor quality - significant improvements needed. "
        
        # Add comparative context
        other_scores = [score for name, score in contextual_scores.items() if name != best_name]
        if other_scores:
            avg_other = sum(other_scores) / len(other_scores)
            if best_score - avg_other > 15:
                summary += "Significantly better for this specific use case than general applications."
            elif best_score - avg_other > 5:
                summary += "Notably better for this specific use case."
            else:
                summary += "Similar quality across different applications."
        
        return summary

class UtilityScoreSynthesizerTool(BaseTool):
    """Tool for synthesizing all analysis results into a single Overall Utility Score with executive summary"""
    
    def __init__(self):
        super().__init__(
            name="utility_score_synthesizer",
            description="Synthesize all dataset analysis into final Overall Utility Score with executive summary"
        )
    
    async def execute(self, analysis_results: Dict[str, Any], persona_tags: List[str], 
                     contextual_scores: Dict[str, float], **kwargs) -> Dict[str, Any]:
        """Synthesize final utility score from all analysis components"""
        try:
            # Step 1: Calculate foundational data integrity score
            data_integrity_score = self._calculate_data_integrity_score(analysis_results)
            
            # Step 2: Identify maximum potential from contextual scores
            max_potential_analysis = self._identify_maximum_potential(contextual_scores, persona_tags)
            
            # Step 3: Synthesize overall utility score
            overall_utility_score = self._synthesize_overall_score(
                data_integrity_score, 
                max_potential_analysis["highest_score"]
            )
            
            # Step 4: Generate executive summary
            executive_summary = self._generate_executive_summary(
                overall_utility_score,
                data_integrity_score,
                max_potential_analysis,
                analysis_results
            )
            
            # Step 5: Generate detailed recommendations
            recommendations = self._generate_final_recommendations(
                overall_utility_score,
                data_integrity_score,
                max_potential_analysis,
                analysis_results
            )
            
            # Step 6: Create utility grade and tier classification
            utility_grade = self._determine_utility_grade(overall_utility_score)
            readiness_assessment = self._assess_readiness(data_integrity_score, overall_utility_score)
            
            result = {
                "success": True,
                "overall_utility_score": round(overall_utility_score, 1),
                "primary_persona": max_potential_analysis["primary_persona"],
                "data_integrity_score": round(data_integrity_score, 1),
                "executive_summary": executive_summary,
                "utility_grade": utility_grade,
                "readiness_assessment": readiness_assessment,
                "recommendations": recommendations,
                "scoring_breakdown": {
                    "data_integrity_components": self._get_integrity_breakdown(analysis_results),
                    "contextual_scores": contextual_scores,
                    "max_potential": max_potential_analysis,
                    "synthesis_formula": f"({max_potential_analysis['highest_score']}/100) × {data_integrity_score:.1f} = {overall_utility_score:.1f}"
                },
                "publication_readiness": self._assess_publication_readiness(
                    overall_utility_score, data_integrity_score, analysis_results
                ),
                "next_steps": self._suggest_next_steps(utility_grade, readiness_assessment)
            }
            
            self.log_execution({
                "utility_score": overall_utility_score,
                "primary_persona": max_potential_analysis["primary_persona"]
            }, {"success": True})
            return result
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": f"Utility score synthesis failed: {str(e)}",
                "overall_utility_score": 0,
                "primary_persona": "#Unknown",
                "executive_summary": "Analysis failed - unable to determine dataset utility."
            }
            self.log_execution({}, error_result)
            return error_result
    
    def _calculate_data_integrity_score(self, analysis_results: Dict[str, Any]) -> float:
        """Calculate foundational data integrity score using the specified formula"""
        # Default scores if analysis not available
        completeness_score = 100.0
        consistency_score = 100.0
        duplicate_score = 100.0
        
        # Extract completeness score (50% weight)
        if "missing_value_analysis" in analysis_results:
            completeness_score = analysis_results["missing_value_analysis"].get("integrity_score", 100.0)
        
        # Extract data type consistency score (30% weight)
        if "type_consistency_analysis" in analysis_results:
            consistency_score = analysis_results["type_consistency_analysis"].get("consistency_score", 100.0)
        
        # Extract duplicate record score (20% weight)
        if "duplicate_analysis" in analysis_results:
            duplicate_score = analysis_results["duplicate_analysis"].get("integrity_score", 100.0)
        
        # Apply the specified formula
        data_integrity_score = (
            0.5 * completeness_score +
            0.3 * consistency_score +
            0.2 * duplicate_score
        )
        
        return max(0.0, min(100.0, data_integrity_score))
    
    def _identify_maximum_potential(self, contextual_scores: Dict[str, float], persona_tags: List[str]) -> Dict[str, Any]:
        """Identify the highest contextual score and corresponding persona"""
        if not contextual_scores:
            return {
                "highest_score": 50.0,
                "primary_persona": persona_tags[0] if persona_tags else "#GeneralPurposeML",
                "score_context": "general_purpose_score",
                "confidence": "low"
            }
        
        # Find maximum score
        max_item = max(contextual_scores.items(), key=lambda x: x[1])
        score_context, highest_score = max_item
        
        # Map score context to persona
        context_to_persona = {
            "general_purpose_score": "#GeneralPurposeML",
            "anomaly_research_score": "#AnomalyDetection",
            "fairness_audit_score": "#FairnessAudit",
            "predictive_modeling_score": "#PredictiveModeling",
            "robustness_testing_score": "#ModelRobustnessTesting",
            "research_benchmark_score": "#DataQualityBenchmark"
        }
        
        primary_persona = context_to_persona.get(score_context, persona_tags[0] if persona_tags else "#GeneralPurposeML")
        
        # Determine confidence based on score separation
        scores_list = list(contextual_scores.values())
        if len(scores_list) > 1:
            second_highest = sorted(scores_list, reverse=True)[1]
            score_gap = highest_score - second_highest
            
            if score_gap > 20:
                confidence = "high"
            elif score_gap > 10:
                confidence = "medium"
            else:
                confidence = "low"
        else:
            confidence = "medium"
        
        return {
            "highest_score": highest_score,
            "primary_persona": primary_persona,
            "score_context": score_context,
            "confidence": confidence,
            "score_gap": score_gap if len(scores_list) > 1 else 0
        }
    
    def _synthesize_overall_score(self, data_integrity_score: float, highest_contextual_score: float) -> float:
        """Apply the core synthesis formula with balanced weighting"""
        # Improved formula that doesn't penalize general-purpose datasets too harshly:
        # Overall Score = 0.7 × Data Integrity Score + 0.3 × Highest Contextual Score
        # This ensures data integrity has the primary weight, with context as a bonus
        overall_score = (0.7 * data_integrity_score) + (0.3 * highest_contextual_score)
        return max(0.0, min(100.0, overall_score))
    
    def _generate_executive_summary(self, overall_score: float, integrity_score: float, 
                                   max_potential: Dict, analysis_results: Dict) -> str:
        """Generate comprehensive executive summary"""
        summary_parts = []
        
        # Overall utility assessment
        if overall_score >= 85:
            summary_parts.append(f"Overall Utility: Excellent ({overall_score:.1f}/100).")
        elif overall_score >= 70:
            summary_parts.append(f"Overall Utility: Good ({overall_score:.1f}/100).")
        elif overall_score >= 55:
            summary_parts.append(f"Overall Utility: Fair ({overall_score:.1f}/100).")
        elif overall_score >= 35:
            summary_parts.append(f"Overall Utility: Poor ({overall_score:.1f}/100).")
        else:
            summary_parts.append(f"Overall Utility: Unacceptable ({overall_score:.1f}/100).")
        
        # Data integrity assessment
        if integrity_score >= 90:
            summary_parts.append("Data integrity is excellent with minimal quality issues.")
        elif integrity_score >= 75:
            summary_parts.append("Data integrity is good with some minor quality concerns.")
        elif integrity_score >= 60:
            summary_parts.append("Data integrity is fair - moderate quality issues present.")
        elif integrity_score >= 40:
            summary_parts.append("Data integrity is poor - significant quality issues detected.")
        else:
            summary_parts.append("Data integrity is critical - major quality problems require immediate attention.")
        
        # Primary use case assessment
        persona_descriptions = {
            "#AnomalyDetection": "This dataset is a premier candidate for anomaly detection research",
            "#FraudResearch": "This dataset is excellent for fraud detection and financial security research",
            "#FairnessAudit": "This dataset is valuable for bias detection and algorithmic fairness studies",
            "#GeneralPurposeML": "This dataset is well-suited for standard machine learning applications",
            "#PredictiveModeling": "This dataset shows strong potential for forecasting and predictive analytics",
            "#ImbalancedLearning": "This dataset is ideal for testing imbalanced learning techniques",
            "#ModelRobustnessTesting": "This dataset is useful for testing model resilience and robustness",
            "#AdversarialTraining": "This dataset presents challenges suitable for adversarial ML research",
            "#SociologicalAnalysis": "This dataset contains rich patterns for social science research",
            "#DataQualityBenchmark": "This dataset serves as a useful benchmark for data quality research"
        }
        
        primary_persona = max_potential["primary_persona"]
        if primary_persona in persona_descriptions:
            summary_parts.append(persona_descriptions[primary_persona] + ".")
        
        # Confidence and readiness assessment
        confidence = max_potential["confidence"]
        if confidence == "high":
            summary_parts.append("Confidence in this assessment is high due to clear quality patterns.")
        elif confidence == "medium":
            summary_parts.append("Confidence in this assessment is moderate - multiple use cases may be viable.")
        else:
            summary_parts.append("Confidence in this assessment is low - quality patterns are mixed or unclear.")
        
        return " ".join(summary_parts)
    
    def _generate_final_recommendations(self, overall_score: float, integrity_score: float,
                                      max_potential: Dict, analysis_results: Dict) -> List[str]:
        """Generate final actionable recommendations"""
        recommendations = []
        
        # High-level strategic recommendations
        if overall_score >= 80:
            recommendations.append("✅ Dataset ready for immediate use in production environments")
            recommendations.append("🚀 Consider this dataset for high-impact research or business applications")
        elif overall_score >= 65:
            recommendations.append("👍 Dataset suitable for most applications with minor preprocessing")
            recommendations.append("🔧 Address identified quality issues to unlock full potential")
        elif overall_score >= 45:
            recommendations.append("⚠️ Dataset requires significant preprocessing before use")
            recommendations.append("🛠️ Focus on data cleaning and quality improvement initiatives")
        else:
            recommendations.append("❌ Dataset not recommended for production use in current state")
            recommendations.append("🔄 Consider data collection improvements or alternative datasets")
        
        # Integrity-specific recommendations
        if integrity_score < 70:
            recommendations.append("🎯 Priority: Address data integrity issues (completeness, consistency, duplicates)")
        
        # Context-specific recommendations
        primary_persona = max_potential["primary_persona"]
        persona_recommendations = {
            "#AnomalyDetection": "📊 Leverage class imbalance for anomaly detection algorithms",
            "#FairnessAudit": "⚖️ Implement bias detection workflows and fairness metrics",
            "#GeneralPurposeML": "🤖 Apply standard ML preprocessing and feature engineering techniques",
            "#PredictiveModeling": "📈 Focus on feature selection and model validation strategies",
            "#ModelRobustnessTesting": "🛡️ Use data quality issues as robustness testing opportunities"
        }
        
        if primary_persona in persona_recommendations:
            recommendations.append(persona_recommendations[primary_persona])
        
        # Publication readiness
        if overall_score >= 70 and integrity_score >= 75:
            recommendations.append("📋 Consider documenting and publishing this dataset for research community")
        
        return recommendations[:8]  # Limit to top 8 recommendations
    
    def _determine_utility_grade(self, overall_score: float) -> Dict[str, Any]:
        """Determine utility grade classification"""
        if overall_score >= 90:
            return {"grade": "A+", "description": "Exceptional", "color": "green"}
        elif overall_score >= 85:
            return {"grade": "A", "description": "Excellent", "color": "green"}
        elif overall_score >= 80:
            return {"grade": "A-", "description": "Very Good", "color": "green"}
        elif overall_score >= 75:
            return {"grade": "B+", "description": "Good", "color": "blue"}
        elif overall_score >= 70:
            return {"grade": "B", "description": "Above Average", "color": "blue"}
        elif overall_score >= 65:
            return {"grade": "B-", "description": "Satisfactory", "color": "blue"}
        elif overall_score >= 60:
            return {"grade": "C+", "description": "Fair", "color": "yellow"}
        elif overall_score >= 55:
            return {"grade": "C", "description": "Acceptable", "color": "yellow"}
        elif overall_score >= 50:
            return {"grade": "C-", "description": "Below Average", "color": "yellow"}
        elif overall_score >= 40:
            return {"grade": "D", "description": "Poor", "color": "orange"}
        else:
            return {"grade": "F", "description": "Unacceptable", "color": "red"}
    
    def _assess_readiness(self, integrity_score: float, overall_score: float) -> Dict[str, Any]:
        """Assess dataset readiness for various stages of use"""
        readiness = {
            "research_ready": overall_score >= 60,
            "production_ready": overall_score >= 75 and integrity_score >= 80,
            "publication_ready": overall_score >= 70 and integrity_score >= 75,
            "immediate_use": overall_score >= 80,
            "preprocessing_required": overall_score < 70,
            "major_improvements_needed": overall_score < 50
        }
        
        # Determine primary readiness state
        if readiness["immediate_use"]:
            primary_state = "immediate_use"
        elif readiness["production_ready"]:
            primary_state = "production_ready"
        elif readiness["research_ready"]:
            primary_state = "research_ready"
        elif readiness["preprocessing_required"]:
            primary_state = "preprocessing_required"
        else:
            primary_state = "major_improvements_needed"
        
        readiness["primary_state"] = primary_state
        
        return readiness
    
    def _get_integrity_breakdown(self, analysis_results: Dict[str, Any]) -> Dict[str, float]:
        """Get detailed breakdown of integrity components"""
        breakdown = {}
        
        if "missing_value_analysis" in analysis_results:
            breakdown["completeness"] = analysis_results["missing_value_analysis"].get("integrity_score", 100.0)
        
        if "type_consistency_analysis" in analysis_results:
            breakdown["consistency"] = analysis_results["type_consistency_analysis"].get("consistency_score", 100.0)
        
        if "duplicate_analysis" in analysis_results:
            breakdown["duplicates"] = analysis_results["duplicate_analysis"].get("integrity_score", 100.0)
        
        return breakdown
    
    def _assess_publication_readiness(self, overall_score: float, integrity_score: float, 
                                    analysis_results: Dict) -> Dict[str, Any]:
        """Assess readiness for dataset publication"""
        readiness_factors = {
            "sufficient_quality": overall_score >= 70,
            "data_integrity": integrity_score >= 75,
            "clear_use_case": overall_score >= 60,
            "documentation_ready": integrity_score >= 80,  # Proxy for documentation quality
            "ethical_considerations": True  # Would need additional analysis
        }
        
        met_criteria = sum(readiness_factors.values())
        total_criteria = len(readiness_factors)
        
        publication_score = (met_criteria / total_criteria) * 100
        
        if publication_score >= 80:
            recommendation = "Recommended for publication"
            status = "ready"
        elif publication_score >= 60:
            recommendation = "Consider publication with minor improvements"
            status = "nearly_ready"
        else:
            recommendation = "Not recommended for publication in current state"
            status = "needs_work"
        
        return {
            "publication_score": round(publication_score, 1),
            "status": status,
            "recommendation": recommendation,
            "criteria_met": readiness_factors,
            "missing_criteria": [k for k, v in readiness_factors.items() if not v]
        }
    
    def _suggest_next_steps(self, utility_grade: Dict, readiness: Dict) -> List[str]:
        """Suggest concrete next steps based on assessment"""
        next_steps = []
        
        primary_state = readiness["primary_state"]
        
        if primary_state == "immediate_use":
            next_steps.extend([
                "Deploy dataset in production environment",
                "Monitor model performance and data drift",
                "Document usage patterns and lessons learned"
            ])
        elif primary_state == "production_ready":
            next_steps.extend([
                "Conduct final validation testing",
                "Prepare deployment documentation",
                "Set up monitoring and alerting systems"
            ])
        elif primary_state == "research_ready":
            next_steps.extend([
                "Begin exploratory data analysis",
                "Design experimental methodology",
                "Address remaining quality issues in parallel"
            ])
        elif primary_state == "preprocessing_required":
            next_steps.extend([
                "Implement data cleaning pipeline",
                "Address missing values and duplicates",
                "Validate preprocessing results"
            ])
        else:  # major_improvements_needed
            next_steps.extend([
                "Reassess data collection methodology",
                "Implement comprehensive quality improvement program",
                "Consider alternative data sources"
            ])
        
        # Add publication steps if applicable
        if readiness.get("publication_ready", False):
            next_steps.append("Prepare dataset for publication with proper documentation")
        
        return next_steps[:6]  # Limit to top 6 steps

# Update tool registry to include new tools
class ToolRegistry:
    """Registry for managing all available tools"""
    
    def __init__(self):
        self.tools = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register all default tools"""
        self.register_tool(DataLoaderTool())
        self.register_tool(DataProfilerTool())
        self.register_tool(ValidationRulesTool())
        self.register_tool(ReportGeneratorTool())
        
        # Data Integrity and Completeness Tools
        self.register_tool(MissingValueAnalyzerTool())
        self.register_tool(DuplicateRecordDetectorTool())
        self.register_tool(DataTypeConsistencyCheckerTool())
        
        # Statistical and Distributional Analysis Tools
        self.register_tool(OutlierDetectionEngineTool())
        self.register_tool(ClassBalanceAssessorTool())
        self.register_tool(FeatureCorrelationMapperTool())
        
        # Machine Learning Usability Tools
        self.register_tool(BaselineModelPerformanceTool())
        self.register_tool(FeatureImportanceAnalyzerTool())
        self.register_tool(DataSeparabilityScoreTool())
        
        # High-Level Analysis Tools
        self.register_tool(DatasetPersonaTaggerTool())
        self.register_tool(ContextualScoringEngineTool())
        self.register_tool(UtilityScoreSynthesizerTool())
    
    def register_tool(self, tool: BaseTool):
        """Register a new tool"""
        self.tools[tool.name] = tool
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name"""
        return self.tools.get(name)
    
    def list_tools(self) -> Dict[str, str]:
        """List all available tools"""
        return {name: tool.description for name, tool in self.tools.items()}
    
    async def execute_tool(self, tool_name: str, *args, **kwargs) -> Dict[str, Any]:
        """Execute a tool by name"""
        tool = self.get_tool(tool_name)
        if not tool:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found. Available tools: {list(self.tools.keys())}"
            }
        
        return await tool.execute(*args, **kwargs)

# Global tool registry instance
tool_registry = ToolRegistry()