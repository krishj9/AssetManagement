"""
Research Response Schema

This module defines the Pydantic model for Research Agent responses.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class ProvenanceMetadata(BaseModel):
    """Metadata describing source, retrieval time, freshness, and traceability"""
    source_type: str = Field(..., description="Type of source (e.g., yfinance, news_api, bedrock_model)")
    source_identifier: Optional[str] = Field(None, description="Identifier for the specific source")
    retrieval_timestamp: datetime = Field(..., description="When the data was retrieved")
    data_freshness_timestamp: datetime = Field(..., description="Timestamp of the underlying data")
    transformation_stage: str = Field(..., description="Stage of transformation (raw, summarized, derived)")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence in the provenance (0-1)")


class MarketDataPoint(BaseModel):
    """Individual market data point for a security"""
    security_id: str = Field(..., description="Security identifier")
    security_name: str = Field(..., description="Security name")
    current_price: float = Field(..., ge=0, description="Current market price")
    previous_close: Optional[float] = Field(None, ge=0, description="Previous closing price")
    price_change: Optional[float] = Field(None, description="Price change from previous close")
    price_change_percentage: Optional[float] = Field(None, description="Price change percentage")
    volume: Optional[float] = Field(None, ge=0, description="Trading volume")
    market_cap: Optional[float] = Field(None, ge=0, description="Market capitalization")
    data_timestamp: datetime = Field(..., description="Timestamp of the market data")
    provenance: ProvenanceMetadata = Field(..., description="Provenance metadata for this data point")


class SentimentAnalysis(BaseModel):
    """Sentiment analysis for a security or market"""
    security_id: Optional[str] = Field(None, description="Security identifier (null for market-wide sentiment)")
    sentiment_score: float = Field(..., ge=-1, le=1, description="Sentiment score (-1 to 1, negative to positive)")
    sentiment_label: str = Field(..., description="Sentiment label (very_negative, negative, neutral, positive, very_positive)")
    news_summary: Optional[str] = Field(None, description="Summary of relevant news")
    news_count: int = Field(..., ge=0, description="Number of news articles analyzed")
    analysis_timestamp: datetime = Field(..., description="When the sentiment analysis was performed")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence in the sentiment analysis (0-1)")
    provenance: ProvenanceMetadata = Field(..., description="Provenance metadata for sentiment analysis")


class Evidence(BaseModel):
    """Supporting evidence for research findings"""
    evidence_type: str = Field(..., description="Type of evidence (market_data, news, analysis, calculation)")
    evidence_description: str = Field(..., description="Description of the evidence")
    evidence_data: Optional[Dict[str, Any]] = Field(None, description="Structured evidence data")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence in this evidence (0-1)")
    provenance: ProvenanceMetadata = Field(..., description="Provenance metadata for this evidence")


class ResearchResponse(BaseModel):
    """
    Response from the Research Agent containing market data and sentiment analysis.
    
    This schema represents the output of market research and sentiment analysis.
    """
    request_id: str = Field(..., description="Unique identifier for the request")
    session_id: str = Field(..., description="Session identifier")
    trace_id: str = Field(..., description="Trace identifier for observability")
    timestamp: datetime = Field(..., description="Response timestamp")
    agent_version: str = Field(..., description="Research agent version")
    schema_version: str = Field("1.0.0", pattern=r"^[0-9]+\.[0-9]+\.[0-9]+$", description="Schema version")
    
    # Market data
    market_data: List[MarketDataPoint] = Field(..., description="Market data for relevant securities")
    market_data_summary: Optional[str] = Field(None, description="Human-readable summary of market data")
    
    # Sentiment analysis
    sentiment_analysis: List[SentimentAnalysis] = Field(..., description="Sentiment analysis for securities and market")
    sentiment_summary: Optional[str] = Field(None, description="Human-readable summary of sentiment")
    
    # Quality indicators
    confidence_score: float = Field(..., ge=0, le=1, description="Overall confidence in research findings (0-1)")
    evidence: List[Evidence] = Field(..., description="Supporting evidence for research findings")
    
    # Provenance
    provenance_metadata: ProvenanceMetadata = Field(..., description="Overall provenance metadata for the research")
    
    # Degraded mode handling
    degraded_mode: bool = Field(False, description="Whether research is in degraded mode")
    degraded_mode_reason: Optional[str] = Field(None, description="Reason for degraded mode if applicable")
    missing_data: Optional[List[str]] = Field(None, description="List of missing data items if in degraded mode")
    
    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "req-12345",
                "session_id": "sess-67890",
                "trace_id": "trace-abcdef",
                "timestamp": "2024-01-15T10:30:00Z",
                "agent_version": "1.0.0",
                "schema_version": "1.0.0",
                "market_data": [
                    {
                        "security_id": "AAPL",
                        "security_name": "Apple Inc.",
                        "current_price": 150.00,
                        "previous_close": 148.50,
                        "price_change": 1.50,
                        "price_change_percentage": 1.01,
                        "volume": 50000000,
                        "market_cap": 2500000000000,
                        "data_timestamp": "2024-01-15T10:00:00Z",
                        "provenance": {
                            "source_type": "yfinance",
                            "source_identifier": "AAPL",
                            "retrieval_timestamp": "2024-01-15T10:05:00Z",
                            "data_freshness_timestamp": "2024-01-15T10:00:00Z",
                            "transformation_stage": "raw",
                            "confidence_score": 1.0
                        }
                    }
                ],
                "market_data_summary": "Market data retrieved successfully for all securities",
                "sentiment_analysis": [
                    {
                        "security_id": "AAPL",
                        "sentiment_score": 0.65,
                        "sentiment_label": "positive",
                        "news_summary": "Positive earnings report and product announcements",
                        "news_count": 15,
                        "analysis_timestamp": "2024-01-15T10:15:00Z",
                        "confidence_score": 0.85,
                        "provenance": {
                            "source_type": "bedrock_model",
                            "source_identifier": "claude-3-sonnet",
                            "retrieval_timestamp": "2024-01-15T10:15:00Z",
                            "data_freshness_timestamp": "2024-01-15T09:00:00Z",
                            "transformation_stage": "derived",
                            "confidence_score": 0.85
                        }
                    }
                ],
                "sentiment_summary": "Overall positive sentiment across portfolio holdings",
                "confidence_score": 0.90,
                "evidence": [
                    {
                        "evidence_type": "market_data",
                        "evidence_description": "Real-time market prices from yfinance",
                        "confidence_score": 1.0,
                        "provenance": {
                            "source_type": "yfinance",
                            "retrieval_timestamp": "2024-01-15T10:05:00Z",
                            "data_freshness_timestamp": "2024-01-15T10:00:00Z",
                            "transformation_stage": "raw",
                            "confidence_score": 1.0
                        }
                    }
                ],
                "provenance_metadata": {
                    "source_type": "research_agent",
                    "source_identifier": "research-agent-v1",
                    "retrieval_timestamp": "2024-01-15T10:30:00Z",
                    "data_freshness_timestamp": "2024-01-15T10:00:00Z",
                    "transformation_stage": "summarized",
                    "confidence_score": 0.90
                },
                "degraded_mode": False,
                "degraded_mode_reason": None,
                "missing_data": None
            }
        }
