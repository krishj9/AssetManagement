# Design Document: Bedrock Multi-Agent Portfolio Platform

## Overview

The Autonomous Portfolio Construction and Rebalancing Platform is a production-grade, serverless, multi-agent financial decision-support system built on Amazon Bedrock Agents. The system uses a native Bedrock Supervisor Agent as the only orchestration entrypoint and delegates domain-specific work to collaborator agents for Research, Risk & Compliance, Memory & Personalization, and Execution.

The platform is designed to:
- produce explainable and evidence-backed portfolio recommendations,
- enforce mandate and suitability checks before trade proposals are surfaced,
- use AgentCore Memory for long-term client context,
- use AgentCore Observability and CloudWatch as the operational source of truth,
- apply Bedrock Guardrails for safety, grounding, and sensitive data protections,
- and require explicit human approval before any action-ready output can proceed.

This design assumes Bedrock native supervisor orchestration and does not introduce a custom orchestration framework.

---

## Design Goals

### Primary goals
- Use Amazon Bedrock native supervisor orchestration for all production workflow coordination.
- Keep agent responsibilities sharply bounded and minimize overlap.
- Enforce human-in-the-loop control for all approval-bearing outputs.
- Make every recommendation explainable, evidence-backed, and auditable.
- Use AWS-native memory, observability, and guardrail services as first-class platform capabilities.

### Secondary goals
- Keep contracts schema-first and versioned.
- Support degraded operation where safe and blocked operation where required.
- Separate environment aliases for dev, test, pre-prod, and prod.
- Enable future extension to downstream OMS or broker execution without changing the core recommendation and approval design.

### Non-goals
- Autonomous trade execution without approval.
- Custom orchestration engine outside Bedrock supervisor/collaborator mode.
- Direct frontend invocation of collaborator agents.
- Exposure of raw chain-of-thought in UI, logs, or telemetry.

---

## System Context

### External actors
- Portfolio manager
- Investment operations analyst
- Compliance reviewer
- Platform administrator
- Release manager

### External systems
- Amazon Bedrock Agents
- Amazon Bedrock AgentCore Memory
- Amazon Bedrock AgentCore Observability
- Amazon Bedrock Guardrails
- Amazon CloudWatch
- Amazon DynamoDB
- Qt desktop client
- Public price data providers such as yfinance
- Optional downstream execution or OMS integration in later phases

---

## Architecture Summary

The architecture is a Bedrock-native hierarchical multi-agent system. The Supervisor Agent receives a request from the Qt frontend through the Bedrock Runtime API, determines which collaborators must be invoked, consolidates their outputs, and returns a structured recommendation package.

The supervisor coordinates four collaborator agents:
1. Research Agent
2. Memory & Personalization Agent
3. Risk & Compliance Agent
4. Execution Agent

The Supervisor Agent is deployed and invoked through environment-specific aliases. Collaborator agents are associated to the supervisor through alias versions appropriate to the environment.

The system uses:
- AgentCore Memory for long-term memory retrieval and persistence,
- AgentCore Observability and CloudWatch for traces, spans, logs, metrics, dashboards, and alarms,
- Bedrock Guardrails for denied topics, content filtering, sensitive information protection, and contextual grounding checks.

---

## Component Model

### 1. Supervisor Agent

#### Responsibilities
- Accept validated rebalance requests from the frontend path.
- Interpret workflow intent and determine task sequence.
- Invoke required collaborator agents.
- Consolidate outputs into a recommendation package.
- Apply workflow-level status decisions such as normal, degraded, low-confidence, or blocked.
- Return a structured result to the frontend.

#### Design constraints
- Must be the only frontend-facing agent entrypoint.
- Must not duplicate collaborator-specific business logic.
- Must preserve request, session, trace, version, and policy metadata across the workflow.
- Must operate in either coordination mode or routing mode depending on latency and synthesis requirements.

### 2. Research Agent

