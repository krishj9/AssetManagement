"""
Approval Artifact Schema

This module defines the Pydantic model for approval artifacts.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from .supervisor_response import WorkflowState, ComplianceVerdict, TradeProposal, MemorySummary


class ApprovalStatus(str, Enum):
    """Approval status"""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    REVISION_REQUESTED = "REVISION_REQUESTED"


class ApprovalArtifact(BaseModel):
    """
    Approval artifact containing trade proposals, compliance results, and approval state.
    
    This is the structured review package that requires human approval before execution.
    """
    approval_id: str = Field(..., description="Unique identifier for the approval artifact")
    request_id: str = Field(..., description="Request ID that generated this artifact")
    trace_id: str = Field(..., description="Trace ID for observability")
    timestamp: datetime = Field(..., description="When the artifact was created")
    agent_version: str = Field(..., description="Supervisor agent version")
    schema_version: str = Field("1.0.0", pattern=r"^[0-9]+\.[0-9]+\.[0-9]+$", description="Schema version")
    policy_version: str = Field(..., description="Policy version used")
    environment_alias: str = Field(..., description="Environment alias (dev, test, pre-prod, prod)")
    
    # Trade proposals
    trade_proposals: List[TradeProposal] = Field(..., description="List of trade proposals")
    trade_proposals_count: int = Field(..., ge=0, description="Number of trade proposals")
    
    # Compliance verdict
    compliance_verdict: ComplianceVerdict = Field(..., description="Compliance verdict")
    
    # Rationale and evidence
    recommendation_rationale: str = Field(..., description="Overall recommendation rationale")
    evidence_summary: Dict[str, Any] = Field(..., description="Summary of supporting evidence")
    
    # Memory summary
    memory_summary: MemorySummary = Field(..., description="Summary of client memory context")
    
    # Workflow state
    workflow_state: WorkflowState = Field(..., description="Workflow quality state")
    
    # Approval state
    approval_status: ApprovalStatus = Field(ApprovalStatus.PENDING, description="Current approval status")
    approval_eligible: bool = Field(..., description="Whether this artifact is eligible for approval")
    approval_blocked_reason: Optional[str] = Field(None, description="Reason if approval is blocked")
    
    # Approval metadata (populated when approved/rejected)
    approved_by: Optional[str] = Field(None, description="User ID who approved (if approved)")
    approved_at: Optional[datetime] = Field(None, description="Timestamp of approval (if approved)")
    rejected_by: Optional[str] = Field(None, description="User ID who rejected (if rejected)")
    rejected_at: Optional[datetime] = Field(None, description="Timestamp of rejection (if rejected)")
    rejection_note: Optional[str] = Field(None, description="Note explaining rejection (if rejected)")
    override_note: Optional[str] = Field(None, description="Note explaining override (if override applied)")
    
    # Timestamps
    created_at: datetime = Field(..., description="When the artifact was created")
    updated_at: datetime = Field(..., description="When the artifact was last updated")
    
    class Config:
        json_schema_extra = {
            "example": {
                "approval_id": "approval-12345",
                "request_id": "req-12345",
                "trace_id": "trace-abcdef",
                "timestamp": "2024-01-15T10:30:00Z",
                "agent_version": "1.0.0",
                "schema_version": "1.0.0",
                "policy_version": "1.0.0",
                "environment_alias": "prod",
                "trade_proposals": [
                    {
                        "trade_id": "trade-001",
                        "security_id": "AAPL",
                        "security_name": "Apple Inc.",
                        "action": "buy",
                        "quantity": 50,
                        "estimated_price": 150.00,
                        "estimated_cost": 10.00,
                        "tax_impact": 0.0,
                        "rationale": "Increase equity allocation to target level",
                        "confidence_score": 0.90
                    }
                ],
                "trade_proposals_count": 1,
                "compliance_verdict": {
                    "status": "COMPLIANT",
                    "violations": [],
                    "violations_count": 0,
                    "critical_violations_count": 0,
                    "blocking_violations_count": 0,
                    "compliance_checks": [],
                    "compliance_checks_passed": 5,
                    "compliance_checks_failed": 0,
                    "compliance_checks_inconclusive": 0,
                    "verdict_summary": "All compliance checks passed",
                    "confidence_score": 1.0
                },
                "recommendation_rationale": "Portfolio drift of 5.2% exceeds threshold. Proposed trades will reduce drift to 1.2%.",
                "evidence_summary": {
                    "drift_analysis": "5.2% overall drift",
                    "risk_metrics": "All within thresholds",
                    "market_conditions": "Favorable"
                },
                "memory_summary": {
                    "memory_items_count": 2,
                    "memory_categories": ["profile_facts", "episodic_decisions"],
                    "conflicts_detected": False,
                    "confidence_score": 0.92,
                    "summary": "Client prefers low volatility investments"
                },
                "workflow_state": "NORMAL",
                "approval_status": "PENDING",
                "approval_eligible": True,
                "approval_blocked_reason": None,
                "approved_by": None,
                "approved_at": None,
                "rejected_by": None,
                "rejected_at": None,
                "rejection_note": None,
                "override_note": None,
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z"
            }
        }
