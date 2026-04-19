"""
DynamoDB Client Wrapper

This module provides a high-level wrapper around boto3 DynamoDB client with:
- Exponential backoff and retry logic
- Structured error handling
- Request/trace correlation
- Logging with metadata
"""

import boto3
import time
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from botocore.exceptions import ClientError
from decimal import Decimal


# Configure logging
logger = logging.getLogger(__name__)


class DynamoDBClientError(Exception):
    """Base exception for DynamoDB client errors"""
    def __init__(self, message: str, error_code: str, retryable: bool = False, original_error: Optional[Exception] = None):
        super().__init__(message)
        self.error_code = error_code
        self.retryable = retryable
        self.original_error = original_error


class DynamoDBClient:
    """
    High-level DynamoDB client wrapper with retry logic and error handling.
    
    Features:
    - Exponential backoff for throttling errors
    - Structured error responses
    - Request/trace correlation logging
    - Conditional write support
    - Batch operation support
    """
    
    def __init__(
        self,
        region_name: str = "us-east-1",
        endpoint_url: Optional[str] = None,
        max_retries: int = 3,
        base_delay: float = 0.1,
        max_delay: float = 2.0
    ):
        """
        Initialize DynamoDB client.
        
        Args:
            region_name: AWS region
            endpoint_url: Optional endpoint URL (for local testing)
            max_retries: Maximum number of retry attempts
            base_delay: Base delay for exponential backoff (seconds)
            max_delay: Maximum delay for exponential backoff (seconds)
        """
        self.region_name = region_name
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        
        # Initialize boto3 clients
        if endpoint_url:
            self.client = boto3.client('dynamodb', region_name=region_name, endpoint_url=endpoint_url)
            self.resource = boto3.resource('dynamodb', region_name=region_name, endpoint_url=endpoint_url)
        else:
            self.client = boto3.client('dynamodb', region_name=region_name)
            self.resource = boto3.resource('dynamodb', region_name=region_name)
        
        logger.info(f"DynamoDB client initialized for region: {region_name}")
    
    def _calculate_backoff_delay(self, attempt: int) -> float:
        """Calculate exponential backoff delay"""
        delay = min(self.base_delay * (2 ** attempt), self.max_delay)
        return delay
    
    def _is_retryable_error(self, error: ClientError) -> bool:
        """Check if error is retryable"""
        error_code = error.response.get('Error', {}).get('Code', '')
        retryable_codes = [
            'ProvisionedThroughputExceededException',
            'ThrottlingException',
            'RequestLimitExceeded',
            'InternalServerError',
            'ServiceUnavailable'
        ]
        return error_code in retryable_codes
    
    def _handle_client_error(self, error: ClientError, operation: str, request_id: Optional[str] = None, trace_id: Optional[str] = None) -> DynamoDBClientError:
        """Convert boto3 ClientError to DynamoDBClientError"""
        error_code = error.response.get('Error', {}).get('Code', 'UnknownError')
        error_message = error.response.get('Error', {}).get('Message', str(error))
        retryable = self._is_retryable_error(error)
        
        message = f"DynamoDB {operation} failed: {error_message}"
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
        
        return DynamoDBClientError(
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
        Execute DynamoDB operation with exponential backoff retry logic.
        
        Args:
            operation_func: Function to execute
            operation_name: Name of the operation (for logging)
            request_id: Request ID for correlation
            trace_id: Trace ID for correlation
        
        Returns:
            Result of the operation
        
        Raises:
            DynamoDBClientError: If operation fails after all retries
        """
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                result = operation_func()
                
                if attempt > 0:
                    logger.info(f"DynamoDB {operation_name} succeeded after {attempt} retries", extra={
                        'operation': operation_name,
                        'request_id': request_id,
                        'trace_id': trace_id,
                        'attempts': attempt + 1
                    })
                
                return result
                
            except ClientError as e:
                last_error = e
                
                if not self._is_retryable_error(e):
                    # Non-retryable error, fail immediately
                    raise self._handle_client_error(e, operation_name, request_id, trace_id)
                
                if attempt < self.max_retries:
                    # Retryable error, apply backoff
                    delay = self._calculate_backoff_delay(attempt)
                    logger.warning(f"DynamoDB {operation_name} failed (attempt {attempt + 1}/{self.max_retries + 1}), retrying in {delay:.2f}s", extra={
                        'operation': operation_name,
                        'request_id': request_id,
                        'trace_id': trace_id,
                        'error_code': e.response.get('Error', {}).get('Code', ''),
                        'attempt': attempt + 1,
                        'delay': delay
                    })
                    time.sleep(delay)
                else:
                    # Max retries exceeded
                    raise self._handle_client_error(e, operation_name, request_id, trace_id)
        
        # Should never reach here, but just in case
        if last_error:
            raise self._handle_client_error(last_error, operation_name, request_id, trace_id)
    
    def get_table(self, table_name: str):
        """Get DynamoDB table resource"""
        return self.resource.Table(table_name)
    
    def put_item(
        self,
        table_name: str,
        item: Dict[str, Any],
        condition_expression: Optional[str] = None,
        expression_attribute_names: Optional[Dict[str, str]] = None,
        expression_attribute_values: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
        trace_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Put item into DynamoDB table.
        
        Args:
            table_name: Name of the table
            item: Item to put
            condition_expression: Optional condition expression
            expression_attribute_names: Optional attribute name mappings
            expression_attribute_values: Optional attribute value mappings
            request_id: Request ID for correlation
            trace_id: Trace ID for correlation
        
        Returns:
            Response from DynamoDB
        
        Raises:
            DynamoDBClientError: If operation fails
        """
        table = self.get_table(table_name)
        
        def operation():
            kwargs = {'Item': item}
            if condition_expression:
                kwargs['ConditionExpression'] = condition_expression
            if expression_attribute_names:
                kwargs['ExpressionAttributeNames'] = expression_attribute_names
            if expression_attribute_values:
                kwargs['ExpressionAttributeValues'] = expression_attribute_values
            
            return table.put_item(**kwargs)
        
        logger.debug(f"DynamoDB put_item to {table_name}", extra={
            'table_name': table_name,
            'request_id': request_id,
            'trace_id': trace_id,
            'has_condition': condition_expression is not None
        })
        
        return self._execute_with_retry(operation, f"put_item({table_name})", request_id, trace_id)
    
    def get_item(
        self,
        table_name: str,
        key: Dict[str, Any],
        consistent_read: bool = False,
        projection_expression: Optional[str] = None,
        expression_attribute_names: Optional[Dict[str, str]] = None,
        request_id: Optional[str] = None,
        trace_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get item from DynamoDB table.
        
        Args:
            table_name: Name of the table
            key: Primary key of the item
            consistent_read: Whether to use consistent read
            projection_expression: Optional projection expression
            expression_attribute_names: Optional attribute name mappings
            request_id: Request ID for correlation
            trace_id: Trace ID for correlation
        
        Returns:
            Item if found, None otherwise
        
        Raises:
            DynamoDBClientError: If operation fails
        """
        table = self.get_table(table_name)
        
        def operation():
            kwargs = {
                'Key': key,
                'ConsistentRead': consistent_read
            }
            if projection_expression:
                kwargs['ProjectionExpression'] = projection_expression
            if expression_attribute_names:
                kwargs['ExpressionAttributeNames'] = expression_attribute_names
            
            response = table.get_item(**kwargs)
            return response.get('Item')
        
        logger.debug(f"DynamoDB get_item from {table_name}", extra={
            'table_name': table_name,
            'request_id': request_id,
            'trace_id': trace_id,
            'consistent_read': consistent_read
        })
        
        return self._execute_with_retry(operation, f"get_item({table_name})", request_id, trace_id)
    
    def update_item(
        self,
        table_name: str,
        key: Dict[str, Any],
        update_expression: str,
        condition_expression: Optional[str] = None,
        expression_attribute_names: Optional[Dict[str, str]] = None,
        expression_attribute_values: Optional[Dict[str, Any]] = None,
        return_values: str = "ALL_NEW",
        request_id: Optional[str] = None,
        trace_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update item in DynamoDB table.
        
        Args:
            table_name: Name of the table
            key: Primary key of the item
            update_expression: Update expression
            condition_expression: Optional condition expression
            expression_attribute_names: Optional attribute name mappings
            expression_attribute_values: Optional attribute value mappings
            return_values: What to return (NONE, ALL_OLD, UPDATED_OLD, ALL_NEW, UPDATED_NEW)
            request_id: Request ID for correlation
            trace_id: Trace ID for correlation
        
        Returns:
            Response from DynamoDB
        
        Raises:
            DynamoDBClientError: If operation fails
        """
        table = self.get_table(table_name)
        
        def operation():
            kwargs = {
                'Key': key,
                'UpdateExpression': update_expression,
                'ReturnValues': return_values
            }
            if condition_expression:
                kwargs['ConditionExpression'] = condition_expression
            if expression_attribute_names:
                kwargs['ExpressionAttributeNames'] = expression_attribute_names
            if expression_attribute_values:
                kwargs['ExpressionAttributeValues'] = expression_attribute_values
            
            return table.update_item(**kwargs)
        
        logger.debug(f"DynamoDB update_item in {table_name}", extra={
            'table_name': table_name,
            'request_id': request_id,
            'trace_id': trace_id,
            'has_condition': condition_expression is not None
        })
        
        return self._execute_with_retry(operation, f"update_item({table_name})", request_id, trace_id)
    
    def delete_item(
        self,
        table_name: str,
        key: Dict[str, Any],
        condition_expression: Optional[str] = None,
        expression_attribute_names: Optional[Dict[str, str]] = None,
        expression_attribute_values: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
        trace_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Delete item from DynamoDB table.
        
        Args:
            table_name: Name of the table
            key: Primary key of the item
            condition_expression: Optional condition expression
            expression_attribute_names: Optional attribute name mappings
            expression_attribute_values: Optional attribute value mappings
            request_id: Request ID for correlation
            trace_id: Trace ID for correlation
        
        Returns:
            Response from DynamoDB
        
        Raises:
            DynamoDBClientError: If operation fails
        """
        table = self.get_table(table_name)
        
        def operation():
            kwargs = {'Key': key}
            if condition_expression:
                kwargs['ConditionExpression'] = condition_expression
            if expression_attribute_names:
                kwargs['ExpressionAttributeNames'] = expression_attribute_names
            if expression_attribute_values:
                kwargs['ExpressionAttributeValues'] = expression_attribute_values
            
            return table.delete_item(**kwargs)
        
        logger.debug(f"DynamoDB delete_item from {table_name}", extra={
            'table_name': table_name,
            'request_id': request_id,
            'trace_id': trace_id,
            'has_condition': condition_expression is not None
        })
        
        return self._execute_with_retry(operation, f"delete_item({table_name})", request_id, trace_id)
    
    def query(
        self,
        table_name: str,
        key_condition_expression: str,
        index_name: Optional[str] = None,
        filter_expression: Optional[str] = None,
        projection_expression: Optional[str] = None,
        expression_attribute_names: Optional[Dict[str, str]] = None,
        expression_attribute_values: Optional[Dict[str, Any]] = None,
        scan_index_forward: bool = True,
        limit: Optional[int] = None,
        consistent_read: bool = False,
        request_id: Optional[str] = None,
        trace_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Query DynamoDB table or index.
        
        Args:
            table_name: Name of the table
            key_condition_expression: Key condition expression
            index_name: Optional index name
            filter_expression: Optional filter expression
            projection_expression: Optional projection expression
            expression_attribute_names: Optional attribute name mappings
            expression_attribute_values: Optional attribute value mappings
            scan_index_forward: Sort order (True = ascending, False = descending)
            limit: Optional limit on number of items
            consistent_read: Whether to use consistent read
            request_id: Request ID for correlation
            trace_id: Trace ID for correlation
        
        Returns:
            List of items
        
        Raises:
            DynamoDBClientError: If operation fails
        """
        table = self.get_table(table_name)
        
        def operation():
            kwargs = {
                'KeyConditionExpression': key_condition_expression,
                'ScanIndexForward': scan_index_forward,
                'ConsistentRead': consistent_read
            }
            if index_name:
                kwargs['IndexName'] = index_name
            if filter_expression:
                kwargs['FilterExpression'] = filter_expression
            if projection_expression:
                kwargs['ProjectionExpression'] = projection_expression
            if expression_attribute_names:
                kwargs['ExpressionAttributeNames'] = expression_attribute_names
            if expression_attribute_values:
                kwargs['ExpressionAttributeValues'] = expression_attribute_values
            if limit:
                kwargs['Limit'] = limit
            
            response = table.query(**kwargs)
            return response.get('Items', [])
        
        logger.debug(f"DynamoDB query on {table_name}", extra={
            'table_name': table_name,
            'index_name': index_name,
            'request_id': request_id,
            'trace_id': trace_id,
            'limit': limit
        })
        
        return self._execute_with_retry(operation, f"query({table_name})", request_id, trace_id)
    
    def batch_write_items(
        self,
        table_name: str,
        items: List[Dict[str, Any]],
        request_id: Optional[str] = None,
        trace_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Batch write items to DynamoDB table.
        
        Args:
            table_name: Name of the table
            items: List of items to write
            request_id: Request ID for correlation
            trace_id: Trace ID for correlation
        
        Returns:
            Response from DynamoDB
        
        Raises:
            DynamoDBClientError: If operation fails
        """
        table = self.get_table(table_name)
        
        def operation():
            with table.batch_writer() as batch:
                for item in items:
                    batch.put_item(Item=item)
            return {'UnprocessedItems': {}}
        
        logger.debug(f"DynamoDB batch_write_items to {table_name}", extra={
            'table_name': table_name,
            'item_count': len(items),
            'request_id': request_id,
            'trace_id': trace_id
        })
        
        return self._execute_with_retry(operation, f"batch_write_items({table_name})", request_id, trace_id)
