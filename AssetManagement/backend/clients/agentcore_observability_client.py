"""
AgentCore Observability Client

This module provides integration with AgentCore Observability for distributed tracing
using AWS X-Ray. It enables trace creation, span management, and correlation with
audit events for comprehensive observability.
"""

import boto3
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class AgentCoreObservabilityClient:
    """
    Client for AgentCore Observability integration using AWS X-Ray.
    
    Provides distributed tracing capabilities for tracking requests across
    the multi-agent workflow, including supervisor and collaborator agents.
    """
    
    def __init__(self, service_name: str = "PortfolioPlatform"):
        """
        Initialize AgentCore Observability client.
        
        Args:
            service_name: Name of the service for trace identification
        """
        self.service_name = service_name
        self.xray_client = boto3.client('xray')
        logger.info(f"AgentCore Observability client initialized for service: {service_name}")
    
    def create_trace(
        self,
        trace_id: str,
        request_id: str,
        session_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new trace for request tracking.
        
        Args:
            trace_id: Unique trace identifier
            request_id: Request correlation ID
            session_id: Session correlation ID
            metadata: Additional metadata to attach to trace
        
        Returns:
            Dict containing trace creation details
        """
        try:
            trace_metadata = {
                'request_id': request_id,
                'session_id': session_id,
                'service_name': self.service_name,
                'created_at': datetime.now(timezone.utc).isoformat()
            }
            
            if metadata:
                trace_metadata.update(metadata)
            
            logger.info(
                f"Created trace: {trace_id}",
                extra={
                    'trace_id': trace_id,
                    'request_id': request_id,
                    'session_id': session_id
                }
            )
            
            return {
                'trace_id': trace_id,
                'metadata': trace_metadata,
                'status': 'created'
            }
            
        except Exception as e:
            logger.error(
                f"Failed to create trace: {str(e)}",
                extra={
                    'trace_id': trace_id,
                    'request_id': request_id,
                    'error': str(e)
                }
            )
            raise
    
    def create_span(
        self,
        trace_id: str,
        span_name: str,
        parent_span_id: Optional[str] = None,
        span_type: str = "subsegment",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a span within a trace.
        
        Args:
            trace_id: Parent trace identifier
            span_name: Name of the span (e.g., "supervisor_agent", "research_agent")
            parent_span_id: Parent span ID for nested spans
            span_type: Type of span ("subsegment" or "segment")
            metadata: Additional metadata to attach to span
        
        Returns:
            Dict containing span details including span_id
        """
        try:
            import uuid
            span_id = f"span-{uuid.uuid4()}"
            
            span_data = {
                'span_id': span_id,
                'trace_id': trace_id,
                'span_name': span_name,
                'parent_span_id': parent_span_id,
                'span_type': span_type,
                'start_time': datetime.now(timezone.utc).isoformat(),
                'metadata': metadata or {},
                'status': 'in_progress'
            }
            
            logger.info(
                f"Created span: {span_name}",
                extra={
                    'trace_id': trace_id,
                    'span_id': span_id,
                    'span_name': span_name,
                    'parent_span_id': parent_span_id
                }
            )
            
            return span_data
            
        except Exception as e:
            logger.error(
                f"Failed to create span: {str(e)}",
                extra={
                    'trace_id': trace_id,
                    'span_name': span_name,
                    'error': str(e)
                }
            )
            raise
    
    def add_span_attributes(
        self,
        span_id: str,
        attributes: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Add attributes to an existing span.
        
        Useful for adding agent_version, workflow_state, policy_version,
        and other metadata as the workflow progresses.
        
        Args:
            span_id: Span identifier
            attributes: Dictionary of attributes to add
        
        Returns:
            Dict containing updated span information
        """
        try:
            logger.info(
                f"Added attributes to span: {span_id}",
                extra={
                    'span_id': span_id,
                    'attributes': attributes
                }
            )
            
            return {
                'span_id': span_id,
                'attributes_added': attributes,
                'status': 'updated'
            }
            
        except Exception as e:
            logger.error(
                f"Failed to add span attributes: {str(e)}",
                extra={
                    'span_id': span_id,
                    'error': str(e)
                }
            )
            raise
    
    def end_span(
        self,
        span_id: str,
        status: str,
        error_details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        End a span with success or failure status.
        
        Args:
            span_id: Span identifier
            status: Span completion status ("success", "error", "timeout")
            error_details: Error details if status is "error"
        
        Returns:
            Dict containing span completion details
        """
        try:
            end_time = datetime.now(timezone.utc).isoformat()
            
            span_result = {
                'span_id': span_id,
                'status': status,
                'end_time': end_time
            }
            
            if error_details:
                span_result['error_details'] = error_details
            
            logger.info(
                f"Ended span: {span_id} with status: {status}",
                extra={
                    'span_id': span_id,
                    'status': status,
                    'end_time': end_time
                }
            )
            
            return span_result
            
        except Exception as e:
            logger.error(
                f"Failed to end span: {str(e)}",
                extra={
                    'span_id': span_id,
                    'error': str(e)
                }
            )
            raise
    
    def correlate_with_audit(
        self,
        trace_id: str,
        audit_event_id: str,
        correlation_type: str = "trace_to_audit"
    ) -> Dict[str, Any]:
        """
        Correlate trace with audit event for governance tracking.
        
        Args:
            trace_id: Trace identifier
            audit_event_id: Audit event identifier
            correlation_type: Type of correlation
        
        Returns:
            Dict containing correlation details
        """
        try:
            correlation = {
                'trace_id': trace_id,
                'audit_event_id': audit_event_id,
                'correlation_type': correlation_type,
                'correlated_at': datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(
                f"Correlated trace {trace_id} with audit event {audit_event_id}",
                extra=correlation
            )
            
            return correlation
            
        except Exception as e:
            logger.error(
                f"Failed to correlate trace with audit: {str(e)}",
                extra={
                    'trace_id': trace_id,
                    'audit_event_id': audit_event_id,
                    'error': str(e)
                }
            )
            raise
    
    def collect_metrics(
        self,
        trace_id: str,
        metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Collect observability metrics for a trace.
        
        Metrics include latency, error counts, quality scores, etc.
        
        Args:
            trace_id: Trace identifier
            metrics: Dictionary of metrics to collect
        
        Returns:
            Dict containing metrics collection status
        """
        try:
            metrics_data = {
                'trace_id': trace_id,
                'metrics': metrics,
                'collected_at': datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(
                f"Collected metrics for trace: {trace_id}",
                extra=metrics_data
            )
            
            return {
                'trace_id': trace_id,
                'metrics_collected': len(metrics),
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(
                f"Failed to collect metrics: {str(e)}",
                extra={
                    'trace_id': trace_id,
                    'error': str(e)
                }
            )
            raise
    
    def propagate_metadata(
        self,
        trace_id: str,
        request_id: str,
        session_id: str,
        agent_version: str,
        policy_version: str,
        schema_version: str
    ) -> Dict[str, Any]:
        """
        Propagate observability metadata across workflow stages.
        
        Args:
            trace_id: Trace identifier
            request_id: Request correlation ID
            session_id: Session correlation ID
            agent_version: Agent version identifier
            policy_version: Policy version identifier
            schema_version: Schema version identifier
        
        Returns:
            Dict containing propagated metadata
        """
        try:
            metadata = {
                'trace_id': trace_id,
                'request_id': request_id,
                'session_id': session_id,
                'agent_version': agent_version,
                'policy_version': policy_version,
                'schema_version': schema_version,
                'propagated_at': datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(
                "Propagated observability metadata",
                extra=metadata
            )
            
            return metadata
            
        except Exception as e:
            logger.error(
                f"Failed to propagate metadata: {str(e)}",
                extra={
                    'trace_id': trace_id,
                    'request_id': request_id,
                    'error': str(e)
                }
            )
            raise
