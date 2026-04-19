"""
Approval Artifacts Repository

This module provides CRUD operations for the Approval Artifacts DynamoDB table.
"""

import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List
from boto3.dynamodb.conditions import Key, Attr
from .dynamodb_client import DynamoDBClient, DynamoDBClientError


class ApprovalArtifactsRepository:
    """
    Repository for Approval Artifacts table operations.
    
    Table: ApprovalArtifacts
    Primary Key: approval_id
    GSI: request_id
    TTL: 90 days
    """
    
    TABLE_NAME = "ApprovalArtifacts"
    GSI_REQUEST_ID = "RequestIdIndex"
    TTL_DAYS = 90
    
    def __init__(self, dynamodb_client: DynamoDBClient):
        """
        Initialize repository.
        
        Args:
            dynamodb_client: DynamoDB client wrapper
        """
        self.client = dynamodb_client
        self.table = dynamodb_client.get_table(self.TABLE_NAME)
    
    def _calculate_ttl(self) -> int:
        """Calculate TTL timestamp (90 days from now)"""
        expiry_time = datetime.now(timezone.utc) + timedelta(days=self.TTL_DAYS)
        return int(expiry_time.timestamp())
    
    def create_approval_artifact(
        self,
        request_id: str,
        trace_id: str,
        agent_version: str,
        schema_version: str,
        policy_version: str,
        trade_proposals: List[Dict[str, Any]],
        compliance_verdict: Dict[str, Any],
        rationale: Dict[str, Any],
        evidence: Dict[str, Any],
        memory_summary: Dict[str, Any],
        workflow_state: str,
        approval_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new approval artifact.
        
        Args:
            request_id: Request ID
            trace_id: Trace ID
            agent_version: Agent version
            schema_version: Schema version
            policy_version: Policy version
            trade_proposals: List of trade proposals
            compliance_verdict: Compliance verdict
            rationale: Rationale for recommendation
            evidence: Supporting evidence
            memory_summary: Memory summary
            workflow_state: Workflow state (NORMAL, DEGRADED, LOW_CONFIDENCE, BLOCKED)
            approval_id: Optional approval ID (generated if not provided)
        
        Returns:
            Created approval artifact
        
        Raises:
            DynamoDBClientError: If operation fails
        """
        if not approval_id:
            approval_id = f"approval-{uuid.uuid4()}"
        
        now = datetime.now(timezone.utc).isoformat()
        ttl = self._calculate_ttl()
        
        item = {
            'approval_id': approval_id,
            'request_id': request_id,
            'trace_id': trace_id,
            'timestamp': now,
            'agent_version': agent_version,
            'schema_version': schema_version,
            'policy_version': policy_version,
            'trade_proposals': trade_proposals,
            'compliance_verdict': compliance_verdict,
            'rationale': rationale,
            'evidence': evidence,
            'memory_summary': memory_summary,
            'workflow_state': workflow_state,
            'approval_status': 'PENDING',
            'created_at': now,
            'updated_at': now,
            'ttl': ttl
        }
        
        self.client.put_item(
            table_name=self.TABLE_NAME,
            item=item,
            condition_expression='attribute_not_exists(approval_id)',  # Prevent overwrites
            request_id=request_id,
            trace_id=trace_id
        )
        
        return item
    
    def get_approval_artifact_by_id(
        self,
        approval_id: str,
        request_id: Optional[str] = None,
        trace_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get approval artifact by approval_id.
        
        Args:
            approval_id: Approval ID
            request_id: Optional request ID for correlation
            trace_id: Optional trace ID for correlation
        
        Returns:
            Approval artifact if found, None otherwise
        
        Raises:
            DynamoDBClientError: If operation fails
        """
        return self.client.get_item(
            table_name=self.TABLE_NAME,
            key={'approval_id': approval_id},
            consistent_read=True,
            request_id=request_id,
            trace_id=trace_id
        )
    
    def get_approval_artifact_by_request_id(
        self,
        request_id: str,
        trace_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get approval artifact by request_id using GSI.
        
        Args:
            request_id: Request ID
            trace_id: Optional trace ID for correlation
        
        Returns:
            Approval artifact if found, None otherwise
        
        Raises:
            DynamoDBClientError: If operation fails
        """
        items = self.client.query(
            table_name=self.TABLE_NAME,
            index_name=self.GSI_REQUEST_ID,
            key_condition_expression=Key('request_id').eq(request_id),
            limit=1,
            request_id=request_id,
            trace_id=trace_id
        )
        
        return items[0] if items else None
    
    def update_approval_status(
        self,
        approval_id: str,
        approval_status: str,
        approved_by: Optional[str] = None,
        approved_at: Optional[str] = None,
        rejected_by: Optional[str] = None,
        rejected_at: Optional[str] = None,
        rejection_note: Optional[str] = None,
        override_note: Optional[str] = None,
        request_id: Optional[str] = None,
        trace_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update approval status with conditional write to prevent race conditions.
        
        Args:
            approval_id: Approval ID
            approval_status: New approval status (APPROVED, REJECTED, REVISION_REQUESTED)
            approved_by: User who approved (required for APPROVED status)
            approved_at: Approval timestamp (required for APPROVED status)
            rejected_by: User who rejected (required for REJECTED status)
            rejected_at: Rejection timestamp (required for REJECTED status)
            rejection_note: Rejection note (optional for REJECTED status)
            override_note: Override note (optional for APPROVED status with overrides)
            request_id: Optional request ID for correlation
            trace_id: Optional trace ID for correlation
        
        Returns:
            Updated approval artifact
        
        Raises:
            DynamoDBClientError: If operation fails or condition check fails
        """
        now = datetime.now(timezone.utc).isoformat()
        
        # Build update expression dynamically
        update_parts = [
            'SET approval_status = :status',
            'updated_at = :updated_at'
        ]
        expression_attribute_values = {
            ':status': approval_status,
            ':updated_at': now,
            ':pending': 'PENDING'
        }
        
        if approved_by:
            update_parts.append('approved_by = :approved_by')
            expression_attribute_values[':approved_by'] = approved_by
        
        if approved_at:
            update_parts.append('approved_at = :approved_at')
            expression_attribute_values[':approved_at'] = approved_at
        
        if rejected_by:
            update_parts.append('rejected_by = :rejected_by')
            expression_attribute_values[':rejected_by'] = rejected_by
        
        if rejected_at:
            update_parts.append('rejected_at = :rejected_at')
            expression_attribute_values[':rejected_at'] = rejected_at
        
        if rejection_note:
            update_parts.append('rejection_note = :rejection_note')
            expression_attribute_values[':rejection_note'] = rejection_note
        
        if override_note:
            update_parts.append('override_note = :override_note')
            expression_attribute_values[':override_note'] = override_note
        
        update_expression = ', '.join(update_parts)
        
        # Conditional write: only update if current status is PENDING
        # This prevents race conditions where multiple users try to approve/reject simultaneously
        condition_expression = 'approval_status = :pending'
        
        response = self.client.update_item(
            table_name=self.TABLE_NAME,
            key={'approval_id': approval_id},
            update_expression=update_expression,
            condition_expression=condition_expression,
            expression_attribute_values=expression_attribute_values,
            return_values='ALL_NEW',
            request_id=request_id,
            trace_id=trace_id
        )
        
        return response.get('Attributes', {})
    
    def update_approval_artifact(
        self,
        approval_id: str,
        updates: Dict[str, Any],
        request_id: Optional[str] = None,
        trace_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update approval artifact fields (general purpose update).
        
        Args:
            approval_id: Approval ID
            updates: Dictionary of fields to update
            request_id: Optional request ID for correlation
            trace_id: Optional trace ID for correlation
        
        Returns:
            Updated approval artifact
        
        Raises:
            DynamoDBClientError: If operation fails
        """
        now = datetime.now(timezone.utc).isoformat()
        updates['updated_at'] = now
        
        # Build update expression
        update_parts = []
        expression_attribute_names = {}
        expression_attribute_values = {}
        
        for i, (key, value) in enumerate(updates.items()):
            attr_name = f'#attr{i}'
            attr_value = f':val{i}'
            update_parts.append(f'{attr_name} = {attr_value}')
            expression_attribute_names[attr_name] = key
            expression_attribute_values[attr_value] = value
        
        update_expression = 'SET ' + ', '.join(update_parts)
        
        response = self.client.update_item(
            table_name=self.TABLE_NAME,
            key={'approval_id': approval_id},
            update_expression=update_expression,
            expression_attribute_names=expression_attribute_names,
            expression_attribute_values=expression_attribute_values,
            return_values='ALL_NEW',
            request_id=request_id,
            trace_id=trace_id
        )
        
        return response.get('Attributes', {})
    
    def invalidate_approval_artifact(
        self,
        approval_id: str,
        invalidation_reason: str,
        request_id: Optional[str] = None,
        trace_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Invalidate an approval artifact (e.g., when recommendation changes).
        
        Args:
            approval_id: Approval ID
            invalidation_reason: Reason for invalidation
            request_id: Optional request ID for correlation
            trace_id: Optional trace ID for correlation
        
        Returns:
            Updated approval artifact
        
        Raises:
            DynamoDBClientError: If operation fails
        """
        now = datetime.now(timezone.utc).isoformat()
        
        response = self.client.update_item(
            table_name=self.TABLE_NAME,
            key={'approval_id': approval_id},
            update_expression='SET approval_status = :status, invalidation_reason = :reason, invalidated_at = :invalidated_at, updated_at = :updated_at',
            expression_attribute_values={
                ':status': 'INVALIDATED',
                ':reason': invalidation_reason,
                ':invalidated_at': now,
                ':updated_at': now
            },
            return_values='ALL_NEW',
            request_id=request_id,
            trace_id=trace_id
        )
        
        return response.get('Attributes', {})
