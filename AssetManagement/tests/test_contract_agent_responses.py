"""
Contract Tests for Agent Response Schemas

Tests validate:
- Required fields presence
- Metadata presence (request_id, session_id, trace_id, timestamp)
- Version fields (agent_version, schema_version)
- Response structure consistency
"""

import pytest
from datetime import datetime, timezone
from pydantic import ValidationError

from AssetManagement.schemas.supervisor_response import SupervisorResponse
from AssetManagement.schemas.research_response import ResearchResponse
from AssetManagement.schemas.memory_personalization_response import MemoryPersonalizationResponse
from AssetManagement.schemas.risk_compliance_response import RiskComplianceResponse, ComplianceVerdict
from AssetManagement.schemas.execution_response import ExecutionResponse


class TestAgentResponseContracts:
    """Contract tests for all agent response schemas."""
    
    # Supervisor Response Tests
    
    def test_supervisor_response_required_fields(self):
        """Test SupervisorResponse has all required fields."""
        response = SupervisorResponse(
            request_id="req-123",
            session_id="sess-456",
            trace_id="trace-789",
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent_version="1.0.0",
            schema_version="1.0.0",
            policy_version="1.0.0",
            workflow_state="NORMAL",
            recommendation_package={}
        )
        
        assert response.request_id == "req-123"
        assert response.session_id == "sess-456"
        assert response.trace_id == "trace-789"
        assert response.agent_version == "1.0.0"
        assert response.schema_version == "1.0.0"
        assert response.policy_version == "1.0.0"
        assert response.workflow_state == "NORMAL"
    
    def test_supervisor_response_metadata_presence(self):
        """Test SupervisorResponse has correlation metadata."""
        response = SupervisorResponse(
            request_id="req-123",
            session_id="sess-456",
            trace_id="trace-789",
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent_version="1.0.0",
            schema_version="1.0.0",
            policy_version="1.0.0",
            workflow_state="NORMAL",
            recommendation_package={}
        )
        
        # Check all correlation IDs are present
        assert response.request_id is not None
        assert response.session_id is not None
        assert response.trace_id is not None
        assert response.timestamp is not None
    
    def test_supervisor_response_version_fields(self):
        """Test SupervisorResponse has version fields."""
        response = SupervisorResponse(
            request_id="req-123",
            session_id="sess-456",
            trace_id="trace-789",
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent_version="1.0.0",
            schema_version="1.0.0",
            policy_version="1.0.0",
            workflow_state="NORMAL",
            recommendation_package={}
        )
        
        assert response.agent_version is not None
        assert response.schema_version is not None
        assert response.policy_version is not None
    
    # Research Response Tests
    
    def test_research_response_required_fields(self):
        """Test ResearchResponse has all required fields."""
        response = ResearchResponse(
            request_id="req-123",
            session_id="sess-456",
            trace_id="trace-789",
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent_version="1.0.0",
            schema_version="1.0.0",
            market_data={},
            sentiment_summary="Positive market sentiment",
            confidence_score=0.9,
            evidence=[],
            provenance_metadata={}
        )
        
        assert response.request_id == "req-123"
        assert response.market_data is not None
        assert response.sentiment_summary is not None
        assert response.confidence_score == 0.9
    
    def test_research_response_metadata_presence(self):
        """Test ResearchResponse has correlation metadata."""
        response = ResearchResponse(
            request_id="req-123",
            session_id="sess-456",
            trace_id="trace-789",
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent_version="1.0.0",
            schema_version="1.0.0",
            market_data={},
            sentiment_summary="",
            confidence_score=0.9,
            evidence=[],
            provenance_metadata={}
        )
        
        assert response.request_id is not None
        assert response.session_id is not None
        assert response.trace_id is not None
        assert response.timestamp is not None
    
    # Memory Response Tests
    
    def test_memory_response_required_fields(self):
        """Test MemoryPersonalizationResponse has all required fields."""
        response = MemoryPersonalizationResponse(
            request_id="req-123",
            session_id="sess-456",
            trace_id="trace-789",
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent_version="1.0.0",
            schema_version="1.0.0",
            memory_items=[],
            conflicts=[],
            confidence_score=0.9,
            memory_version="1.0.0"
        )
        
        assert response.request_id == "req-123"
        assert response.memory_items is not None
        assert response.conflicts is not None
        assert response.memory_version == "1.0.0"
    
    def test_memory_response_metadata_presence(self):
        """Test MemoryPersonalizationResponse has correlation metadata."""
        response = MemoryPersonalizationResponse(
            request_id="req-123",
            session_id="sess-456",
            trace_id="trace-789",
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent_version="1.0.0",
            schema_version="1.0.0",
            memory_items=[],
            conflicts=[],
            confidence_score=0.9,
            memory_version="1.0.0"
        )
        
        assert response.request_id is not None
        assert response.session_id is not None
        assert response.trace_id is not None
    
    # Risk & Compliance Response Tests
    
    def test_compliance_response_required_fields(self):
        """Test RiskComplianceResponse has all required fields."""
        response = RiskComplianceResponse(
            request_id="req-123",
            session_id="sess-456",
            trace_id="trace-789",
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent_version="1.0.0",
            schema_version="1.0.0",
            drift_analysis={},
            risk_metrics={},
            compliance_verdict=ComplianceVerdict(
                verdict="COMPLIANT",
                rationale="All checks passed",
                evidence=[],
                unresolved_controls=[]
            ),
            evidence=[],
            confidence_score=0.95
        )
        
        assert response.request_id == "req-123"
        assert response.drift_analysis is not None
        assert response.risk_metrics is not None
        assert response.compliance_verdict is not None
        assert response.compliance_verdict.verdict == "COMPLIANT"
    
    def test_compliance_response_metadata_presence(self):
        """Test RiskComplianceResponse has correlation metadata."""
        response = RiskComplianceResponse(
            request_id="req-123",
            session_id="sess-456",
            trace_id="trace-789",
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent_version="1.0.0",
            schema_version="1.0.0",
            drift_analysis={},
            risk_metrics={},
            compliance_verdict=ComplianceVerdict(
                verdict="COMPLIANT",
                rationale="",
                evidence=[],
                unresolved_controls=[]
            ),
            evidence=[],
            confidence_score=0.95
        )
        
        assert response.request_id is not None
        assert response.session_id is not None
        assert response.trace_id is not None
    
    # Execution Response Tests
    
    def test_execution_response_required_fields(self):
        """Test ExecutionResponse has all required fields."""
        response = ExecutionResponse(
            request_id="req-123",
            session_id="sess-456",
            trace_id="trace-789",
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent_version="1.0.0",
            schema_version="1.0.0",
            trade_proposals=[],
            confidence_score=0.85,
            evidence=[],
            provenance_metadata={}
        )
        
        assert response.request_id == "req-123"
        assert response.trade_proposals is not None
        assert response.confidence_score == 0.85
    
    def test_execution_response_metadata_presence(self):
        """Test ExecutionResponse has correlation metadata."""
        response = ExecutionResponse(
            request_id="req-123",
            session_id="sess-456",
            trace_id="trace-789",
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent_version="1.0.0",
            schema_version="1.0.0",
            trade_proposals=[],
            confidence_score=0.85,
            evidence=[],
            provenance_metadata={}
        )
        
        assert response.request_id is not None
        assert response.session_id is not None
        assert response.trace_id is not None
    
    # Cross-Schema Consistency Tests
    
    def test_all_responses_have_correlation_ids(self):
        """Test that all agent responses have correlation IDs."""
        responses = [
            SupervisorResponse(
                request_id="req-123", session_id="sess-456", trace_id="trace-789",
                timestamp=datetime.now(timezone.utc).isoformat(),
                agent_version="1.0.0", schema_version="1.0.0", policy_version="1.0.0",
                workflow_state="NORMAL", recommendation_package={}
            ),
            ResearchResponse(
                request_id="req-123", session_id="sess-456", trace_id="trace-789",
                timestamp=datetime.now(timezone.utc).isoformat(),
                agent_version="1.0.0", schema_version="1.0.0",
                market_data={}, sentiment_summary="", confidence_score=0.9,
                evidence=[], provenance_metadata={}
            ),
            MemoryPersonalizationResponse(
                request_id="req-123", session_id="sess-456", trace_id="trace-789",
                timestamp=datetime.now(timezone.utc).isoformat(),
                agent_version="1.0.0", schema_version="1.0.0",
                memory_items=[], conflicts=[], confidence_score=0.9, memory_version="1.0.0"
            ),
            RiskComplianceResponse(
                request_id="req-123", session_id="sess-456", trace_id="trace-789",
                timestamp=datetime.now(timezone.utc).isoformat(),
                agent_version="1.0.0", schema_version="1.0.0",
                drift_analysis={}, risk_metrics={},
                compliance_verdict=ComplianceVerdict(
                    verdict="COMPLIANT", rationale="", evidence=[], unresolved_controls=[]
                ),
                evidence=[], confidence_score=0.95
            ),
            ExecutionResponse(
                request_id="req-123", session_id="sess-456", trace_id="trace-789",
                timestamp=datetime.now(timezone.utc).isoformat(),
                agent_version="1.0.0", schema_version="1.0.0",
                trade_proposals=[], confidence_score=0.85,
                evidence=[], provenance_metadata={}
            )
        ]
        
        for response in responses:
            assert hasattr(response, 'request_id')
            assert hasattr(response, 'session_id')
            assert hasattr(response, 'trace_id')
            assert hasattr(response, 'timestamp')
            assert response.request_id == "req-123"
            assert response.session_id == "sess-456"
            assert response.trace_id == "trace-789"
    
    def test_all_responses_have_version_fields(self):
        """Test that all agent responses have version fields."""
        responses = [
            SupervisorResponse(
                request_id="req-123", session_id="sess-456", trace_id="trace-789",
                timestamp=datetime.now(timezone.utc).isoformat(),
                agent_version="1.0.0", schema_version="1.0.0", policy_version="1.0.0",
                workflow_state="NORMAL", recommendation_package={}
            ),
            ResearchResponse(
                request_id="req-123", session_id="sess-456", trace_id="trace-789",
                timestamp=datetime.now(timezone.utc).isoformat(),
                agent_version="1.0.0", schema_version="1.0.0",
                market_data={}, sentiment_summary="", confidence_score=0.9,
                evidence=[], provenance_metadata={}
            )
        ]
        
        for response in responses:
            assert hasattr(response, 'agent_version')
            assert hasattr(response, 'schema_version')
            assert response.agent_version == "1.0.0"
            assert response.schema_version == "1.0.0"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
