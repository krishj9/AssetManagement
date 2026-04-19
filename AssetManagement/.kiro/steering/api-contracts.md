# API and Contract Standards

## General rules
- All agent outputs must be valid JSON matching an explicit schema
- Required fields must be present even when values are null or unavailable
- Include request_id, session_id, timestamp, and agent_version in all major payloads
- Include confidence and evidence metadata in recommendation-bearing outputs

## Error handling
- Do not return plain string errors for downstream processing
- Use structured error objects with code, message, severity, retryable, and source_agent
- Compliance failures are blocking errors
- Stale or partial research must be marked as degraded mode

## Compatibility
- Schemas must be backward compatible or versioned
- UI-facing DTOs must not directly expose provider-specific payload formats