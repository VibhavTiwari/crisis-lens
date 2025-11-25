import spacy
from typing import List, Dict, Any, Tuple
from services.observability import observability_service

class CoreferenceResolver:
    """
    Coreference resolution to identify pronoun references
    
    Note: neuralcoref is being deprecated, so this uses a simplified approach.
    For production, consider: https://github.com/allenai/allennlp-models#coreference-resolution
    """
    
    def __init__(self):
        self.nlp = None
        self._load_model()
    
    def _load_model(self):
        """Load spaCy model"""
        try:
            self.nlp = spacy.load("en_core_web_sm")
            observability_service.log_info("Loaded spaCy model for coreference")
        except Exception as e:
            observability_service.log_error(f"Failed to load spaCy: {e}")
            self.nlp = None
    
    def resolve_simplified(self, text: str) -> Dict[str, Any]:
        """
        Simplified coreference resolution using spaCy's dependency parsing
        
        Returns:
            Dict with resolved text and coreference chains
        """
        if not self.nlp:
            return {'resolved_text': text, 'chains': []}
        
        doc = self.nlp(text)
        
        # Find pronouns and their potential antecedents
        chains = []
        pronouns = ['he', 'she', 'it', 'they', 'him', 'her', 'them', 'his', 'hers']
        
        for token in doc:
            if token.text.lower() in pronouns:
                # Look for nearest noun in previous tokens
                antecedent = None
                for prev_token in reversed(list(doc[:token.i])):
                    if prev_token.pos_ in ['PROPN', 'NOUN'] and prev_token.dep_ in ['nsubj', 'dobj']:
                        antecedent = prev_token
                        break
                
                if antecedent:
                    chains.append({
                        'pronoun': token.text,
                        'position': token.i,
                        'antecedent': antecedent.text,
                        'antecedent_position': antecedent.i
                    })
        
        # Build resolved text
        resolved_text = text
        for chain in reversed(chains):  # Reverse to maintain positions
            if chain['pronoun'].lower() in ['he', 'she', 'it', 'they']:
                # Replace pronoun with antecedent
                # This is simplified - production would handle case, plurality, etc.
                pass
        
        result = {
            'resolved_text': resolved_text,
            'chains': chains,
            'pronoun_count': len(chains)
        }
        
        return result
    
    def extract_entity_mentions(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract all mentions of entities
        
        Returns:
            List of entity mentions with positions
        """
        if not self.nlp:
            return []
        
        doc = self.nlp(text)
        
        mentions = []
        for ent in doc.ents:
            mentions.append({
                'text': ent.text,
                'label': ent.label_,
                'start': ent.start_char,
                'end': ent.end_char
            })
        
        return mentions
    
    def cluster_mentions(self, mentions: List[Dict[str, Any]]) -> List[List[Dict]]:
        """
        Cluster mentions that refer to the same entity
        
        Simple string matching - production would use embeddings
        """
        clusters = []
        used = set()
        
        for i, mention in enumerate(mentions):
            if i in used:
                continue
            
            cluster = [mention]
            for j, other in enumerate(mentions[i+1:], start=i+1):
                if j in used:
                    continue
                
                # Simple matching
                if mention['text'].lower() == other['text'].lower():
                    cluster.append(other)
                    used.add(j)
            
            clusters.append(cluster)
        
        return clusters

# Singleton
coreference_resolver = CoreferenceResolver()
