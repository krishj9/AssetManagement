"""
Health Check Router

This module provides health check and readiness endpoints.
"""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health")
async def health_check(request: Request):
    """
    Health check endpoint.
    
    Returns basic health status of the service.
    """
    return {
        "status": "healthy",
        "service": "Portfolio Management Platform API",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/health/ready")
async def readiness_check(request: Request):
    """
    Readiness check endpoint.
    
    Checks if the service is ready to accept requests.
    This should verify:
    - Database connectivity
    - External service availability
    - Required resources
    """
    # TODO: Add actual readiness checks
    # For now, return ready if service is running
    
    checks = {
        "dynamodb": "ready",  # TODO: Check DynamoDB connectivity
        "bedrock": "ready",   # TODO: Check Bedrock API availability
        "memory": "ready"     # TODO: Check AgentCore Memory availability
    }
    
    all_ready = all(status == "ready" for status in checks.values())
    
    if all_ready:
        return {
            "status": "ready",
            "checks": checks,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    else:
        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "checks": checks,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )


@router.get("/health/live")
async def liveness_check(request: Request):
    """
    Liveness check endpoint.
    
    Returns 200 if the service is alive (process is running).
    """
    return {
        "status": "alive",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
