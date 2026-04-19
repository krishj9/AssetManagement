"""
FastAPI Application Main Entry Point

This module defines the FastAPI application for the Portfolio Management Platform.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from .middleware.request_validation import RequestValidationMiddleware
from .middleware.error_handler import ErrorHandlerMiddleware
from .routers import health, approval, audit

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Portfolio Management Platform API",
    description="Backend API for Autonomous Portfolio Construction and Rebalancing Platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Qt desktop client (local dev)
        "http://localhost:8080",  # Alternative local port
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Trace-ID"]
)

# Add custom middleware
app.add_middleware(RequestValidationMiddleware)
app.add_middleware(ErrorHandlerMiddleware)

# Include routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(approval.router, prefix="/api/approval", tags=["approval"])
app.include_router(audit.router, prefix="/api/audit", tags=["audit"])


@app.middleware("http")
async def add_correlation_ids(request: Request, call_next):
    """
    Add correlation IDs to all requests.
    
    Generates request_id and trace_id if not provided in headers.
    """
    # Get or generate request_id
    request_id = request.headers.get("X-Request-ID")
    if not request_id:
        request_id = f"req-{uuid.uuid4()}"
    
    # Get or generate trace_id
    trace_id = request.headers.get("X-Trace-ID")
    if not trace_id:
        trace_id = f"trace-{uuid.uuid4()}"
    
    # Store in request state
    request.state.request_id = request_id
    request.state.trace_id = trace_id
    request.state.timestamp = datetime.now(timezone.utc).isoformat()
    
    # Log request
    logger.info(f"Request received: {request.method} {request.url.path}", extra={
        'request_id': request_id,
        'trace_id': trace_id,
        'method': request.method,
        'path': request.url.path
    })
    
    # Process request
    response = await call_next(request)
    
    # Add correlation IDs to response headers
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Trace-ID"] = trace_id
    
    return response


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    
    return response


@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("Portfolio Management Platform API starting up")
    logger.info(f"Environment: {app.state.environment if hasattr(app.state, 'environment') else 'dev'}")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("Portfolio Management Platform API shutting down")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Portfolio Management Platform API",
        "version": "1.0.0",
        "status": "running"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