#### Responsibilities
- Retrieve latest market prices using approved public data sources.
- Produce market context, news summary, and sentiment summary using Bedrock-hosted models.
- Distinguish between retrieved facts and model-derived commentary.
- Return evidence, provenance, and freshness metadata.

#### Design constraints
- Must not fabricate unsupported market facts.
- Must clearly mark partial or stale research.
- Must separate raw source retrieval from downstream interpretation.

### 3. Memory & Personalization Agent

#### Responsibilities
- Retrieve relevant long-term client memory from AgentCore Memory.
- Return structured personalization context to the supervisor.
- Propose memory candidates for persistence after workflow completion.
- Manage memory correction and invalidation pathways through approved interfaces.

#### Design constraints
- Must not expose raw memory store payloads.
- Must label memory by category, recency, and confidence.
- Must distinguish retrieval from post-session writeback processing.

### 4. Risk & Compliance Agent

#### Responsibilities
- Calculate portfolio drift.
- Evaluate policy and mandate constraints.
- Produce risk metrics and compliance verdicts.
- Identify blocking and non-blocking violations.

#### Design constraints
- Deterministic checks must be separate from model-assisted explanation.
- Compliance outcomes must be machine-readable.
- Unresolved compliance conditions must produce a blocked recommendation state.

### 5. Execution Agent

#### Responsibilities
- Generate structured trade proposals from approved upstream analysis.
- Estimate allocation effects, costs, and available tax-impact information.
- Produce approval-artifact-ready outputs.

#### Design constraints
- Must never execute trades directly.
- Must not generate approval-ready output when compliance is unresolved or failed.
- Must produce structured rationale tied to evidence and upstream findings.

### 6. Qt Desktop Frontend

#### Responsibilities
- Collect rebalance request input.
- Invoke the supervisor alias via Bedrock Runtime API.
- Present workflow progress, safe reasoning summaries, memory summary, allocation views, compliance status, and approval controls.
- Collect approval, rejection, or revision actions.

#### Design constraints
- Must consume only structured DTOs.
- Must not display raw chain-of-thought.
- Must block or disable actions based on workflow state and policy.

### 7. AgentCore Memory

#### Responsibilities
- Store and retrieve long-term client memory.
- Support memory extraction and consolidation lifecycle.
- Support memory categories, access control, and structured retrieval.

#### Design constraints
- Long-term memory formation is asynchronous.
- Retrieval and write behavior must support auditability and correction.
- Memory namespaces and categories should support future scale and policy separation.

### 8. AgentCore Observability and CloudWatch

#### Responsibilities
- Provide traceability across request lifecycle.
- Provide metrics, spans, logs, dashboards, and alerts.
- Correlate agent execution with memory activity and audit events.

#### Design constraints
- Must be the production source of truth for operational observability.
- Must support trace-to-audit correlation.
- Must not include raw chain-of-thought.

### 9. Bedrock Guardrails

#### Responsibilities
- Enforce denied topics.
- Enforce content filtering.
- Enforce sensitive information handling.
- Enforce contextual grounding for recommendation-bearing outputs.

#### Design constraints
- Some violations may be non-overridable by policy.
- Grounding checks should be applied where outputs depend on retrieved evidence.
- Guardrail outcomes must be structured and logged.

### 10. DynamoDB Persistence Layer

#### Responsibilities
- Store and retrieve approval artifacts with approval state tracking.
- Store and retrieve audit events with queryable access patterns.
- Store and retrieve session state with automatic TTL-based cleanup.
- Store and retrieve memory consolidation queue tasks with status tracking.

#### Design constraints
- Must use primary keys and GSIs for efficient queries; avoid expensive scans.
- Must use conditional writes for approval state transitions to prevent race conditions.
- Must implement TTL for automatic cleanup of expired records.
- Must use on-demand billing mode for cost optimization and automatic scaling.
- Must support point-in-time recovery (PITR) for disaster recovery.
- Must use encryption at rest with AWS-managed keys.
- Must integrate with CloudWatch for metrics and alarms.

---

## Logical Workflow

### Request path

