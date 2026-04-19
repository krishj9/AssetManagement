"""
Supervisor Agent Orchestrator

This module implements the orchestration logic for the Supervisor Agent,
which coordinates all collaborator agents and consolidates their outputs
into a comprehensive recommendation package.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

from AssetManagement.backend.clients.bedrock_agent_client import BedrockAgentClient
from AssetManagement.backend.clients.agentcore_memory_client import AgentCoreMemoryClient
from AssetManagement.backend.clients.agentcore_observability_client import AgentCoreObservabilityClient
from AssetManagement.backend.clients.bedrock_guardrails_client import BedrockGuardrailsClient
from AssetManagement.backend.clients.cloudwatch_client import CloudWatchClient
from AssetManagement.infra.audit_events_repository import AuditEventsRepository
from AssetManagement.infra.approval_artifacts_repository import ApprovalArtifactsRepository
from AssetManagement.schemas.portfolio_rebalance_request import PortfolioRebalanceRequest
from AssetManagement.schemas.supervisor_response import SupervisorResponse
from AssetManagement.schemas.research_response import ResearchResponse
from AssetManagement.schemas.memory_personalization_response import MemoryPersonalizationResponse
from AssetManagement.schemas.risk_compliance_response import RiskComplianceResponse
from AssetManagement.schemas.execution_response import ExecutionResponse

logger = logging.getLogger(__name__)


class SupervisorAgentOrchestrator:
    """
    Orchestrator for Supervisor Agent workflow.
    
    Coordinates the invocation of all collaborator agents (Research, Memory,
    Risk & Compliance, Execution) and consolidates their outputs into a
    unified recommendation package.
    """
    
    # Agent Instructions for Bedrock Agent Configuration
    AGENT_INSTRUCTIONS = """
You are the Supervisor Agent for an autonomous portfolio management platform.

Your role is to:
1. Coordinate collaborator agents (Research, Memory, Risk & Compliance, Execution)
2. Consolidate their outputs into a recommendation package
3. Determine workflow state (NORMAL, DEGRADED, LOW_CONFIDENCE, BLOCKED)
4. Preserve metadata (request_id, session_id, trace_id, versions)

Workflow:
1. Receive portfolio rebalance request
2. Invoke Memory & Personalization Agent for client context
3. Invoke Research Agent for market data
4. Invoke Risk & Compliance Agent for drift and compliance checks
5. If compliance is BLOCKED, return blocked response
6. Otherwise, invoke Execution Agent for trade proposals
7. Consolidate all outputs and return recommendation package

Output Format: SupervisorResponse JSON schema

