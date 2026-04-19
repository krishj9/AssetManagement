"""
Supervisor Response Schema

This module defines the Pydantic model for supervisor agent responses.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class WorkflowState(str, Enum):
    """Workflow quality state"""
    NORMAL = "NORMAL"
    DEGRADED = "DEGRADED"
    LOW_CONFIDENCE = "LOW_CONFIDENCE"
    BLOCKED = "BLOCKED"


class StructuredError(BaseModel):
    """Structured error object"""
    code: str = Field(..., description="Error code (e.g., INVALID_REQUEST, VALIDATION_ERROR, GUARDRAIL_VIOLATION)")
    message: str = Field(..., description="Human-readable error message")
    severity: str = Field(..., description="Error severity (ERROR, WARNING, INFO)")
    retryable: bool = Field(..., description="Whether the error is retryable")
    source_agent: Optional[str] = Field(None, description="Agent that generated the error")
    request_id: Optional[str] = Field(None, description="Request ID for correlation")
    trace_id: Optional[str] = Field(None, description="Trace ID for correlation")
    timestamp: Optional[datetime] = Field(None, description="Timestamp when error occurred")
    related_context: Optional[Dict[str, Any]] = Field(None, description="Additional context about the error")


class RecommendationQualityMetadata(BaseModel):
    """Quality metadata for recommendations"""
    overall_confidence: float = Field(..., ge=0, le=1, description="Overall confidence score (0-1)")
    workflow_state: WorkflowState = Field(..., description="Workflow quality state")
    contributing_agents: List[str] = Field(..., description="Agents that contributed to the recommendation")
    missing_evidence: Optional[List[str]] = Field(None, description="List of missing evidence items")
    stale_data_flags: Optional[List[str]] = Field(None, description="List of stale data indicators")
    unresolved_controls: Optional[List[str]] = Field(None, description="List of unresolved control checks")
    advisory_completeness: float = Field(..., ge=0, le=1, description="Completeness score for advisory content (0-1)")
    approval_eligibility: bool = Field(..., description="Whether the recommendation is eligible for approval")


class ComplianceVerdict(BaseModel):
    """Compliance verdict from Risk & Compliance Agent"""
    status: str = Field(..., description="Compliance status (COMPLIANT, NON_COMPLIANT, UNRESOLVED)")
    violations: Optional[List[Dict[str, Any]]] = Field(None, description="List of compliance violations if any")
    evidence: Optional[Dict[str, Any]] = Field(None, description="Evidence supporting the verdict")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence in the verdict (0-1)")


class TradeProposal(BaseModel):
    """Individual trade proposal"""
    trade_id: str = Field(..., description="Unique identifier for the trade")
    security_id: str = Field(..., description="Security identifier")
    security_name: str = Field(..., description="Security name")
    action: str = Field(..., description="Trade action (buy, sell)")
    quantity: float = Field(..., ge=0, description="Quantity to trade")
    estimated_price: float = Field(..., ge=0, description="Estimated execution price")
    estimated_cost: Optional[float] = Field(None, description="Estimated transaction cost")
    tax_impact: Optional[float] = Field(None, description="Estimated tax impact")
    rationale: str = Field(..., description="Rationale for the trade")
    evidence: Optional[Dict[str, Any]] = Field(None, description="Supporting evidence")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence in the proposal (0-1)")


class MemorySummary(BaseModel):
    """Summary of retrieved memory"""
    memory_items_count: int = Field(..., ge=0, description="Number of memory items retrieved")
    memory_categories: List[str] = Field(..., description="Categories of memory retrieved")
    conflicts_detected: bool = Field(..., description="Whether conflicts were detected")
    confidence_score: float = Field(..., ge=0, le=1, description="Overall confidence in memory (0-1)")
    summary: Optional[str] = Field(None, description="Human-readable summary of memory context")


class ResearchSummary(BaseModel):
    """Summary of research findings"""
    market_data_freshness: datetime = Field(..., description="Timestamp of market data")
    sentiment_summary: Optional[str] = Field(None, description="Market sentiment summary")
    degraded_mode: bool = Field(False, description="Whether research is in degraded mode")
    degraded_mode_reason: Optional[str] = Field(None, description="Reason for degraded mode if applicable")
    confidence_score: float = Field(..., ge=0, le=1, description="Overall confidence in research (0-1)")


class RiskAnalysisSummary(BaseModel):
    """Summary of risk analysis"""
    drift_percentage: float = Field(..., description="Portfolio drift percentage")
    risk_metrics: Dict[str, float] = Field(..., description="Risk metrics (concentration, volatility, etc.)")
    compliance_verdict: ComplianceVerdict = Field(..., description="Compliance verdict")
    confidence_score: float = Field(..., ge=0, le=1, description="Overall confidence in risk analysis (0-1)")


class RecommendationPackage(BaseModel):
    """Consolidated recommendation package from all agents"""
    portfolio_summary: Dict[str, Any] = Field(..., description="Portfolio summary")
    current_vs_target_allocation: Dict[str, Any] = Field(..., description="Current vs target allocation comparison")
    research_summary: ResearchSummary = Field(..., description="Research findings summary")
    memory_summary: MemorySummary = Field(..., description="Memory context summary")
    risk_analysis_summary: RiskAnalysisSummary = Field(..., description="Risk analysis summary")
    trade_proposals: List[TradeProposal] = Field(..., description="List of trade proposals")
    recommendation_rationale: str = Field(..., description="Overall recommendation rationale")
    quality_metadata: RecommendationQualityMetadata = Field(..., description="Quality metadata")


class SupervisorResponse(BaseModel):
    """
    Response from the Supervisor Agent after orchestrating collaborator agents.
    
    This is the primary output schema for the portfolio rebalancing workflow.
    """
    request_id: str = Field(..., description="Unique identifier for the request")
    session_id: str = Field(..., description="Session identifier")
    trace_id: str = Field(..., description="Trace identifier for observability")
    timestamp: datetime = Field(..., description="Response timestamp")
    agent_version: str = Field(..., description="Supervisor agent version")
    schema_version: str = Field("1.0.0", pattern=r"^[0-9]+\.[0-9]+\.[0-9]+$", description="Schema version")
    policy_version: str = Field(..., description="Policy version used")
    environment_alias: str = Field(..., description="Environment alias (dev, test, pre-prod, prod)")
    workflow_state: WorkflowState = Field(..., description="Overall workflow state")
    recommendation_package: Optional[RecommendationPackage] = Field(None, description="Recommendation package (null if error)")
    structured_error: Optional[StructuredError] = Field(None, description="Structured error if workflow failed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "req-12345",
                "session_id": "sess-67890",
                "trace_id": "trace-abcdef",
                "timestamp": "2024-01-15T10:30:00Z",
                "agent_version": "1.0.0",
                "schema_version": "1.0.0",
                "policy_version": "1.0.0",
                "environment_alias": "prod",
                "workflow_state": "NORMAL",
                "recommendation_package": {
                    "portfolio_summary": {},
                    "current_vs_target_allocation": {},
                    "research_summary": {
                        "market_data_freshness": "2024-01-15T10:00:00Z",
                        "confidence_score": 0.95
                    },
                    "memory_summary": {
                        "memory_items_count": 5,
                        "memory_categories": ["profile_facts", "episodic_decisions"],
                        "conflicts_detected": False,
                        "confidence_score": 0.90
                    },
                    "risk_analysis_summary": {
                        "drift_percentage": 5.2,
                        "risk_metrics": {"concentration": 0.15},
                        "compliance_verdict": {
                            "status": "COMPLIANT",
                            "confidence_score": 1.0
                        },
                        "confidence_score": 0.95
                    },
                    "trade_proposals": [],
                    "recommendation_rationale": "Portfolio is within acceptable drift range",
                    "quality_metadata": {
                        "overall_confidence": 0.93,
                        "workflow_state": "NORMAL",
                        "contributing_agents": ["research", "memory", "risk_compliance", "execution"],
                        "advisory_completeness": 1.0,
                        "approval_eligibility": True
                    }
                },
                "structured_error": None
            }
        }
