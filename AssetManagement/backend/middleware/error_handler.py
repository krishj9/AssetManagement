"""
Error Handler Middleware

This middleware catches exceptions and converts them to structured error responses.
"""

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import ValidationError
import logging
import traceback
from typing import Callable
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Middleware for handling exceptions and converting them to structured errors.
    
    Converts all exceptions to Structured_Error format for consistent error responses.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Handle exceptions and convert to structured errors.
        
        Args:
            request: Incoming request
            call_next: Next middleware or route handler
        
        Returns:
            Response from next handler or structured error response
        """
        try:
            response = await call_next(request)
            return response
            
        except ValidationError as e:
            # Pydantic validation error
            request_id = getattr(request.state, 'request_id', None)
            trace_id = getattr(request.state, 'trace_id', None)
            
            logger.error(f"Validation error: {str(e)}", extra={
                'request_id': request_id,
                'trace_id': trace_id,
                'path': request.url.path,
                'method': request.method,
                'error_type': 'ValidationError'
            })
            
            return JSONResponse(
                status_code=422,
                content={
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "Request validation failed",
                        "severity": "error",
                        "retryable": False,
                        "source_agent": None,
                        "request_id": request_id,
                        "trace_id": trace_id,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "related_context": {
                            "validation_errors": e.errors()
                        }
                    }
                }
            )
        
        except ValueError as e:
            # Value error (e.g., invalid input)
            request_id = getattr(request.state, 'request_id', None)
            trace_id = getattr(request.state, 'trace_id', None)
            
            logger.error(f"Value error: {str(e)}", extra={
                'request_id': request_id,
                'trace_id': trace_id,
                'path': request.url.path,
                'method': request.method,
                'error_type': 'ValueError'
            })
            
            return JSONResponse(
                status_code=400,
                content={
                    "error": {
                        "code": "INVALID_INPUT",
                        "message": str(e),
                        "severity": "error",
                        "retryable": False,
                        "source_agent": None,
                        "request_id": request_id,
                        "trace_id": trace_id,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "related_context": {}
                    }
                }
            )
        
        except PermissionError as e:
            # Permission error (authorization failure)
            request_id = getattr(request.state, 'request_id', None)
            trace_id = getattr(request.state, 'trace_id', None)
            
            logger.error(f"Permission error: {str(e)}", extra={
                'request_id': request_id,
                'trace_id': trace_id,
                'path': request.url.path,
                'method': request.method,
                'error_type': 'PermissionError'
            })
            
            return JSONResponse(
                status_code=403,
                content={
                    "error": {
                        "code": "AUTHORIZATION_FAILURE",
                        "message": "Insufficient permissions to perform this action",
                        "severity": "error",
                        "retryable": False,
                        "source_agent": None,
                        "request_id": request_id,
                        "trace_id": trace_id,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "related_context": {
                            "details": str(e)
                        }
                    }
                }
            )
        
        except Exception as e:
            # Unexpected error
            request_id = getattr(request.state, 'request_id', None)
            trace_id = getattr(request.state, 'trace_id', None)
            
            logger.error(f"Unexpected error: {str(e)}", extra={
                'request_id': request_id,
                'trace_id': trace_id,
                'path': request.url.path,
                'method': request.method,
                'error_type': type(e).__name__,
                'traceback': traceback.format_exc()
            })
            
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "code": "INTERNAL_SERVER_ERROR",
                        "message": "An unexpected error occurred",
                        "severity": "critical",
                        "retryable": True,
                        "source_agent": None,
                        "request_id": request_id,
                        "trace_id": trace_id,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "related_context": {
                            "error_type": type(e).__name__
                        }
                    }
                }
            )
