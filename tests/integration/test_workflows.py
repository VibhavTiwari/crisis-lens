"""
Test workflows
Run with: pytest tests/integration/test_workflows.py
"""
import pytest
import asyncio
from workflows.executor import workflow_executor
from workflows.state_manager import state_manager
from services.redis_service import redis_service

@pytest.mark.asyncio
async def test_workflow_creation():
    """Test workflow creation"""
    # Connect to Redis
    await redis_service.connect()
    
    # Sample raw item
    raw_item = {
        'id': 'test_item_1',
        'source': 'test',
        'source_id': '123',
        'url': 'http://test.com/item',
        'title': 'Test Crisis Item',
        'text': 'This is a test item for workflow testing',
        'timestamp': '2024-01-01T00:00:00Z',
        'language_hint': 'en'
    }
    
    # Start workflow
    workflow_id = await workflow_executor.start_workflow(raw_item)
    
    assert workflow_id is not None
    assert isinstance(workflow_id, str)
    
    # Wait a bit for workflow to process
    await asyncio.sleep(2)
    
    # Check status
    status = await workflow_executor.get_workflow_status(workflow_id)
    
    assert status['workflow_id'] == workflow_id
    assert status['status'] in ['running', 'completed', 'paused']
    
    await redis_service.disconnect()

@pytest.mark.asyncio
async def test_state_persistence():
    """Test state save and load"""
    await redis_service.connect()
    
    from workflows.state import WorkflowState
    from datetime import datetime
    
    # Create test state
    state: WorkflowState = {
        'workflow_id': 'test_workflow_123',
        'raw_item_id': 'item_123',
        'raw_item': {'id': 'item_123', 'title': 'Test'},
        'status': 'running',
        'errors': [],
        'retry_count': 0,
        'started_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
    
    # Save state
    await state_manager.save_state('test_workflow_123', state)
    
    # Load state
    loaded_state = await state_manager.load_state('test_workflow_123')
    
    assert loaded_state['workflow_id'] == 'test_workflow_123'
    assert loaded_state['status'] == 'running'
    
    # Clean up
    await state_manager.delete_state('test_workflow_123')
    await redis_service.disconnect()

@pytest.mark.asyncio
async def test_checkpoint():
    """Test checkpoint creation and restoration"""
    await redis_service.connect()
    
    from workflows.state import WorkflowState
    from datetime import datetime
    
    state: WorkflowState = {
        'workflow_id': 'test_checkpoint',
        'raw_item_id': 'item_123',
        'raw_item': {},
        'status': 'running',
        'errors': [],
        'retry_count': 0,
        'started_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
    
    # Create checkpoint
    await state_manager.create_checkpoint('test_checkpoint', 'before_review', state)
    
    # Modify state
    state['status'] = 'completed'
    
    # Restore from checkpoint
    restored = await state_manager.restore_checkpoint('test_checkpoint', 'before_review')
    
    assert restored['status'] == 'running'  # Original state
    
    await redis_service.disconnect()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
