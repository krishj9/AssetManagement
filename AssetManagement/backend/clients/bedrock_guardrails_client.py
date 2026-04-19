"""
Bedrock Guardrails Client

This module provides integration with Amazon Bedrock Guardrails for policy enforcement,
content filtering, sensitive information detection, and contextual grounding checks.
"""

import boto3
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class BedrockGuardrailsClient:
    """
    Client for Amazon Bedrock Guardrails policy enforcement.
    
    Provides content filtering, denied topic detection, PII filtering,
    and contextual grounding checks for agent inputs and outputs.
    """
    
    def __init__(
        self,
        guardrail_id: str,
        guardrail_version: str = "DRAFT"
    ):
        """
        Initialize Bedrock Guardrails client.
        
        Args:
            guardrail_id: Guardrail identifier
            guardrail_version: Guardrail version (default: "DRAFT")
        """
        self.guardrail_id = guardrail_id
        self.guardrail_version = guardrail_version
        self.client = boto3.client('bedrock-runtime')
        
        logger.info(
            f"Bedrock Guardrails client initialized",
            extra={
                'guardrail_id': guardrail_id,
                'guardrail_version': guardrail_version
            }
        )
    
    def apply_guardrails(
        self,
        text: str,
        source: str,
        request_id: Optional[str] = None,
        trace_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Apply guardrails to text (input or output).
        
        Args:
            text: Text to check
            source: Source type ("INPUT" or "OUTPUT")
            request_id: Request correlation ID
            trace_id: Trace correlation ID
        
        Returns:
            Dict containing guardrail evaluation results
        """
        try:
            response = self.client.apply_guardrail(
                guardrailIdentifier=self.guardrail_id,
                guardrailVersion=self.guardrail_version,
                source=source,
                content=[{'text': {'text': text}}]
            )
            
            action = response.get('action', 'NONE')
            outputs = response.get('outputs', [])
            assessments = response.get('assessments', [])
            
            result = {
                'action': action,
                'outputs': outputs,
                'assessments': assessments,
                'blocked': action == 'GUARDRAIL_INTERVENED',
                'source': source,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            if action == 'GUARDRAIL_INTERVENED':
                logger.warning(
                    f"Guardrail intervention on {source}",
                    extra={
                        'request_id': request_id,
                        'trace_id': trace_id,
                        'source': source,
                        'action': action,
                        'assessments': assessments
                    }
                )
            else:
                logger.info(
                    f"Guardrail check passed for {source}",
                    extra={
                        'request_id': request_id,
                        'trace_id': trace_id,
                        'source': source
                    }
                )
            
            return result
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            logger.error(
                f"Guardrail application failed: {error_message}",
                extra={
                    'request_id': request_id,
                    'trace_id': trace_id,
                    'error_code': error_code,
                    'error_message': error_message
                }
            )
            
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error applying guardrails: {str(e)}",
                extra={
                    'request_id': request_id,
                    'trace_id': trace_id,
                    'error': str(e)
                }
            )
            raise
    
    def check_denied_topics(
        self,
        text: str,
        request_id: Optional[str] = None,
        trace_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Check for denied topics in text.
        
        Denied topics include:
        - Unsupported performance claims
        - Fabricated market facts
        - Harmful financial advice
        
        Args:
            text: Text to check
            request_id: Request correlation ID
            trace_id: Trace correlation ID
        
        Returns:
            Dict containing denied topic check results
        """
        try:
            result = self.apply_guardrails(
                text=text,
                source='OUTPUT',
                request_id=request_id,
                trace_id=trace_id
            )
            
            # Extract denied topic assessments
            denied_topics = []
            for assessment in result.get('assessments', []):
                if assessment.get('topicPolicy'):
                    topic_policy = assessment['topicPolicy']
                    for topic in topic_policy.get('topics', []):
                        if topic.get('action') == 'BLOCKED':
                            denied_topics.append({
                                'topic_name': topic.get('name'),
                                'topic_type': topic.get('type'),
                                'action': topic.get('action')
                            })
            
            return {
                'blocked': len(denied_topics) > 0,
                'denied_topics': denied_topics,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(
                f"Denied topic check failed: {str(e)}",
                extra={
                    'request_id': request_id,
                    'trace_id': trace_id,
                    'error': str(e)
                }
            )
            raise
    
    def filter_sensitive_information(
        self,
        text: str,
        request_id: Optional[str] = None,
        trace_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Filter sensitive information (PII, credentials, etc.).
        
        Args:
            text: Text to filter
            request_id: Request correlation ID
            trace_id: Trace correlation ID
        
        Returns:
            Dict containing filtered text and detected PII types
        """
        try:
            result = self.apply_guardrails(
                text=text,
                source='OUTPUT',
                request_id=request_id,
                trace_id=trace_id
            )
            
            # Extract PII assessments
            pii_detected = []
            filtered_text = text
            
            for assessment in result.get('assessments', []):
                if assessment.get('sensitiveInformationPolicy'):
                    pii_policy = assessment['sensitiveInformationPolicy']
                    for pii_entity in pii_policy.get('piiEntities', []):
                        if pii_entity.get('action') == 'ANONYMIZED':
                            pii_detected.append({
                                'type': pii_entity.get('type'),
                                'action': pii_entity.get('action')
                            })
            
            # Get filtered output if available
            outputs = result.get('outputs', [])
            if outputs and len(outputs) > 0:
                filtered_text = outputs[0].get('text', text)
            
            return {
                'filtered_text': filtered_text,
                'pii_detected': pii_detected,
                'pii_count': len(pii_detected),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(
                f"Sensitive information filtering failed: {str(e)}",
                extra={
                    'request_id': request_id,
                    'trace_id': trace_id,
                    'error': str(e)
                }
            )
            raise
    
    def check_contextual_grounding(
        self,
        text: str,
        evidence: List[str],
        request_id: Optional[str] = None,
        trace_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Check if text is grounded in provided evidence.
        
        This ensures recommendation-bearing outputs are supported by
        retrieved facts and not fabricated.
        
        Args:
            text: Text to check
            evidence: List of evidence sources
            request_id: Request correlation ID
            trace_id: Trace correlation ID
        
        Returns:
            Dict containing grounding check results
        """
        try:
            # Combine text and evidence for grounding check
            combined_text = f"Text: {text}\n\nEvidence: {' '.join(evidence)}"
            
            result = self.apply_guardrails(
                text=combined_text,
                source='OUTPUT',
                request_id=request_id,
                trace_id=trace_id
            )
            
            # Extract contextual grounding assessments
            grounding_score = 1.0
            grounded = True
            
            for assessment in result.get('assessments', []):
                if assessment.get('contextualGroundingPolicy'):
                    grounding_policy = assessment['contextualGroundingPolicy']
                    for filter_result in grounding_policy.get('filters', []):
                        if filter_result.get('action') == 'BLOCKED':
                            grounded = False
                            grounding_score = filter_result.get('score', 0.0)
            
            return {
                'grounded': grounded,
                'grounding_score': grounding_score,
                'evidence_count': len(evidence),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(
                f"Contextual grounding check failed: {str(e)}",
                extra={
                    'request_id': request_id,
                    'trace_id': trace_id,
                    'error': str(e)
                }
            )
            raise
    
    def log_violation(
        self,
        violation_type: str,
        text_snippet: str,
        details: Dict[str, Any],
        request_id: Optional[str] = None,
        trace_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Log guardrail violation for audit and monitoring.
        
        Args:
            violation_type: Type of violation (denied_topic, pii, grounding, etc.)
            text_snippet: Snippet of text that triggered violation
            details: Additional violation details
            request_id: Request correlation ID
            trace_id: Trace correlation ID
        
        Returns:
            Dict containing violation log entry
        """
        try:
            violation_log = {
                'violation_type': violation_type,
                'text_snippet': text_snippet[:200],  # Truncate for logging
                'details': details,
                'request_id': request_id,
                'trace_id': trace_id,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            logger.warning(
                f"Guardrail violation: {violation_type}",
                extra=violation_log
            )
            
            return violation_log
            
        except Exception as e:
            logger.error(
                f"Failed to log violation: {str(e)}",
                extra={
                    'request_id': request_id,
                    'trace_id': trace_id,
                    'error': str(e)
                }
            )
            raise
    
    def create_structured_error(
        self,
        violation_result: Dict[str, Any],
        request_id: str,
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Create structured error response for guardrail violations.
        
        Args:
            violation_result: Guardrail violation result
            request_id: Request correlation ID
            trace_id: Trace correlation ID
        
        Returns:
            Dict containing structured error
        """
        try:
            error = {
                'code': 'GUARDRAIL_VIOLATION',
                'message': 'Content blocked by guardrail policy',
                'severity': 'error',
                'retryable': False,
                'source_agent': 'guardrails',
                'request_id': request_id,
                'trace_id': trace_id,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'related_context': {
                    'action': violation_result.get('action'),
                    'assessments': violation_result.get('assessments', [])
                }
            }
            
            return error
            
        except Exception as e:
            logger.error(
                f"Failed to create structured error: {str(e)}",
                extra={
                    'request_id': request_id,
                    'trace_id': trace_id,
                    'error': str(e)
                }
            )
            raise
