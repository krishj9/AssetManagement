"""
Contract Tests for Structured_Error Schema

Tests validate:
- Required fields (code, message, severity)
- Correlation metadata (request_id, trace_id)
- Error code format
- Severity levels
- Retryable flag
"""

import pytest
from datetime import datetime, timezone
from pydantic import ValidationError

from AssetManagement.schemas.supervisor_response import StructuredError


class TestStructuredErrorContract:
    """Contract tests for Structured_Error schema."""
    
    def test_required_fields_present(self):
        """Test that all required fields must be present."""
        error = StructuredError(
            code="VALIDATION_ERROR",
            message="Invalid input data",
            severity="error",
            retryable=False,
            source_agent="supervisor",
            request_id="req-123",
            trace_id="trace-456",
            timestamp=datetime.now(timezone.utc).isoformat(),
            related_context={}
        )
        
        assert error.code == "VALIDATION_ERROR"
        assert error.message == "Invalid input data"
        assert error.severity == "error"
        assert error.retryable is False
    
    def test_missing_required_field_code(self):
        """Test that missing code raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            StructuredError(
                message="Invalid input data",
                severity="error",
                retryable=False,
                source_agent="supervisor",
                request_id="req-123",
                trace_id="trace-456",
                timestamp=datetime.now(timezone.utc).isoformat(),
                related_context={}
            )
        
        assert "code" in str(exc_info.value)
    
    def test_missing_required_field_message(self):
        """Test that missing message raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            StructuredError(
                code="VALIDATION_ERROR",
                severity="error",
                retryable=False,
                source_agent="supervisor",
                request_id="req-123",
                trace_id="trace-456",
                timestamp=datetime.now(timezone.utc).isoformat(),
                related_context={}
            )
        
        assert "message" in str(exc_info.value)
    
    def test_missing_required_field_severity(self):
        """Test that missing severity raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            StructuredError(
                code="VALIDATION_ERROR",
                message="Invalid input data",
                retryable=False,
                source_agent="supervisor",
                request_id="req-123",
                trace_id="trace-456",
                timestamp=datetime.now(timezone.utc).isoformat(),
                related_context={}
            )
        
        assert "severity" in str(exc_info.value)
    
    def test_correlation_metadata_present(self):
        """Test that correlation metadata is present."""
        error = StructuredError(
            code="VALIDATION_ERROR",
            message="Invalid input data",
            severity="error",
            retryable=False,
            source_agent="supervisor",
            request_id="req-123",
            trace_id="trace-456",
            timestamp=datetime.now(timezone.utc).isoformat(),
            related_context={}
        )
        
        assert error.request_id == "req-123"
        assert error.trace_id == "trace-456"
        assert error.timestamp is not None
    
    def test_error_code_format(self):
        """Test that error codes follow expected format."""
        valid_codes = [
            "VALIDATION_ERROR",
            "INTERNAL_ERROR",
            "NOT_FOUND",
            "BLOCKED_STATE",
            "COMPLIANCE_VIOLATION",
            "GUARDRAIL_VIOLATION"
        ]
        
        for code in valid_codes:
            error = StructuredError(
                code=code,
                message="Test error",
                severity="error",
                retryable=False,
                source_agent="supervisor",
                request_id="req-123",
                trace_id="trace-456",
                timestamp=datetime.now(timezone.utc).isoformat(),
                related_context={}
            )
            
            assert error.code == code
            assert error.code.isupper() or "_" in error.code
    
    def test_severity_levels(self):
        """Test that severity levels are valid."""
        valid_severities = ["info", "warning", "error", "critical"]
        
        for severity in valid_severities:
            error = StructuredError(
                code="TEST_ERROR",
                message="Test error",
                severity=severity,
                retryable=False,
                source_agent="supervisor",
                request_id="req-123",
                trace_id="trace-456",
                timestamp=datetime.now(timezone.utc).isoformat(),
                related_context={}
            )
            
            assert error.severity == severity
    
    def test_retryable_flag_true(self):
        """Test that retryable flag can be True."""
        error = StructuredError(
            code="TIMEOUT_ERROR",
            message="Request timed out",
            severity="error",
            retryable=True,
            source_agent="supervisor",
            request_id="req-123",
            trace_id="trace-456",
            timestamp=datetime.now(timezone.utc).isoformat(),
            related_context={}
        )
        
        assert error.retryable is True
    
    def test_retryable_flag_false(self):
        """Test that retryable flag can be False."""
        error = StructuredError(
            code="VALIDATION_ERROR",
            message="Invalid input",
            severity="error",
            retryable=False,
            source_agent="supervisor",
            request_id="req-123",
            trace_id="trace-456",
            timestamp=datetime.now(timezone.utc).isoformat(),
            related_context={}
        )
        
        assert error.retryable is False
    
    def test_source_agent_field(self):
        """Test that source_agent field is present."""
        agents = ["supervisor", "research", "memory", "compliance", "execution"]
        
        for agent in agents:
            error = StructuredError(
                code="TEST_ERROR",
                message="Test error",
                severity="error",
                retryable=False,
                source_agent=agent,
                request_id="req-123",
                trace_id="trace-456",
                timestamp=datetime.now(timezone.utc).isoformat(),
                related_context={}
            )
            
            assert error.source_agent == agent
    
    def test_related_context_optional(self):
        """Test that related_context is optional."""
        error = StructuredError(
            code="TEST_ERROR",
            message="Test error",
            severity="error",
            retryable=False,
            source_agent="supervisor",
            request_id="req-123",
            trace_id="trace-456",
            timestamp=datetime.now(timezone.utc).isoformat(),
            related_context={"key": "value"}
        )
        
        assert error.related_context == {"key": "value"}
    
    def test_related_context_empty(self):
        """Test that related_context can be empty."""
        error = StructuredError(
            code="TEST_ERROR",
            message="Test error",
            severity="error",
            retryable=False,
            source_agent="supervisor",
            request_id="req-123",
            trace_id="trace-456",
            timestamp=datetime.now(timezone.utc).isoformat(),
            related_context={}
        )
        
        assert error.related_context == {}
    
    def test_serialization_round_trip(self):
        """Test that error can be serialized and deserialized."""
        original = StructuredError(
            code="VALIDATION_ERROR",
            message="Invalid input data",
            severity="error",
            retryable=False,
            source_agent="supervisor",
            request_id="req-123",
            trace_id="trace-456",
            timestamp=datetime.now(timezone.utc).isoformat(),
            related_context={"field": "client_id"}
        )
        
        # Serialize to dict
        data = original.dict()
        
        # Deserialize back
        restored = StructuredError(**data)
        
        assert restored.code == original.code
        assert restored.message == original.message
        assert restored.severity == original.severity
        assert restored.retryable == original.retryable
        assert restored.request_id == original.request_id
    
    def test_json_serialization_round_trip(self):
        """Test that error can be serialized to JSON and back."""
        original = StructuredError(
            code="VALIDATION_ERROR",
            message="Invalid input data",
            severity="error",
            retryable=False,
            source_agent="supervisor",
            request_id="req-123",
            trace_id="trace-456",
            timestamp=datetime.now(timezone.utc).isoformat(),
            related_context={}
        )
        
        # Serialize to JSON
        json_str = original.json()
        
        # Deserialize back
        restored = StructuredError.parse_raw(json_str)
        
        assert restored.code == original.code
        assert restored.message == original.message
        assert restored.severity == original.severity


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
