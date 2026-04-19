"""
Audit Router

This module provides endpoints for audit log queries.
"""

from fastapi import APIRouter, Request, Query, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
from typing import Optional
import logging

from AssetManagement.backend.persistence.dynamodb_client import DynamoDBClient
from AssetManagement.backend.persistence.audit_events_repository import AuditEventsRepository

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize clients (in production, use dependency injection)
dynamodb_client = DynamoDBClient()
audit_repo = AuditEventsRepository(dynamodb_client)


@router.get("/events")
async def query_audit_events(
    request: Request,
    request_id: Optional[str] = Query(None, description="Filter by request ID"),
    trace_id: Optional[str] = Query(None, description="Filter by trace ID"),
    start_time: Optional[str] = Query(None, description="Start time (ISO 8601)"),
    end_time: Optional[str] = Query(None, description="End time (ISO 8601)"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    limit: Optional[int] = Query(100, ge=1, le=1000, description="Maximum number of results")
):
    """
    Query audit events.
    
    Supports filtering by:
    - request_id
    - trace_id
    - timestamp range
    - event_type
    """
    req_id = request.state.request_id
    req_trace_id = request.state.trace_id
    
    try:
        logger.info("Querying audit events", extra={
            'request_id': req_id,
            'trace_id': req_trace_id,
            'filter_request_id': request_id,
            'filter_trace_id': trace_id,
            'start_time': start_time,
            'end_time': end_time,
            'event_type': event_type,
            'limit': limit
        })
        
        events = []
        
        # Query by request_id
        if request_id:
            events = audit_repo.query_audit_events_by_request_id(
                request_id=request_id,
                start_time=start_time,
                end_time=end_time,
                limit=limit
            )
        
        # Query by trace_id
        elif trace_id:
            events = audit_repo.query_audit_events_by_trace_id(
                trace_id=trace_id,
                start_time=start_time,
                end_time=end_time,
                limit=limit
            )
        
        # Query by timestamp range
        elif start_time:
            events = audit_repo.query_audit_events_by_timestamp_range(
                start_time=start_time,
                end_time=end_time,
                event_type=event_type,
                limit=limit
            )
        
        # No filter provided
        else:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "MISSING_FILTER",
                    "message": "Must provide request_id, trace_id, or start_time",
                    "severity": "error",
                    "retryable": False,
                    "request_id": req_id,
                    "trace_id": req_trace_id,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
        
        logger.info(f"Retrieved {len(events)} audit events", extra={
            'request_id': req_id,
            'trace_id': req_trace_id,
            'event_count': len(events)
        })
        
        return JSONResponse(
            status_code=200,
            content={
                'events': events,
                'count': len(events),
                'limit': limit
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to query audit events: {str(e)}", extra={
            'request_id': req_id,
            'trace_id': req_trace_id,
            'error': str(e)
        })
        raise HTTPException(
            status_code=500,
            detail={
                "code": "INTERNAL_ERROR",
                "message": f"Failed to query audit events: {str(e)}",
                "severity": "error",
                "retryable": True,
                "request_id": req_id,
                "trace_id": req_trace_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )


@router.get("/events/{event_id}")
async def get_audit_event(event_id: str, request: Request):
    """
    Get audit event by ID.
    
    Args:
        event_id: Audit event ID
    """
    request_id = request.state.request_id
    trace_id = request.state.trace_id
    
    try:
        logger.info(f"Retrieving audit event: {event_id}", extra={
            'request_id': request_id,
            'trace_id': trace_id,
            'event_id': event_id
        })
        
        # Get audit event by ID
        event = audit_repo.get_audit_event_by_id(event_id)
        
        if not event:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "NOT_FOUND",
                    "message": f"Audit event not found: {event_id}",
                    "severity": "error",
                    "retryable": False,
                    "request_id": request_id,
                    "trace_id": trace_id,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
        
        logger.info(f"Retrieved audit event: {event_id}", extra={
            'request_id': request_id,
            'trace_id': trace_id,
            'event_id': event_id,
            'event_type': event.get('event_type')
        })
        
        return JSONResponse(
            status_code=200,
            content=event
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve audit event: {str(e)}", extra={
            'request_id': request_id,
            'trace_id': trace_id,
            'event_id': event_id,
            'error': str(e)
        })
        raise HTTPException(
            status_code=500,
            detail={
                "code": "INTERNAL_ERROR",
                "message": f"Failed to retrieve audit event: {str(e)}",
                "severity": "error",
                "retryable": True,
                "request_id": request_id,
                "trace_id": trace_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )


@router.get("/events/export")
async def export_audit_events(
    request: Request,
    request_id: Optional[str] = Query(None, description="Filter by request ID"),
    trace_id: Optional[str] = Query(None, description="Filter by trace ID"),
    start_time: Optional[str] = Query(None, description="Start time (ISO 8601)"),
    end_time: Optional[str] = Query(None, description="End time (ISO 8601)"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    format: Optional[str] = Query("json", description="Export format (json, csv)")
):
    """
    Export audit events for governance review.
    
    Supports filtering by:
    - request_id
    - trace_id
    - timestamp range
    - event_type
    
    Export formats:
    - json: JSON array of events
    - csv: CSV format with headers
    """
    req_id = request.state.request_id
    req_trace_id = request.state.trace_id
    
    try:
        logger.info("Exporting audit events", extra={
            'request_id': req_id,
            'trace_id': req_trace_id,
            'filter_request_id': request_id,
            'filter_trace_id': trace_id,
            'start_time': start_time,
            'end_time': end_time,
            'event_type': event_type,
            'format': format
        })
        
        # Query events (no limit for export)
        events = []
        
        if request_id:
            events = audit_repo.query_audit_events_by_request_id(
                request_id=request_id,
                start_time=start_time,
                end_time=end_time,
                limit=10000  # High limit for export
            )
        elif trace_id:
            events = audit_repo.query_audit_events_by_trace_id(
                trace_id=trace_id,
                start_time=start_time,
                end_time=end_time,
                limit=10000
            )
        elif start_time:
            events = audit_repo.query_audit_events_by_timestamp_range(
                start_time=start_time,
                end_time=end_time,
                event_type=event_type,
                limit=10000
            )
        else:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "MISSING_FILTER",
                    "message": "Must provide request_id, trace_id, or start_time",
                    "severity": "error",
                    "retryable": False,
                    "request_id": req_id,
                    "trace_id": req_trace_id,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
        
        logger.info(f"Exported {len(events)} audit events", extra={
            'request_id': req_id,
            'trace_id': req_trace_id,
            'event_count': len(events),
            'format': format
        })
        
        # Return JSON format (CSV conversion can be added later)
        if format == "json":
            return JSONResponse(
                status_code=200,
                content={
                    'events': events,
                    'count': len(events),
                    'exported_at': datetime.now(timezone.utc).isoformat()
                }
            )
        else:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "UNSUPPORTED_FORMAT",
                    "message": f"Unsupported export format: {format}",
                    "severity": "error",
                    "retryable": False,
                    "request_id": req_id,
                    "trace_id": req_trace_id,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to export audit events: {str(e)}", extra={
            'request_id': req_id,
            'trace_id': req_trace_id,
            'error': str(e)
        })
        raise HTTPException(
            status_code=500,
            detail={
                "code": "INTERNAL_ERROR",
                "message": f"Failed to export audit events: {str(e)}",
                "severity": "error",
                "retryable": True,
                "request_id": req_id,
                "trace_id": req_trace_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )
