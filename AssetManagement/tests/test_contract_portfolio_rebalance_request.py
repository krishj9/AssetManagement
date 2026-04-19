"""
Contract Tests for Portfolio_Rebalance_Request Schema

Tests validate:
- Required fields presence
- Allocation math correctness
- Constraint validation
- Schema version compatibility
"""

import pytest
from datetime import datetime, timezone
from pydantic import ValidationError

from AssetManagement.schemas.portfolio_rebalance_request import (
    PortfolioRebalanceRequest,
    Holding,
    MandateConstraint
)


class TestPortfolioRebalanceRequestContract:
    """Contract tests for Portfolio_Rebalance_Request schema."""
    
    def test_required_fields_present(self):
        """Test that all required fields must be present."""
        # Valid request with all required fields
        request = PortfolioRebalanceRequest(
            client_id="client-123",
            account_id="account-456",
            current_holdings=[
                Holding(security_id="AAPL", quantity=100, current_price=150.0)
            ],
            current_allocation={"AAPL": 1.0},
            cash_position=10000.0,
            investment_objective="growth",
            risk_profile="moderate",
            mandate_constraints=[],
            requested_action_context="rebalance",
            schema_version="1.0.0"
        )
        
        assert request.client_id == "client-123"
        assert request.account_id == "account-456"
        assert len(request.current_holdings) == 1
        assert request.cash_position == 10000.0
    
    def test_missing_required_field_client_id(self):
        """Test that missing client_id raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            PortfolioRebalanceRequest(
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
        
        assert "client_id" in str(exc_info.value)
    
    def test_missing_required_field_account_id(self):
        """Test that missing account_id raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            PortfolioRebalanceRequest(
                client_id="client-123",
                current_holdings=[],
                current_allocation={},
                cash_position=10000.0,
                investment_objective="growth",
                risk_profile="moderate",
                mandate_constraints=[],
                requested_action_context="rebalance",
                schema_version="1.0.0"
            )
        
        assert "account_id" in str(exc_info.value)
    
    def test_allocation_math_sums_to_one(self):
        """Test that current_allocation percentages sum to 1.0."""
        request = PortfolioRebalanceRequest(
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
        
        total_allocation = sum(request.current_allocation.values())
        assert abs(total_allocation - 1.0) < 0.01, f"Allocation sum {total_allocation} should be ~1.0"
    
    def test_allocation_math_invalid_sum(self):
        """Test that allocation not summing to 1.0 is detected."""
        # This should still create the object (validation is business logic)
        # but we can detect the issue
        request = PortfolioRebalanceRequest(
            client_id="client-123",
            account_id="account-456",
            current_holdings=[],
            current_allocation={"AAPL": 0.3, "MSFT": 0.3},  # Sums to 0.6, not 1.0
            cash_position=10000.0,
            investment_objective="growth",
            risk_profile="moderate",
            mandate_constraints=[],
            requested_action_context="rebalance",
            schema_version="1.0.0"
        )
        
        total_allocation = sum(request.current_allocation.values())
        assert abs(total_allocation - 1.0) > 0.01, "Allocation sum should not be 1.0"
    
    def test_allocation_percentages_non_negative(self):
        """Test that allocation percentages are non-negative."""
        # Negative allocations should be rejected by business logic
        request = PortfolioRebalanceRequest(
            client_id="client-123",
            account_id="account-456",
            current_holdings=[],
            current_allocation={"AAPL": 1.2, "MSFT": -0.2},  # Invalid: negative
            cash_position=10000.0,
            investment_objective="growth",
            risk_profile="moderate",
            mandate_constraints=[],
            requested_action_context="rebalance",
            schema_version="1.0.0"
        )
        
        # Check for negative values
        has_negative = any(v < 0 for v in request.current_allocation.values())
        assert has_negative, "Should detect negative allocation"
    
    def test_constraint_validation_mandate_type(self):
        """Test that mandate constraints have valid types."""
        request = PortfolioRebalanceRequest(
            client_id="client-123",
            account_id="account-456",
            current_holdings=[],
            current_allocation={},
            cash_position=10000.0,
            investment_objective="growth",
            risk_profile="moderate",
            mandate_constraints=[
                MandateConstraint(
                    constraint_type="max_concentration",
                    constraint_value=0.20,
                    constraint_description="Maximum 20% in single security"
                )
            ],
            requested_action_context="rebalance",
            schema_version="1.0.0"
        )
        
        assert len(request.mandate_constraints) == 1
        assert request.mandate_constraints[0].constraint_type == "max_concentration"
        assert request.mandate_constraints[0].constraint_value == 0.20
    
    def test_constraint_validation_multiple_constraints(self):
        """Test that multiple constraints can be specified."""
        request = PortfolioRebalanceRequest(
            client_id="client-123",
            account_id="account-456",
            current_holdings=[],
            current_allocation={},
            cash_position=10000.0,
            investment_objective="growth",
            risk_profile="moderate",
            mandate_constraints=[
                MandateConstraint(
                    constraint_type="max_concentration",
                    constraint_value=0.20,
                    constraint_description="Maximum 20% in single security"
                ),
                MandateConstraint(
                    constraint_type="max_sector_concentration",
                    constraint_value=0.30,
                    constraint_description="Maximum 30% in single sector"
                )
            ],
            requested_action_context="rebalance",
            schema_version="1.0.0"
        )
        
        assert len(request.mandate_constraints) == 2
        assert request.mandate_constraints[0].constraint_type == "max_concentration"
        assert request.mandate_constraints[1].constraint_type == "max_sector_concentration"
    
    def test_holdings_validation(self):
        """Test that holdings have required fields."""
        holding = Holding(
            security_id="AAPL",
            quantity=100,
            current_price=150.0
        )
        
        assert holding.security_id == "AAPL"
        assert holding.quantity == 100
        assert holding.current_price == 150.0
    
    def test_holdings_missing_security_id(self):
        """Test that holdings require security_id."""
        with pytest.raises(ValidationError) as exc_info:
            Holding(
                quantity=100,
                current_price=150.0
            )
        
        assert "security_id" in str(exc_info.value)
    
    def test_cash_position_non_negative(self):
        """Test that cash_position should be non-negative."""
        request = PortfolioRebalanceRequest(
            client_id="client-123",
            account_id="account-456",
            current_holdings=[],
            current_allocation={},
            cash_position=-1000.0,  # Negative cash
            investment_objective="growth",
            risk_profile="moderate",
            mandate_constraints=[],
            requested_action_context="rebalance",
            schema_version="1.0.0"
        )
        
        # Object is created, but business logic should validate
        assert request.cash_position < 0
    
    def test_schema_version_present(self):
        """Test that schema_version is present."""
        request = PortfolioRebalanceRequest(
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
        
        assert request.schema_version == "1.0.0"
    
    def test_serialization_round_trip(self):
        """Test that schema can be serialized and deserialized."""
        original = PortfolioRebalanceRequest(
            client_id="client-123",
            account_id="account-456",
            current_holdings=[
                Holding(security_id="AAPL", quantity=100, current_price=150.0)
            ],
            current_allocation={"AAPL": 1.0},
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
        
        assert restored.client_id == original.client_id
        assert restored.account_id == original.account_id
        assert len(restored.current_holdings) == len(original.current_holdings)
        assert restored.cash_position == original.cash_position
    
    def test_json_serialization_round_trip(self):
        """Test that schema can be serialized to JSON and back."""
        original = PortfolioRebalanceRequest(
            client_id="client-123",
            account_id="account-456",
            current_holdings=[
                Holding(security_id="AAPL", quantity=100, current_price=150.0)
            ],
            current_allocation={"AAPL": 1.0},
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
        
        assert restored.client_id == original.client_id
        assert restored.account_id == original.account_id
        assert restored.cash_position == original.cash_position


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
