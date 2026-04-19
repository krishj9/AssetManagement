"""
Memory Consolidation Queue Repository

This module provides CRUD operations for the Memory Consolidation Queue DynamoDB table.
"""

import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List
from boto3.dynamodb.conditions import Key, Attr
from .dynamodb_client import DynamoDBClient, DynamoDBClientError


class MemoryConsolidationQueueRepository:
    """
    Repository for Memory Consolidation Queue table operations.
    
    Table: MemoryConsolidationQueue
    Primary Key: consolidation_id
    GSI: consolidation_status + created_at
    TTL: 30 days
    """
    
    TABLE_NAME = "MemoryConsolidationQueue"
    GSI_STATUS_CREATED_AT = "StatusCreatedAtIndex"
    TTL_DAYS = 30
    
    def __init__(self, dynamodb_client: DynamoDBClient):
        """
        Initialize repository.
        
        Args:
            dynamodb_client: DynamoDB client wrapper
        """
        self.client = dynamodb_client
        self.table = dynamodb_client.get_table(self.TABLE_NAME)
    
    def _calculate_ttl(self) -> int:
        """Calculate TTL timestamp (30 days from now)"""
        expiry_time = datetime.now(timezone.utc) + timedelta(days=self.TTL_DAYS)
        return int(expiry_time.timestamp())
    
    def create_consolidation_task(
        self,
        request_id: str,
        client_id: str,
        memory_candidates: List[Dict[str, Any]],
        consolidation_id: Optional[str] = None,
        trace_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new memory consolidation task.
        
        Args:
            request_id: Request ID
            client_id: Client ID
            memory_candidates: List of memory candidates to consolidate
            consolidation_id: Optional consolidation ID (generated if not provided)
            trace_id: Optional trace ID for correlation
        
        Returns:
            Created consolidation task
        
        Raises:
            DynamoDBClientError: If operation fails
        """
        if not consolidation_id:
            consolidation_id = f"consolidation-{uuid.uuid4()}"
        
        now = datetime.now(timezone.utc).isoformat()
        ttl = self._calculate_ttl()
        
        item = {
            'consolidation_id': consolidation_id,
            'request_id': request_id,
            'client_id': client_id,
            'memory_candidates': memory_candidates,
            'consolidation_status': 'PENDING',
            'created_at': now,
            'updated_at': now,
            'ttl': ttl
        }
        
        self.client.put_item(
            table_name=self.TABLE_NAME,
            item=item,
            condition_expression='attribute_not_exists(consolidation_id)',  # Prevent overwrites
            request_id=request_id,
            trace_id=trace_id
        )
        
        return item
    
    def get_consolidation_task(
        self,
        consolidation_id: str,
        request_id: Optional[str] = None,
        trace_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get consolidation task by consolidation_id.
        
        Args:
            consolidation_id: Consolidation ID
            request_id: Optional request ID for correlation
            trace_id: Optional trace ID for correlation
        
        Returns:
            Consolidation task if found, None otherwise
        
        Raises:
            DynamoDBClientError: If operation fails
        """
        return self.client.get_item(
            table_name=self.TABLE_NAME,
            key={'consolidation_id': consolidation_id},
            consistent_read=True,
            request_id=request_id,
            trace_id=trace_id
        )
    
    def query_consolidation_tasks_by_status(
        self,
        consolidation_status: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: Optional[int] = None,
        request_id: Optional[str] = None,
        trace_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Query consolidation tasks by status with time ordering using GSI.
        
        Args:
            consolidation_status: Consolidation status (PENDING, IN_PROGRESS, COMPLETED, FAILED)
            start_time: Optional start time (ISO 8601)
            end_time: Optional end time (ISO 8601)
            limit: Optional limit on number of items
            request_id: Optional request ID for correlation
            trace_id: Optional trace ID for correlation
        
        Returns:
            List of consolidation tasks ordered by created_at
        
        Raises:
            DynamoDBClientError: If operation fails
        """
        # Build key condition expression
        if start_time and end_time:
            key_condition = Key('consolidation_status').eq(consolidation_status) & Key('created_at').between(start_time, end_time)
        elif start_time:
            key_condition = Key('consolidation_status').eq(consolidation_status) & Key('created_at').gte(start_time)
        elif end_time:
            key_condition = Key('consolidation_status').eq(consolidation_status) & Key('created_at').lte(end_time)
        else:
            key_condition = Key('consolidation_status').eq(consolidation_status)
        
        return self.client.query(
            table_name=self.TABLE_NAME,
            index_name=self.GSI_STATUS_CREATED_AT,
            key_condition_expression=key_condition,
            scan_index_forward=True,  # Ascending order by created_at
            limit=limit,
            request_id=request_id,
            trace_id=trace_id
        )
    
    def update_consolidation_status(
        self,
        consolidation_id: str,
        consolidation_status: str,
        processed_at: Optional[str] = None,
        error_details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
        trace_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update consolidation task status with conditional write.
        
        Args:
            consolidation_id: Consolidation ID
            consolidation_status: New status (IN_PROGRESS, COMPLETED, FAILED)
            processed_at: Optional processing completion timestamp
            error_details: Optional error details (for FAILED status)
            request_id: Optional request ID for correlation
            trace_id: Optional trace ID for correlation
        
        Returns:
            Updated consolidation task
        
        Raises:
            DynamoDBClientError: If operation fails or condition check fails
        """
        now = datetime.now(timezone.utc).isoformat()
        
        # Build update expression dynamically
        update_parts = [
            'SET consolidation_status = :status',
            'updated_at = :updated_at'
        ]
        expression_attribute_values = {
            ':status': consolidation_status,
            ':updated_at': now
        }
        
        if processed_at:
            update_parts.append('processed_at = :processed_at')
            expression_attribute_values[':processed_at'] = processed_at
        
        if error_details:
            update_parts.append('error_details = :error_details')
            expression_attribute_values[':error_details'] = error_details
        
        update_expression = ', '.join(update_parts)
        
        # Conditional write: prevent overwriting COMPLETED or FAILED status
        condition_expression = 'consolidation_status IN (:pending, :in_progress)'
        expression_attribute_values[':pending'] = 'PENDING'
        expression_attribute_values[':in_progress'] = 'IN_PROGRESS'
        
        response = self.client.update_item(
            table_name=self.TABLE_NAME,
            key={'consolidation_id': consolidation_id},
            update_expression=update_expression,
            condition_expression=condition_expression,
            expression_attribute_values=expression_attribute_values,
            return_values='ALL_NEW',
            request_id=request_id,
            trace_id=trace_id
        )
        
        return response.get('Attributes', {})
    
    def update_consolidation_task(
        self,
        consolidation_id: str,
        updates: Dict[str, Any],
        request_id: Optional[str] = None,
        trace_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update consolidation task fields (general purpose update).
        
        Args:
            consolidation_id: Consolidation ID
            updates: Dictionary of fields to update
            request_id: Optional request ID for correlation
            trace_id: Optional trace ID for correlation
        
        Returns:
            Updated consolidation task
        
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
            key={'consolidation_id': consolidation_id},
            update_expression=update_expression,
            expression_attribute_names=expression_attribute_names,
            expression_attribute_values=expression_attribute_values,
            return_values='ALL_NEW',
            request_id=request_id,
            trace_id=trace_id
        )
        
        return response.get('Attributes', {})
