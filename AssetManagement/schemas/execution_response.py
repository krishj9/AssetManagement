"""
Execution Response Schema

This module defines the Pydantic model for Execution Agent responses.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from .research_response import ProvenanceMetadata


class TradeAction(str, Enum):
    """Trade action type"""
    BUY = "buy"
    SELL = "sell"


class TradeProposal(BaseModel):
    """Individual trade proposal"""
    trade_id: str = Field(..., description="Unique identifier for the trade")
    security_id: str = Field(..., description="Security identifier")
    security_name: str = Field(..., description="Security name")
    security_type: Optional[str] = Field(None, description="Type of security")
    action: TradeAction = Field(..., description="Trade action (buy or sell)")
    quantity: float = Field(..., ge=0, description="Quantity to trade")
    estimated_price: float = Field(..., ge=0, description="Estimated execution price")
    estimated_total_value: float = Field(..., ge=0, description="Estimated total value (quantity * estimated_price)")
    estimated_cost: Optional[float] = Field(None, description="Estimated transaction cost (commissions, fees)")
    tax_impact: Optional[float] = Field(None, description="Estimated tax impact (capital gains/losses)")
    rationale: str = Field(..., description="Rationale for the trade")
    evidence: Optional[Dict[str, Any]] = Field(None, description="Supporting evidence for the trade")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence in the proposal (0-1)")
    provenance: ProvenanceMetadata = Field(..., description="Provenance metadata for this proposal")


class PortfolioImpact(BaseModel):
    """Estimated impact of trade proposals on portfolio"""
    expected_allocation_changes: Dict[str, float] = Field(..., description="Expected allocation changes by asset class")
    expected_drift_reduction: float = Field(..., description="Expected reduction in portfolio drift")
    expected_risk_metric_changes: Dict[str, float] = Field(..., description="Expected changes in risk metrics")
    total_estimated_cost: float = Field(..., description="Total estimated transaction costs")
    total_estimated_tax_impact: float = Field(..., description="Total estimated tax impact")
    net_cash_impact: float = Field(..., description="Net cash impact (positive = cash in, negative = cash out)")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence in impact estimates (0-1)")


class ExecutionEvidence(BaseModel):
    """Evidence supporting trade proposals"""
    evidence_type: str = Field(..., description="Type of evidence (drift_analysis, compliance_check, optimization, market_data)")
    evidence_description: str = Field(..., description="Description of the evidence")
    evidence_data: Optional[Dict[str, Any]] = Field(None, description="Structured evidence data")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence in this evidence (0-1)")
    provenance: ProvenanceMetadata = Field(..., description="Provenance metadata for this evidence")


class ExecutionResponse(BaseModel):
    """
    Response from the Execution Agent containing trade proposals and portfolio impact analysis.
    
    This schema represents the output of trade proposal generation.
    """
    request_id: str = Field(..., description="Unique identifier for the request")
    session_id: str = Field(..., description="Session identifier")
    trace_id: str = Field(..., description="Trace identifier for observability")
    timestamp: datetime = Field(..., description="Response timestamp")
    agent_version: str = Field(..., description="Execution agent version")
    schema_version: str = Field("1.0.0", pattern=r"^[0-9]+\.[0-9]+\.[0-9]+$", description="Schema version")
    
    # Trade proposals
    trade_proposals: List[TradeProposal] = Field(..., description="List of trade proposals")
    trade_proposals_count: int = Field(..., ge=0, description="Total number of trade proposals")
    
    # Portfolio impact
    portfolio_impact: PortfolioImpact = Field(..., description="Estimated impact on portfolio")
    
    # Approval status
    approval_ready: bool = Field(..., description="Whether proposals are ready for approval")
    approval_blocked_reason: Optional[str] = Field(None, description="Reason if approval is blocked")
    
    # Quality indicators
    overall_confidence_score: float = Field(..., ge=0, le=1, description="Overall confidence in proposals (0-1)")
    
    # Evidence
    evidence: List[ExecutionEvidence] = Field(..., description="Supporting evidence for proposals")
    
    # Provenance
    provenance_metadata: ProvenanceMetadata = Field(..., description="Overall provenance metadata")
    
    # Summary
    execution_summary: str = Field(..., description="Human-readable summary of trade proposals")
    
    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "req-12345",
                "session_id": "sess-67890",
                "trace_id": "trace-abcdef",
                "timestamp": "2024-01-15T10:30:00Z",
                "agent_version": "1.0.0",
                "schema_version": "1.0.0",
                "trade_proposals": [
                    {
                        "trade_id": "trade-001",
                        "security_id": "AAPL",
                        "security_name": "Apple Inc.",
                        "security_type": "stock",
                        "action": "buy",
                        "quantity": 50,
                        "estimated_price": 150.00,
                        "estimated_total_value": 7500.00,
                        "estimated_cost": 10.00,
                        "tax_impact": 0.0,
                        "rationale": "Increase equity allocation to target level and reduce drift",
                        "evidence": {
                            "drift_reduction": 2.5,
                            "target_allocation": 60.0,
                            "current_allocation": 57.5
                        },
                        "confidence_score": 0.90,
                        "provenance": {
                            "source_type": "execution_agent",
                            "source_identifier": "trade_optimizer",
                            "retrieval_timestamp": "2024-01-15T10:30:00Z",
                            "data_freshness_timestamp": "2024-01-15T10:30:00Z",
                            "transformation_stage": "derived",
                            "confidence_score": 0.90
                        }
                    },
                    {
                        "trade_id": "trade-002",
                        "security_id": "BND",
                        "security_name": "Vanguard Total Bond Market ETF",
                        "security_type": "etf",
                        "action": "sell",
                        "quantity": 30,
                        "estimated_price": 75.00,
                        "estimated_total_value": 2250.00,
                        "estimated_cost": 5.00,
                        "tax_impact": 50.00,
                        "rationale": "Reduce fixed income allocation to target level",
                        "evidence": {
                            "drift_reduction": 1.5,
                            "target_allocation": 30.0,
                            "current_allocation": 31.5
                        },
                        "confidence_score": 0.90,
                        "provenance": {
                            "source_type": "execution_agent",
                            "source_identifier": "trade_optimizer",
                            "retrieval_timestamp": "2024-01-15T10:30:00Z",
                            "data_freshness_timestamp": "2024-01-15T10:30:00Z",
                            "transformation_stage": "derived",
                            "confidence_score": 0.90
                        }
                    }
                ],
                "trade_proposals_count": 2,
                "portfolio_impact": {
                    "expected_allocation_changes": {
                        "equities": 2.5,
                        "fixed_income": -1.5,
                        "cash": -1.0
                    },
                    "expected_drift_reduction": 4.0,
                    "expected_risk_metric_changes": {
                        "concentration": 0.5
                    },
                    "total_estimated_cost": 15.00,
                    "total_estimated_tax_impact": 50.00,
                    "net_cash_impact": -5265.00,
                    "confidence_score": 0.85
                },
                "approval_ready": True,
                "approval_blocked_reason": None,
                "overall_confidence_score": 0.88,
                "evidence": [
                    {
                        "evidence_type": "drift_analysis",
                        "evidence_description": "Portfolio drift analysis showing 5.2% overall drift",
                        "evidence_data": {
                            "overall_drift": 5.2,
                            "drift_threshold": 5.0
                        },
                        "confidence_score": 1.0,
                        "provenance": {
                            "source_type": "risk_compliance_agent",
                            "source_identifier": "drift_calculator",
                            "retrieval_timestamp": "2024-01-15T10:25:00Z",
                            "data_freshness_timestamp": "2024-01-15T10:25:00Z",
                            "transformation_stage": "derived",
                            "confidence_score": 1.0
                        }
                    }
                ],
                "provenance_metadata": {
                    "source_type": "execution_agent",
                    "source_identifier": "execution-agent-v1",
                    "retrieval_timestamp": "2024-01-15T10:30:00Z",
                    "data_freshness_timestamp": "2024-01-15T10:30:00Z",
                    "transformation_stage": "derived",
                    "confidence_score": 0.88
                },
                "execution_summary": "Generated 2 trade proposals to reduce portfolio drift from 5.2% to 1.2%. Total estimated cost: $15.00, tax impact: $50.00."
            }
        }
