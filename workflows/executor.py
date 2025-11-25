from typing import Optional
from datetime import datetime
import uuid
from workflows.verification_workflow import verification_workflow
from workflows.state import WorkflowState
from workflows.state_manager import state_manager
from services.observability import observability_service

class WorkflowExecutor:
    """Execute and manage workflows"""
    
    @staticmethod
    async def start_workflow(raw_item: dict) -> str:
        """
        Start a new verification workflow
        
        Args:
            raw_item: Raw item data
            
        Returns:
            Workflow ID
        """
        workflow_id = str(uuid.uuid4())
        
        # Initialize state
        initial_state: WorkflowState = {
            'workflow_id': workflow_id,
            'raw_item_id': raw_item.get('id'),
            'raw_item': raw_item,
            'normalized_item': None,
            'entities': [],
            'claims': [],
            'topics': [],
            'evidence': [],
            'veracity_scores': {},
            'risk_score': 0.0,
            'needs_human_review': False,
            'errors': [],
            'retry_count': 0,
            'started_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'status': 'running'
        }
        
        # Save initial state
        await state_manager.save_state(workflow_id, initial_state)
        
        observability_service.log_info(f"Started workflow {workflow_id}")
        
        # Execute workflow
        try:
            final_state = await verification_workflow.ainvoke(initial_state)
            
            # Save final state
            await state_manager.save_state(workflow_id, final_state)
            
            observability_service.log_info(f"Workflow {workflow_id} completed")
            
        except Exception as e:
            observability_service.log_error(f"Workflow {workflow_id} failed: {e}")
            initial_state['status'] = 'failed'
            initial_state['errors'].append(str(e))
            await state_manager.save_state(workflow_id, initial_state)
        
        return workflow_id
    
    @staticmethod
    async def resume_workflow(workflow_id: str, human_decision: Optional[str] = None):
        """
        Resume a paused workflow
        
        Args:
            workflow_id: Workflow ID
            human_decision: Human review decision ('approved' or 'rejected')
        """
        # Load state
        state = await state_manager.load_state(workflow_id)
        
        if state['status'] != 'paused':
            raise ValueError(f"Workflow {workflow_id} is not paused")
        
        # Update human review status
        if human_decision:
            state['human_review_status'] = human_decision
        
        state['status'] = 'running'
        state['updated_at'] = datetime.utcnow()
        
        # Continue execution
        try:
            # In LangGraph, we'd use streaming or continue from checkpoint
            # For simplicity, we'll re-execute from current state
            final_state = await verification_workflow.ainvoke(state)
            
            await state_manager.save_state(workflow_id, final_state)
            
            observability_service.log_info(f"Workflow {workflow_id} resumed and completed")
            
        except Exception as e:
            observability_service.log_error(f"Workflow {workflow_id} resume failed: {e}")
            state['status'] = 'failed'
            state['errors'].append(str(e))
            await state_manager.save_state(workflow_id, state)
    
    @staticmethod
    async def get_workflow_status(workflow_id: str) -> dict:
        """Get workflow status"""
        state = await state_manager.load_state(workflow_id)
        
        return {
            'workflow_id': workflow_id,
            'status': state['status'],
            'risk_score': state.get('risk_score'),
            'needs_human_review': state.get('needs_human_review'),
            'human_review_status': state.get('human_review_status'),
            'errors': state.get('errors', []),
            'started_at': state['started_at'],
            'updated_at': state['updated_at']
        }
    
    @staticmethod
    async def cancel_workflow(workflow_id: str):
        """Cancel a workflow"""
        state = await state_manager.load_state(workflow_id)
        
        state['status'] = 'cancelled'
        state['updated_at'] = datetime.utcnow()
        
        await state_manager.save_state(workflow_id, state)
        
        observability_service.log_info(f"Workflow {workflow_id} cancelled")

# Singleton
workflow_executor = WorkflowExecutor()
