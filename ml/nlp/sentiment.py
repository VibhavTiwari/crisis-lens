from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from typing import Dict, Any, List
from services.observability import observability_service

class SentimentAnalyzer:
    """Sentiment analysis for crisis-related text"""
    
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text
        
        Uses VADER (Valence Aware Dictionary and sEntiment Reasoner)
        Optimized for social media text
        
        Returns:
            Dict with sentiment scores
        """
        scores = self.analyzer.polarity_scores(text)
        
        # Determine overall sentiment
        compound = scores['compound']
        if compound >= 0.05:
            sentiment = 'positive'
        elif compound <= -0.05:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'sentiment': sentiment,
            'compound': compound,
            'positive': scores['pos'],
            'negative': scores['neg'],
            'neutral': scores['neu']
        }
    
    def analyze_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Analyze sentiment for multiple texts"""
        return [self.analyze(text) for text in texts]
    
    def get_emotion_distribution(self, texts: List[str]) -> Dict[str, int]:
        """
        Get distribution of sentiments
        
        Returns:
            Count of positive, negative, neutral
        """
        results = self.analyze_batch(texts)
        
        distribution = {
            'positive': 0,
            'negative': 0,
            'neutral': 0
        }
        
        for result in results:
            distribution[result['sentiment']] += 1
        
        return distribution
    
    def detect_urgency_markers(self, text: str) -> Dict[str, Any]:
        """
        Detect urgency and alarm markers in text
        
        Returns:
            Dict with urgency indicators
        """
        text_lower = text.lower()
        
        # Urgency keywords
        urgency_words = [
            'urgent', 'emergency', 'critical', 'immediate', 'asap',
            'help', 'danger', 'warning', 'alert', 'breaking'
        ]
        
        # Alarm markers
        alarm_words = [
            'fire', 'explosion', 'attack', 'disaster', 'crisis',
            'emergency', 'evacuate', 'danger'
        ]
        
        urgency_count = sum(1 for word in urgency_words if word in text_lower)
        alarm_count = sum(1 for word in alarm_words if word in text_lower)
        
        # Check for exclamation marks (indicator of urgency)
        exclamations = text.count('!')
        
        # Calculate urgency score (0-1)
        urgency_score = min(
            (urgency_count * 0.3 + alarm_count * 0.4 + exclamations * 0.1),
            1.0
        )
        
        return {
            'urgency_score': urgency_score,
            'urgency_words_found': urgency_count,
            'alarm_words_found': alarm_count,
            'exclamation_count': exclamations,
            'is_urgent': urgency_score > 0.5
        }
    
    def analyze_crisis_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Comprehensive sentiment analysis for crisis text
        
        Combines general sentiment with urgency detection
        """
        sentiment = self.analyze(text)
        urgency = self.detect_urgency_markers(text)
        
        return {
            **sentiment,
            'urgency': urgency,
            'requires_attention': (
                urgency['is_urgent'] or
                sentiment['sentiment'] == 'negative'
            )
        }

# Singleton
sentiment_analyzer = SentimentAnalyzer()
