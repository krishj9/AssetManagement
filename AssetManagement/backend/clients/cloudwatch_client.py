"""
CloudWatch Client

This module provides integration with Amazon CloudWatch for custom metrics
and structured logging.
"""

import boto3
import logging
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class CloudWatchClient:
    """
    Client for Amazon CloudWatch metrics and logging.
    
    Provides custom metrics collection and structured logging capabilities
    for monitoring the multi-agent portfolio platform.
    """
    
    def __init__(
        self,
        namespace: str = "PortfolioPlatform",
        log_group: str = "/aws/portfolio-platform",
        log_stream: Optional[str] = None
    ):
        """
        Initialize CloudWatch client.
        
        Args:
            namespace: CloudWatch metrics namespace
            log_group: CloudWatch Logs log group name
            log_stream: CloudWatch Logs log stream name (auto-generated if None)
        """
        self.namespace = namespace
        self.log_group = log_group
        self.log_stream = log_stream or f"stream-{datetime.now(timezone.utc).strftime('%Y%m%d')}"
        
        self.cloudwatch = boto3.client('cloudwatch')
        self.logs = boto3.client('logs')
        
        # Ensure log group and stream exist
        self._ensure_log_group_exists()
        self._ensure_log_stream_exists()
        
        logger.info(
            f"CloudWatch client initialized",
            extra={
                'namespace': namespace,
                'log_group': log_group,
                'log_stream': self.log_stream
            }
        )
    
    def _ensure_log_group_exists(self):
        """Ensure CloudWatch Logs log group exists."""
        try:
            self.logs.create_log_group(logGroupName=self.log_group)
            logger.info(f"Created log group: {self.log_group}")
        except self.logs.exceptions.ResourceAlreadyExistsException:
            pass  # Log group already exists
        except Exception as e:
            logger.error(f"Failed to create log group: {str(e)}")
    
    def _ensure_log_stream_exists(self):
        """Ensure CloudWatch Logs log stream exists."""
        try:
            self.logs.create_log_stream(
                logGroupName=self.log_group,
                logStreamName=self.log_stream
            )
            logger.info(f"Created log stream: {self.log_stream}")
        except self.logs.exceptions.ResourceAlreadyExistsException:
            pass  # Log stream already exists
        except Exception as e:
            logger.error(f"Failed to create log stream: {str(e)}")
    
    def put_metric(
        self,
        metric_name: str,
        value: float,
        unit: str = 'Count',
        dimensions: Optional[List[Dict[str, str]]] = None,
        timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Put a custom metric to CloudWatch.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            unit: Metric unit (Count, Milliseconds, etc.)
            dimensions: List of dimension dicts with 'Name' and 'Value' keys
            timestamp: Metric timestamp (defaults to now)
        
        Returns:
            Dict containing metric submission status
        """
        try:
            metric_data = {
                'MetricName': metric_name,
                'Value': value,
                'Unit': unit,
                'Timestamp': timestamp or datetime.now(timezone.utc)
            }
            
            if dimensions:
                metric_data['Dimensions'] = dimensions
            
            response = self.cloudwatch.put_metric_data(
                Namespace=self.namespace,
                MetricData=[metric_data]
            )
            
            logger.debug(
                f"Put metric: {metric_name} = {value} {unit}",
                extra={
                    'metric_name': metric_name,
                    'value': value,
                    'unit': unit,
                    'dimensions': dimensions
                }
            )
            
            return {
                'metric_name': metric_name,
                'value': value,
                'status': 'success'
            }
            
        except ClientError as e:
            logger.error(
                f"Failed to put metric: {str(e)}",
                extra={
                    'metric_name': metric_name,
                    'error': str(e)
                }
            )
            raise
    
    def put_request_volume(self, count: int = 1):
        """Put request volume metric."""
        return self.put_metric(
            metric_name='RequestVolume',
            value=count,
            unit='Count'
        )
    
    def put_request_latency(self, latency_ms: float, operation: str):
        """Put request latency metric."""
        return self.put_metric(
            metric_name='RequestLatency',
            value=latency_ms,
            unit='Milliseconds',
            dimensions=[{'Name': 'Operation', 'Value': operation}]
        )
    
    def put_error_rate(self, error_count: int = 1, error_type: Optional[str] = None):
        """Put error rate metric."""
        dimensions = []
        if error_type:
            dimensions.append({'Name': 'ErrorType', 'Value': error_type})
        
        return self.put_metric(
            metric_name='ErrorRate',
            value=error_count,
            unit='Count',
            dimensions=dimensions if dimensions else None
        )
    
    def put_blocked_state_rate(self, count: int = 1):
        """Put blocked state rate metric."""
        return self.put_metric(
            metric_name='BlockedStateRate',
            value=count,
            unit='Count'
        )
    
    def put_degraded_mode_rate(self, count: int = 1):
        """Put degraded mode rate metric."""
        return self.put_metric(
            metric_name='DegradedModeRate',
            value=count,
            unit='Count'
        )
    
    def put_agent_invocation_count(self, agent_name: str, count: int = 1):
        """Put agent invocation count metric."""
        return self.put_metric(
            metric_name='AgentInvocationCount',
            value=count,
            unit='Count',
            dimensions=[{'Name': 'AgentName', 'Value': agent_name}]
        )
    
    def put_agent_invocation_latency(self, agent_name: str, latency_ms: float):
        """Put agent invocation latency metric."""
        return self.put_metric(
            metric_name='AgentInvocationLatency',
            value=latency_ms,
            unit='Milliseconds',
            dimensions=[{'Name': 'AgentName', 'Value': agent_name}]
        )
    
    def put_approval_action_count(self, action: str, count: int = 1):
        """Put approval action count metric."""
        return self.put_metric(
            metric_name='ApprovalActionCount',
            value=count,
            unit='Count',
            dimensions=[{'Name': 'Action', 'Value': action}]
        )
    
    def put_guardrail_violation_count(self, violation_type: str, count: int = 1):
        """Put guardrail violation count metric."""
        return self.put_metric(
            metric_name='GuardrailViolationCount',
            value=count,
            unit='Count',
            dimensions=[{'Name': 'ViolationType', 'Value': violation_type}]
        )
    
    def log_structured(
        self,
        message: str,
        metadata: Dict[str, Any],
        log_level: str = 'INFO'
    ) -> Dict[str, Any]:
        """
        Log structured message to CloudWatch Logs.
        
        Args:
            message: Log message
            metadata: Structured metadata (request_id, trace_id, etc.)
            log_level: Log level (INFO, WARNING, ERROR, etc.)
        
        Returns:
            Dict containing log submission status
        """
        try:
            log_entry = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'level': log_level,
                'message': message,
                'metadata': metadata
            }
            
            log_event = {
                'timestamp': int(datetime.now(timezone.utc).timestamp() * 1000),
                'message': json.dumps(log_entry)
            }
            
            response = self.logs.put_log_events(
                logGroupName=self.log_group,
                logStreamName=self.log_stream,
                logEvents=[log_event]
            )
            
            return {
                'message': message,
                'status': 'success',
                'next_sequence_token': response.get('nextSequenceToken')
            }
            
        except ClientError as e:
            logger.error(
                f"Failed to log structured message: {str(e)}",
                extra={
                    'message': message,
                    'error': str(e)
                }
            )
            raise
    
    def log_request(
        self,
        request_id: str,
        trace_id: str,
        operation: str,
        status: str,
        latency_ms: float,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log request with correlation IDs."""
        log_metadata = {
            'request_id': request_id,
            'trace_id': trace_id,
            'operation': operation,
            'status': status,
            'latency_ms': latency_ms
        }
        
        if metadata:
            log_metadata.update(metadata)
        
        return self.log_structured(
            message=f"Request {operation} completed with status {status}",
            metadata=log_metadata,
            log_level='INFO' if status == 'success' else 'ERROR'
        )
    
    def log_agent_invocation(
        self,
        agent_name: str,
        request_id: str,
        trace_id: str,
        session_id: str,
        status: str,
        latency_ms: float,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log agent invocation with correlation IDs."""
        log_metadata = {
            'agent_name': agent_name,
            'request_id': request_id,
            'trace_id': trace_id,
            'session_id': session_id,
            'status': status,
            'latency_ms': latency_ms
        }
        
        if metadata:
            log_metadata.update(metadata)
        
        return self.log_structured(
            message=f"Agent {agent_name} invocation completed with status {status}",
            metadata=log_metadata,
            log_level='INFO' if status == 'success' else 'ERROR'
        )
    
    def log_error(
        self,
        error_code: str,
        error_message: str,
        request_id: str,
        trace_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log error with correlation IDs."""
        log_metadata = {
            'error_code': error_code,
            'error_message': error_message,
            'request_id': request_id,
            'trace_id': trace_id
        }
        
        if metadata:
            log_metadata.update(metadata)
        
        return self.log_structured(
            message=f"Error: {error_code} - {error_message}",
            metadata=log_metadata,
            log_level='ERROR'
        )
    
    def log_approval_action(
        self,
        approval_id: str,
        action: str,
        request_id: str,
        trace_id: str,
        approved_by: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log approval action with correlation IDs."""
        log_metadata = {
            'approval_id': approval_id,
            'action': action,
            'request_id': request_id,
            'trace_id': trace_id
        }
        
        if approved_by:
            log_metadata['approved_by'] = approved_by
        
        if metadata:
            log_metadata.update(metadata)
        
        return self.log_structured(
            message=f"Approval action: {action} for approval {approval_id}",
            metadata=log_metadata,
            log_level='INFO'
        )
    
    def create_dashboard(self, dashboard_name: str) -> Dict[str, Any]:
        """
        Create CloudWatch dashboard for monitoring.
        
        Args:
            dashboard_name: Name of the dashboard
        
        Returns:
            Dict containing dashboard creation status
        """
        try:
            dashboard_body = {
                "widgets": [
                    {
                        "type": "metric",
                        "properties": {
                            "metrics": [
                                [self.namespace, "RequestVolume"],
                                [self.namespace, "ErrorRate"],
                                [self.namespace, "BlockedStateRate"],
                                [self.namespace, "DegradedModeRate"]
                            ],
                            "period": 300,
                            "stat": "Sum",
                            "region": "us-east-1",
                            "title": "Request Metrics"
                        }
                    },
                    {
                        "type": "metric",
                        "properties": {
                            "metrics": [
                                [self.namespace, "RequestLatency"],
                                [self.namespace, "AgentInvocationLatency"]
                            ],
                            "period": 300,
                            "stat": "Average",
                            "region": "us-east-1",
                            "title": "Latency Metrics"
                        }
                    }
                ]
            }
            
            response = self.cloudwatch.put_dashboard(
                DashboardName=dashboard_name,
                DashboardBody=json.dumps(dashboard_body)
            )
            
            logger.info(f"Created CloudWatch dashboard: {dashboard_name}")
            
            return {
                'dashboard_name': dashboard_name,
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(
                f"Failed to create dashboard: {str(e)}",
                extra={
                    'dashboard_name': dashboard_name,
                    'error': str(e)
                }
            )
            raise
