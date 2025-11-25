from typing import Dict, Any
import json
from services.redis_service import redis_service
from workflows.state import WorkflowState
from datetime import datetime

class StateManager:
    """Manage workflow state persistence in Redis"""
    
    @staticmethod
    async def save_state(workflow_id: str, state: WorkflowState):
        """Save workflow state to Redis"""
        # Convert datetime objects to strings
        state_copy = state.copy()
        if 'started_at' in state_copy and isinstance(state_copy['started_at'], datetime):
            state_copy['started_at'] = state_copy['started_at'].isoformat()
        if 'updated_at' in state_copy and isinstance(state_copy['updated_at'], datetime):
            state_copy['updated_at'] = state_copy['updated_at'].isoformat()
        
        await redis_service.set(
            f"workflow:state:{workflow_id}",
            state_copy,
            ttl=86400 * 7  # 7 days
        )
    
    @staticmethod
    async def load_state(workflow_id: str) -> WorkflowState:
        """Load workflow state from Redis"""
        state = await redis_service.get(f"workflow:state:{workflow_id}")
        
        if not state:
            raise ValueError(f"Workflow state not found: {workflow_id}")
        
        # Convert string dates back to datetime
        if 'started_at' in state and isinstance(state['started_at'], str):
            state['started_at'] = datetime.fromisoformat(state['started_at'])
        if 'updated_at' in state and isinstance(state['updated_at'], str):
            state['updated_at'] = datetime.fromisoformat(state['updated_at'])
        
        return state
    
    @staticmethod
    async def delete_state(workflow_id: str):
        """Delete workflow state"""
        await redis_service.delete(f"workflow:state:{workflow_id}")
    
    @staticmethod
    async def create_checkpoint(workflow_id: str, checkpoint_name: str, state: WorkflowState):
        """Create a named checkpoint"""
        await redis_service.set(
            f"workflow:checkpoint:{workflow_id}:{checkpoint_name}",
            state,
            ttl=86400 * 7
        )
    
    @staticmethod
    async def restore_checkpoint(workflow_id: str, checkpoint_name: str) -> WorkflowState:
        """Restore from a checkpoint"""
        state = await redis_service.get(f"workflow:checkpoint:{workflow_id}:{checkpoint_name}")
        
        if not state:
            raise ValueError(f"Checkpoint not found: {checkpoint_name}")
        
        return state
    
    @staticmethod
    async def list_workflows(status: str = None) -> list[str]:
        """List all workflow IDs (simplified - in production use Redis SCAN)"""
        # This is a simplified version
        # In production, maintain a separate index
        return []

# Singleton
state_manager = StateManager()
