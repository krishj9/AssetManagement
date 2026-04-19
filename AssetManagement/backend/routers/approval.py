"""
Approval Router

This module provides endpoints for approval workflow operations.
"""

from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
from typing import Optional
import logging
import uuid

from AssetManagement.backend.persistence.dynamodb_client import DynamoDBClient
from AssetManagement.backend.persistence.approval_artifacts_repository import ApprovalArtifactsRepository
from AssetManagement.backend.persistence.audit_events_repository import AuditEventsRepository
from AssetManagement.schemas.approval_artifact import ApprovalArtifact

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize clients (in production, use dependency injection)
dynamodb_client = DynamoDBClient()
approval_repo = ApprovalArtifactsRepository(dynamodb_client)
audit_repo = AuditEventsRepository(dynamodb_client)


@router.post("/artifacts")
async def create_approval_artifact(request: Request, artifact_data: dict):
    """
    Create a new approval artifact.
    
    This endpoint is called by the supervisor agent after consolidating
    collaborator outputs into a recommendation package.
    """
    request_id = request.state.request_id
    trace_id = request.state.trace_id
    
    try:
        logger.info("Creating approval artifact", extra={
            'request_id': request_id,
            'trace_id': trace_id
        })
        
        # Validate workflow state
        workflow_state = artifact_data.get('workflow_state', 'NORMAL')
        if workflow_state == 'BLOCKED':
            logger.warning("Attempted to create approval artifact in BLOCKED state", extra={
                'request_id': request_id,
                'trace_id': trace_id,
                'workflow_state': workflow_state
            })
        
        # Create approval artifact
        approval = approval_repo.create_approval_artifact(
            request_id=artifact_data['request_id'],
            trace_id=artifact_data['trace_id'],
            agent_version=artifact_data.get('agent_version', '1.0.0'),
            schema_version=artifact_data.get('schema_version', '1.0.0'),
            policy_version=artifact_data.get('policy_version', '1.0.0'),
            trade_proposals=artifact_data.get('trade_proposals', []),
            compliance_verdict=artifact_data.get('compliance_verdict', {}),
            rationale=artifact_data.get('rationale', ''),
            evidence=artifact_data.get('evidence', []),
            memory_summary=artifact_data.get('memory_summary', {}),
            workflow_state=workflow_state,
            approval_status='PENDING'
        )
        
        # Log audit event
        audit_repo.create_audit_event(
            event_type='APPROVAL_ACTION',
            action_details={
                'action': 'created',
                'approval_id': approval['approval_id'],
                'workflow_state': workflow_state
            },
            outcome='success',
            environment_alias='dev',
            request_id=artifact_data['request_id'],
            trace_id=artifact_data['trace_id'],
            session_id=artifact_data.get('session_id', ''),
            agent_identity='approval_service',
            agent_version='1.0.0',
            policy_version=artifact_data.get('policy_version', '1.0.0')
        )
        
        logger.info(f"Created approval artifact: {approval['approval_id']}", extra={
            'request_id': request_id,
            'trace_id': trace_id,
            'approval_id': approval['approval_id']
        })
        
        return JSONResponse(
            status_code=201,
            content=approval
        )
        
    except KeyError as e:
        logger.error(f"Missing required field: {str(e)}", extra={
            'request_id': request_id,
            'trace_id': trace_id,
            'error': str(e)
        })
        raise HTTPException(
            status_code=400,
            detail={
                "code": "MISSING_FIELD",
                "message": f"Missing required field: {str(e)}",
                "severity": "error",
                "retryable": False,
                "request_id": request_id,
                "trace_id": trace_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )
    except Exception as e:
        logger.error(f"Failed to create approval artifact: {str(e)}", extra={
            'request_id': request_id,
            'trace_id': trace_id,
            'error': str(e)
        })
        raise HTTPException(
            status_code=500,
            detail={
                "code": "INTERNAL_ERROR",
                "message": f"Failed to create approval artifact: {str(e)}",
                "severity": "error",
                "retryable": True,
                "request_id": request_id,
                "trace_id": trace_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )


@router.get("/artifacts/{approval_id}")
async def get_approval_artifact(approval_id: str, request: Request):
    """
    Get approval artifact by ID.
    
    Args:
        approval_id: Approval artifact ID
    """
    request_id = request.state.request_id
    trace_id = request.state.trace_id
    
    try:
        logger.info(f"Retrieving approval artifact: {approval_id}", extra={
            'request_id': request_id,
            'trace_id': trace_id,
            'approval_id': approval_id
        })
        
        # Get approval artifact
        approval = approval_repo.get_approval_artifact_by_id(approval_id)
        
        if not approval:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "NOT_FOUND",
                    "message": f"Approval artifact not found: {approval_id}",
                    "severity": "error",
                    "retryable": False,
                    "request_id": request_id,
                    "trace_id": trace_id,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
        
        logger.info(f"Retrieved approval artifact: {approval_id}", extra={
            'request_id': request_id,
            'trace_id': trace_id,
            'approval_id': approval_id,
            'approval_status': approval.get('approval_status')
        })
        
        return JSONResponse(
            status_code=200,
            content=approval
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve approval artifact: {str(e)}", extra={
            'request_id': request_id,
            'trace_id': trace_id,
            'approval_id': approval_id,
            'error': str(e)
        })
        raise HTTPException(
            status_code=500,
            detail={
                "code": "INTERNAL_ERROR",
                "message": f"Failed to retrieve approval artifact: {str(e)}",
                "severity": "error",
                "retryable": True,
                "request_id": request_id,
                "trace_id": trace_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )


@router.put("/artifacts/{approval_id}/approve")
async def approve_artifact(approval_id: str, request: Request, approval_data: dict):
    """
    Approve an approval artifact.
    
    Args:
        approval_id: Approval artifact ID
    """
    request_id = request.state.request_id
    trace_id = request.state.trace_id
    
    try:
        logger.info(f"Approving artifact: {approval_id}", extra={
            'request_id': request_id,
            'trace_id': trace_id,
            'approval_id': approval_id
        })
        
        # Get current artifact to validate workflow state
        artifact = approval_repo.get_approval_artifact_by_id(approval_id)
        
        if not artifact:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "NOT_FOUND",
                    "message": f"Approval artifact not found: {approval_id}",
                    "severity": "error",
                    "retryable": False,
                    "request_id": request_id,
                    "trace_id": trace_id,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
        
        # Validate workflow state
        workflow_state = artifact.get('workflow_state', 'NORMAL')
        if workflow_state == 'BLOCKED':
            logger.warning(f"Cannot approve blocked recommendation: {approval_id}", extra={
                'request_id': request_id,
                'trace_id': trace_id,
                'approval_id': approval_id,
                'workflow_state': workflow_state
            })
            raise HTTPException(
                status_code=403,
                detail={
                    "code": "BLOCKED_STATE",
                    "message": "Cannot approve recommendation in BLOCKED state",
                    "severity": "error",
                    "retryable": False,
                    "request_id": request_id,
                    "trace_id": trace_id,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
        
        # Validate compliance verdict
        compliance_verdict = artifact.get('compliance_verdict', {})
        verdict = compliance_verdict.get('verdict', 'UNRESOLVED')
        if verdict in ['NON_COMPLIANT', 'UNRESOLVED']:
            logger.warning(f"Cannot approve with compliance verdict {verdict}: {approval_id}", extra={
                'request_id': request_id,
                'trace_id': trace_id,
                'approval_id': approval_id,
                'compliance_verdict': verdict
            })
            raise HTTPException(
                status_code=403,
                detail={
                    "code": "COMPLIANCE_VIOLATION",
                    "message": f"Cannot approve with compliance verdict: {verdict}",
                    "severity": "error",
                    "retryable": False,
                    "request_id": request_id,
                    "trace_id": trace_id,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
        
        # Update approval status with conditional write
        approved_by = approval_data.get('approved_by', 'unknown')
        approved_at = datetime.now(timezone.utc).isoformat()
        
        updated = approval_repo.update_approval_status(
            approval_id=approval_id,
            approval_status='APPROVED',
            approved_by=approved_by,
            approved_at=approved_at
        )
        
        # Log audit event
        audit_repo.create_audit_event(
            event_type='APPROVAL_ACTION',
            action_details={
                'action': 'approved',
                'approval_id': approval_id,
                'approved_by': approved_by
            },
            outcome='success',
            environment_alias='dev',
            request_id=artifact.get('request_id', request_id),
            trace_id=artifact.get('trace_id', trace_id),
            session_id=approval_data.get('session_id', ''),
            agent_identity='approval_service',
            agent_version='1.0.0',
            policy_version=artifact.get('policy_version', '1.0.0'),
            actor_identity=approved_by,
            actor_role='approver'
        )
        
        logger.info(f"Approved artifact: {approval_id}", extra={
            'request_id': request_id,
            'trace_id': trace_id,
            'approval_id': approval_id,
            'approved_by': approved_by
        })
        
        return JSONResponse(
            status_code=200,
            content=updated
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to approve artifact: {str(e)}", extra={
            'request_id': request_id,
            'trace_id': trace_id,
            'approval_id': approval_id,
            'error': str(e)
        })
        raise HTTPException(
            status_code=500,
            detail={
                "code": "INTERNAL_ERROR",
                "message": f"Failed to approve artifact: {str(e)}",
                "severity": "error",
                "retryable": True,
                "request_id": request_id,
                "trace_id": trace_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )


@router.put("/artifacts/{approval_id}/reject")
async def reject_artifact(approval_id: str, request: Request, rejection_data: dict):
    """
    Reject an approval artifact.
    
    Args:
        approval_id: Approval artifact ID
    """
    request_id = request.state.request_id
    trace_id = request.state.trace_id
    
    try:
        logger.info(f"Rejecting artifact: {approval_id}", extra={
            'request_id': request_id,
            'trace_id': trace_id,
            'approval_id': approval_id
        })
        
        # Get current artifact
        artifact = approval_repo.get_approval_artifact_by_id(approval_id)
        
        if not artifact:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "NOT_FOUND",
                    "message": f"Approval artifact not found: {approval_id}",
                    "severity": "error",
                    "retryable": False,
                    "request_id": request_id,
                    "trace_id": trace_id,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
        
        # Update approval status with conditional write
        rejected_by = rejection_data.get('rejected_by', 'unknown')
        rejected_at = datetime.now(timezone.utc).isoformat()
        rejection_note = rejection_data.get('rejection_note', '')
        
        updated = approval_repo.update_approval_status(
            approval_id=approval_id,
            approval_status='REJECTED',
            approved_by=rejected_by,
            approved_at=rejected_at
        )
        
        # Log audit event
        audit_repo.create_audit_event(
            event_type='APPROVAL_ACTION',
            action_details={
                'action': 'rejected',
                'approval_id': approval_id,
                'rejected_by': rejected_by,
                'rejection_note': rejection_note
            },
            outcome='success',
            environment_alias='dev',
            request_id=artifact.get('request_id', request_id),
            trace_id=artifact.get('trace_id', trace_id),
            session_id=rejection_data.get('session_id', ''),
            agent_identity='approval_service',
            agent_version='1.0.0',
            policy_version=artifact.get('policy_version', '1.0.0'),
            actor_identity=rejected_by,
            actor_role='approver'
        )
        
        logger.info(f"Rejected artifact: {approval_id}", extra={
            'request_id': request_id,
            'trace_id': trace_id,
            'approval_id': approval_id,
            'rejected_by': rejected_by
        })
        
        return JSONResponse(
            status_code=200,
            content=updated
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to reject artifact: {str(e)}", extra={
            'request_id': request_id,
            'trace_id': trace_id,
            'approval_id': approval_id,
            'error': str(e)
        })
        raise HTTPException(
            status_code=500,
            detail={
                "code": "INTERNAL_ERROR",
                "message": f"Failed to reject artifact: {str(e)}",
                "severity": "error",
                "retryable": True,
                "request_id": request_id,
                "trace_id": trace_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )
