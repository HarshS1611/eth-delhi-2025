#!/usr/bin/env python3
"""
Legal Compliance Tools - Fetch.ai uAgents Integration
ETH Delhi 2025 - Dataset Legal Analysis Tools
"""

from typing import Dict, List, Any, Optional, Tuple, Union
import pandas as pd
import numpy as np
import hashlib
import re
import logging
from datetime import datetime
from abc import ABC, abstractmethod
import json
from pathlib import Path

# Try to import optional NLP dependencies
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

class BaseLegalTool(ABC):
    """Base class for all legal compliance tools"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"legal_tool.{name}")
    
    @abstractmethod
    async def execute(self, *args, **kwargs) -> Dict[str, Any]:
        """Execute the legal tool with given parameters"""
        pass
    
    def log_execution(self, params: Dict[str, Any], result: Dict[str, Any]):
        """Log tool execution for compliance tracking"""
        self.logger.info(f"Legal tool '{self.name}' executed with params: {params}")
        self.logger.debug(f"Legal tool result: {result}")

class DatasetFingerprintingTool(BaseLegalTool):
    """Tool for verifying dataset originality through content fingerprinting"""
    
    def __init__(self):
        super().__init__(
            name="dataset_fingerprinting",
            description="Verify dataset originality by checking against known public datasets using content fingerprinting"
        )
        
        # Initialize known dataset fingerprints database (would be loaded from external source in production)
        self.known_datasets = self._load_known_datasets()
        
    def _load_known_datasets(self) -> Dict[str, Dict[str, str]]:
        """Load known dataset fingerprints database"""
        # In production, this would load from a comprehensive database
        # For demo purposes, we'll create a sample database
        return {
            "iris_fingerprint_example": {
                "fingerprint": "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456",
                "source": "Kaggle",
                "name": "Iris Dataset",
                "url": "https://www.kaggle.com/datasets/uciml/iris",
                "license": "Public Domain"
            },
            "titanic_fingerprint_example": {
                "fingerprint": "b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef1234567a",
                "source": "Kaggle",
                "name": "Titanic Dataset",
                "url": "https://www.kaggle.com/c/titanic/data",
                "license": "Open Database License"
            },
            "housing_fingerprint_example": {
                "fingerprint": "c3d4e5f6789012345678901234567890abcdef1234567890abcdef1234567ab2",
                "source": "UCI ML Repository",
                "name": "California Housing Dataset",
                "url": "https://archive.ics.uci.edu/ml/datasets/california+housing",
                "license": "Public Domain"
            }
        }
    
    async def execute(self, data: pd.DataFrame, dataset_name: str = "unknown", **kwargs) -> Dict[str, Any]:
        """Generate dataset fingerprint and check against known datasets"""
        try:
            # Step 1: Generate dataset fingerprint
            self.logger.info("🔍 Generating dataset fingerprint...")
            fingerprint = self._generate_fingerprint(data)
            
            # Step 2: Check against known datasets
            self.logger.info("🔎 Checking against known dataset database...")
            match_result = self._check_against_known_datasets(fingerprint)
            
            # Step 3: Analyze dataset characteristics for additional verification
            characteristics = self._analyze_dataset_characteristics(data)
            
            # Step 4: Calculate originality score
            originality_score = self._calculate_originality_score(match_result, characteristics)
            
            # Step 5: Generate compliance assessment
            compliance_assessment = self._generate_compliance_assessment(match_result, originality_score)
            
            result = {
                "success": True,
                "dataset_fingerprint": fingerprint,
                "verification_status": match_result["status"],
                "originality_score": originality_score,
                "match_details": match_result,
                "dataset_characteristics": characteristics,
                "compliance_assessment": compliance_assessment,
                "recommendations": self._generate_fingerprint_recommendations(match_result, originality_score),
                "analysis_timestamp": datetime.now().isoformat()
            }
            
            self.log_execution({"dataset_shape": data.shape, "dataset_name": dataset_name}, 
                             {"status": match_result["status"], "originality_score": originality_score})
            return result
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": f"Dataset fingerprinting failed: {str(e)}",
                "dataset_fingerprint": None,
                "verification_status": "error"
            }
            self.log_execution({"dataset_shape": data.shape if data is not None else "unknown"}, error_result)
            return error_result
    
    def _generate_fingerprint(self, df: pd.DataFrame) -> str:
        """Generate format-agnostic fingerprint of dataset content"""
        try:
            # Step 1: Create a copy to avoid modifying original data
            df_normalized = df.copy()
            
            # Step 2: Handle missing values consistently
            df_normalized = df_normalized.fillna('__NULL__')
            
            # Step 3: Convert all columns to string for consistent hashing
            for col in df_normalized.columns:
                df_normalized[col] = df_normalized[col].astype(str)
            
            # Step 4: Sort columns alphabetically
            df_normalized = df_normalized.reindex(sorted(df_normalized.columns), axis=1)
            
            # Step 5: Sort rows by all columns to ensure consistent ordering
            df_normalized = df_normalized.sort_values(by=list(df_normalized.columns)).reset_index(drop=True)
            
            # Step 6: Create content string
            content_string = ""
            
            # Add column names and types
            for col in df_normalized.columns:
                content_string += f"COL:{col}|"
            
            # Add data rows
            for _, row in df_normalized.iterrows():
                row_string = "|".join(row.astype(str))
                content_string += f"ROW:{row_string}|"
            
            # Step 7: Generate SHA-256 hash
            fingerprint = hashlib.sha256(content_string.encode('utf-8')).hexdigest()
            
            return fingerprint
            
        except Exception as e:
            self.logger.error(f"Fingerprint generation failed: {e}")
            raise
    
    def _check_against_known_datasets(self, fingerprint: str) -> Dict[str, Any]:
        """Check fingerprint against known datasets database"""
        
        # Check for exact match
        for dataset_id, dataset_info in self.known_datasets.items():
            if dataset_info["fingerprint"] == fingerprint:
                return {
                    "status": "Known Public Dataset",
                    "match_type": "exact",
                    "confidence": 1.0,
                    "source_info": {
                        "source": dataset_info["source"],
                        "name": dataset_info["name"],
                        "url": dataset_info["url"],
                        "license": dataset_info.get("license", "Unknown")
                    },
                    "dataset_id": dataset_id
                }
        
        # Check for partial matches (first 16 characters for demo)
        fingerprint_prefix = fingerprint[:16]
        for dataset_id, dataset_info in self.known_datasets.items():
            if dataset_info["fingerprint"][:16] == fingerprint_prefix:
                return {
                    "status": "Potential Match",
                    "match_type": "partial",
                    "confidence": 0.7,
                    "source_info": {
                        "source": dataset_info["source"],
                        "name": dataset_info["name"],
                        "url": dataset_info["url"],
                        "license": dataset_info.get("license", "Unknown")
                    },
                    "dataset_id": dataset_id,
                    "note": "Partial fingerprint match - manual verification recommended"
                }
        
        # No match found
        return {
            "status": "Original",
            "match_type": "none",
            "confidence": 0.0,
            "source_info": None,
            "dataset_id": None
        }
    
    def _analyze_dataset_characteristics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze dataset characteristics for additional verification"""
        
        characteristics = {
            "shape": {
                "rows": int(df.shape[0]),
                "columns": int(df.shape[1])
            },
            "column_info": {
                "column_names": list(df.columns),
                "data_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
                "column_count_by_type": df.dtypes.value_counts().to_dict()
            },
            "data_profile": {
                "missing_values": int(df.isnull().sum().sum()),
                "duplicate_rows": int(df.duplicated().sum()),
                "unique_values_per_column": {col: int(df[col].nunique()) for col in df.columns}
            },
            "statistical_signature": self._generate_statistical_signature(df)
        }
        
        return characteristics
    
    def _generate_statistical_signature(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate statistical signature for additional verification"""
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) == 0:
            return {"note": "No numeric columns for statistical signature"}
        
        signature = {}
        
        for col in numeric_cols:
            col_stats = df[col].describe()
            signature[col] = {
                "mean": round(float(col_stats['mean']), 6),
                "std": round(float(col_stats['std']), 6),
                "min": round(float(col_stats['min']), 6),
                "max": round(float(col_stats['max']), 6),
                "median": round(float(col_stats['50%']), 6)
            }
        
        return signature
    
    def _calculate_originality_score(self, match_result: Dict, characteristics: Dict) -> float:
        """Calculate originality score (0-100)"""
        
        base_score = 100.0
        
        # Penalize based on match status
        if match_result["status"] == "Known Public Dataset":
            base_score = 0.0  # Exact match = no originality
        elif match_result["status"] == "Potential Match":
            base_score = 30.0  # Partial match = low originality
        
        # Adjust based on dataset characteristics (for original datasets)
        if match_result["status"] == "Original":
            shape = characteristics["shape"]
            
            # Bonus for reasonable dataset size
            if 100 <= shape["rows"] <= 100000 and 2 <= shape["columns"] <= 100:
                base_score += 0  # No penalty for reasonable size
            elif shape["rows"] < 10 or shape["columns"] < 2:
                base_score -= 20  # Penalty for very small datasets
            
            # Bonus for data quality
            missing_pct = (characteristics["data_profile"]["missing_values"] / 
                          (shape["rows"] * shape["columns"])) * 100
            
            if missing_pct < 5:
                base_score += 0  # No bonus for good quality (expected)
            elif missing_pct > 50:
                base_score -= 10  # Penalty for poor quality
        
        return max(0.0, min(100.0, base_score))
    
    def _generate_compliance_assessment(self, match_result: Dict, originality_score: float) -> Dict[str, Any]:
        """Generate legal compliance assessment"""
        
        assessment = {
            "legal_status": "Unknown",
            "risk_level": "Low",
            "license_requirements": [],
            "attribution_required": False,
            "commercial_use_allowed": "Unknown",
            "redistribution_allowed": "Unknown"
        }
        
        if match_result["status"] == "Known Public Dataset":
            source_info = match_result["source_info"]
            license_type = source_info.get("license", "Unknown")
            
            assessment.update({
                "legal_status": "Identified Public Dataset",
                "risk_level": "Medium" if license_type == "Unknown" else "Low",
                "source_license": license_type,
                "attribution_required": True,
                "source_attribution": f"Source: {source_info['name']} from {source_info['source']} ({source_info['url']})"
            })
            
            # License-specific requirements
            if "Public Domain" in license_type:
                assessment.update({
                    "commercial_use_allowed": "Yes",
                    "redistribution_allowed": "Yes",
                    "attribution_required": False
                })
            elif "Open Database" in license_type:
                assessment.update({
                    "commercial_use_allowed": "Yes",
                    "redistribution_allowed": "Yes",
                    "license_requirements": ["Must maintain same license", "Attribution required"]
                })
        
        elif match_result["status"] == "Potential Match":
            assessment.update({
                "legal_status": "Potential Public Dataset Match",
                "risk_level": "Medium",
                "license_requirements": ["Manual verification required", "Legal review recommended"]
            })
        
        else:  # Original
            assessment.update({
                "legal_status": "Appears Original",
                "risk_level": "Low",
                "commercial_use_allowed": "Subject to data source rights",
                "redistribution_allowed": "Subject to data source rights"
            })
        
        return assessment
    
    def _generate_fingerprint_recommendations(self, match_result: Dict, originality_score: float) -> List[str]:
        """Generate recommendations based on fingerprinting results"""
        
        recommendations = []
        
        if match_result["status"] == "Known Public Dataset":
            source_info = match_result["source_info"]
            recommendations.extend([
                f"🔍 Identified as known public dataset: {source_info['name']}",
                f"📜 Check license requirements: {source_info.get('license', 'License unknown')}",
                f"🔗 Original source: {source_info['url']}",
                "⚖️ Ensure proper attribution if using this dataset",
                "📋 Document dataset provenance in your research"
            ])
        
        elif match_result["status"] == "Potential Match":
            recommendations.extend([
                "🔍 Partial match detected - manual verification recommended",
                "👨‍💼 Consider legal review before commercial use",
                "📝 Document verification process for compliance",
                "🔗 Check original source for licensing requirements"
            ])
        
        else:  # Original
            if originality_score >= 80:
                recommendations.extend([
                    "✅ Dataset appears original with high confidence",
                    "📊 Consider publishing with proper documentation",
                    "🔒 Implement appropriate access controls if sensitive"
                ])
            elif originality_score >= 60:
                recommendations.extend([
                    "⚠️ Dataset appears original but verify data sources",
                    "📝 Document data collection methodology",
                    "🔍 Conduct additional provenance checks"
                ])
            else:
                recommendations.extend([
                    "⚠️ Low originality score - investigate data sources",
                    "🔍 Conduct thorough provenance verification",
                    "👨‍💼 Consider legal review before publication"
                ])
        
        # General recommendations
        recommendations.extend([
            "📋 Maintain fingerprint records for future verification",
            "🔄 Re-verify if dataset is modified or updated"
        ])
        
        return recommendations

class PIIScannerTool(BaseLegalTool):
    """Tool for detecting Personally Identifiable Information (PII) in datasets"""
    
    def __init__(self):
        super().__init__(
            name="pii_scanner",
            description="Automatically detect sensitive personal data for privacy protection and compliance"
        )
        
        # Initialize PII detection patterns
        self.pii_patterns = self._initialize_pii_patterns()
        
        # Load NER model if available
        self.nlp_model = self._load_ner_model()
    
    def _initialize_pii_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize regex patterns for PII detection"""
        
        patterns = {
            "email": {
                "pattern": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                "risk_level": "High",
                "description": "Email addresses"
            },
            "phone_international": {
                "pattern": r'(\+\d{1,3}\s?)?\(?\d{1,4}\)?[\s.-]?\d{1,4}[\s.-]?\d{1,4}[\s.-]?\d{1,9}',
                "risk_level": "High",
                "description": "Phone numbers (international format)"
            },
            "phone_us": {
                "pattern": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
                "risk_level": "High",
                "description": "US phone numbers"
            },
            "ssn_us": {
                "pattern": r'\b\d{3}-\d{2}-\d{4}\b',
                "risk_level": "Critical",
                "description": "US Social Security Numbers"
            },
            "credit_card": {
                "pattern": r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
                "risk_level": "Critical",
                "description": "Credit card numbers"
            },
            "ip_address": {
                "pattern": r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
                "risk_level": "Medium",
                "description": "IP addresses"
            },
            "aadhaar_india": {
                "pattern": r'\b\d{4}\s?\d{4}\s?\d{4}\b',
                "risk_level": "Critical",
                "description": "Indian Aadhaar numbers"
            },
            "pan_india": {
                "pattern": r'\b[A-Z]{5}\d{4}[A-Z]{1}\b',
                "risk_level": "High",
                "description": "Indian PAN numbers"
            },
            "passport": {
                "pattern": r'\b[A-Z]{1,2}\d{6,9}\b',
                "risk_level": "Critical",
                "description": "Passport numbers"
            },
            "bank_account": {
                "pattern": r'\b\d{8,17}\b',
                "risk_level": "Critical",
                "description": "Bank account numbers (potential)"
            },
            "date_of_birth": {
                "pattern": r'\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{2,4}[/-]\d{1,2}[/-]\d{1,2})\b',
                "risk_level": "Medium",
                "description": "Date of birth patterns"
            },
            "postal_code_us": {
                "pattern": r'\b\d{5}(?:-\d{4})?\b',
                "risk_level": "Low",
                "description": "US postal codes"
            },
            "postal_code_uk": {
                "pattern": r'\b[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}\b',
                "risk_level": "Low",
                "description": "UK postal codes"
            }
        }
        
        return patterns
    
    def _load_ner_model(self):
        """Load Named Entity Recognition model for advanced PII detection"""
        
        if not SPACY_AVAILABLE:
            self.logger.warning("SpaCy not available - using regex patterns only")
            return None
        
        try:
            # Try to load English model
            nlp = spacy.load("en_core_web_sm")
            self.logger.info("✅ SpaCy NER model loaded successfully")
            return nlp
        except Exception as e:
            self.logger.warning(f"Could not load SpaCy model: {e}")
            return None
    
    async def execute(self, data: pd.DataFrame, column_subset: List[str] = None, 
                     include_ner: bool = True, **kwargs) -> Dict[str, Any]:
        """Scan dataset for PII and generate risk assessment"""
        
        try:
            # Step 1: Determine columns to scan
            columns_to_scan = column_subset if column_subset else list(data.columns)
            self.logger.info(f"🔍 Scanning {len(columns_to_scan)} columns for PII...")
            
            # Step 2: Pattern-based PII detection
            pattern_results = self._scan_with_patterns(data, columns_to_scan)
            
            # Step 3: NER-based detection (if available and requested)
            ner_results = {}
            if include_ner and self.nlp_model:
                self.logger.info("🧠 Running NER-based PII detection...")
                ner_results = self._scan_with_ner(data, columns_to_scan)
            
            # Step 4: Combine results and calculate risk score
            combined_results = self._combine_detection_results(pattern_results, ner_results)
            risk_assessment = self._calculate_pii_risk(combined_results, data.shape[0])
            
            # Step 5: Generate recommendations
            recommendations = self._generate_pii_recommendations(combined_results, risk_assessment)
            
            # Step 6: Generate compliance report
            compliance_report = self._generate_pii_compliance_report(combined_results, risk_assessment)
            
            result = {
                "success": True,
                "pii_risk_score": risk_assessment["overall_score"],
                "risk_level": risk_assessment["risk_level"],
                "columns_scanned": len(columns_to_scan),
                "pii_detections": combined_results,
                "risk_assessment": risk_assessment,
                "compliance_report": compliance_report,
                "recommendations": recommendations,
                "analysis_timestamp": datetime.now().isoformat(),
                "detection_methods": {
                    "pattern_matching": True,
                    "ner_detection": include_ner and self.nlp_model is not None
                }
            }
            
            self.log_execution({
                "columns_scanned": len(columns_to_scan),
                "include_ner": include_ner
            }, {
                "risk_level": risk_assessment["risk_level"],
                "pii_columns_found": len([col for col, data in combined_results.items() if data["total_detections"] > 0])
            })
            
            return result
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": f"PII scanning failed: {str(e)}",
                "pii_risk_score": 0,
                "risk_level": "Unknown"
            }
            self.log_execution({"columns_scanned": len(columns_to_scan) if columns_to_scan else 0}, error_result)
            return error_result
    
    def _scan_with_patterns(self, df: pd.DataFrame, columns: List[str]) -> Dict[str, Any]:
        """Scan dataset using regex patterns"""
        
        results = {}
        
        for column in columns:
            if column not in df.columns:
                continue
            
            column_results = {
                "pattern_detections": {},
                "total_detections": 0,
                "detection_rate": 0.0,
                "risk_level": "Low",
                "samples": []
            }
            
            # Convert column to string for pattern matching
            column_data = df[column].astype(str)
            non_null_count = column_data.notna().sum()
            
            if non_null_count == 0:
                results[column] = column_results
                continue
            
            # Test each pattern
            for pattern_name, pattern_info in self.pii_patterns.items():
                pattern = pattern_info["pattern"]
                matches = []
                
                for idx, value in column_data.items():
                    if pd.isna(value) or value == 'nan':
                        continue
                    
                    found_matches = re.findall(pattern, str(value))
                    if found_matches:
                        matches.extend([(idx, match) for match in found_matches])
                
                if matches:
                    # Store up to 3 sample matches (anonymized)
                    samples = [self._anonymize_sample(match[1]) for match in matches[:3]]
                    
                    column_results["pattern_detections"][pattern_name] = {
                        "count": len(matches),
                        "pattern_description": pattern_info["description"],
                        "risk_level": pattern_info["risk_level"],
                        "detection_rate": round((len(matches) / non_null_count) * 100, 2),
                        "samples": samples
                    }
                    
                    column_results["total_detections"] += len(matches)
            
            # Calculate overall column metrics
            if column_results["total_detections"] > 0:
                column_results["detection_rate"] = round(
                    (column_results["total_detections"] / non_null_count) * 100, 2
                )
                column_results["risk_level"] = self._determine_column_risk_level(
                    column_results["pattern_detections"]
                )
            
            results[column] = column_results
        
        return results
    
    def _scan_with_ner(self, df: pd.DataFrame, columns: List[str]) -> Dict[str, Any]:
        """Scan dataset using Named Entity Recognition"""
        
        if not self.nlp_model:
            return {}
        
        results = {}
        
        # Entity types that indicate PII
        pii_entities = {
            "PERSON": {"risk_level": "High", "description": "Person names"},
            "ORG": {"risk_level": "Medium", "description": "Organizations"},
            "GPE": {"risk_level": "Medium", "description": "Geopolitical entities (cities, countries)"},
            "LOC": {"risk_level": "Medium", "description": "Locations"},
            "MONEY": {"risk_level": "Medium", "description": "Monetary values"},
            "DATE": {"risk_level": "Low", "description": "Dates"},
            "TIME": {"risk_level": "Low", "description": "Times"}
        }
        
        for column in columns:
            if column not in df.columns:
                continue
            
            column_results = {
                "ner_detections": {},
                "total_entities": 0,
                "entity_rate": 0.0,
                "risk_level": "Low"
            }
            
            # Sample up to 100 non-null text values for NER processing
            column_data = df[column].dropna().astype(str)
            if len(column_data) == 0:
                results[column] = column_results
                continue
            
            sample_data = column_data.sample(min(100, len(column_data)), random_state=42)
            
            entity_counts = {}
            total_entities = 0
            
            for text in sample_data:
                if len(str(text)) > 1000:  # Skip very long texts for performance
                    text = str(text)[:1000]
                
                try:
                    doc = self.nlp_model(str(text))
                    
                    for ent in doc.ents:
                        if ent.label_ in pii_entities:
                            if ent.label_ not in entity_counts:
                                entity_counts[ent.label_] = {
                                    "count": 0,
                                    "samples": [],
                                    "risk_level": pii_entities[ent.label_]["risk_level"],
                                    "description": pii_entities[ent.label_]["description"]
                                }
                            
                            entity_counts[ent.label_]["count"] += 1
                            
                            # Store anonymized samples
                            if len(entity_counts[ent.label_]["samples"]) < 3:
                                entity_counts[ent.label_]["samples"].append(
                                    self._anonymize_sample(ent.text)
                                )
                            
                            total_entities += 1
                
                except Exception as e:
                    self.logger.warning(f"NER processing failed for text: {e}")
                    continue
            
            # Calculate rates and risk
            if total_entities > 0:
                column_results["ner_detections"] = entity_counts
                column_results["total_entities"] = total_entities
                column_results["entity_rate"] = round((total_entities / len(sample_data)) * 100, 2)
                column_results["risk_level"] = self._determine_ner_risk_level(entity_counts)
            
            results[column] = column_results
        
        return results
    
    def _combine_detection_results(self, pattern_results: Dict, ner_results: Dict) -> Dict[str, Any]:
        """Combine pattern and NER detection results"""
        
        combined = {}
        all_columns = set(pattern_results.keys()) | set(ner_results.keys())
        
        for column in all_columns:
            pattern_data = pattern_results.get(column, {})
            ner_data = ner_results.get(column, {})
            
            combined[column] = {
                "pattern_detections": pattern_data.get("pattern_detections", {}),
                "ner_detections": ner_data.get("ner_detections", {}),
                "total_detections": pattern_data.get("total_detections", 0),
                "total_entities": ner_data.get("total_entities", 0),
                "detection_rate": pattern_data.get("detection_rate", 0.0),
                "entity_rate": ner_data.get("entity_rate", 0.0),
                "combined_risk_level": self._combine_risk_levels(
                    pattern_data.get("risk_level", "Low"),
                    ner_data.get("risk_level", "Low")
                )
            }
        
        return combined
    
    def _calculate_pii_risk(self, combined_results: Dict, total_rows: int) -> Dict[str, Any]:
        """Calculate overall PII risk assessment"""
        
        risk_scores = {
            "Critical": 10,
            "High": 7,
            "Medium": 4,
            "Low": 1
        }
        
        total_score = 0
        max_possible_score = 0
        
        columns_with_pii = 0
        critical_columns = 0
        high_risk_columns = 0
        
        risk_breakdown = {
            "Critical": 0,
            "High": 0,
            "Medium": 0,
            "Low": 0
        }
        
        for column, data in combined_results.items():
            column_risk = data["combined_risk_level"]
            
            if data["total_detections"] > 0 or data["total_entities"] > 0:
                columns_with_pii += 1
                total_score += risk_scores[column_risk]
                risk_breakdown[column_risk] += 1
                
                if column_risk == "Critical":
                    critical_columns += 1
                elif column_risk == "High":
                    high_risk_columns += 1
            
            max_possible_score += risk_scores["Critical"]  # Assuming worst case
        
        # Calculate normalized risk score (0-100)
        if max_possible_score > 0:
            normalized_score = min(100, (total_score / max_possible_score) * 100)
        else:
            normalized_score = 0
        
        # Determine overall risk level
        if critical_columns > 0 or normalized_score >= 70:
            overall_risk = "High"
        elif high_risk_columns > 0 or normalized_score >= 40:
            overall_risk = "Medium"
        elif columns_with_pii > 0:
            overall_risk = "Low"
        else:
            overall_risk = "Minimal"
        
        return {
            "overall_score": round(normalized_score, 1),
            "risk_level": overall_risk,
            "columns_with_pii": columns_with_pii,
            "critical_columns": critical_columns,
            "high_risk_columns": high_risk_columns,
            "total_columns_scanned": len(combined_results),
            "risk_breakdown": risk_breakdown,
            "pii_density": round((columns_with_pii / len(combined_results)) * 100, 1) if combined_results else 0
        }
    
    def _determine_column_risk_level(self, pattern_detections: Dict) -> str:
        """Determine risk level for a column based on pattern detections"""
        
        if not pattern_detections:
            return "Low"
        
        risk_levels = [info["risk_level"] for info in pattern_detections.values()]
        
        if "Critical" in risk_levels:
            return "Critical"
        elif "High" in risk_levels:
            return "High"
        elif "Medium" in risk_levels:
            return "Medium"
        else:
            return "Low"
    
    def _determine_ner_risk_level(self, entity_counts: Dict) -> str:
        """Determine risk level based on NER entities"""
        
        if not entity_counts:
            return "Low"
        
        # High risk if person names are detected
        if "PERSON" in entity_counts and entity_counts["PERSON"]["count"] > 0:
            return "High"
        
        # Medium risk for other PII entities
        if any(count_info["count"] > 0 for count_info in entity_counts.values()):
            return "Medium"
        
        return "Low"
    
    def _combine_risk_levels(self, pattern_risk: str, ner_risk: str) -> str:
        """Combine risk levels from pattern and NER detection"""
        
        risk_hierarchy = ["Critical", "High", "Medium", "Low"]
        
        pattern_idx = risk_hierarchy.index(pattern_risk) if pattern_risk in risk_hierarchy else 3
        ner_idx = risk_hierarchy.index(ner_risk) if ner_risk in risk_hierarchy else 3
        
        # Return the higher risk level
        return risk_hierarchy[min(pattern_idx, ner_idx)]
    
    def _anonymize_sample(self, sample: str) -> str:
        """Anonymize sample data for reporting"""
        
        if len(sample) <= 2:
            return "*" * len(sample)
        
        # Show first and last character, mask the middle
        return sample[0] + "*" * (len(sample) - 2) + sample[-1]
    
    def _generate_pii_compliance_report(self, combined_results: Dict, risk_assessment: Dict) -> Dict[str, Any]:
        """Generate PII compliance report"""
        
        gdpr_compliance = {
            "requires_consent": risk_assessment["columns_with_pii"] > 0,
            "requires_anonymization": risk_assessment["critical_columns"] > 0,
            "data_subject_rights": risk_assessment["columns_with_pii"] > 0,
            "breach_notification_required": risk_assessment["critical_columns"] > 0
        }
        
        ccpa_compliance = {
            "personal_information_present": risk_assessment["columns_with_pii"] > 0,
            "sensitive_personal_information": risk_assessment["critical_columns"] > 0,
            "consumer_rights_applicable": risk_assessment["columns_with_pii"] > 0
        }
        
        return {
            "gdpr_assessment": gdpr_compliance,
            "ccpa_assessment": ccpa_compliance,
            "recommended_actions": self._get_compliance_actions(risk_assessment),
            "data_protection_measures": self._recommend_protection_measures(risk_assessment)
        }
    
    def _get_compliance_actions(self, risk_assessment: Dict) -> List[str]:
        """Get recommended compliance actions"""
        
        actions = []
        
        if risk_assessment["critical_columns"] > 0:
            actions.extend([
                "Implement immediate data anonymization for critical PII",
                "Establish data access controls and audit trails",
                "Conduct privacy impact assessment (PIA)"
            ])
        
        if risk_assessment["high_risk_columns"] > 0:
            actions.extend([
                "Review data collection justification",
                "Implement pseudonymization techniques",
                "Establish data retention policies"
            ])
        
        if risk_assessment["columns_with_pii"] > 0:
            actions.extend([
                "Document data processing activities",
                "Establish privacy notices and consent mechanisms",
                "Train staff on data protection requirements"
            ])
        
        return actions
    
    def _recommend_protection_measures(self, risk_assessment: Dict) -> List[str]:
        """Recommend data protection measures"""
        
        measures = []
        
        risk_level = risk_assessment["risk_level"]
        
        if risk_level in ["High", "Critical"]:
            measures.extend([
                "🔒 Implement encryption at rest and in transit",
                "🔐 Use strong access controls and authentication",
                "📝 Maintain detailed audit logs",
                "🛡️ Regular security assessments"
            ])
        
        if risk_level in ["Medium", "High", "Critical"]:
            measures.extend([
                "🎭 Apply data masking for non-production environments",
                "📊 Implement data loss prevention (DLP) tools",
                "⏰ Establish automated data retention policies"
            ])
        
        measures.extend([
            "📋 Regular privacy compliance reviews",
            "🎓 Staff training on data protection",
            "📞 Incident response procedures"
        ])
        
        return measures
    
    def _generate_pii_recommendations(self, combined_results: Dict, risk_assessment: Dict) -> List[str]:
        """Generate PII-specific recommendations"""
        
        recommendations = []
        
        risk_level = risk_assessment["risk_level"]
        
        if risk_level == "High":
            recommendations.extend([
                "🚨 HIGH RISK: Immediate action required for PII protection",
                "🔒 Implement data anonymization before any sharing or processing",
                "👨‍💼 Conduct legal review for compliance requirements",
                "📋 Establish data governance procedures"
            ])
        elif risk_level == "Medium":
            recommendations.extend([
                "⚠️ MEDIUM RISK: Review PII handling procedures",
                "🎭 Consider pseudonymization techniques",
                "📝 Document data processing justification",
                "🔍 Regular PII scanning recommended"
            ])
        elif risk_level == "Low":
            recommendations.extend([
                "✅ LOW RISK: Basic PII protection measures sufficient",
                "📊 Monitor for additional PII in future data updates",
                "📋 Maintain current privacy practices"
            ])
        else:
            recommendations.extend([
                "✅ MINIMAL RISK: No immediate PII concerns detected",
                "🔄 Regular scanning recommended for new data"
            ])
        
        # Specific recommendations based on detected PII types
        for column, data in combined_results.items():
            if data["total_detections"] > 0:
                high_risk_patterns = [
                    pattern for pattern, info in data["pattern_detections"].items()
                    if info["risk_level"] in ["Critical", "High"]
                ]
                
                if high_risk_patterns:
                    recommendations.append(
                        f"🎯 Column '{column}': Contains {', '.join(high_risk_patterns)} - prioritize for protection"
                    )
        
        # General recommendations
        recommendations.extend([
            "📖 Review privacy policies and consent mechanisms",
            "🔄 Implement regular PII scanning procedures",
            "📚 Maintain PII inventory and data mapping"
        ])
        
        return recommendations