1. Operator submits a rebalance request in the Qt client.
2. Frontend validates the local form and sends a structured request to the Supervisor Agent alias.
3. Supervisor validates schema and creates workflow correlation metadata (request_id, session_id, trace_id).
4. System stores session state in DynamoDB Session State table.
5. Supervisor invokes Memory & Personalization Agent to hydrate client context.
6. Supervisor invokes Research Agent for market context and sentiment.
7. Supervisor invokes Risk & Compliance Agent for drift, risk metrics, and mandate checks.
8. If compliance is blocked or unresolved, supervisor returns blocked response and does not request trade proposal generation.
9. If compliance is acceptable and sufficient data is available, supervisor invokes Execution Agent.
10. Execution Agent returns structured trade proposal package.
11. Supervisor consolidates outputs, sets workflow quality state, and returns recommendation package to frontend.
12. System creates Approval_Artifact and stores it in DynamoDB Approval Artifacts table.
13. System logs all agent invocations and outcomes as audit events in DynamoDB Audit Events table.
14. Frontend renders allocation comparison, trade proposal, compliance results, memory summary, and approval controls.
15. Human operator approves, rejects, or requests revision.
16. System updates approval artifact in DynamoDB with approval status, approved_by, approved_at (or rejection details).
17. System logs approval action as audit event in DynamoDB Audit Events table.
18. Approved outcomes generate memory consolidation tasks stored in DynamoDB Memory Consolidation Queue table.
19. Post-session memory extraction and consolidation update long-term memory asynchronously via AgentCore Memory.
20. System updates consolidation task status in DynamoDB Memory Consolidation Queue table.

---

## State Model

The system uses a workflow status model instead of treating all outputs as equivalent.

### States
- `NORMAL`: All required controls satisfied and recommendation is reviewable.
- `DEGRADED`: Non-critical information is missing, stale, or uncertain, but advisory review is still allowed by policy.
- `LOW_CONFIDENCE`: Recommendation is complete enough to inspect, but quality indicators are below preferred thresholds.
- `BLOCKED`: Critical controls are unresolved; approval is not allowed.

### State ownership
- Collaborator agents report local quality and blocking conditions.
- Supervisor determines final workflow state.
- Frontend uses workflow state to enable or disable actions.

### State transition rules
- Missing or unresolved compliance data causes `BLOCKED`.
- Non-critical research gaps may cause `DEGRADED`.
- Low evidence strength or stale memory may cause `LOW_CONFIDENCE`.
- Material recommendation changes invalidate prior approval state.

---

## Data Model Overview

The system uses versioned, schema-first, machine-readable contracts.

### Core objects
- `Portfolio_Rebalance_Request`
- `Supervisor_Response`
- `Research_Response`
- `Memory_Personalization_Response`
- `Risk_Compliance_Response`
- `Execution_Response`
- `Trade_Proposal`
- `Approval_Artifact`
- `Structured_Error`
- `Audit_Event`
- `Memory_Record`
- `Recommendation_Quality_Metadata`

### Shared metadata fields
Every major contract should include:
- request_id
- session_id
- trace_id
- timestamp
- agent_version
- schema_version
- policy_version
- environment_alias

### Recommendation metadata
Every recommendation-bearing object should include:
- confidence_score
- evidence
- provenance_metadata
- workflow_state
- degraded_mode_reason if applicable

---

## DynamoDB Table Design

The system uses four DynamoDB tables for durable persistence.

### Table 1: Approval Artifacts

**Purpose:** Store approval artifacts with approval state tracking and queryable access by approval_id and request_id.

**Primary Key:**
- Partition Key: `approval_id` (String)

**Global Secondary Indexes:**
- GSI1: `request_id` (Partition Key) → allows lookup by request_id

