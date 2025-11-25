"""
Unit tests for Twitter agent.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from agents.twitter_agent import TwitterAgent


@pytest.mark.unit
class TestTwitterAgent:
    """Test suite for Twitter agent."""
    
    @pytest.fixture
    def agent(self):
        """Create Twitter agent instance."""
        return TwitterAgent(bearer_token="test_token")
    
    def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent is not None
        assert hasattr(agent, 'bearer_token')
    
    @pytest.mark.asyncio
    async def test_fetch_tweets_success(self, agent):
        """Test successful tweet fetching."""
        mock_response = {
            "data": [
                {
                    "id": "123",
                    "text": "Test tweet about crisis",
                    "created_at": "2024-01-01T00:00:00Z"
                }
            ]
        }
        
        with patch.object(agent, '_make_api_request', return_value=mock_response):
            results = await agent.fetch_recent_tweets("crisis")
            
            assert len(results) == 1
            assert results[0]["id"] == "123"
            assert "crisis" in results[0]["text"].lower()
    
    @pytest.mark.asyncio
    async def test_fetch_tweets_empty_result(self, agent):
        """Test handling of empty results."""
        mock_response = {"data": []}
        
        with patch.object(agent, '_make_api_request', return_value=mock_response):
            results = await agent.fetch_recent_tweets("nonexistent")
            assert results == []
    
    @pytest.mark.asyncio
    async def test_fetch_tweets_api_error(self, agent):
        """Test handling of API errors."""
        with patch.object(agent, '_make_api_request', side_effect=Exception("API Error")):
            with pytest.raises(Exception):
                await agent.fetch_recent_tweets("crisis")
    
    def test_normalize_tweet(self, agent):
        """Test tweet normalization."""
        raw_tweet = {
            "id": "123",
            "text": "Crisis in progress",
            "created_at": "2024-01-01T00:00:00Z",
            "author_id": "456"
        }
        
        normalized = agent.normalize_tweet(raw_tweet)
        
        assert normalized["id"] == "twitter_123"
        assert normalized["title"] == "Crisis in progress"
        assert normalized["source"] == "twitter"
        assert "url" in normalized
    
    @pytest.mark.asyncio
    async def test_run_agent_workflow(self, agent, mock_kafka_producer):
        """Test complete agent workflow."""
        with patch.object(agent, 'fetch_recent_tweets') as mock_fetch:
            mock_fetch.return_value = [
                {"id": "1", "text": "Test tweet", "created_at": "2024-01-01T00:00:00Z"}
            ]
            
            with patch('agents.twitter_agent.get_kafka_producer', return_value=mock_kafka_producer):
                await agent.run()
                
                # Verify Kafka producer was called
                assert mock_kafka_producer.send_event.called
