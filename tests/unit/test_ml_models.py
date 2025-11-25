"""
Test ML models
Run with: pytest tests/unit/test_ml_models.py
"""
import pytest
from ml.models.embeddings import embeddings_model
from ml.models.bertopic_model import topic_model
from ml.models.nli_model import nli_model
from ml.models.clip_model import clip_model

def test_embeddings():
    """Test sentence embeddings"""
    text = "This is a test sentence for embeddings"
    embedding = embeddings_model.encode_single(text)
    
    assert len(embedding) == 384  # all-MiniLM-L6-v2 dimension
    assert all(isinstance(x, float) for x in embedding)

def test_embeddings_similarity():
    """Test semantic similarity"""
    text1 = "The building is on fire"
    text2 = "Fire in the building"
    text3 = "The cat is sleeping"
    
    sim_high = embeddings_model.similarity(text1, text2)
    sim_low = embeddings_model.similarity(text1, text3)
    
    assert sim_high > sim_low
    assert 0 <= sim_high <= 1
    assert 0 <= sim_low <= 1

def test_bertopic():
    """Test topic modeling"""
    documents = [
        "Floods in Mumbai causing damage",
        "Heavy rains lead to flooding in the city",
        "Fire breaks out in factory",
        "Building catches fire, no casualties"
    ]
    
    topics, probs = topic_model.fit(documents)
    
    assert len(topics) == len(documents)
    assert len(probs) == len(documents)

def test_nli():
    """Test Natural Language Inference"""
    premise = "The building is on fire"
    hypothesis_support = "There is a fire"
    hypothesis_contradict = "The building is safe"
    
    result_support = nli_model.predict(premise, hypothesis_support)
    result_contradict = nli_model.predict(premise, hypothesis_contradict)
    
    assert result_support['label'] in ['entailment', 'neutral']
    assert result_contradict['label'] in ['contradiction', 'neutral']
    
    # Check support scores
    support_score = nli_model.check_veracity(hypothesis_support, premise)
    contradict_score = nli_model.check_veracity(hypothesis_contradict, premise)
    
    assert support_score > contradict_score
    assert -1 <= support_score <= 1
    assert -1 <= contradict_score <= 1

@pytest.mark.skip(reason="Requires GPU or slow on CPU")
def test_clip():
    """Test CLIP multimodal model"""
    # This would require actual image, skipping for now
    pass

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