**Attributes:**
- `approval_id` (String, PK)
- `request_id` (String, GSI1 PK)
- `trace_id` (String)
- `timestamp` (String, ISO 8601)
- `agent_version` (String)
- `schema_version` (String)
- `policy_version` (String)
- `trade_proposals` (List of Maps)
- `compliance_verdict` (Map)
- `rationale` (Map)
- `evidence` (Map)
- `memory_summary` (Map)
- `workflow_state` (String: NORMAL, DEGRADED, LOW_CONFIDENCE, BLOCKED)
- `approval_status` (String: PENDING, APPROVED, REJECTED, REVISION_REQUESTED)
- `approved_by` (String, optional)
- `approved_at` (String, ISO 8601, optional)
- `rejected_by` (String, optional)
- `rejected_at` (String, ISO 8601, optional)
- `rejection_note` (String, optional)
- `override_note` (String, optional)
- `created_at` (String, ISO 8601)
- `updated_at` (String, ISO 8601)
- `ttl` (Number, Unix timestamp for TTL expiration)

**Access Patterns:**
- Get approval artifact by approval_id (primary key lookup)
- Get approval artifact by request_id (GSI1 query)
- Update approval status with conditional write (prevent race conditions)

**TTL:** 90 days after creation for compliance retention

---

### Table 2: Audit Events

**Purpose:** Store audit events with queryable access by event_id, request_id, trace_id, and timestamp for compliance review.

**Primary Key:**
- Partition Key: `event_id` (String)

**Global Secondary Indexes:**
- GSI1: `request_id` (Partition Key), `timestamp` (Sort Key) → allows query by request_id with time ordering
- GSI2: `trace_id` (Partition Key), `timestamp` (Sort Key) → allows query by trace_id with time ordering
- GSI3: `timestamp` (Partition Key), `event_type` (Sort Key) → allows time-range queries with event type filtering

**Attributes:**
- `event_id` (String, PK)
- `event_type` (String: REQUEST_RECEIVED, AGENT_INVOKED, AGENT_COMPLETED, STRUCTURED_ERROR, COMPLIANCE_VERDICT, GUARDRAIL_EVENT, MEMORY_READ, MEMORY_WRITE, MEMORY_CORRECTION, APPROVAL_ACTION, RELEASE_PROMOTION, ROLLBACK_EVENT)
- `request_id` (String, GSI1 PK)
- `session_id` (String)
- `trace_id` (String, GSI2 PK)
- `timestamp` (String, ISO 8601, GSI1/GSI2/GSI3 SK)
- `actor_identity` (String, optional for human actions)
- `actor_role` (String, optional for human actions)
- `agent_identity` (String, optional for agent actions)
- `agent_version` (String, optional for agent actions)
- `action_details` (Map)
- `outcome` (String)
- `policy_version` (String)
- `environment_alias` (String)
- `ttl` (Number, Unix timestamp for TTL expiration)

**Access Patterns:**
- Get audit event by event_id (primary key lookup)
- Query audit events by request_id with time ordering (GSI1)
- Query audit events by trace_id with time ordering (GSI2)
- Query audit events by timestamp range with event type filtering (GSI3)

**TTL:** 7 years (2557 days) for regulatory compliance

---

### Table 3: Session State

**Purpose:** Store session state with automatic TTL-based cleanup for active user sessions.

**Primary Key:**
- Partition Key: `session_id` (String)

**Attributes:**
- `session_id` (String, PK)
- `request_id` (String)
- `user_identity` (String)
- `user_role` (String)
- `workflow_state` (String: NORMAL, DEGRADED, LOW_CONFIDENCE, BLOCKED)
- `created_at` (String, ISO 8601)
- `updated_at` (String, ISO 8601)
- `last_activity_at` (String, ISO 8601)
- `ttl` (Number, Unix timestamp for TTL expiration)

**Access Patterns:**
- Get session state by session_id (primary key lookup)
- Update session state with last_activity_at timestamp

**TTL:** 24 hours after last_activity_at for automatic cleanup

---

### Table 4: Memory Consolidation Queue

**Purpose:** Store memory consolidation tasks with status tracking for asynchronous memory processing.

**Primary Key:**
- Partition Key: `consolidation_id` (String)

