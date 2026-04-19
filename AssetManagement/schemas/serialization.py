"""
Schema Serialization and Deserialization Utilities

This module provides utilities for serializing and deserializing schema objects
to/from JSON, with proper error handling and validation.
"""

import json
from typing import Type, TypeVar, Dict, Any, Optional
from pydantic import BaseModel, ValidationError
from datetime import datetime


T = TypeVar('T', bound=BaseModel)


class SerializationError(Exception):
    """Exception raised when serialization fails"""
    pass


class DeserializationError(Exception):
    """Exception raised when deserialization fails"""
    pass


def serialize_to_json(model: BaseModel, indent: Optional[int] = None) -> str:
    """
    Serialize a Pydantic model to JSON string.
    
    Args:
        model: Pydantic model instance to serialize
        indent: Number of spaces for indentation (None for compact)
        
    Returns:
        JSON string representation
        
    Raises:
        SerializationError: If serialization fails
    """
    try:
        return model.model_dump_json(indent=indent)
    except Exception as e:
        raise SerializationError(f"Failed to serialize {type(model).__name__}: {str(e)}")


def serialize_to_dict(model: BaseModel) -> Dict[str, Any]:
    """
    Serialize a Pydantic model to dictionary.
    
    Args:
        model: Pydantic model instance to serialize
        
    Returns:
        Dictionary representation
        
    Raises:
        SerializationError: If serialization fails
    """
    try:
        return model.model_dump()
    except Exception as e:
        raise SerializationError(f"Failed to serialize {type(model).__name__} to dict: {str(e)}")


def deserialize_from_json(model_class: Type[T], json_str: str) -> T:
    """
    Deserialize a JSON string to a Pydantic model.
    
    Args:
        model_class: Pydantic model class to deserialize to
        json_str: JSON string to deserialize
        
    Returns:
        Instance of model_class
        
    Raises:
        DeserializationError: If deserialization or validation fails
    """
    try:
        return model_class.model_validate_json(json_str)
    except ValidationError as e:
        raise DeserializationError(f"Validation failed for {model_class.__name__}: {str(e)}")
    except json.JSONDecodeError as e:
        raise DeserializationError(f"Invalid JSON for {model_class.__name__}: {str(e)}")
    except Exception as e:
        raise DeserializationError(f"Failed to deserialize {model_class.__name__}: {str(e)}")


def deserialize_from_dict(model_class: Type[T], data: Dict[str, Any]) -> T:
    """
    Deserialize a dictionary to a Pydantic model.
    
    Args:
        model_class: Pydantic model class to deserialize to
        data: Dictionary to deserialize
        
    Returns:
        Instance of model_class
        
    Raises:
        DeserializationError: If deserialization or validation fails
    """
    try:
        return model_class.model_validate(data)
    except ValidationError as e:
        raise DeserializationError(f"Validation failed for {model_class.__name__}: {str(e)}")
    except Exception as e:
        raise DeserializationError(f"Failed to deserialize {model_class.__name__}: {str(e)}")


def safe_deserialize_from_json(model_class: Type[T], json_str: str) -> tuple[Optional[T], Optional[str]]:
    """
    Safely deserialize a JSON string to a Pydantic model without raising exceptions.
    
    Args:
        model_class: Pydantic model class to deserialize to
        json_str: JSON string to deserialize
        
    Returns:
        Tuple of (model_instance, error_message)
        If successful: (instance, None)
        If failed: (None, error_message)
    """
    try:
        instance = deserialize_from_json(model_class, json_str)
        return instance, None
    except DeserializationError as e:
        return None, str(e)


def safe_deserialize_from_dict(model_class: Type[T], data: Dict[str, Any]) -> tuple[Optional[T], Optional[str]]:
    """
    Safely deserialize a dictionary to a Pydantic model without raising exceptions.
    
    Args:
        model_class: Pydantic model class to deserialize to
        data: Dictionary to deserialize
        
    Returns:
        Tuple of (model_instance, error_message)
        If successful: (instance, None)
        If failed: (None, error_message)
    """
    try:
        instance = deserialize_from_dict(model_class, data)
        return instance, None
    except DeserializationError as e:
        return None, str(e)


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder for datetime objects"""
    
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def serialize_with_datetime(data: Dict[str, Any], indent: Optional[int] = None) -> str:
    """
    Serialize a dictionary to JSON with proper datetime handling.
    
    Args:
        data: Dictionary to serialize
        indent: Number of spaces for indentation (None for compact)
        
    Returns:
        JSON string representation
        
    Raises:
        SerializationError: If serialization fails
    """
    try:
        return json.dumps(data, cls=DateTimeEncoder, indent=indent)
    except Exception as e:
        raise SerializationError(f"Failed to serialize with datetime: {str(e)}")


def validate_and_serialize(model: BaseModel, indent: Optional[int] = None) -> str:
    """
    Validate a model and serialize it to JSON.
    
    This performs a round-trip validation to ensure the model is fully valid.
    
    Args:
        model: Pydantic model instance to validate and serialize
        indent: Number of spaces for indentation (None for compact)
        
    Returns:
        JSON string representation
        
    Raises:
        SerializationError: If validation or serialization fails
    """
    try:
        # Perform round-trip validation
        model_class = type(model)
        json_str = serialize_to_json(model, indent=None)
        validated_model = deserialize_from_json(model_class, json_str)
        
        # Serialize with requested indentation
        return serialize_to_json(validated_model, indent=indent)
    except (SerializationError, DeserializationError) as e:
        raise SerializationError(f"Validation and serialization failed: {str(e)}")
