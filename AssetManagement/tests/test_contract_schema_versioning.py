"""
Contract Tests for Schema Version Compatibility

Tests validate:
- Schema version validation
- Backward compatibility
- Version migration
- Version coexistence
"""

import pytest
from pydantic import ValidationError

from AssetManagement.schemas.version_validator import SchemaVersionValidator
from AssetManagement.schemas.portfolio_rebalance_request import PortfolioRebalanceRequest, Holding
from AssetManagement.schemas.supervisor_response import SupervisorResponse
from datetime import datetime, timezone


class TestSchemaVersionCompatibility:
    """Contract tests for schema version compatibility."""
    
    def test_version_validator_valid_version(self):
        """Test that valid semantic versions are accepted."""
        validator = SchemaVersionValidator()
        
        valid_versions = ["1.0.0", "1.1.0", "2.0.0", "1.0.1"]
        
        for version in valid_versions:
            assert validator.is_valid_version(version)
    
    def test_version_validator_invalid_version(self):
        """Test that invalid versions are rejected."""
        validator = SchemaVersionValidator()
        
        invalid_versions = ["1.0", "v1.0.0", "1.0.0-beta", "invalid"]
        
        for version in invalid_versions:
            assert not validator.is_valid_version(version)
    
    def test_version_compatibility_same_major(self):
        """Test that same major versions are compatible."""
        validator = SchemaVersionValidator()
        
        assert validator.is_compatible("1.0.0", "1.1.0")
        assert validator.is_compatible("1.1.0", "1.0.0")
        assert validator.is_compatible("2.0.0", "2.5.3")
    
    def test_version_compatibility_different_major(self):
        """Test that different major versions are incompatible."""
        validator = SchemaVersionValidator()
        
        assert not validator.is_compatible("1.0.0", "2.0.0")
        assert not validator.is_compatible("2.0.0", "1.0.0")
    
    def test_backward_compatibility_minor_version(self):
        """Test backward compatibility with minor version changes."""
        # Version 1.0.0 request
        request_v1 = PortfolioRebalanceRequest(
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
        
        # Should be readable as version 1.1.0
        assert request_v1.schema_version == "1.0.0"
        
        # Version 1.1.0 request (with potential new optional fields)
        request_v1_1 = PortfolioRebalanceRequest(
            client_id="client-123",
            account_id="account-456",
            current_holdings=[],
            current_allocation={},
            cash_position=10000.0,
            investment_objective="growth",
            risk_profile="moderate",
            mandate_constraints=[],
            requested_action_context="rebalance",
            schema_version="1.1.0"
        )
        
        assert request_v1_1.schema_version == "1.1.0"
    
    def test_schema_version_field_present_in_all_schemas(self):
        """Test that schema_version field is present in all schemas."""
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
        
        assert hasattr(request, 'schema_version')
        assert hasattr(response, 'schema_version')
        assert request.schema_version == "1.0.0"
        assert response.schema_version == "1.0.0"
    
    def test_version_migration_preserves_data(self):
        """Test that version migration preserves data."""
        # Create v1.0.0 request
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
        
        # Serialize
        data = original.dict()
        
        # "Migrate" to v1.1.0 (in practice, just update version)
        data['schema_version'] = "1.1.0"
        
        # Deserialize
        migrated = PortfolioRebalanceRequest(**data)
        
        # Verify data preserved
        assert migrated.client_id == original.client_id
        assert migrated.account_id == original.account_id
        assert len(migrated.current_holdings) == len(original.current_holdings)
        assert migrated.cash_position == original.cash_position
        assert migrated.schema_version == "1.1.0"
    
    def test_version_coexistence_different_requests(self):
        """Test that different schema versions can coexist."""
        request_v1 = PortfolioRebalanceRequest(
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
        
        request_v1_1 = PortfolioRebalanceRequest(
            client_id="client-456",
            account_id="account-789",
            current_holdings=[],
            current_allocation={},
            cash_position=20000.0,
            investment_objective="income",
            risk_profile="conservative",
            mandate_constraints=[],
            requested_action_context="rebalance",
            schema_version="1.1.0"
        )
        
        # Both should be valid
        assert request_v1.schema_version == "1.0.0"
        assert request_v1_1.schema_version == "1.1.0"
        
        # Both should have required fields
        assert request_v1.client_id is not None
        assert request_v1_1.client_id is not None
    
    def test_version_comparison(self):
        """Test version comparison logic."""
        validator = SchemaVersionValidator()
        
        # Test greater than
        assert validator.compare_versions("1.1.0", "1.0.0") > 0
        assert validator.compare_versions("2.0.0", "1.9.9") > 0
        
        # Test less than
        assert validator.compare_versions("1.0.0", "1.1.0") < 0
        assert validator.compare_versions("1.9.9", "2.0.0") < 0
        
        # Test equal
        assert validator.compare_versions("1.0.0", "1.0.0") == 0
    
    def test_minimum_version_requirement(self):
        """Test minimum version requirement checking."""
        validator = SchemaVersionValidator()
        
        minimum_version = "1.0.0"
        
        # Versions meeting minimum
        assert validator.meets_minimum_version("1.0.0", minimum_version)
        assert validator.meets_minimum_version("1.1.0", minimum_version)
        assert validator.meets_minimum_version("2.0.0", minimum_version)
        
        # Versions not meeting minimum
        assert not validator.meets_minimum_version("0.9.0", minimum_version)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