# Legal Tools Registry
class LegalToolRegistry:
    """Registry for managing legal compliance tools"""
    
    def __init__(self):
        self.tools = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register all default legal tools"""
        self.register_tool(DatasetFingerprintingTool())
        self.register_tool(PIIScannerTool())
    
    def register_tool(self, tool: BaseLegalTool):
        """Register a new legal tool"""
        self.tools[tool.name] = tool
    
    def get_tool(self, name: str) -> Optional[BaseLegalTool]:
        """Get a legal tool by name"""
        return self.tools.get(name)
    
    def list_tools(self) -> Dict[str, str]:
        """List all available legal tools"""
        return {name: tool.description for name, tool in self.tools.items()}
    
    async def execute_tool(self, tool_name: str, *args, **kwargs) -> Dict[str, Any]:
        """Execute a legal tool by name"""
        tool = self.get_tool(tool_name)
        if not tool:
            return {
                "success": False,
                "error": f"Legal tool '{tool_name}' not found. Available tools: {list(self.tools.keys())}"
            }
        
        return await tool.execute(*args, **kwargs)

# Global legal tools registry instance
legal_tool_registry = LegalToolRegistry()

# Export for external use
__all__ = [
    'BaseLegalTool',
    'DatasetFingerprintingTool', 
    'PIIScannerTool',
    'LegalToolRegistry',
    'legal_tool_registry'
]
