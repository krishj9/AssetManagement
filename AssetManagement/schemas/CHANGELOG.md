# Schema Changelog

This document tracks all changes to schema definitions across versions.

## Version 1.0.0 (2024-01-15)

### Initial Release

All schemas created for the initial production release of the Bedrock Multi-Agent Portfolio Platform.

#### Portfolio_Rebalance_Request (v1.0.0)
- **Added**: Initial schema for portfolio rebalance requests
- **Fields**: client_id, account_id, current_holdings, current_allocation, target_allocation, cash_position, investment_objective, risk_profile, mandate_constraints, requested_action_context, schema_version
- **Validation**: Allocation percentages must sum to 100% (±0.1% tolerance), market_value must match quantity * current_price

#### Supervisor_Response (v1.0.0)
- **Added**: Initial schema for supervisor agent responses
- **Fields**: request_id, session_id, trace_id, timestamp, agent_version, schema_version, policy_version, environment_alias, workflow_state, recommendation_package, structured_error
- **Enums**: WorkflowState (NORMAL, DEGRADED, LOW_CONFIDENCE, BLOCKED)

#### Research_Response (v1.0.0)
- **Added**: Initial schema for research agent responses
- **Fields**: request_id, session_id, trace_id, timestamp, agent_version, schema_version, market_data, sentiment_analysis, confidence_score, evidence, provenance_metadata, degraded_mode, degraded_mode_reason, missing_data
- **Nested Models**: MarketDataPoint, SentimentAnalysis, Evidence, ProvenanceMetadata

#### Memory_Personalization_Response (v1.0.0)
- **Added**: Initial schema for memory & personalization agent responses
- **Fields**: request_id, session_id, trace_id, timestamp, agent_version, schema_version, memory_items, memory_items_count, memory_categories_retrieved, conflicts, conflicts_detected, overall_confidence_score, memory_completeness, memory_version, memory_freshness, stale_memory_warning, low_confidence_warning, degraded_mode, memory_summary
- **Nested Models**: MemoryItem, MemoryConflict
- **Enums**: MemoryCategory (PROFILE_FACTS, EPISODIC_DECISIONS, DERIVED_PREFERENCES, REJECTED_CANDIDATES)

#### Risk_Compliance_Response (v1.0.0)
- **Added**: Initial schema for risk & compliance agent responses
- **Fields**: request_id, session_id, trace_id, timestamp, agent_version, schema_version, drift_analysis, risk_metrics, compliance_verdict, evidence, overall_confidence_score, provenance_metadata
- **Nested Models**: DriftAnalysis, RiskMetric, ComplianceViolation, ComplianceCheck, ComplianceVerdict, RiskComplianceEvidence
- **Enums**: ComplianceStatus (COMPLIANT, NON_COMPLIANT, UNRESOLVED), ViolationSeverity (CRITICAL, HIGH, MEDIUM, LOW, INFO)

#### Execution_Response (v1.0.0)
- **Added**: Initial schema for execution agent responses
- **Fields**: request_id, session_id, trace_id, timestamp, agent_version, schema_version, trade_proposals, trade_proposals_count, portfolio_impact, approval_ready, approval_blocked_reason, overall_confidence_score, evidence, provenance_metadata, execution_summary
- **Nested Models**: TradeProposal, PortfolioImpact, ExecutionEvidence
- **Enums**: TradeAction (BUY, SELL)

#### Approval_Artifact (v1.0.0)
- **Added**: Initial schema for approval artifacts
- **Fields**: approval_id, request_id, trace_id, timestamp, agent_version, schema_version, policy_version, environment_alias, trade_proposals, trade_proposals_count, compliance_verdict, recommendation_rationale, evidence_summary, memory_summary, workflow_state, approval_status, approval_eligible, approval_blocked_reason, approved_by, approved_at, rejected_by, rejected_at, rejection_note, override_note, created_at, updated_at
- **Enums**: ApprovalStatus (PENDING, APPROVED, REJECTED, REVISION_REQUESTED)

#### Audit_Event (v1.0.0)
- **Added**: Initial schema for audit events
- **Fields**: event_id, event_type, request_id, session_id, trace_id, timestamp, actor_identity, actor_role, agent_identity, agent_version, action_details, outcome, policy_version, environment_alias, metadata
- **Enums**: EventType (REQUEST_RECEIVED, AGENT_INVOKED, AGENT_COMPLETED, STRUCTURED_ERROR, COMPLIANCE_VERDICT, GUARDRAIL_EVENT, MEMORY_READ, MEMORY_WRITE, MEMORY_CORRECTION, APPROVAL_ACTION, RELEASE_PROMOTION, ROLLBACK_EVENT)

#### Memory_Record (v1.0.0)
- **Added**: Initial schema for memory records in AgentCore Memory
- **Fields**: memory_id, client_id, category, content, content_summary, confidence_score, created_at, updated_at, memory_version, provenance, expiry_policy, is_active, is_archived, invalidated, invalidation_reason
- **Nested Models**: ExpiryPolicy, MemoryProvenance

#### Structured_Error (v1.0.0)
- **Added**: Initial schema for structured errors
- **Fields**: code, message, severity, retryable, source_agent, request_id, trace_id, timestamp, related_context

#### Recommendation_Quality_Metadata (v1.0.0)
- **Added**: Initial schema for recommendation quality metadata
- **Fields**: overall_confidence, workflow_state, contributing_agents, missing_evidence, stale_data_flags, unresolved_controls, advisory_completeness, approval_eligibility

---

## Schema Versioning Guidelines

### Semantic Versioning

Schemas follow semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes (incompatible with previous versions)
  - Removing required fields
  - Changing field types
  - Changing validation rules that reject previously valid data
  - Renaming fields

- **MINOR**: Backward-compatible additions
  - Adding optional fields
  - Adding new enum values
  - Relaxing validation rules

- **PATCH**: Bug fixes and clarifications
  - Documentation updates
  - Fixing validation bugs that were too strict
  - Internal implementation changes

### Backward Compatibility Rules

1. **Same major version = backward compatible**
   - Clients using v1.0.0 can work with servers using v1.1.0 or v1.2.0
   - Servers must accept requests from any v1.x.x client

2. **Different major version = breaking change**
   - Clients using v1.x.x cannot work with servers using v2.x.x
   - Requires explicit migration

3. **Optional fields**
   - New fields must be optional to maintain backward compatibility
   - Use sensible defaults for new optional fields

4. **Deprecation process**
   - Mark fields as deprecated in MINOR version
   - Remove deprecated fields in next MAJOR version
   - Provide migration guide for breaking changes

### Adding New Schema Versions

When adding a new schema version:

1. Update the schema file with changes
2. Increment version number according to semantic versioning
3. Add entry to this CHANGELOG with:
   - Version number and date
   - List of changes (Added, Changed, Deprecated, Removed, Fixed)
   - Migration notes if breaking changes
4. Update `SchemaVersionValidator.SUPPORTED_VERSIONS` in `version_validator.py`
5. Update `SchemaVersionValidator.CURRENT_VERSION` if this is the new production version
6. Run all contract tests to ensure backward compatibility
7. Update example data in schema Config classes

---

## Future Versions

### Planned for v1.1.0 (TBD)
- No changes planned yet

### Planned for v2.0.0 (TBD)
- No breaking changes planned yet
