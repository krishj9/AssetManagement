"""
Memory Personalization Response Schema

This module defines the Pydantic model for Memory & Personalization Agent responses.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class MemoryCategory(str, Enum):
    """Category of memory item"""
    PROFILE_FACTS = "profile_facts"
    EPISODIC_DECISIONS = "episodic_decisions"
    DERIVED_PREFERENCES = "derived_preferences"
    REJECTED_CANDIDATES = "rejected_candidates"


class MemoryItem(BaseModel):
    """Individual memory item retrieved from AgentCore Memory"""
    memory_id: str = Field(..., description="Unique identifier for the memory item")
    category: MemoryCategory = Field(..., description="Category of memory")
    content: Dict[str, Any] = Field(..., description="Memory content (structured data)")
    content_summary: Optional[str] = Field(None, description="Human-readable summary of memory content")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence in this memory item (0-1)")
    recency_score: float = Field(..., ge=0, le=1, description="Recency score (0=old, 1=recent)")
    relevance_score: float = Field(..., ge=0, le=1, description="Relevance score to current request (0-1)")
    created_at: datetime = Field(..., description="When the memory was created")
    updated_at: datetime = Field(..., description="When the memory was last updated")
    memory_version: str = Field(..., description="Version of the memory item")
    source_interaction: Optional[str] = Field(None, description="Source interaction that created this memory")


class MemoryConflict(BaseModel):
    """Detected conflict between memory items or between memory and current context"""
    conflict_id: str = Field(..., description="Unique identifier for the conflict")
    conflict_type: str = Field(..., description="Type of conflict (memory_vs_memory, memory_vs_context)")
    conflicting_memory_ids: List[str] = Field(..., description="IDs of conflicting memory items")
    conflict_description: str = Field(..., description="Description of the conflict")
    resolution_suggestion: Optional[str] = Field(None, description="Suggested resolution for the conflict")
    severity: str = Field(..., description="Severity of conflict (low, medium, high)")


class MemoryPersonalizationResponse(BaseModel):
    """
    Response from the Memory & Personalization Agent containing retrieved memory and personalization context.
    
    This schema represents the output of memory retrieval and personalization analysis.
    """
    request_id: str = Field(..., description="Unique identifier for the request")
    session_id: str = Field(..., description="Session identifier")
    trace_id: str = Field(..., description="Trace identifier for observability")
    timestamp: datetime = Field(..., description="Response timestamp")
    agent_version: str = Field(..., description="Memory & Personalization agent version")
    schema_version: str = Field("1.0.0", pattern=r"^[0-9]+\.[0-9]+\.[0-9]+$", description="Schema version")
    
    # Memory items
    memory_items: List[MemoryItem] = Field(..., description="Retrieved memory items")
    memory_items_count: int = Field(..., ge=0, description="Total number of memory items retrieved")
    memory_categories_retrieved: List[MemoryCategory] = Field(..., description="Categories of memory retrieved")
    
    # Conflicts
    conflicts: List[MemoryConflict] = Field(default_factory=list, description="Detected conflicts")
    conflicts_detected: bool = Field(..., description="Whether any conflicts were detected")
    
    # Quality indicators
    overall_confidence_score: float = Field(..., ge=0, le=1, description="Overall confidence in retrieved memory (0-1)")
    memory_completeness: float = Field(..., ge=0, le=1, description="Completeness of memory for this request (0-1)")
    
    # Memory version tracking
    memory_version: str = Field(..., description="Version of the memory store used")
    memory_freshness: datetime = Field(..., description="Timestamp of most recent memory update")
    
    # Stale or low-confidence flags
    stale_memory_warning: bool = Field(False, description="Whether memory is stale")
    stale_memory_reason: Optional[str] = Field(None, description="Reason for stale memory warning")
    low_confidence_warning: bool = Field(False, description="Whether confidence is below threshold")
    low_confidence_reason: Optional[str] = Field(None, description="Reason for low confidence warning")
    
    # Degraded mode handling
    degraded_mode: bool = Field(False, description="Whether memory retrieval is in degraded mode")
    degraded_mode_reason: Optional[str] = Field(None, description="Reason for degraded mode if applicable")
    
    # Summary
    memory_summary: Optional[str] = Field(None, description="Human-readable summary of retrieved memory context")
    
    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "req-12345",
                "session_id": "sess-67890",
                "trace_id": "trace-abcdef",
                "timestamp": "2024-01-15T10:30:00Z",
                "agent_version": "1.0.0",
                "schema_version": "1.0.0",
                "memory_items": [
                    {
                        "memory_id": "mem-001",
                        "category": "profile_facts",
                        "content": {
                            "client_preference": "prefers_low_volatility",
                            "risk_tolerance": "conservative"
                        },
                        "content_summary": "Client prefers low volatility investments",
                        "confidence_score": 0.95,
                        "recency_score": 0.80,
                        "relevance_score": 0.90,
                        "created_at": "2023-06-15T10:00:00Z",
                        "updated_at": "2024-01-10T14:30:00Z",
                        "memory_version": "1.2.0",
                        "source_interaction": "req-previous-001"
                    },
                    {
                        "memory_id": "mem-002",
                        "category": "episodic_decisions",
                        "content": {
                            "decision": "rejected_high_yield_bonds",
                            "reason": "too_risky_for_profile"
                        },
                        "content_summary": "Previously rejected high-yield bonds due to risk",
                        "confidence_score": 1.0,
                        "recency_score": 0.60,
                        "relevance_score": 0.85,
                        "created_at": "2023-09-20T11:00:00Z",
                        "updated_at": "2023-09-20T11:00:00Z",
                        "memory_version": "1.0.0",
                        "source_interaction": "req-previous-002"
                    }
                ],
                "memory_items_count": 2,
                "memory_categories_retrieved": ["profile_facts", "episodic_decisions"],
                "conflicts": [],
                "conflicts_detected": False,
                "overall_confidence_score": 0.92,
                "memory_completeness": 0.85,
                "memory_version": "1.2.0",
                "memory_freshness": "2024-01-10T14:30:00Z",
                "stale_memory_warning": False,
                "stale_memory_reason": None,
                "low_confidence_warning": False,
                "low_confidence_reason": None,
                "degraded_mode": False,
                "degraded_mode_reason": None,
                "memory_summary": "Client has conservative risk profile with preference for low volatility. Previously rejected high-yield bonds."
            }
        }
