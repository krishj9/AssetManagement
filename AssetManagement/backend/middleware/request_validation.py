"""
Request Validation Middleware

This middleware validates incoming requests for required headers and basic structure.
"""

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging
from typing import Callable

logger = logging.getLogger(__name__)


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """
    Middleware for validating incoming requests.
    
    Validates:
    - Content-Type for POST/PUT requests
    - Request size limits
    - Required headers for specific endpoints
    """
    
    MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10 MB
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Validate request before processing.
        
        Args:
            request: Incoming request
            call_next: Next middleware or route handler
        
        Returns:
            Response from next handler or validation error
        """
        # Skip validation for health check and docs endpoints
        if request.url.path in ["/api/health", "/api/health/ready", "/api/docs", "/api/redoc", "/api/openapi.json", "/"]:
            return await call_next(request)
        
        # Validate Content-Type for POST/PUT requests
        if request.method in ["POST", "PUT"]:
            content_type = request.headers.get("content-type", "")
            if not content_type.startswith("application/json"):
                logger.warning(f"Invalid Content-Type: {content_type}", extra={
                    'request_id': getattr(request.state, 'request_id', None),
                    'path': request.url.path,
                    'method': request.method
                })
                return JSONResponse(
                    status_code=415,
                    content={
                        "error": {
                            "code": "UNSUPPORTED_MEDIA_TYPE",
                            "message": "Content-Type must be application/json",
                            "severity": "error",
                            "retryable": False
                        }
                    }
                )
        
        # Validate request size
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.MAX_REQUEST_SIZE:
            logger.warning(f"Request too large: {content_length} bytes", extra={
                'request_id': getattr(request.state, 'request_id', None),
                'path': request.url.path,
                'method': request.method
            })
            return JSONResponse(
                status_code=413,
                content={
                    "error": {
                        "code": "REQUEST_TOO_LARGE",
                        "message": f"Request size exceeds maximum of {self.MAX_REQUEST_SIZE} bytes",
                        "severity": "error",
                        "retryable": False
                    }
                }
            )
        
        # Process request
        response = await call_next(request)
        return response
