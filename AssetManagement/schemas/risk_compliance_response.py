"""
Risk Compliance Response Schema

This module defines the Pydantic model for Risk & Compliance Agent responses.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from .research_response import ProvenanceMetadata


class ComplianceStatus(str, Enum):
    """Compliance verdict status"""
    COMPLIANT = "COMPLIANT"
    NON_COMPLIANT = "NON_COMPLIANT"
    UNRESOLVED = "UNRESOLVED"


class ViolationSeverity(str, Enum):
    """Severity of compliance violation"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class DriftAnalysis(BaseModel):
    """Portfolio drift analysis"""
    overall_drift_percentage: float = Field(..., description="Overall portfolio drift percentage")
    drift_by_asset_class: Dict[str, float] = Field(..., description="Drift percentage by asset class")
    largest_drift_asset_class: str = Field(..., description="Asset class with largest drift")
    largest_drift_percentage: float = Field(..., description="Largest drift percentage")
    drift_threshold_exceeded: bool = Field(..., description="Whether drift exceeds configured threshold")
    drift_threshold: float = Field(..., description="Configured drift threshold")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence in drift calculation (0-1)")


class RiskMetric(BaseModel):
    """Individual risk metric"""
    metric_name: str = Field(..., description="Name of the risk metric (e.g., concentration, volatility, correlation)")
    metric_value: float = Field(..., description="Calculated value of the metric")
    metric_threshold: Optional[float] = Field(None, description="Threshold for the metric if applicable")
    threshold_exceeded: bool = Field(..., description="Whether the metric exceeds threshold")
    metric_description: str = Field(..., description="Description of what the metric measures")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence in the metric calculation (0-1)")


class ComplianceViolation(BaseModel):
    """Individual compliance violation"""
    violation_id: str = Field(..., description="Unique identifier for the violation")
    violation_type: str = Field(..., description="Type of violation (mandate, suitability, policy, regulatory)")
    rule_id: str = Field(..., description="Identifier of the rule that was violated")
    rule_description: str = Field(..., description="Description of the rule")
    violation_description: str = Field(..., description="Description of how the rule was violated")
    severity: ViolationSeverity = Field(..., description="Severity of the violation")
    affected_securities: Optional[List[str]] = Field(None, description="Securities affected by the violation")
    affected_asset_classes: Optional[List[str]] = Field(None, description="Asset classes affected by the violation")
    remediation_suggestion: Optional[str] = Field(None, description="Suggested remediation for the violation")
    blocking: bool = Field(..., description="Whether this violation blocks approval")


class ComplianceCheck(BaseModel):
    """Individual compliance check result"""
    check_id: str = Field(..., description="Unique identifier for the check")
    check_name: str = Field(..., description="Name of the compliance check")
    check_type: str = Field(..., description="Type of check (mandate, suitability, policy, regulatory)")
    check_result: str = Field(..., description="Result of the check (passed, failed, inconclusive)")
    check_description: str = Field(..., description="Description of what was checked")
    evidence: Optional[Dict[str, Any]] = Field(None, description="Evidence supporting the check result")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence in the check result (0-1)")


class ComplianceVerdict(BaseModel):
    """Overall compliance verdict"""
    status: ComplianceStatus = Field(..., description="Overall compliance status")
    violations: List[ComplianceViolation] = Field(default_factory=list, description="List of violations if any")
    violations_count: int = Field(..., ge=0, description="Total number of violations")
    critical_violations_count: int = Field(..., ge=0, description="Number of critical violations")
    blocking_violations_count: int = Field(..., ge=0, description="Number of blocking violations")
    compliance_checks: List[ComplianceCheck] = Field(..., description="List of all compliance checks performed")
    compliance_checks_passed: int = Field(..., ge=0, description="Number of checks passed")
    compliance_checks_failed: int = Field(..., ge=0, description="Number of checks failed")
    compliance_checks_inconclusive: int = Field(..., ge=0, description="Number of checks inconclusive")
    verdict_summary: str = Field(..., description="Human-readable summary of the verdict")
    confidence_score: float = Field(..., ge=0, le=1, description="Overall confidence in the verdict (0-1)")


class RiskComplianceEvidence(BaseModel):
    """Evidence supporting risk and compliance findings"""
    evidence_type: str = Field(..., description="Type of evidence (calculation, rule_check, data_point, analysis)")
    evidence_description: str = Field(..., description="Description of the evidence")
    evidence_data: Optional[Dict[str, Any]] = Field(None, description="Structured evidence data")
    deterministic: bool = Field(..., description="Whether this is a deterministic finding or model-assisted")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence in this evidence (0-1)")
    provenance: ProvenanceMetadata = Field(..., description="Provenance metadata for this evidence")