Never expose raw chain-of-thought. Only return structured JSON.
"""
    
    def __init__(
        self,
        bedrock_client: BedrockAgentClient,
        memory_client: AgentCoreMemoryClient,
        observability_client: AgentCoreObservabilityClient,
        guardrails_client: BedrockGuardrailsClient,
        cloudwatch_client: CloudWatchClient,
        audit_repo: AuditEventsRepository,
        approval_repo: ApprovalArtifactsRepository,
        supervisor_agent_id: str,
        supervisor_agent_alias: str = "dev"
    ):
        """
        Initialize Supervisor Agent Orchestrator.
        
        Args:
            bedrock_client: Bedrock Agent Runtime client
            memory_client: AgentCore Memory client
            observability_client: AgentCore Observability client
            guardrails_client: Bedrock Guardrails client
            cloudwatch_client: CloudWatch client
            audit_repo: Audit events repository
            approval_repo: Approval artifacts repository
            supervisor_agent_id: Supervisor agent ID from AWS
            supervisor_agent_alias: Agent alias (dev, test, prod)
        """
        self.bedrock_client = bedrock_client
        self.memory_client = memory_client
        self.observability_client = observability_client
        self.guardrails_client = guardrails_client
        self.cloudwatch_client = cloudwatch_client
        self.audit_repo = audit_repo
        self.approval_repo = approval_repo
        self.supervisor_agent_id = supervisor_agent_id
        self.supervisor_agent_alias = supervisor_agent_alias
        
        logger.info(
            "Supervisor Agent Orchestrator initialized",
            extra={
                'agent_id': supervisor_agent_id,
                'agent_alias': supervisor_agent_alias
            }
        )
    
    async def process_rebalance_request(
        self,
        request: PortfolioRebalanceRequest
    ) -> SupervisorResponse:
        """
        Process portfolio rebalance request through multi-agent workflow.
        
        Args:
            request: Portfolio rebalance request
        
        Returns:
            SupervisorResponse with recommendation package
        """
        # Generate correlation IDs
        session_id = f"sess-{uuid.uuid4()}"
        request_id = f"req-{uuid.uuid4()}"
        trace_id = f"trace-{uuid.uuid4()}"
        
        start_time = datetime.now(timezone.utc)
        
        try:
            logger.info(
                "Processing rebalance request",
                extra={
                    'request_id': request_id,
                    'session_id': session_id,
                    'trace_id': trace_id,
                    'client_id': request.client_id,
                    'account_id': request.account_id
                }
            )
            
            # Create trace
            self.observability_client.create_trace(
                trace_id=trace_id,
                request_id=request_id,
                session_id=session_id,
                metadata={
                    'client_id': request.client_id,
                    'account_id': request.account_id
                }
            )
            
            # Validate request
            self._validate_request(request)
            
            # Invoke Memory & Personalization Agent
            memory_response = await self._invoke_memory_agent(
                request, session_id, request_id, trace_id
            )
            
            # Invoke Research Agent
            research_response = await self._invoke_research_agent(
                request, session_id, request_id, trace_id
            )
            
            # Invoke Risk & Compliance Agent
            compliance_response = await self._invoke_compliance_agent(
                request, memory_response, research_response,
                session_id, request_id, trace_id
            )
            
            # Check if blocked
            if compliance_response.compliance_verdict.verdict in ['NON_COMPLIANT', 'UNRESOLVED']:
                return self._create_blocked_response(
                    request, memory_response, research_response,
                    compliance_response, session_id, request_id, trace_id
                )
            
            # Invoke Execution Agent
            execution_response = await self._invoke_execution_agent(
                request, memory_response, research_response, compliance_response,
                session_id, request_id, trace_id
            )
            
            # Consolidate outputs
            supervisor_response = self._consolidate_outputs(
                request, memory_response, research_response,
                compliance_response, execution_response,
                session_id, request_id, trace_id
            )
            
            # Determine workflow state
            workflow_state = self._determine_workflow_state(
                memory_response, research_response,
                compliance_response, execution_response
            )
            
            supervisor_response.workflow_state = workflow_state
            
            # Record metrics
            latency_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            self.cloudwatch_client.put_request_latency(latency_ms, 'process_rebalance_request')
            self.cloudwatch_client.put_request_volume()
            
            if workflow_state == 'BLOCKED':
                self.cloudwatch_client.put_blocked_state_rate()
            elif workflow_state == 'DEGRADED':
                self.cloudwatch_client.put_degraded_mode_rate()
            
            logger.info(
                "Rebalance request processed successfully",
                extra={
                    'request_id': request_id,
                    'session_id': session_id,
                    'trace_id': trace_id,
                    'workflow_state': workflow_state,
                    'latency_ms': latency_ms
                }
            )
            
            return supervisor_response
            
        except Exception as e:
            logger.error(
                f"Failed to process rebalance request: {str(e)}",
                extra={
                    'request_id': request_id,
                    'session_id': session_id,
                    'trace_id': trace_id,
                    'error': str(e)
                }
            )
            
            # Record error metrics
            self.cloudwatch_client.put_error_rate(error_type='supervisor_error')
            
            # Log audit event
            self.audit_repo.create_audit_event(
                event_type='ERROR',
                action_details={'error': str(e)},
                outcome='failure',
                environment_alias=self.supervisor_agent_alias,
                request_id=request_id,
                trace_id=trace_id,
                session_id=session_id,
                agent_identity='supervisor_agent',
                agent_version='1.0.0',
                policy_version='1.0.0'
            )
            
            raise
    
    def _validate_request(self, request: PortfolioRebalanceRequest):
        """Validate portfolio rebalance request."""
        # Validation is handled by Pydantic model
        # Additional business logic validation can be added here
        pass
    
    async def _invoke_memory_agent(
        self,
        request: PortfolioRebalanceRequest,
        session_id: str,
        request_id: str,
        trace_id: str
    ) -> MemoryPersonalizationResponse:
        """Invoke Memory & Personalization Agent."""
        start_time = datetime.now(timezone.utc)
        
        try:
            logger.info(
                "Invoking Memory & Personalization Agent",
                extra={
                    'request_id': request_id,
                    'session_id': session_id,
                    'trace_id': trace_id
                }
            )
            
            # Create span
            span = self.observability_client.create_span(
                trace_id=trace_id,
                span_name='memory_agent',
                metadata={'agent': 'memory_personalization'}
            )
            
            # Invoke agent (placeholder - actual implementation will use Bedrock Agent Runtime)
            # For now, return a mock response
            memory_response = MemoryPersonalizationResponse(
                request_id=request_id,
                session_id=session_id,
                trace_id=trace_id,
                timestamp=datetime.now(timezone.utc).isoformat(),
                agent_version='1.0.0',
                schema_version='1.0.0',
                memory_items=[],
                conflicts=[],
                confidence_score=0.9,
                memory_version='1.0.0'
            )
            
            # End span
            latency_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            self.observability_client.end_span(span['span_id'], 'success')
            
            # Record metrics
            self.cloudwatch_client.put_agent_invocation_count('memory_agent')
            self.cloudwatch_client.put_agent_invocation_latency('memory_agent', latency_ms)
            
            # Log audit event
            self.audit_repo.create_audit_event(
                event_type='AGENT_COMPLETED',
                action_details={'agent': 'memory_agent'},
                outcome='success',
                environment_alias=self.supervisor_agent_alias,
                request_id=request_id,
                trace_id=trace_id,
                session_id=session_id,
                agent_identity='memory_agent',
                agent_version='1.0.0',
                policy_version='1.0.0'
            )
            
            return memory_response
            
        except Exception as e:
            logger.error(
                f"Memory agent invocation failed: {str(e)}",
                extra={
                    'request_id': request_id,
                    'trace_id': trace_id,
                    'error': str(e)
                }
            )
            raise
    
    async def _invoke_research_agent(
        self,
        request: PortfolioRebalanceRequest,
        session_id: str,
        request_id: str,
        trace_id: str
    ) -> ResearchResponse:
        """Invoke Research Agent."""
        # Similar implementation to _invoke_memory_agent
        # Placeholder for now
        return ResearchResponse(
            request_id=request_id,
            session_id=session_id,
            trace_id=trace_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent_version='1.0.0',
            schema_version='1.0.0',
            market_data={},
            sentiment_summary='',
            confidence_score=0.9,
            evidence=[],
            provenance_metadata={}
        )
    
    async def _invoke_compliance_agent(
        self,
        request: PortfolioRebalanceRequest,
        memory_response: MemoryPersonalizationResponse,
        research_response: ResearchResponse,
        session_id: str,
        request_id: str,
        trace_id: str
    ) -> RiskComplianceResponse:
        """Invoke Risk & Compliance Agent."""
        # Placeholder
        from AssetManagement.schemas.risk_compliance_response import ComplianceVerdict
        
        return RiskComplianceResponse(
            request_id=request_id,
            session_id=session_id,
            trace_id=trace_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent_version='1.0.0',
            schema_version='1.0.0',
            drift_analysis={},
            risk_metrics={},
            compliance_verdict=ComplianceVerdict(
                verdict='COMPLIANT',
                rationale='All compliance checks passed',
                evidence=[],
                unresolved_controls=[]
            ),
            evidence=[],
            confidence_score=0.9
        )
    
    async def _invoke_execution_agent(
        self,
        request: PortfolioRebalanceRequest,
        memory_response: MemoryPersonalizationResponse,
        research_response: ResearchResponse,
        compliance_response: RiskComplianceResponse,
        session_id: str,
        request_id: str,
        trace_id: str
    ) -> ExecutionResponse:
        """Invoke Execution Agent."""
        # Placeholder
        return ExecutionResponse(
            request_id=request_id,
            session_id=session_id,
            trace_id=trace_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent_version='1.0.0',
            schema_version='1.0.0',
            trade_proposals=[],
            confidence_score=0.9,
            evidence=[],
            provenance_metadata={}
        )
    
    def _create_blocked_response(
        self,
        request: PortfolioRebalanceRequest,
        memory_response: MemoryPersonalizationResponse,
        research_response: ResearchResponse,
        compliance_response: RiskComplianceResponse,
        session_id: str,
        request_id: str,
        trace_id: str
    ) -> SupervisorResponse:
        """Create blocked response when compliance fails."""
        return SupervisorResponse(
            request_id=request_id,
            session_id=session_id,
            trace_id=trace_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent_version='1.0.0',
            schema_version='1.0.0',
            policy_version='1.0.0',
            workflow_state='BLOCKED',
            recommendation_package={}
        )
    
    def _consolidate_outputs(
        self,
        request: PortfolioRebalanceRequest,
        memory_response: MemoryPersonalizationResponse,
        research_response: ResearchResponse,
        compliance_response: RiskComplianceResponse,
        execution_response: ExecutionResponse,
        session_id: str,
        request_id: str,
        trace_id: str
    ) -> SupervisorResponse:
        """Consolidate all agent outputs into recommendation package."""
        recommendation_package = {
            'memory': memory_response.dict(),
            'research': research_response.dict(),
            'compliance': compliance_response.dict(),
            'execution': execution_response.dict()
        }
        
        return SupervisorResponse(
            request_id=request_id,
            session_id=session_id,
            trace_id=trace_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent_version='1.0.0',
            schema_version='1.0.0',
            policy_version='1.0.0',
            workflow_state='NORMAL',
            recommendation_package=recommendation_package
        )
    
    def _determine_workflow_state(
        self,
        memory_response: MemoryPersonalizationResponse,
        research_response: ResearchResponse,
        compliance_response: RiskComplianceResponse,
        execution_response: ExecutionResponse
    ) -> str:
        """Determine workflow state based on agent responses."""
        # Check for blocked state
        if compliance_response.compliance_verdict.verdict in ['NON_COMPLIANT', 'UNRESOLVED']:
            return 'BLOCKED'
        
        # Check for degraded mode
        if hasattr(research_response, 'degraded_mode_reason') and research_response.degraded_mode_reason:
            return 'DEGRADED'
        
        # Check for low confidence
        min_confidence = min(
            memory_response.confidence_score,
            research_response.confidence_score,
            compliance_response.confidence_score,
            execution_response.confidence_score
        )
        
        if min_confidence < 0.7:
            return 'LOW_CONFIDENCE'
        
        return 'NORMAL'
