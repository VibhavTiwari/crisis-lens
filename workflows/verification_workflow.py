from langgraph.graph import StateGraph, END
from typing import Dict, Any
from datetime import datetime
import uuid

from workflows.state import WorkflowState
from workflows.state_manager import state_manager
from services.observability import observability_service

# Import agents
from agents.ingestion.normalization import NormalizationService
from agents.digestion.entity_extraction import EntityExtractionAgent
from agents.digestion.claim_extraction import ClaimExtractionAgent
from agents.digestion.topic_assignment import TopicAssignmentAgent
from agents.digestion.evidence_retrieval import EvidenceRetrievalAgent
from agents.digestion.nli_veracity import NliVeracityAgent
from agents.scoring.risk_scoring import RiskScoringAgent
from agents.publishing.advisory_drafting import AdvisoryDraftingAgent
from agents.publishing.translation import AdvisoryTranslationAgent

# Initialize services/agents
normalization_service = NormalizationService()
entity_agent = EntityExtractionAgent()
claim_agent = ClaimExtractionAgent()
topic_agent = TopicAssignmentAgent()
evidence_agent = EvidenceRetrievalAgent()
nli_agent = NliVeracityAgent()
risk_agent = RiskScoringAgent()
advisory_agent = AdvisoryDraftingAgent()
translation_agent = AdvisoryTranslationAgent()

# Node functions
async def normalize_node(state: WorkflowState) -> WorkflowState:
    """Normalize the raw item"""
    observability_service.log_info(f"Normalizing item {state['raw_item_id']}")
    
    try:
        from schemas.item import RawItem, NormalizedItem
        
        # Convert dict to RawItem
        raw_item_obj = RawItem(**state['raw_item'])
        
        # Normalize
        normalized = await normalization_service.normalize(raw_item_obj)
        
        state['normalized_item'] = normalized.dict()
        state['language_detected'] = normalized.language_detected
        state['updated_at'] = datetime.utcnow()
        
    except Exception as e:
        observability_service.log_error(f"Normalization failed: {e}")
        state['errors'].append(f"Normalization: {str(e)}")
    
    return state

async def extract_entities_node(state: WorkflowState) -> WorkflowState:
    """Extract entities from normalized item"""
    observability_service.log_info("Extracting entities")
    
    try:
        from schemas.item import NormalizedItem
        
        normalized_obj = NormalizedItem(**state['normalized_item'])
        result = await entity_agent.run(normalized_obj)
        
        state['entities'] = result.entities
        state['updated_at'] = datetime.utcnow()
        
    except Exception as e:
        observability_service.log_error(f"Entity extraction failed: {e}")
        state['errors'].append(f"Entities: {str(e)}")
    
    return state

async def extract_claims_node(state: WorkflowState) -> WorkflowState:
    """Extract claims from normalized item"""
    observability_service.log_info("Extracting claims")
    
    try:
        from schemas.item import NormalizedItem
        
        normalized_obj = NormalizedItem(**state['normalized_item'])
        claims = await claim_agent.run(normalized_obj)
        
        state['claims'] = [c.dict() for c in claims]
        state['updated_at'] = datetime.utcnow()
        
    except Exception as e:
        observability_service.log_error(f"Claim extraction failed: {e}")
        state['errors'].append(f"Claims: {str(e)}")
    
    return state

async def assign_topics_node(state: WorkflowState) -> WorkflowState:
    """Assign topics to item"""
    observability_service.log_info("Assigning topics")
    
    try:
        from schemas.item import NormalizedItem
        
        normalized_obj = NormalizedItem(**state['normalized_item'])
        result = await topic_agent.run(normalized_obj)
        
        state['topics'] = result.topics
        state['updated_at'] = datetime.utcnow()
        
    except Exception as e:
        observability_service.log_error(f"Topic assignment failed: {e}")
        state['errors'].append(f"Topics: {str(e)}")
    
    return state

async def retrieve_evidence_node(state: WorkflowState) -> WorkflowState:
    """Retrieve evidence for claims"""
    observability_service.log_info("Retrieving evidence")
    
    try:
        from schemas.claim import Claim
        
        all_evidence = []
        
        for claim_data in state.get('claims', []):
            claim_obj = Claim(**claim_data)
            result = await evidence_agent.run(claim_obj)
            all_evidence.extend([e.dict() for e in result.evidence])
        
        state['evidence'] = all_evidence
        state['updated_at'] = datetime.utcnow()
        
    except Exception as e:
        observability_service.log_error(f"Evidence retrieval failed: {e}")
        state['errors'].append(f"Evidence: {str(e)}")
    
    return state

async def assess_veracity_node(state: WorkflowState) -> WorkflowState:
    """Assess veracity using NLI"""
    observability_service.log_info("Assessing veracity")
    
    try:
        from schemas.claim import Claim
        
        veracity_scores = {}
        
        for claim_data in state.get('claims', []):
            claim_obj = Claim(**claim_data)
            result = await nli_agent.run(claim_obj)
            veracity_scores[claim_obj.id] = result.veracity_likelihood
        
        state['veracity_scores'] = veracity_scores
        state['updated_at'] = datetime.utcnow()
        
    except Exception as e:
        observability_service.log_error(f"Veracity assessment failed: {e}")
        state['errors'].append(f"Veracity: {str(e)}")
    
    return state

