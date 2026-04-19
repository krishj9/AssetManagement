"""
Bedrock Agent Runtime Client

This module provides a client wrapper for invoking Amazon Bedrock Agents.
"""

import boto3
import json
import time
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class BedrockAgentClientError(Exception):
    """Base exception for Bedrock Agent client errors"""
    def __init__(
        self,
        message: str,
        error_code: str,
        retryable: bool = False,
        original_error: Optional[Exception] = None
    ):
        super().__init__(message)
        self.error_code = error_code
        self.retryable = retryable
        self.original_error = original_error


class BedrockAgentClient:
    """
    Client wrapper for Amazon Bedrock Agent Runtime API.
    
    Features:
    - Agent invocation with request/response serialization
    - Timeout and retry logic
    - Error handling and structured error responses
    - Agent alias management
    - Request/trace correlation
    """
    
    def __init__(
        self,
        region_name: str = "us-east-1",
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 10.0,
        timeout: int = 300  # 5 minutes default timeout
    ):
        """
        Initialize Bedrock Agent client.
        
        Args:
            region_name: AWS region
            max_retries: Maximum number of retry attempts
            base_delay: Base delay for exponential backoff (seconds)
            max_delay: Maximum delay for exponential backoff (seconds)
            timeout: Request timeout in seconds
        """
        self.region_name = region_name
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.timeout = timeout
        
        # Initialize boto3 client
        self.client = boto3.client(
            'bedrock-agent-runtime',
            region_name=region_name
        )
        
        logger.info(f"Bedrock Agent client initialized for region: {region_name}")
    
    def _calculate_backoff_delay(self, attempt: int) -> float:
        """Calculate exponential backoff delay"""
        delay = min(self.base_delay * (2 ** attempt), self.max_delay)
        return delay
    
    def _is_retryable_error(self, error: ClientError) -> bool:
        """Check if error is retryable"""
        error_code = error.response.get('Error', {}).get('Code', '')
        retryable_codes = [
            'ThrottlingException',
            'ServiceUnavailableException',
            'InternalServerException',
            'RequestLimitExceeded',
            'TooManyRequestsException'
        ]
        return error_code in retryable_codes
    
    def _handle_client_error(
        self,
        error: ClientError,
        operation: str,
        request_id: Optional[str] = None,
        trace_id: Optional[str] = None
    ) -> BedrockAgentClientError:
        """Convert boto3 ClientError to BedrockAgentClientError"""
        error_code = error.response.get('Error', {}).get('Code', 'UnknownError')
        error_message = error.response.get('Error', {}).get('Message', str(error))
        retryable = self._is_retryable_error(error)
        
        message = f"Bedrock Agent {operation} failed: {error_message}"
        if request_id:
            message += f" (request_id: {request_id})"
        if trace_id:
            message += f" (trace_id: {trace_id})"
        
        logger.error(message, extra={
            'error_code': error_code,
            'operation': operation,
            'request_id': request_id,
            'trace_id': trace_id,
            'retryable': retryable
        })
        
        return BedrockAgentClientError(
            message=message,
            error_code=error_code,
            retryable=retryable,
            original_error=error
        )
    
    def _execute_with_retry(
        self,
        operation_func,
        operation_name: str,
        request_id: Optional[str] = None,
        trace_id: Optional[str] = None
    ) -> Any:
        """
        Execute Bedrock Agent operation with exponential backoff retry logic.
        
        Args:
            operation_func: Function to execute
            operation_name: Name of the operation (for logging)
            request_id: Request ID for correlation
            trace_id: Trace ID for correlation
        
        Returns:
            Result of the operation
        
        Raises:
            BedrockAgentClientError: If operation fails after all retries
        """
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                result = operation_func()
                
                if attempt > 0:
                    logger.info(
                        f"Bedrock Agent {operation_name} succeeded after {attempt} retries",
                        extra={
                            'operation': operation_name,
                            'request_id': request_id,
                            'trace_id': trace_id,
                            'attempts': attempt + 1
                        }
                    )
                
                return result
                
            except ClientError as e:
                last_error = e
                
                if not self._is_retryable_error(e):
                    # Non-retryable error, fail immediately
                    raise self._handle_client_error(e, operation_name, request_id, trace_id)
                
                if attempt < self.max_retries:
                    # Retryable error, apply backoff
                    delay = self._calculate_backoff_delay(attempt)
                    logger.warning(
                        f"Bedrock Agent {operation_name} failed (attempt {attempt + 1}/{self.max_retries + 1}), retrying in {delay:.2f}s",
                        extra={
                            'operation': operation_name,
                            'request_id': request_id,
                            'trace_id': trace_id,
                            'error_code': e.response.get('Error', {}).get('Code', ''),
                            'attempt': attempt + 1,
                            'delay': delay
                        }
                    )
                    time.sleep(delay)
                else:
                    # Max retries exceeded
                    raise self._handle_client_error(e, operation_name, request_id, trace_id)
        
        # Should never reach here, but just in case
        if last_error:
            raise self._handle_client_error(last_error, operation_name, request_id, trace_id)
    
    def invoke_agent(
        self,
        agent_id: str,
        agent_alias_id: str,
        session_id: str,
        input_text: str,
        request_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        enable_trace: bool = False,
        session_state: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Invoke a Bedrock Agent.
        
        Args:
            agent_id: Agent ID
            agent_alias_id: Agent alias ID (e.g., dev, test, prod)
            session_id: Session ID for conversation continuity
            input_text: Input text for the agent
            request_id: Optional request ID for correlation
            trace_id: Optional trace ID for correlation
            enable_trace: Whether to enable trace output
            session_state: Optional session state
        
        Returns:
            Agent response with completion text and metadata
        
        Raises:
            BedrockAgentClientError: If invocation fails
        """
        def operation():
            kwargs = {
                'agentId': agent_id,
                'agentAliasId': agent_alias_id,
                'sessionId': session_id,
                'inputText': input_text,
                'enableTrace': enable_trace
            }
            
            if session_state:
                kwargs['sessionState'] = session_state
            
            response = self.client.invoke_agent(**kwargs)
            
            # Process streaming response
            completion = ""
            trace_events = []
            
            event_stream = response.get('completion', [])
            for event in event_stream:
                if 'chunk' in event:
                    chunk = event['chunk']
                    if 'bytes' in chunk:
                        completion += chunk['bytes'].decode('utf-8')
                
                if 'trace' in event and enable_trace:
                    trace_events.append(event['trace'])
            
            return {
                'completion': completion,
                'session_id': response.get('sessionId'),
                'content_type': response.get('contentType', 'text/plain'),
                'trace_events': trace_events if enable_trace else None,
                'response_metadata': response.get('ResponseMetadata', {})
            }
        
        logger.info(f"Invoking Bedrock Agent: {agent_id} (alias: {agent_alias_id})", extra={
            'agent_id': agent_id,
            'agent_alias_id': agent_alias_id,
            'session_id': session_id,
            'request_id': request_id,
            'trace_id': trace_id,
            'enable_trace': enable_trace
        })
        
        start_time = time.time()
        
        try:
            result = self._execute_with_retry(
                operation,
                f"invoke_agent({agent_id})",
                request_id,
                trace_id
            )
            
            elapsed_time = time.time() - start_time
            
            logger.info(f"Bedrock Agent invocation completed in {elapsed_time:.2f}s", extra={
                'agent_id': agent_id,
                'agent_alias_id': agent_alias_id,
                'session_id': session_id,
                'request_id': request_id,
                'trace_id': trace_id,
                'elapsed_time': elapsed_time
            })
            
            return result
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"Bedrock Agent invocation failed after {elapsed_time:.2f}s", extra={
                'agent_id': agent_id,
                'agent_alias_id': agent_alias_id,
                'session_id': session_id,
                'request_id': request_id,
                'trace_id': trace_id,
                'elapsed_time': elapsed_time,
                'error': str(e)
            })
            raise
    
    def get_agent_alias(
        self,
        agent_id: str,
        agent_alias_id: str,
        request_id: Optional[str] = None,
        trace_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get agent alias information.
        
        Args:
            agent_id: Agent ID
            agent_alias_id: Agent alias ID
            request_id: Optional request ID for correlation
            trace_id: Optional trace ID for correlation
        
        Returns:
            Agent alias information
        
        Raises:
            BedrockAgentClientError: If operation fails
        """
        # Note: This uses bedrock-agent client, not bedrock-agent-runtime
        bedrock_agent_client = boto3.client('bedrock-agent', region_name=self.region_name)
        
        def operation():
            response = bedrock_agent_client.get_agent_alias(
                agentId=agent_id,
                agentAliasId=agent_alias_id
            )
            return response.get('agentAlias', {})
        
        logger.debug(f"Getting agent alias: {agent_id}/{agent_alias_id}", extra={
            'agent_id': agent_id,
            'agent_alias_id': agent_alias_id,
            'request_id': request_id,
            'trace_id': trace_id
        })
        
        return self._execute_with_retry(
            operation,
            f"get_agent_alias({agent_id}/{agent_alias_id})",
            request_id,
            trace_id
        )
    
    def list_agent_aliases(
        self,
        agent_id: str,
        request_id: Optional[str] = None,
        trace_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List all aliases for an agent.
        
        Args:
            agent_id: Agent ID
            request_id: Optional request ID for correlation
            trace_id: Optional trace ID for correlation
        
        Returns:
            List of agent aliases
        
        Raises:
            BedrockAgentClientError: If operation fails
        """
        # Note: This uses bedrock-agent client, not bedrock-agent-runtime
        bedrock_agent_client = boto3.client('bedrock-agent', region_name=self.region_name)
        
        def operation():
            response = bedrock_agent_client.list_agent_aliases(
                agentId=agent_id,
                maxResults=100
            )
            return response.get('agentAliasSummaries', [])
        
        logger.debug(f"Listing agent aliases: {agent_id}", extra={
            'agent_id': agent_id,
            'request_id': request_id,
            'trace_id': trace_id
        })
        
        return self._execute_with_retry(
            operation,
            f"list_agent_aliases({agent_id})",
            request_id,
            trace_id
        )
