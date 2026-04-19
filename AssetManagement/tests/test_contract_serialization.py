"""
Property-Based Tests for Schema Serialization Round-Trips

Tests validate:
- Serialization to dict and back
- Serialization to JSON and back
- Data preservation through serialization
- Edge cases and boundary values
"""

import pytest
from hypothesis import given, strategies as st
from datetime import datetime, timezone

from AssetManagement.schemas.portfolio_rebalance_request import PortfolioRebalanceRequest, Holding
from AssetManagement.schemas.supervisor_response import SupervisorResponse
from AssetManagement.schemas.approval_artifact import ApprovalArtifact


class TestSerializationRoundTrips:
    """Property-based tests for schema serialization."""
    
    @given(
        client_id=st.text(min_size=1, max_size=50),
        account_id=st.text(min_size=1, max_size=50),
        cash_position=st.floats(min_value=0.0, max_value=1000000.0, allow_nan=False, allow_infinity=False)
    )
    def test_portfolio_request_dict_round_trip(self, client_id, account_id, cash_position):
        """Property test: PortfolioRebalanceRequest dict serialization round-trip."""
        original = PortfolioRebalanceRequest(
            client_id=client_id,
            account_id=account_id,
            current_holdings=[],
            current_allocation={},
            cash_position=cash_position,
            investment_objective="growth",
            risk_profile="moderate",
            mandate_constraints=[],
            requested_action_context="rebalance",
            schema_version="1.0.0"
        )
        
        # Serialize to dict
        data = original.dict()
        
        # Deserialize back
        restored = PortfolioRebalanceRequest(**data)
        
        # Verify data preserved
        assert restored.client_id == original.client_id
        assert restored.account_id == original.account_id
        assert restored.cash_position == original.cash_position
    
    @given(
        client_id=st.text(min_size=1, max_size=50),
        account_id=st.text(min_size=1, max_size=50)
    )
    def test_portfolio_request_json_round_trip(self, client_id, account_id):
        """Property test: PortfolioRebalanceRequest JSON serialization round-trip."""
        original = PortfolioRebalanceRequest(
            client_id=client_id,
            account_id=account_id,
            current_holdings=[],
            current_allocation={},
            cash_position=10000.0,
            investment_objective="growth",
            risk_profile="moderate",
            mandate_constraints=[],
            requested_action_context="rebalance",
            schema_version="1.0.0"
        )
        
        # Serialize to JSON
        json_str = original.json()
        
        # Deserialize back
        restored = PortfolioRebalanceRequest.parse_raw(json_str)
        
        # Verify data preserved
        assert restored.client_id == original.client_id
        assert restored.account_id == original.account_id
    
    def test_holding_serialization_round_trip(self):
        """Test Holding serialization round-trip."""
        original = Holding(
            security_id="AAPL",
            quantity=100,
            current_price=150.0
        )
        
        # Serialize to dict
        data = original.dict()
        
        # Deserialize back
        restored = Holding(**data)
        
        assert restored.security_id == original.security_id
        assert restored.quantity == original.quantity
        assert restored.current_price == original.current_price
    
    @given(
        request_id=st.text(min_size=1, max_size=50),
        session_id=st.text(min_size=1, max_size=50),
        trace_id=st.text(min_size=1, max_size=50)
    )
    def test_supervisor_response_dict_round_trip(self, request_id, session_id, trace_id):
        """Property test: SupervisorResponse dict serialization round-trip."""
        original = SupervisorResponse(
            request_id=request_id,
            session_id=session_id,
            trace_id=trace_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent_version="1.0.0",
            schema_version="1.0.0",
            policy_version="1.0.0",
            workflow_state="NORMAL",
            recommendation_package={}
        )
        
        # Serialize to dict
        data = original.dict()
        
        # Deserialize back
        restored = SupervisorResponse(**data)
        
        # Verify data preserved
        assert restored.request_id == original.request_id
        assert restored.session_id == original.session_id
        assert restored.trace_id == original.trace_id
    
    @given(
        approval_id=st.text(min_size=1, max_size=50),
        request_id=st.text(min_size=1, max_size=50)
    )
    def test_approval_artifact_json_round_trip(self, approval_id, request_id):
        """Property test: ApprovalArtifact JSON serialization round-trip."""
        original = ApprovalArtifact(
            approval_id=approval_id,
            request_id=request_id,
            trace_id="trace-123",
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
        
        # Serialize to JSON
        json_str = original.json()
        
        # Deserialize back
        restored = ApprovalArtifact.parse_raw(json_str)
        
        # Verify data preserved
        assert restored.approval_id == original.approval_id
        assert restored.request_id == original.request_id
    
    def test_nested_object_serialization(self):
        """Test serialization of nested objects."""
        original = PortfolioRebalanceRequest(
            client_id="client-123",
            account_id="account-456",
            current_holdings=[
                Holding(security_id="AAPL", quantity=100, current_price=150.0),
                Holding(security_id="MSFT", quantity=50, current_price=300.0)
            ],
            current_allocation={"AAPL": 0.5, "MSFT": 0.5},
            cash_position=10000.0,
            investment_objective="growth",
            risk_profile="moderate",
            mandate_constraints=[],
            requested_action_context="rebalance",
            schema_version="1.0.0"
        )
        
        # Serialize to dict
        data = original.dict()
        
        # Deserialize back
        restored = PortfolioRebalanceRequest(**data)
        
        # Verify nested objects preserved
        assert len(restored.current_holdings) == 2
        assert restored.current_holdings[0].security_id == "AAPL"
        assert restored.current_holdings[1].security_id == "MSFT"
    
    def test_empty_collections_serialization(self):
        """Test serialization of empty collections."""
        original = PortfolioRebalanceRequest(
            client_id="client-123",
            account_id="account-456",
            current_holdings=[],
            current_allocation={},
            cash_position=10000.0,
            investment_objective="growth",
            risk_profile="moderate",
            mandate_constraints=[],
            requested_action_context="rebalance",
            schema_version="1.0.0"
        )
        
        # Serialize to JSON
        json_str = original.json()
        
        # Deserialize back
        restored = PortfolioRebalanceRequest.parse_raw(json_str)
        
        # Verify empty collections preserved
        assert len(restored.current_holdings) == 0
        assert len(restored.current_allocation) == 0
        assert len(restored.mandate_constraints) == 0
    
    def test_special_characters_in_strings(self):
        """Test serialization with special characters."""
        original = PortfolioRebalanceRequest(
            client_id="client-123-!@#$%",
            account_id="account-456-&*()",
            current_holdings=[],
            current_allocation={},
            cash_position=10000.0,
            investment_objective="growth",
            risk_profile="moderate",
            mandate_constraints=[],
            requested_action_context="rebalance",
            schema_version="1.0.0"
        )
        
        # Serialize to JSON
        json_str = original.json()
        
        # Deserialize back
        restored = PortfolioRebalanceRequest.parse_raw(json_str)
        
        # Verify special characters preserved
        assert restored.client_id == original.client_id
        assert restored.account_id == original.account_id
    
    def test_unicode_characters_serialization(self):
        """Test serialization with unicode characters."""
        original = PortfolioRebalanceRequest(
            client_id="client-测试-123",
            account_id="account-テスト-456",
            current_holdings=[],
            current_allocation={},
            cash_position=10000.0,
            investment_objective="growth",
            risk_profile="moderate",
            mandate_constraints=[],
            requested_action_context="rebalance",
            schema_version="1.0.0"
        )
        
        # Serialize to JSON
        json_str = original.json()
        
        # Deserialize back
        restored = PortfolioRebalanceRequest.parse_raw(json_str)
        
        # Verify unicode preserved
        assert restored.client_id == original.client_id
        assert restored.account_id == original.account_id


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
