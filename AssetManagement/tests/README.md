# Test Suite for Bedrock Multi-Agent Portfolio Platform

## Overview

This directory contains comprehensive contract tests for all schemas in the platform. Contract tests validate schema structure, required fields, serialization, and version compatibility.

## Test Categories

### 1. Contract Tests (Phase 1.3)

#### Portfolio Rebalance Request Tests
- **File:** `test_contract_portfolio_rebalance_request.py`
- **Coverage:**
  - Required fields validation
  - Allocation math correctness (sum to 1.0)
  - Constraint validation
  - Holdings validation
  - Serialization round-trips

#### Agent Response Tests
- **File:** `test_contract_agent_responses.py`
- **Coverage:**
  - Required fields for all agent responses
  - Metadata presence (request_id, session_id, trace_id, timestamp)
  - Version fields (agent_version, schema_version)
  - Cross-schema consistency

#### Structured Error Tests
- **File:** `test_contract_structured_error.py`
- **Coverage:**
  - Required fields (code, message, severity)
  - Correlation metadata
  - Error code format
  - Severity levels
  - Retryable flag

#### Approval Artifact Tests
- **File:** `test_contract_approval_artifact.py`
- **Coverage:**
  - Required fields completeness
  - Approval state transitions (PENDING → APPROVED/REJECTED)
  - Workflow state validation (NORMAL, DEGRADED, LOW_CONFIDENCE, BLOCKED)
  - Compliance verdict integration

#### Schema Versioning Tests
- **File:** `test_contract_schema_versioning.py`
- **Coverage:**
  - Schema version validation
  - Backward compatibility
  - Version migration
  - Version coexistence

#### Serialization Tests (Property-Based)
- **File:** `test_contract_serialization.py`
- **Coverage:**
  - Dict serialization round-trips
  - JSON serialization round-trips
  - Nested object preservation
  - Edge cases (empty collections, special characters, unicode)

## Running Tests

### Install Test Dependencies

```bash
pip install -r requirements-test.txt
```

### Run All Contract Tests

```bash
# Run all tests
pytest AssetManagement/tests/ -v

# Run with coverage
pytest AssetManagement/tests/ --cov=AssetManagement/schemas --cov-report=html

# Run specific test file
pytest AssetManagement/tests/test_contract_portfolio_rebalance_request.py -v

# Run with detailed output
pytest AssetManagement/tests/ -vv
```

### Run Property-Based Tests

```bash
# Run with more examples (default is 100)
pytest AssetManagement/tests/test_contract_serialization.py --hypothesis-show-statistics

# Run with specific seed for reproducibility
pytest AssetManagement/tests/test_contract_serialization.py --hypothesis-seed=12345
```

## Test Results

### Expected Pass Rate

All contract tests must achieve **100% pass rate** before promotion to production. This is a critical release gate.

### Coverage Goals

- **Schema Coverage:** 100% of all schemas tested
- **Field Coverage:** 100% of required fields validated
- **Serialization Coverage:** All schemas tested for round-trip serialization

## Test Structure

Each test file follows this structure:

```python
class TestSchemaContract:
    """Contract tests for Schema."""
    
    def test_required_fields_present(self):
        """Test that all required fields must be present."""
        pass
    
    def test_serialization_round_trip(self):
        """Test that schema can be serialized and deserialized."""
        pass
```

## Adding New Tests

When adding new schemas or fields:

1. Create a new test file: `test_contract_<schema_name>.py`
2. Add tests for required fields
3. Add tests for validation rules
4. Add serialization round-trip tests
5. Update this README

## Continuous Integration

These tests should be run:
- On every commit (pre-commit hook)
- On every pull request
- Before deployment to any environment
- As part of release gate validation

## Test Maintenance

- Review tests when schemas change
- Update tests for new schema versions
- Maintain backward compatibility tests
- Document breaking changes

## Related Documentation

- Schema definitions: `AssetManagement/schemas/`
- Schema changelog: `AssetManagement/schemas/CHANGELOG.md`
- Design document: `.kiro/specs/bedrock-multi-agent-portfolio-platform/design.md`
- Requirements: `.kiro/specs/bedrock-multi-agent-portfolio-platform/requirements.md`
