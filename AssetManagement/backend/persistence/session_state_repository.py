"""
Session State Repository

This module provides CRUD operations for the Session State DynamoDB table.
"""

import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
from .dynamodb_client import DynamoDBClient, DynamoDBClientError


class SessionStateRepository:
    """
    Repository for Session State table operations.
    
    Table: SessionState
    Primary Key: session_id
    TTL: 24 hours after last_activity_at
    """
    
    TABLE_NAME = "SessionState"
    TTL_HOURS = 24
    
    def __init__(self, dynamodb_client: DynamoDBClient):
        """
        Initialize repository.
        
        Args:
            dynamodb_client: DynamoDB client wrapper
        """
        self.client = dynamodb_client
        self.table = dynamodb_client.get_table(self.TABLE_NAME)
    
    def _calculate_ttl(self, last_activity_at: Optional[datetime] = None) -> int:
        """
        Calculate TTL timestamp (24 hours after last_activity_at).
        
        Args:
            last_activity_at: Last activity timestamp (defaults to now)
        
        Returns:
            TTL timestamp (Unix epoch)
        """
        if not last_activity_at:
            last_activity_at = datetime.now(timezone.utc)
        
        expiry_time = last_activity_at + timedelta(hours=self.TTL_HOURS)
        return int(expiry_time.timestamp())
    
    def create_session_state(
        self,
        request_id: str,
        user_identity: str,
        user_role: str,
        workflow_state: str,
        session_id: Optional[str] = None,
        trace_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new session state.
        
        Args:
            request_id: Request ID
            user_identity: User identity
            user_role: User role
            workflow_state: Workflow state (NORMAL, DEGRADED, LOW_CONFIDENCE, BLOCKED)
            session_id: Optional session ID (generated if not provided)
            trace_id: Optional trace ID for correlation
        
        Returns:
            Created session state
        
        Raises:
            DynamoDBClientError: If operation fails
        """
        if not session_id:
            session_id = f"sess-{uuid.uuid4()}"
        
        now = datetime.now(timezone.utc)
        now_iso = now.isoformat()
        ttl = self._calculate_ttl(now)
        
        item = {
            'session_id': session_id,
            'request_id': request_id,
            'user_identity': user_identity,
            'user_role': user_role,
            'workflow_state': workflow_state,
            'created_at': now_iso,
            'updated_at': now_iso,
            'last_activity_at': now_iso,
            'ttl': ttl
        }
        
        self.client.put_item(
            table_name=self.TABLE_NAME,
            item=item,
            condition_expression='attribute_not_exists(session_id)',  # Prevent overwrites
            request_id=request_id,
            trace_id=trace_id
        )
        
        return item
    
    def get_session_state(
        self,
        session_id: str,
        request_id: Optional[str] = None,
        trace_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get session state by session_id.
        
        Args:
            session_id: Session ID
            request_id: Optional request ID for correlation
            trace_id: Optional trace ID for correlation
        
        Returns:
            Session state if found, None otherwise
        
        Raises:
            DynamoDBClientError: If operation fails
        """
        return self.client.get_item(
            table_name=self.TABLE_NAME,
            key={'session_id': session_id},
            consistent_read=True,
            request_id=request_id,
            trace_id=trace_id
        )
    
    def update_session_state(
        self,
        session_id: str,
        updates: Dict[str, Any],
        update_activity: bool = True,
        request_id: Optional[str] = None,
        trace_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update session state fields.
        
        Args:
            session_id: Session ID
            updates: Dictionary of fields to update
            update_activity: Whether to update last_activity_at and TTL
            request_id: Optional request ID for correlation
            trace_id: Optional trace ID for correlation
        
        Returns:
            Updated session state
        
        Raises:
            DynamoDBClientError: If operation fails
        """
        now = datetime.now(timezone.utc)
        now_iso = now.isoformat()
        
        updates['updated_at'] = now_iso
        
        if update_activity:
            updates['last_activity_at'] = now_iso
            updates['ttl'] = self._calculate_ttl(now)
        
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
            key={'session_id': session_id},
            update_expression=update_expression,
            expression_attribute_names=expression_attribute_names,
            expression_attribute_values=expression_attribute_values,
            return_values='ALL_NEW',
            request_id=request_id,
            trace_id=trace_id
        )
        
        return response.get('Attributes', {})
    
    def update_session_activity(
        self,
        session_id: str,
        request_id: Optional[str] = None,
        trace_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update session last_activity_at timestamp and extend TTL.
        
        Args:
            session_id: Session ID
            request_id: Optional request ID for correlation
            trace_id: Optional trace ID for correlation
        
        Returns:
            Updated session state
        
        Raises:
            DynamoDBClientError: If operation fails
        """
        now = datetime.now(timezone.utc)
        now_iso = now.isoformat()
        ttl = self._calculate_ttl(now)
        
        response = self.client.update_item(
            table_name=self.TABLE_NAME,
            key={'session_id': session_id},
            update_expression='SET last_activity_at = :last_activity_at, updated_at = :updated_at, #ttl = :ttl',
            expression_attribute_names={
                '#ttl': 'ttl'
            },
            expression_attribute_values={
                ':last_activity_at': now_iso,
                ':updated_at': now_iso,
                ':ttl': ttl
            },
            return_values='ALL_NEW',
            request_id=request_id,
            trace_id=trace_id
        )
        
        return response.get('Attributes', {})
    
    def delete_session_state(
        self,
        session_id: str,
        request_id: Optional[str] = None,
        trace_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Delete session state.
        
        Args:
            session_id: Session ID
            request_id: Optional request ID for correlation
            trace_id: Optional trace ID for correlation
        
        Returns:
            Response from DynamoDB
        
        Raises:
            DynamoDBClientError: If operation fails
        """
        return self.client.delete_item(
            table_name=self.TABLE_NAME,
            key={'session_id': session_id},
            request_id=request_id,
            trace_id=trace_id
        )
