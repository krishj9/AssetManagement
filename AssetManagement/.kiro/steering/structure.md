# Project Structure and Development Rules

## Repository layout
- docs/ for architecture, governance, and runbooks
- agents/ for agent-specific code, prompts, schemas, and adapters
- schemas/ for shared JSON schemas
- tests/contracts for schema and interface tests
- tests/evals for scenario, safety, and regression evaluations
- frontend/qt for desktop UI
- infra/ for AWS setup artifacts, deployment notes, and scripts
- .kiro/steering for persistent project instructions
- .kiro/specs for feature specifications

## Coding rules
- Keep Bedrock agent contracts separate from UI models
- Every agent contract must have a schema
- Every feature spec must produce requirements.md, design.md, and tasks.md
- Never generate code before requirements and design are reviewed
- All changes to prompts or policies must trigger tests and eval review
- Every operator action affecting recommendations must be audit logged

## Architecture rules
- Supervisor Agent is the only entrypoint for frontend requests
- Collaborator agents are Research, Risk & Compliance, Memory & Personalization, and Execution
- Memory access is limited to approved memory read/write interfaces
- UI consumes structured DTOs only