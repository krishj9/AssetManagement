"""
Contract Tests for Approval_Artifact Schema

Tests validate:
- Required fields completeness
- Approval state transitions
- Workflow state validation
- Compliance verdict integration
"""

import pytest
from datetime import datetime, timezone
from pydantic import ValidationError

from AssetManagement.schemas.approval_artifact import ApprovalArtifact


class TestApprovalArtifactContract:
    """Contract tests for Approval_Artifact schema."""
    
    def test_required_fields_present(self):
        """Test that all required fields must be present."""
        artifact = ApprovalArtifact(
            approval_id="approval-123",
            request_id="req-456",
            trace_id="trace-789",
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent_version="1.0.0",
            schema_version="1.0.0",
            policy_version="1.0.0",
            trade_proposals=[],
            compliance_verdict={},
            rationale="Test rationale",
            evidence=[],
            memory_summary={},
            workflow_state="NORMAL",
            approval_status="PENDING"
        )
        
        assert artifact.approval_id == "approval-123"
        assert artifact.request_id == "req-456"
        assert artifact.workflow_state == "NORMAL"
        assert artifact.approval_status == "PENDING"
    
    def test_approval_state_transitions_pending_to_approved(self):
        """Test approval state transition from PENDING to APPROVED."""
        artifact = ApprovalArtifact(
            approval_id="approval-123",
            request_id="req-456",
            trace_id="trace-789",
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent_version="1.0.0",
            schema_version="1.0.0",
            policy_version="1.0.0",
            trade_proposals=[],
            compliance_verdict={},
            rationale="",
            evidence=[],
            memory_summary={},
            workflow_state="NORMAL",
            approval_status="PENDING"
        )
        
        # Simulate state transition
        artifact.approval_status = "APPROVED"
        artifact.approved_by = "user@example.com"
        artifact.approved_at = datetime.now(timezone.utc).isoformat()
        
        assert artifact.approval_status == "APPROVED"
        assert artifact.approved_by == "user@example.com"
        assert artifact.approved_at is not None
    
    def test_approval_state_transitions_pending_to_rejected(self):
        """Test approval state transition from PENDING to REJECTED."""
        artifact = ApprovalArtifact(
            approval_id="approval-123",
            request_id="req-456",
            trace_id="trace-789",
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent_version="1.0.0",
            schema_version="1.0.0",
            policy_version="1.0.0",
            trade_proposals=[],
            compliance_verdict={},
            rationale="",
            evidence=[],
            memory_summary={},
            workflow_state="NORMAL",
            approval_status="PENDING"
        )
        
        # Simulate state transition
        artifact.approval_status = "REJECTED"
        artifact.approved_by = "user@example.com"
        artifact.approved_at = datetime.now(timezone.utc).isoformat()
        
        assert artifact.approval_status == "REJECTED"
        assert artifact.approved_by == "user@example.com"
    
    def test_workflow_state_normal(self):
        """Test workflow_state can be NORMAL."""
        artifact = ApprovalArtifact(
            approval_id="approval-123",
            request_id="req-456",
            trace_id="trace-789",
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent_version="1.0.0",
            schema_version="1.0.0",
            policy_version="1.0.0",
            trade_proposals=[],
            compliance_verdict={},
            rationale="",
            evidence=[],
            memory_summary={},
            workflow_state="NORMAL",
            approval_status="PENDING"
        )
        
        assert artifact.workflow_state == "NORMAL"
    
    def test_workflow_state_blocked(self):
        """Test workflow_state can be BLOCKED."""
        artifact = ApprovalArtifact(
            approval_id="approval-123",
            request_id="req-456",
            trace_id="trace-789",
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent_version="1.0.0",
            schema_version="1.0.0",
            policy_version="1.0.0",
            trade_proposals=[],
            compliance_verdict={"verdict": "NON_COMPLIANT"},
            rationale="",
            evidence=[],
            memory_summary={},
            workflow_state="BLOCKED",
            approval_status="PENDING"
        )
        
        assert artifact.workflow_state == "BLOCKED"
    
    def test_workflow_state_degraded(self):
        """Test workflow_state can be DEGRADED."""
        artifact = ApprovalArtifact(
            approval_id="approval-123",
            request_id="req-456",
            trace_id="trace-789",
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent_version="1.0.0",
            schema_version="1.0.0",
            policy_version="1.0.0",
            trade_proposals=[],
            compliance_verdict={},
            rationale="",
            evidence=[],
            memory_summary={},
            workflow_state="DEGRADED",
            approval_status="PENDING"
        )
        
        assert artifact.workflow_state == "DEGRADED"
    
    def test_workflow_state_low_confidence(self):
        """Test workflow_state can be LOW_CONFIDENCE."""
        artifact = ApprovalArtifact(
            approval_id="approval-123",
            request_id="req-456",
            trace_id="trace-789",
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent_version="1.0.0",
            schema_version="1.0.0",
            policy_version="1.0.0",
            trade_proposals=[],
            compliance_verdict={},
            rationale="",
            evidence=[],
            memory_summary={},
            workflow_state="LOW_CONFIDENCE",
            approval_status="PENDING"
        )
        
        assert artifact.workflow_state == "LOW_CONFIDENCE"
    
    def test_compliance_verdict_integration(self):
        """Test that compliance_verdict is integrated."""
        artifact = ApprovalArtifact(
            approval_id="approval-123",
            request_id="req-456",
            trace_id="trace-789",
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent_version="1.0.0",
            schema_version="1.0.0",
            policy_version="1.0.0",
            trade_proposals=[],
            compliance_verdict={
                "verdict": "COMPLIANT",
                "rationale": "All checks passed",
                "evidence": [],
                "unresolved_controls": []
            },
            rationale="",
            evidence=[],
            memory_summary={},
            workflow_state="NORMAL",
            approval_status="PENDING"
        )
        
        assert artifact.compliance_verdict["verdict"] == "COMPLIANT"
    
    def test_trade_proposals_present(self):
        """Test that trade_proposals field is present."""
        artifact = ApprovalArtifact(
            approval_id="approval-123",
            request_id="req-456",
            trace_id="trace-789",
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent_version="1.0.0",
            schema_version="1.0.0",
            policy_version="1.0.0",
            trade_proposals=[
                {
                    "trade_id": "trade-1",
                    "security_id": "AAPL",
                    "action": "buy",
                    "quantity": 100,
                    "estimated_price": 150.0
                }
            ],
            compliance_verdict={},
            rationale="",
            evidence=[],
            memory_summary={},
            workflow_state="NORMAL",
            approval_status="PENDING"
        )
        
        assert len(artifact.trade_proposals) == 1
        assert artifact.trade_proposals[0]["security_id"] == "AAPL"
    
    def test_memory_summary_present(self):
        """Test that memory_summary field is present."""
        artifact = ApprovalArtifact(
            approval_id="approval-123",
            request_id="req-456",
            trace_id="trace-789",
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent_version="1.0.0",
            schema_version="1.0.0",
            policy_version="1.0.0",
            trade_proposals=[],
            compliance_verdict={},
            rationale="",
            evidence=[],
            memory_summary={
                "memory_items": [],
                "conflicts": []
            },
            workflow_state="NORMAL",
            approval_status="PENDING"
        )
        
        assert artifact.memory_summary is not None
        assert "memory_items" in artifact.memory_summary
    
    def test_version_fields_present(self):
        """Test that all version fields are present."""
        artifact = ApprovalArtifact(
            approval_id="approval-123",
            request_id="req-456",
            trace_id="trace-789",
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent_version="1.0.0",
            schema_version="1.0.0",
            policy_version="1.0.0",
            trade_proposals=[],
            compliance_verdict={},
            rationale="",
            evidence=[],
            memory_summary={},
            workflow_state="NORMAL",
            approval_status="PENDING"
        )
        
        assert artifact.agent_version == "1.0.0"
        assert artifact.schema_version == "1.0.0"
        assert artifact.policy_version == "1.0.0"
    
    def test_serialization_round_trip(self):
        """Test that artifact can be serialized and deserialized."""
        original = ApprovalArtifact(
            approval_id="approval-123",
            request_id="req-456",
            trace_id="trace-789",
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent_version="1.0.0",
            schema_version="1.0.0",
            policy_version="1.0.0",
            trade_proposals=[],
            compliance_verdict={},
            rationale="Test rationale",
            evidence=["evidence1"],
            memory_summary={},
            workflow_state="NORMAL",
            approval_status="PENDING"
        )
        
        # Serialize to dict
        data = original.dict()
        
        # Deserialize back
        restored = ApprovalArtifact(**data)
        
        assert restored.approval_id == original.approval_id
        assert restored.request_id == original.request_id
        assert restored.workflow_state == original.workflow_state
        assert restored.approval_status == original.approval_status


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