**Global Secondary Indexes:**
- GSI1: `consolidation_status` (Partition Key), `created_at` (Sort Key) → allows query by status with time ordering

**Attributes:**
- `consolidation_id` (String, PK)
- `request_id` (String)
- `client_id` (String)
- `memory_candidates` (List of Maps)
- `consolidation_status` (String: PENDING, IN_PROGRESS, COMPLETED, FAILED)
- `created_at` (String, ISO 8601, GSI1 SK)
- `updated_at` (String, ISO 8601)
- `processed_at` (String, ISO 8601, optional)
- `error_details` (Map, optional)
- `ttl` (Number, Unix timestamp for TTL expiration)

**Access Patterns:**
- Get consolidation task by consolidation_id (primary key lookup)
- Query pending consolidation tasks by status with time ordering (GSI1)
- Update consolidation status with conditional write

**TTL:** 30 days after creation for cleanup

---

## DynamoDB Design Principles

### Efficiency
- Use primary keys and GSIs for all queries; avoid expensive scans.
- Use sparse GSIs where appropriate to reduce index size and cost.
- Use projection expressions to retrieve only required attributes.

### Consistency
- Use conditional writes for approval state transitions to prevent race conditions.
- Use optimistic locking with version attributes where needed.

### Cost Optimization
- Use on-demand billing mode for automatic scaling and cost optimization.
- Use TTL for automatic cleanup of expired records.
- Monitor read/write capacity and throttling in CloudWatch.

### Durability and Recovery
- Enable point-in-time recovery (PITR) for all tables for disaster recovery.
- Use encryption at rest with AWS-managed keys.
- Enable DynamoDB Streams for audit event processing if needed.

### Access Control
- Use IAM roles and policies to control access to DynamoDB tables based on RBAC requirements.
- Separate read and write permissions by role.

---

## Memory Lifecycle Design

Memory is not just a simple read/write store. The design must support retrieval, extraction, consolidation, correction, and lifecycle governance.

### Memory categories
- Profile facts
- Episodic decisions
- Derived preferences
- Rejected memory candidates

### Retrieval design
- Memory retrieval is handled by the Memory & Personalization Agent through approved interfaces.
- Retrieval uses semantic relevance and category-aware filtering.
- Memory results include recency, confidence, and memory version metadata.

### Writeback design
After a workflow concludes, the system prepares memory candidates such as:
- approved portfolio preferences,
- decision rationales,
- persistent client dislikes or exclusions,
- important decision outcomes.

### Extraction and consolidation design
- New memory candidates are extracted from recent workflow artifacts.
- Consolidation merges or updates new candidates against existing memory.
- Low-confidence or conflicting candidates are not automatically treated as authoritative.
- Memory formation is asynchronous and may not be immediately available for subsequent sessions.

### Correction and deletion design
- Authorized users may invalidate or correct memory records.
- Memory expiry and archival policies govern long-lived inferred preferences.
- All corrections, invalidations, deletions, and merges are auditable.

### Observability for memory
The system must track:
- read counts,
- write counts,
- extraction start/completion,
- extraction success/failure counts,
- consolidation start/completion,
- updates, additions, and rejected candidates.

---

## Guardrails and Policy Enforcement Design

Guardrails are applied as a dedicated control layer, not as an afterthought.

### Guardrail categories
- Denied topics
- Harmful content filtering
- Sensitive information filtering
- Contextual grounding checks
- Word filters where policy requires them

### Guardrail placement
- Input screening before recommendation-bearing prompts where appropriate.
- Output screening before recommendation-bearing responses are accepted into downstream processing.
- Grounding checks on outputs derived from research evidence and retrieved sources.
- Sensitive-information filtering on operator-visible summaries where required.

### Guardrail outcome handling
- Non-critical guardrail issues may produce flagged or degraded outputs if policy allows.
- Critical policy violations produce blocked responses.
- Non-overridable violations are determined by governance policy.
- All guardrail outcomes are logged with policy version and trace correlation.

---

## Trust Boundaries and RBAC