async def calculate_risk_node(state: WorkflowState) -> WorkflowState:
    """Calculate risk score"""
    observability_service.log_info("Calculating risk")
    
    try:
        from schemas.item import NormalizedItem
        
        normalized_obj = NormalizedItem(**state['normalized_item'])
        result = await risk_agent.run(normalized_obj)
        
        state['risk_score'] = result.risk_score
        state['updated_at'] = datetime.utcnow()
        
    except Exception as e:
        observability_service.log_error(f"Risk calculation failed: {e}")
        state['errors'].append(f"Risk: {str(e)}")
        state['risk_score'] = 0.5  # Default
    
    return state

async def check_human_review_needed(state: WorkflowState) -> str:
    """Determine if human review is needed"""
    risk_score = state.get('risk_score', 0)
    
    # High risk items need human review
    if risk_score > 0.7:
        state['needs_human_review'] = True
        state['human_review_status'] = 'pending'
        return 'human_review'
    else:
        state['needs_human_review'] = False
        return 'draft_advisory'

async def human_review_node(state: WorkflowState) -> WorkflowState:
    """Pause for human review"""
    observability_service.log_info("Waiting for human review")
    
    state['status'] = 'paused'
    state['updated_at'] = datetime.utcnow()
    
    # Save state and wait for external input
    await state_manager.save_state(state['workflow_id'], state)
    
    # In a real system, this would send a notification
    # and the workflow would resume when a reviewer approves/rejects
    
    return state

async def draft_advisory_node(state: WorkflowState) -> WorkflowState:
    """Draft advisory"""
    observability_service.log_info("Drafting advisory")
    
    try:
        from schemas.item import NormalizedItem
        
        normalized_obj = NormalizedItem(**state['normalized_item'])
        advisory = await advisory_agent.run(normalized_obj)
        
        state['advisory_draft'] = advisory.dict()
        state['updated_at'] = datetime.utcnow()
        
    except Exception as e:
        observability_service.log_error(f"Advisory drafting failed: {e}")
        state['errors'].append(f"Advisory: {str(e)}")
    
    return state

async def translate_advisory_node(state: WorkflowState) -> WorkflowState:
    """Translate advisory"""
    observability_service.log_info("Translating advisory")
    
    try:
        from schemas.advisory import Advisory
        
        if state.get('advisory_draft'):
            advisory_obj = Advisory(**state['advisory_draft'])
            result = await translation_agent.run(advisory_obj)
            
            state['advisory_translations'] = result.translations
            state['updated_at'] = datetime.utcnow()
        
    except Exception as e:
        observability_service.log_error(f"Translation failed: {e}")
        state['errors'].append(f"Translation: {str(e)}")
    
    return state

async def complete_workflow_node(state: WorkflowState) -> WorkflowState:
    """Complete the workflow"""
    observability_service.log_info(f"Completing workflow {state['workflow_id']}")
    
    state['status'] = 'completed'
    state['updated_at'] = datetime.utcnow()
    
    await state_manager.save_state(state['workflow_id'], state)
    
    return state

# Build the graph
def create_verification_workflow() -> StateGraph:
    """Create the verification workflow graph"""
    
    workflow = StateGraph(WorkflowState)
    
    # Add nodes
    workflow.add_node("normalize", normalize_node)
    workflow.add_node("extract_entities", extract_entities_node)
    workflow.add_node("extract_claims", extract_claims_node)
    workflow.add_node("assign_topics", assign_topics_node)
    workflow.add_node("retrieve_evidence", retrieve_evidence_node)
    workflow.add_node("assess_veracity", assess_veracity_node)
    workflow.add_node("calculate_risk", calculate_risk_node)
    workflow.add_node("human_review", human_review_node)
    workflow.add_node("draft_advisory", draft_advisory_node)
    workflow.add_node("translate_advisory", translate_advisory_node)
    workflow.add_node("complete", complete_workflow_node)
    
    # Set entry point
    workflow.set_entry_point("normalize")
    
    # Add edges (sequential flow)
    workflow.add_edge("normalize", "extract_entities")
    workflow.add_edge("extract_entities", "extract_claims")
    workflow.add_edge("extract_claims", "assign_topics")
    workflow.add_edge("assign_topics", "retrieve_evidence")
    workflow.add_edge("retrieve_evidence", "assess_veracity")
    workflow.add_edge("assess_veracity", "calculate_risk")
    
    # Conditional routing after risk calculation
    workflow.add_conditional_edges(
        "calculate_risk",
        check_human_review_needed,
        {
            "human_review": "human_review",
            "draft_advisory": "draft_advisory"
        }
    )
    
    # Human review can lead to advisory or end
    workflow.add_edge("human_review", "draft_advisory")
    
    # Continue to translation and completion
    workflow.add_edge("draft_advisory", "translate_advisory")
    workflow.add_edge("translate_advisory", "complete")
    workflow.add_edge("complete", END)
    
    return workflow.compile()

# Singleton compiled workflow
verification_workflow = create_verification_workflow()
