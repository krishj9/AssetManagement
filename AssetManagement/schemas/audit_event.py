"""
Audit Event Schema

This module defines the Pydantic model for audit events.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class EventType(str, Enum):
    """Type of audit event"""
    REQUEST_RECEIVED = "REQUEST_RECEIVED"
    AGENT_INVOKED = "AGENT_INVOKED"
    AGENT_COMPLETED = "AGENT_COMPLETED"
    STRUCTURED_ERROR = "STRUCTURED_ERROR"
    COMPLIANCE_VERDICT = "COMPLIANCE_VERDICT"
    GUARDRAIL_EVENT = "GUARDRAIL_EVENT"
    MEMORY_READ = "MEMORY_READ"
    MEMORY_WRITE = "MEMORY_WRITE"
    MEMORY_CORRECTION = "MEMORY_CORRECTION"
    APPROVAL_ACTION = "APPROVAL_ACTION"
    RELEASE_PROMOTION = "RELEASE_PROMOTION"
    ROLLBACK_EVENT = "ROLLBACK_EVENT"


class AuditEvent(BaseModel):
    """
    Audit event for tracking all system actions, decisions, and state changes.
    
    This schema is used for comprehensive audit logging and compliance tracking.
    """
    event_id: str = Field(..., description="Unique identifier for the audit event")
    event_type: EventType = Field(..., description="Type of audit event")
    request_id: Optional[str] = Field(None, description="Request ID if applicable")
    session_id: Optional[str] = Field(None, description="Session ID if applicable")
    trace_id: Optional[str] = Field(None, description="Trace ID for observability correlation")
    timestamp: datetime = Field(..., description="When the event occurred")
    
    # Actor information (for human actions)
    actor_identity: Optional[str] = Field(None, description="Identity of the human actor (user ID)")
    actor_role: Optional[str] = Field(None, description="Role of the human actor")
    
    # Agent information (for agent actions)
    agent_identity: Optional[str] = Field(None, description="Identity of the agent")
    agent_version: Optional[str] = Field(None, description="Version of the agent")
    
    # Action details
    action_details: Dict[str, Any] = Field(..., description="Structured details about the action")
    outcome: str = Field(..., description="Outcome of the action (success, failure, partial)")
    
    # Policy and environment
    policy_version: Optional[str] = Field(None, description="Policy version in effect")
    environment_alias: str = Field(..., description="Environment alias (dev, test, pre-prod, prod)")
    
    # Additional metadata
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "event-12345",
                "event_type": "APPROVAL_ACTION",
                "request_id": "req-12345",
                "session_id": "sess-67890",
                "trace_id": "trace-abcdef",
                "timestamp": "2024-01-15T10:35:00Z",
                "actor_identity": "user-001",
                "actor_role": "portfolio_manager",
                "agent_identity": None,
                "agent_version": None,
                "action_details": {
                    "approval_id": "approval-12345",
                    "action": "approved",
                    "trade_proposals_count": 1
                },
                "outcome": "success",
                "policy_version": "1.0.0",
                "environment_alias": "prod",
                "metadata": {
                    "client_id": "CLIENT-12345",
                    "account_id": "ACCT-67890"
                }
            }
        }