### Trust boundaries
1. **Frontend boundary**  
   The Qt client is trusted only for user interaction, not for business logic enforcement.
2. **Supervisor boundary**  
   The supervisor is the only orchestration boundary for frontend-originated requests.
3. **Collaborator boundary**  
   Collaborators are bounded specialists with no direct frontend exposure.
4. **Memory boundary**  
   AgentCore Memory is accessible only through approved memory interfaces.
5. **Approval boundary**  
   Human approval is a control boundary that cannot be bypassed through normal product paths.
6. **Release boundary**  
   Alias promotion and production policy changes are privileged operations.

### RBAC roles
- Operator
- Portfolio manager
- Compliance reviewer
- Platform admin
- Release manager

### Role rules
- Only authorized roles may approve recommendations.
- Only authorized roles may override eligible warnings.
- Only authorized roles may correct or invalidate memory.
- Only authorized roles may review restricted audit data.
- Only authorized roles may promote aliases across environments.

---

## Environment and Alias Design

### Environment model
The system uses isolated environments:
- dev
- test
- pre-prod
- prod

### Alias design
- The Supervisor Agent is invoked through an environment-specific alias.
- Collaborator agents are attached to the supervisor through alias versions appropriate to the same environment.
- Alias metadata is propagated into audit and observability records.

### Promotion rules
- Promotions occur only after successful eval and review gates.
- Each environment maintains separately documented prompt, policy, schema, and agent versions.
- Rollback uses prior approved aliases.
- Production must never depend on development aliases.

---

## Observability Design

### Objectives
- Trace every request end to end.
- Provide latency, error, and quality monitoring.
- Correlate memory behavior with recommendation quality.
- Correlate audit events with runtime traces.

### Telemetry strategy
For each request:
- Create a trace.
- Represent supervisor and collaborator work as correlated spans or equivalent trace units.
- Capture workflow state transitions.
- Capture relevant structured inputs and outputs without exposing hidden reasoning.
- Capture memory retrieval, extraction, consolidation, and write outcomes.
- Capture approval actions and policy outcomes.

### Monitoring dimensions
- request volume
- latency
- error rate
- blocked-state rate
- degraded-mode rate
- low-confidence rate
- memory retrieval frequency
- extraction and consolidation failure rates
- guardrail violation rate
- approval turnaround time
- override frequency

### Dashboards
- executive workflow dashboard
- agent performance dashboard
- memory health dashboard
- compliance and guardrail dashboard
- approval workflow dashboard

### Alerting
Create alarms for:
- elevated error rate
- rising blocked-state rate
- memory consolidation failures
- abnormal latency
- abnormal guardrail violation spikes
- approval workflow failures

---

## Audit Design

Audit is a first-class design capability and complements observability.

### Audit event categories
- request received
- agent invoked
- agent completed
- structured error emitted
- compliance verdict generated
- guardrail event recorded
- memory read
- memory write
- memory correction
- approval action
- release promotion
- rollback event

### Audit correlation
Every auditable action should include:
- request_id
- trace_id where available
- timestamp
- actor identity or agent identity
- version metadata
- environment alias

### Audit access
Audit data is not directly exposed to the general frontend surface. Access is mediated by role-aware backend or administrative workflows.

---

## Failure Handling Design

### Error model
All machine-consumable failures use `Structured_Error`.

### Failure categories
- validation failure
- research retrieval failure
- memory retrieval failure
- compliance failure
- execution proposal failure
- guardrail violation
- authorization failure
- unsupported schema version
- invalid entrypoint
- approval required

### Handling approach
- Validation failure: immediate error response.
- Non-critical data failure: degraded mode if policy allows.
- Compliance unresolved or failed: blocked state.
- Guardrail critical violation: blocked state.
- Memory conflict: low-confidence or blocked depending on policy and affected scope.
- Observability or audit failure: treat as blocking if policy requires audit completeness for approval progression.

---

## Recommendation Assembly Design

The Supervisor Agent consolidates collaborator outputs into a single structured recommendation package.