class RiskComplianceResponse(BaseModel):
    """
    Response from the Risk & Compliance Agent containing drift analysis, risk metrics, and compliance verdict.
    
    This schema represents the output of risk and compliance analysis.
    """
    request_id: str = Field(..., description="Unique identifier for the request")
    session_id: str = Field(..., description="Session identifier")
    trace_id: str = Field(..., description="Trace identifier for observability")
    timestamp: datetime = Field(..., description="Response timestamp")
    agent_version: str = Field(..., description="Risk & Compliance agent version")
    schema_version: str = Field("1.0.0", pattern=r"^[0-9]+\.[0-9]+\.[0-9]+$", description="Schema version")
    
    # Drift analysis
    drift_analysis: DriftAnalysis = Field(..., description="Portfolio drift analysis")
    
    # Risk metrics
    risk_metrics: List[RiskMetric] = Field(..., description="Calculated risk metrics")
    risk_metrics_summary: str = Field(..., description="Human-readable summary of risk metrics")
    
    # Compliance verdict
    compliance_verdict: ComplianceVerdict = Field(..., description="Overall compliance verdict")
    
    # Evidence
    evidence: List[RiskComplianceEvidence] = Field(..., description="Supporting evidence for findings")
    
    # Quality indicators
    overall_confidence_score: float = Field(..., ge=0, le=1, description="Overall confidence in analysis (0-1)")
    
    # Provenance
    provenance_metadata: ProvenanceMetadata = Field(..., description="Overall provenance metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "req-12345",
                "session_id": "sess-67890",
                "trace_id": "trace-abcdef",
                "timestamp": "2024-01-15T10:30:00Z",
                "agent_version": "1.0.0",
                "schema_version": "1.0.0",
                "drift_analysis": {
                    "overall_drift_percentage": 5.2,
                    "drift_by_asset_class": {
                        "equities": 3.5,
                        "fixed_income": -2.0,
                        "cash": -1.5
                    },
                    "largest_drift_asset_class": "equities",
                    "largest_drift_percentage": 3.5,
                    "drift_threshold_exceeded": True,
                    "drift_threshold": 5.0,
                    "confidence_score": 1.0
                },
                "risk_metrics": [
                    {
                        "metric_name": "single_security_concentration",
                        "metric_value": 8.5,
                        "metric_threshold": 10.0,
                        "threshold_exceeded": False,
                        "metric_description": "Maximum percentage of portfolio in a single security",
                        "confidence_score": 1.0
                    },
                    {
                        "metric_name": "sector_concentration",
                        "metric_value": 22.0,
                        "metric_threshold": 25.0,
                        "threshold_exceeded": False,
                        "metric_description": "Maximum percentage of portfolio in a single sector",
                        "confidence_score": 1.0
                    }
                ],
                "risk_metrics_summary": "All risk metrics within acceptable thresholds",
                "compliance_verdict": {
                    "status": "COMPLIANT",
                    "violations": [],
                    "violations_count": 0,
                    "critical_violations_count": 0,
                    "blocking_violations_count": 0,
                    "compliance_checks": [
                        {
                            "check_id": "check-001",
                            "check_name": "mandate_concentration_check",
                            "check_type": "mandate",
                            "check_result": "passed",
                            "check_description": "Verify single security concentration within mandate limits",
                            "confidence_score": 1.0
                        }
                    ],
                    "compliance_checks_passed": 5,
                    "compliance_checks_failed": 0,
                    "compliance_checks_inconclusive": 0,
                    "verdict_summary": "All compliance checks passed. Portfolio complies with all mandates and policies.",
                    "confidence_score": 1.0
                },
                "evidence": [
                    {
                        "evidence_type": "calculation",
                        "evidence_description": "Drift calculation based on current vs target allocation",
                        "deterministic": True,
                        "confidence_score": 1.0,
                        "provenance": {
                            "source_type": "risk_compliance_agent",
                            "source_identifier": "drift_calculator",
                            "retrieval_timestamp": "2024-01-15T10:30:00Z",
                            "data_freshness_timestamp": "2024-01-15T10:30:00Z",
                            "transformation_stage": "derived",
                            "confidence_score": 1.0
                        }
                    }
                ],
                "overall_confidence_score": 1.0,
                "provenance_metadata": {
                    "source_type": "risk_compliance_agent",
                    "source_identifier": "risk-compliance-agent-v1",
                    "retrieval_timestamp": "2024-01-15T10:30:00Z",
                    "data_freshness_timestamp": "2024-01-15T10:30:00Z",
                    "transformation_stage": "derived",
                    "confidence_score": 1.0
                }
            }
        }
