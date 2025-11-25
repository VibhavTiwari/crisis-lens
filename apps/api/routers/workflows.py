from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from models.base import get_db
from models.user import User
from apps.api.auth.rbac import get_current_user, require_permission
from workflows.executor import workflow_executor
from services.observability import observability_service

router = APIRouter(prefix="/workflows", tags=["Workflows"])

class WorkflowStart(BaseModel):
    raw_item: dict

class WorkflowResume(BaseModel):
    human_decision: str  # 'approved' or 'rejected'
    feedback: Optional[str] = None

class WorkflowStatus(BaseModel):
    workflow_id: str
    status: str
    risk_score: Optional[float]
    needs_human_review: bool
    human_review_status: Optional[str]
    errors: list[str]
    started_at: str
    updated_at: str

@router.post("/start")
async def start_workflow(
    data: WorkflowStart,
    current_user: User = Depends(require_permission("workflows", "create"))
):
    """Start a new verification workflow"""
    try:
        workflow_id = await workflow_executor.start_workflow(data.raw_item)
        
        return {
            "workflow_id": workflow_id,
            "message": "Workflow started successfully"
        }
        
    except Exception as e:
        observability_service.log_error(f"Failed to start workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{workflow_id}/resume")
async def resume_workflow(
    workflow_id: str,
    data: WorkflowResume,
    current_user: User = Depends(require_permission("workflows", "update"))
):
    """Resume a paused workflow after human review"""
    try:
        await workflow_executor.resume_workflow(workflow_id, data.human_decision)
        
        return {
            "workflow_id": workflow_id,
            "message": "Workflow resumed successfully"
        }
        
    except Exception as e:
        observability_service.log_error(f"Failed to resume workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{workflow_id}/status", response_model=WorkflowStatus)
async def get_workflow_status(
    workflow_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get workflow status"""
    try:
        status = await workflow_executor.get_workflow_status(workflow_id)
        
        return WorkflowStatus(
            workflow_id=status['workflow_id'],
            status=status['status'],
            risk_score=status.get('risk_score'),
            needs_human_review=status.get('needs_human_review', False),
            human_review_status=status.get('human_review_status'),
            errors=status.get('errors', []),
            started_at=status['started_at'].isoformat() if status.get('started_at') else '',
            updated_at=status['updated_at'].isoformat() if status.get('updated_at') else ''
        )
        
    except Exception as e:
        observability_service.log_error(f"Failed to get workflow status: {e}")
        raise HTTPException(status_code=404, detail="Workflow not found")

@router.post("/{workflow_id}/cancel")
async def cancel_workflow(
    workflow_id: str,
    current_user: User = Depends(require_permission("workflows", "delete"))
):
    """Cancel a workflow"""
    try:
        await workflow_executor.cancel_workflow(workflow_id)
        
        return {
            "workflow_id": workflow_id,
            "message": "Workflow cancelled successfully"
        }
        
    except Exception as e:
        observability_service.log_error(f"Failed to cancel workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pending-review")
async def get_pending_reviews(
    current_user: User = Depends(require_permission("workflows", "read"))
):
    """Get workflows pending human review"""
    # In production, maintain an index of workflows by status
    # For now, return empty list
    return {
        "pending_reviews": []
    }
