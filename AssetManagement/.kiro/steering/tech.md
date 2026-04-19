# Technology Stack

## Runtime platform
- Amazon Bedrock Agents for multi-agent collaboration
- Amazon Bedrock native Supervisor Agent for orchestration
- Amazon Bedrock AgentCore Memory for persistent client memory
- Amazon Bedrock AgentCore Observability for traces, logs, spans, and metrics
- Amazon Bedrock Guardrails for responsible AI controls
- Amazon Bedrock Runtime API for invocation

## Application components
- Qt desktop frontend for operator workflow and approvals
- Python Fast API backend/client integration for AWS SDK calls
- JSON schema validation for all agent input and output contracts
- Public data sources such as yfinance for price data

## Engineering standards
- Schema-first development
- Spec-driven development using Kiro specs
- No free-form downstream agent outputs; use structured JSON
- Version prompts, policies, schemas, and release aliases
- All major features require tests and eval scenarios
- All recommendation paths require observability and auditability

## Constraints
- No custom orchestration framework
- Bedrock supervisor is the only production orchestrator
- No autonomous production execution without human approval
- No raw chain-of-thought exposure in UI
- Observability must use AWS-native services as the production source of truth