from langgraph.graph import StateGraph, END
from workflows.state import WorkflowState
from typing import List
import asyncio

# Parallel processing nodes
async def process_claims_parallel(state: WorkflowState) -> WorkflowState:
    """Process multiple claims in parallel"""
    from schemas.claim import Claim
    from agents.digestion.evidence_retrieval import EvidenceRetrievalAgent
    from agents.digestion.nli_veracity import NliVeracityAgent
    
    evidence_agent = EvidenceRetrievalAgent()
    nli_agent = NliVeracityAgent()
    
    claims = [Claim(**c) for c in state.get('claims', [])]
    
    # Process all claims concurrently
    tasks = []
    for claim in claims:
        # Create task for evidence + NLI for each claim
        async def process_claim(c):
            # Retrieve evidence
            c_with_evidence = await evidence_agent.run(c)
            # Assess veracity
            c_final = await nli_agent.run(c_with_evidence)
            return c_final
        
        tasks.append(process_claim(claim))
    
    # Wait for all claims to be processed
    processed_claims = await asyncio.gather(*tasks)
    
    # Update state
    state['claims'] = [c.dict() for c in processed_claims]
    
    return state

async def merge_results(states: List[WorkflowState]) -> WorkflowState:
    """Merge results from parallel branches"""
    # Take the first state as base
    merged = states[0].copy()
    
    # Merge claims from all states
    all_claims = []
    for s in states:
        all_claims.extend(s.get('claims', []))
    
    merged['claims'] = all_claims
    
    # Merge errors
    all_errors = []
    for s in states:
        all_errors.extend(s.get('errors', []))
    
    merged['errors'] = all_errors
    
    return merged

def create_parallel_workflow() -> StateGraph:
    """Create a workflow with parallel processing"""
    
    workflow = StateGraph(WorkflowState)
    
    # This is a simplified example
    # In production, you'd use LangGraph's parallel execution features
    
    workflow.add_node("process_parallel", process_claims_parallel)
    workflow.set_entry_point("process_parallel")
    workflow.add_edge("process_parallel", END)
    
    return workflow.compile()
