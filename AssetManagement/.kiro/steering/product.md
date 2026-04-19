# Product Overview

## Product name
Autonomous Portfolio Construction and Rebalancing Platform

## Purpose
This product is a production-grade multi-agent financial decision-support system that constructs and rebalances client portfolios using Amazon Bedrock Agents with a native Bedrock supervisor.

## Target users
- Portfolio managers
- Investment operations analysts
- Risk and compliance reviewers
- Financial advisors
- Internal platform administrators

## Core capabilities
- Accept client portfolio rebalance requests
- Use a Bedrock Supervisor Agent to orchestrate specialist agents
- Retrieve current market data and summarize news and sentiment
- Retrieve and update long-term client preferences and past decisions
- Calculate drift, risk, and compliance constraints
- Generate proposed trades and approval-ready trade tickets
- Require human approval before any execution-ready output is finalized

## Business goals
- Reduce time to produce rebalance recommendations
- Improve consistency and auditability of portfolio reviews
- Enforce mandate compliance and approval controls
- Build a governed, explainable AI system for financial workflows

## Product boundaries
- The system provides recommendations and approval artifacts
- The system does not autonomously execute trades in production without explicit human approval
- The system must not present unsupported performance claims or unverified market facts

## Success criteria
- Recommendations are explainable and evidence-backed
- Compliance checks are always performed before trade proposals are surfaced
- All agent activity is observable and auditable
- Long-term memory improves client-specific personalization over time