### Inputs to assembly
- request details
- memory context
- research bundle
- risk/compliance results
- execution proposal
- quality metadata
- guardrail outcomes

### Output sections
- portfolio summary
- current vs target allocation
- compliance verdict
- recommendation rationale
- evidence summary
- memory summary
- trade proposal
- workflow quality state
- operator actions permitted

### Assembly rules
- Must preserve source attribution and provenance.
- Must distinguish deterministic checks from narrative explanation.
- Must not present incomplete or blocked results as approval-ready.
- Must not include raw chain-of-thought.

---

## Frontend Interaction Design

### Main views
- request intake
- live workflow status
- safe reasoning and evidence summary
- memory summary
- allocation comparison
- trade proposal review
- approval controls
- governance metadata panel

### UX rules
- Show workflow progress per major stage.
- Clearly distinguish current, target, and proposed states.
- Surface blocked and degraded states prominently.
- Require note entry for rejection and approved override flows where policy allows.
- Disable approval when workflow state is blocked.
- Show trace and policy identifiers for review context.
- Never show raw chain-of-thought or internal-only logs.

---

## Security and Data Protection Design

### Principles
- Least privilege
- role-based authorization
- structured data minimization
- redaction where appropriate
- environment separation
- controlled memory access

### Sensitive information handling
- Sensitive information should be filtered or redacted where policy requires.
- UI summaries should avoid unnecessary client-identifying detail.
- Observability and audit surfaces should minimize exposure according to role.

---

## Evaluation and Release Design

### Eval categories
- contract tests
- golden scenario tests
- safety and adversarial tests
- compliance tests
- regression tests
- operational tests

### Release gate flow
1. change prompts, policies, schemas, or agent config
2. run required eval suites
3. review quality and safety results
4. promote environment alias if gates pass
5. monitor post-promotion telemetry
6. rollback if critical regressions occur

### Promotion artifacts
Each promotion should record:
- supervisor alias version
- collaborator alias versions
- policy version
- schema version
- prompt/instruction version
- eval run reference
- approval metadata for release

---

## Design Decisions

### Decision 1: Use Bedrock Supervisor as the only orchestrator
Rationale: This aligns with the target architecture and reduces orchestration duplication.

### Decision 2: Keep collaborator responsibilities sharply bounded
Rationale: Bedrock multi-agent guidance emphasizes minimizing overlap for better team performance.

### Decision 3: Treat memory as a lifecycle, not a key-value store
Rationale: AgentCore Memory supports extraction and consolidation and requires observability and correction patterns.

### Decision 4: Use workflow state model of normal, degraded, low-confidence, blocked
Rationale: Financial decision support requires clear separation between incomplete-but-reviewable and unsafe-to-approve outputs.

### Decision 5: Use AWS-native observability as the source of truth
Rationale: AgentCore Observability and CloudWatch align with the platform and reduce operational fragmentation.

### Decision 6: Require evidence, provenance, and structured rationale everywhere
Rationale: Explainability and auditability are core to financial decision workflows.

### Decision 7: Treat approval as an explicit control boundary
Rationale: Human accountability must remain central even when agents automate analysis.

---

## Open Design Considerations

These are not blockers for the initial design, but they should be refined in detailed implementation specs:
- whether supervisor uses coordination mode or routing mode by default,
- exact schema definitions for recommendation quality scoring,
- specific memory namespaces and category taxonomies,
- policy definitions for overridable versus non-overridable guardrail failures,
- exact latency targets and timeout budgets,
- future OMS or broker integration model,
- fine-grained approval routing for multi-step human review.

---

## Implementation Readiness Checklist

- Supervisor and collaborator roles clearly defined
- Request and response contracts identified
- Memory retrieval and writeback lifecycle identified
- Guardrail control points identified
- Workflow state model defined
- Trust boundaries and RBAC model defined
- Environment alias strategy defined
- Observability and audit correlation model defined
- Eval and promotion flow defined
- Frontend interaction model defined