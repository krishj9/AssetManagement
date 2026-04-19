"""
Memory Record Schema

This module defines the Pydantic model for memory records stored in AgentCore Memory.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from .memory_personalization_response import MemoryCategory


class ExpiryPolicy(BaseModel):
    """Expiry policy for memory records"""
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp (null = no expiry)")
    expiry_reason: Optional[str] = Field(None, description="Reason for expiry policy")
    auto_archive: bool = Field(False, description="Whether to archive on expiry instead of delete")


class MemoryProvenance(BaseModel):
    """Provenance information for memory record"""
    source_interaction: str = Field(..., description="Source interaction that created this memory")
    originating_request_id: str = Field(..., description="Request ID that originated this memory")
    consolidation_outcome: Optional[str] = Field(None, description="Outcome of consolidation process")
    created_by_agent: str = Field(..., description="Agent that created this memory")
    created_by_agent_version: str = Field(..., description="Version of agent that created this memory")


class MemoryRecord(BaseModel):
    """
    Memory record stored in AgentCore Memory for long-term client context.
    
    This schema represents persistent memory items that personalize recommendations.
    """
    memory_id: str = Field(..., description="Unique identifier for the memory record")
    client_id: str = Field(..., description="Client ID this memory belongs to")
    category: MemoryCategory = Field(..., description="Category of memory")
    
    # Content
    content: Dict[str, Any] = Field(..., description="Structured memory content")
    content_summary: Optional[str] = Field(None, description="Human-readable summary of content")
    
    # Quality indicators
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence in this memory (0-1)")
    
    # Timestamps
    created_at: datetime = Field(..., description="When the memory was created")
    updated_at: datetime = Field(..., description="When the memory was last updated")
    
    # Versioning
    memory_version: str = Field(..., pattern=r"^[0-9]+\.[0-9]+\.[0-9]+$", description="Version of the memory record")
    
    # Provenance
    provenance: MemoryProvenance = Field(..., description="Provenance information")
    
    # Expiry policy
    expiry_policy: ExpiryPolicy = Field(..., description="Expiry policy for this memory")
    
    # Status
    is_active: bool = Field(True, description="Whether this memory is active")
    is_archived: bool = Field(False, description="Whether this memory is archived")
    invalidated: bool = Field(False, description="Whether this memory has been invalidated")
    invalidation_reason: Optional[str] = Field(None, description="Reason for invalidation if applicable")
    
    class Config:
        json_schema_extra = {
            "example": {
                "memory_id": "mem-12345",
                "client_id": "CLIENT-12345",
                "category": "profile_facts",
                "content": {
                    "risk_tolerance": "conservative",
                    "investment_objective": "capital_preservation",
                    "prefers_low_volatility": True
                },
                "content_summary": "Client has conservative risk profile with preference for low volatility",
                "confidence_score": 0.95,
                "created_at": "2023-06-15T10:00:00Z",
                "updated_at": "2024-01-10T14:30:00Z",
                "memory_version": "1.2.0",
                "provenance": {
                    "source_interaction": "req-previous-001",
                    "originating_request_id": "req-previous-001",
                    "consolidation_outcome": "merged_with_existing",
                    "created_by_agent": "memory_personalization_agent",
                    "created_by_agent_version": "1.0.0"
                },
                "expiry_policy": {
                    "expires_at": None,
                    "expiry_reason": None,
                    "auto_archive": False
                },
                "is_active": True,
                "is_archived": False,
                "invalidated": False,
                "invalidation_reason": None
            }
        }
