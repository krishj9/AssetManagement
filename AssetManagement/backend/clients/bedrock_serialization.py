"""
Bedrock Agent Request/Response Serialization

This module provides utilities for serializing and deserializing
requests and responses for Bedrock Agents.
"""

import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)


class BedrockSerializationError(Exception):
    """Exception raised for serialization/deserialization errors"""
    pass


class BedrockRequestSerializer:
    """
    Serializer for Bedrock Agent requests.
    
    Converts Pydantic models to JSON strings suitable for Bedrock Agent input.
    """
    
    @staticmethod
    def serialize_request(
        request_model: BaseModel,
        request_id: Optional[str] = None,
        trace_id: Optional[str] = None
    ) -> str:
        """
        Serialize a Pydantic request model to JSON string.
        
        Args:
            request_model: Pydantic model instance
            request_id: Optional request ID for logging
            trace_id: Optional trace ID for logging
        
        Returns:
            JSON string representation
        
        Raises:
            BedrockSerializationError: If serialization fails
        """
        try:
            # Convert Pydantic model to dict
            request_dict = request_model.model_dump(mode='json', exclude_none=False)
            
            # Serialize to JSON string
            json_str = json.dumps(request_dict, indent=None, separators=(',', ':'))
            
            logger.debug("Serialized request", extra={
                'request_id': request_id,
                'trace_id': trace_id,
                'model_type': type(request_model).__name__,
                'json_length': len(json_str)
            })
            
            return json_str
            
        except Exception as e:
            logger.error(f"Request serialization failed: {str(e)}", extra={
                'request_id': request_id,
                'trace_id': trace_id,
                'model_type': type(request_model).__name__,
                'error': str(e)
            })
            raise BedrockSerializationError(f"Failed to serialize request: {str(e)}") from e
    
    @staticmethod
    def serialize_dict(
        data: Dict[str, Any],
        request_id: Optional[str] = None,
        trace_id: Optional[str] = None
    ) -> str:
        """
        Serialize a dictionary to JSON string.
        
        Args:
            data: Dictionary to serialize
            request_id: Optional request ID for logging
            trace_id: Optional trace ID for logging
        
        Returns:
            JSON string representation
        
        Raises:
            BedrockSerializationError: If serialization fails
        """
        try:
            # Handle datetime objects
            def json_serializer(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
            
            json_str = json.dumps(data, default=json_serializer, indent=None, separators=(',', ':'))
            
            logger.debug("Serialized dictionary", extra={
                'request_id': request_id,
                'trace_id': trace_id,
                'json_length': len(json_str)
            })
            
            return json_str
            
        except Exception as e:
            logger.error(f"Dictionary serialization failed: {str(e)}", extra={
                'request_id': request_id,
                'trace_id': trace_id,
                'error': str(e)
            })
            raise BedrockSerializationError(f"Failed to serialize dictionary: {str(e)}") from e


class BedrockResponseDeserializer:
    """
    Deserializer for Bedrock Agent responses.
    
    Converts JSON strings from Bedrock Agent output to Pydantic models.
    """
    
    @staticmethod
    def deserialize_response(
        json_str: str,
        response_model_class: type[BaseModel],
        request_id: Optional[str] = None,
        trace_id: Optional[str] = None
    ) -> BaseModel:
        """
        Deserialize JSON string to Pydantic response model.
        
        Args:
            json_str: JSON string from Bedrock Agent
            response_model_class: Pydantic model class to deserialize into
            request_id: Optional request ID for logging
            trace_id: Optional trace ID for logging
        
        Returns:
            Pydantic model instance
        
        Raises:
            BedrockSerializationError: If deserialization fails
        """
        try:
            # Parse JSON string
            response_dict = json.loads(json_str)
            
            # Validate and create Pydantic model
            response_model = response_model_class(**response_dict)
            
            logger.debug("Deserialized response", extra={
                'request_id': request_id,
                'trace_id': trace_id,
                'model_type': response_model_class.__name__,
                'json_length': len(json_str)
            })
            
            return response_model
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {str(e)}", extra={
                'request_id': request_id,
                'trace_id': trace_id,
                'model_type': response_model_class.__name__,
                'json_str': json_str[:500],  # Log first 500 chars
                'error': str(e)
            })
            raise BedrockSerializationError(f"Failed to parse JSON: {str(e)}") from e
            
        except ValidationError as e:
            logger.error(f"Response validation failed: {str(e)}", extra={
                'request_id': request_id,
                'trace_id': trace_id,
                'model_type': response_model_class.__name__,
                'validation_errors': e.errors(),
                'error': str(e)
            })
            raise BedrockSerializationError(f"Failed to validate response: {str(e)}") from e
            
        except Exception as e:
            logger.error(f"Response deserialization failed: {str(e)}", extra={
                'request_id': request_id,
                'trace_id': trace_id,
                'model_type': response_model_class.__name__,
                'error': str(e)
            })
            raise BedrockSerializationError(f"Failed to deserialize response: {str(e)}") from e
    
    @staticmethod
    def deserialize_to_dict(
        json_str: str,
        request_id: Optional[str] = None,
        trace_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Deserialize JSON string to dictionary.
        
        Args:
            json_str: JSON string from Bedrock Agent
            request_id: Optional request ID for logging
            trace_id: Optional trace ID for logging
        
        Returns:
            Dictionary representation
        
        Raises:
            BedrockSerializationError: If deserialization fails
        """
        try:
            response_dict = json.loads(json_str)
            
            logger.debug("Deserialized to dictionary", extra={
                'request_id': request_id,
                'trace_id': trace_id,
                'json_length': len(json_str)
            })
            
            return response_dict
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {str(e)}", extra={
                'request_id': request_id,
                'trace_id': trace_id,
                'json_str': json_str[:500],  # Log first 500 chars
                'error': str(e)
            })
            raise BedrockSerializationError(f"Failed to parse JSON: {str(e)}") from e
    
    @staticmethod
    def extract_json_from_text(
        text: str,
        request_id: Optional[str] = None,
        trace_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Extract JSON from text that may contain additional content.
        
        Bedrock agents may return JSON wrapped in markdown code blocks or
        with additional explanatory text. This method attempts to extract
        the JSON portion.
        
        Args:
            text: Text containing JSON
            request_id: Optional request ID for logging
            trace_id: Optional trace ID for logging
        
        Returns:
            Extracted JSON string or None if not found
        """
        # Try to find JSON in markdown code blocks
        import re
        
        # Pattern for markdown code blocks with json
        json_block_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
        match = re.search(json_block_pattern, text, re.DOTALL)
        
        if match:
            logger.debug("Extracted JSON from markdown code block", extra={
                'request_id': request_id,
                'trace_id': trace_id
            })
            return match.group(1)
        
        # Try to find JSON object directly
        json_pattern = r'\{.*\}'
        match = re.search(json_pattern, text, re.DOTALL)
        
        if match:
            logger.debug("Extracted JSON from text", extra={
                'request_id': request_id,
                'trace_id': trace_id
            })
            return match.group(0)
        
        logger.warning("No JSON found in text", extra={
            'request_id': request_id,
            'trace_id': trace_id,
            'text_preview': text[:200]
        })
        
        return None
