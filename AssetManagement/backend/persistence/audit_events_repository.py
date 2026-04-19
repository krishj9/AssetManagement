"""
Audit Events Repository

This module provides operations for the Audit Events DynamoDB table.
"""

import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List
from boto3.dynamodb.conditions import Key, Attr
from .dynamodb_client import DynamoDBClient, DynamoDBClientError


class AuditEventsRepository:
    """
    Repository for Audit Events table operations.
    
    Table: AuditEvents
    Primary Key: event_id
    GSI1: request_id + timestamp
    GSI2: trace_id + timestamp
    GSI3: timestamp + event_type
    TTL: 7 years (2557 days)
    """
    
    TABLE_NAME = "AuditEvents"
    GSI_REQUEST_ID_TIMESTAMP = "RequestIdTimestampIndex"
    GSI_TRACE_ID_TIMESTAMP = "TraceIdTimestampIndex"
    GSI_TIMESTAMP_EVENT_TYPE = "TimestampEventTypeIndex"
    TTL_DAYS = 2557  # 7 years
    
    def __init__(self, dynamodb_client: DynamoDBClient):
        """
        Initialize repository.
        
        Args:
            dynamodb_client: DynamoDB client wrapper
        """
        self.client = dynamodb_client
        self.table = dynamodb_client.get_table(self.TABLE_NAME)
    
    def _calculate_ttl(self) -> int:
        """Calculate TTL timestamp (7 years from now)"""
        expiry_time = datetime.now(timezone.utc) + timedelta(days=self.TTL_DAYS)
        return int(expiry_time.timestamp())
    
    def create_audit_event(
        self,
        event_type: str,
        action_details: Dict[str, Any],
        outcome: str,
        environment_alias: str,
        request_id: Optional[str] = None,
        session_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        actor_identity: Optional[str] = None,
        actor_role: Optional[str] = None,
        agent_identity: Optional[str] = None,
        agent_version: Optional[str] = None,
        policy_version: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        event_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new audit event.
        
        Args:
            event_type: Type of event (REQUEST_RECEIVED, AGENT_INVOKED, etc.)
            action_details: Structured details about the action
            outcome: Outcome of the action (success, failure, partial)
            environment_alias: Environment alias (dev, test, pre-prod, prod)
            request_id: Optional request ID
            session_id: Optional session ID
            trace_id: Optional trace ID
            actor_identity: Optional human actor identity
            actor_role: Optional human actor role
            agent_identity: Optional agent identity
            agent_version: Optional agent version
            policy_version: Optional policy version
            metadata: Optional additional metadata
            event_id: Optional event ID (generated if not provided)
        
        Returns:
            Created audit event
        
        Raises:
            DynamoDBClientError: If operation fails
        """
        if not event_id:
            event_id = f"event-{uuid.uuid4()}"
        
        now = datetime.now(timezone.utc).isoformat()
        ttl = self._calculate_ttl()
        
        item = {
            'event_id': event_id,
            'event_type': event_type,
            'timestamp': now,
            'action_details': action_details,
            'outcome': outcome,
            'environment_alias': environment_alias,
            'ttl': ttl
        }
        
        # Add optional fields
        if request_id:
            item['request_id'] = request_id
        if session_id:
            item['session_id'] = session_id
        if trace_id:
            item['trace_id'] = trace_id
        if actor_identity:
            item['actor_identity'] = actor_identity
        if actor_role:
            item['actor_role'] = actor_role
        if agent_identity:
            item['agent_identity'] = agent_identity
        if agent_version:
            item['agent_version'] = agent_version
        if policy_version:
            item['policy_version'] = policy_version
        if metadata:
            item['metadata'] = metadata
        
        self.client.put_item(
            table_name=self.TABLE_NAME,
            item=item,
            request_id=request_id,
            trace_id=trace_id
        )
        
        return item
    
    def batch_create_audit_events(
        self,
        events: List[Dict[str, Any]],
        request_id: Optional[str] = None,
        trace_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Batch create audit events.
        
        Args:
            events: List of audit event dictionaries
            request_id: Optional request ID for correlation
            trace_id: Optional trace ID for correlation
        
        Returns:
            Response from DynamoDB
        
        Raises:
            DynamoDBClientError: If operation fails
        """
        # Ensure all events have required fields and TTL
        ttl = self._calculate_ttl()
        now = datetime.now(timezone.utc).isoformat()
        
        items = []
        for event in events:
            if 'event_id' not in event:
                event['event_id'] = f"event-{uuid.uuid4()}"
            if 'timestamp' not in event:
                event['timestamp'] = now
            if 'ttl' not in event:
                event['ttl'] = ttl
            items.append(event)
        
        return self.client.batch_write_items(
            table_name=self.TABLE_NAME,
            items=items,
            request_id=request_id,
            trace_id=trace_id
        )
    
    def get_audit_event_by_id(
        self,
        event_id: str,
        request_id: Optional[str] = None,
        trace_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get audit event by event_id.
        
        Args:
            event_id: Event ID
            request_id: Optional request ID for correlation
            trace_id: Optional trace ID for correlation
        
        Returns:
            Audit event if found, None otherwise
        
        Raises:
            DynamoDBClientError: If operation fails
        """
        return self.client.get_item(
            table_name=self.TABLE_NAME,
            key={'event_id': event_id},
            consistent_read=True,
            request_id=request_id,
            trace_id=trace_id
        )
    
    def query_audit_events_by_request_id(
        self,
        request_id: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: Optional[int] = None,
        trace_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Query audit events by request_id with time ordering using GSI1.
        
        Args:
            request_id: Request ID
            start_time: Optional start time (ISO 8601)
            end_time: Optional end time (ISO 8601)
            limit: Optional limit on number of items
            trace_id: Optional trace ID for correlation
        
        Returns:
            List of audit events ordered by timestamp
        
        Raises:
            DynamoDBClientError: If operation fails
        """
        # Build key condition expression
        if start_time and end_time:
            key_condition = Key('request_id').eq(request_id) & Key('timestamp').between(start_time, end_time)
        elif start_time:
            key_condition = Key('request_id').eq(request_id) & Key('timestamp').gte(start_time)
        elif end_time:
            key_condition = Key('request_id').eq(request_id) & Key('timestamp').lte(end_time)
        else:
            key_condition = Key('request_id').eq(request_id)
        
        return self.client.query(
            table_name=self.TABLE_NAME,
            index_name=self.GSI_REQUEST_ID_TIMESTAMP,
            key_condition_expression=key_condition,
            scan_index_forward=True,  # Ascending order by timestamp
            limit=limit,
            request_id=request_id,
            trace_id=trace_id
        )
    
    def query_audit_events_by_trace_id(
        self,
        trace_id: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: Optional[int] = None,
        request_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Query audit events by trace_id with time ordering using GSI2.
        
        Args:
            trace_id: Trace ID
            start_time: Optional start time (ISO 8601)
            end_time: Optional end time (ISO 8601)
            limit: Optional limit on number of items
            request_id: Optional request ID for correlation
        
        Returns:
            List of audit events ordered by timestamp
        
        Raises:
            DynamoDBClientError: If operation fails
        """
        # Build key condition expression
        if start_time and end_time:
            key_condition = Key('trace_id').eq(trace_id) & Key('timestamp').between(start_time, end_time)
        elif start_time:
            key_condition = Key('trace_id').eq(trace_id) & Key('timestamp').gte(start_time)
        elif end_time:
            key_condition = Key('trace_id').eq(trace_id) & Key('timestamp').lte(end_time)
        else:
            key_condition = Key('trace_id').eq(trace_id)
        
        return self.client.query(
            table_name=self.TABLE_NAME,
            index_name=self.GSI_TRACE_ID_TIMESTAMP,
            key_condition_expression=key_condition,
            scan_index_forward=True,  # Ascending order by timestamp
            limit=limit,
            request_id=request_id,
            trace_id=trace_id
        )
    
    def query_audit_events_by_timestamp_range(
        self,
        start_time: str,
        end_time: Optional[str] = None,
        event_type: Optional[str] = None,
        limit: Optional[int] = None,
        request_id: Optional[str] = None,
        trace_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Query audit events by timestamp range with optional event type filtering using GSI3.
        
        Args:
            start_time: Start time (ISO 8601)
            end_time: Optional end time (ISO 8601)
            event_type: Optional event type filter
            limit: Optional limit on number of items
            request_id: Optional request ID for correlation
            trace_id: Optional trace ID for correlation
        
        Returns:
            List of audit events ordered by timestamp
        
        Raises:
            DynamoDBClientError: If operation fails
        """
        # Build key condition expression
        if event_type:
            if end_time:
                key_condition = Key('timestamp').between(start_time, end_time) & Key('event_type').eq(event_type)
            else:
                key_condition = Key('timestamp').gte(start_time) & Key('event_type').eq(event_type)
        else:
            if end_time:
                key_condition = Key('timestamp').between(start_time, end_time)
            else:
                key_condition = Key('timestamp').gte(start_time)
        
        return self.client.query(
            table_name=self.TABLE_NAME,
            index_name=self.GSI_TIMESTAMP_EVENT_TYPE,
            key_condition_expression=key_condition,
            scan_index_forward=True,  # Ascending order by timestamp
            limit=limit,
            request_id=request_id,
            trace_id=trace_id
        )
