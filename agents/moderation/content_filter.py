"""
Content Moderation Agent

Filters harmful, inappropriate, or policy-violating content using:
- Keyword filtering
- ML-based classification
- External moderation APIs (Perspective API)
- Human review queue
"""
from typing import Dict, Any, List, Optional
from enum import Enum
import re
import logging

logger = logging.getLogger(__name__)


class ModerationCategory(Enum):
    """Content moderation categories."""
    SAFE = "safe"
    SPAM = "spam"
    HATE_SPEECH = "hate_speech"
    VIOLENCE = "violence"
    SEXUAL_CONTENT = "sexual_content"
    HARASSMENT = "harassment"
    MISINFORMATION = "misinformation"
    REQUIRES_REVIEW = "requires_review"


class ContentModerator:
    """Main content moderation service."""
    
    def __init__(self):
        self.keyword_filter = KeywordFilter()
        self.ml_classifier = MLContentClassifier()
        self.external_api = PerspectiveAPIClient()
    
    async def moderate_content(
        self,
        content: str,
        content_type: str = "text"
    ) -> Dict[str, Any]:
        """
        Moderate content through multiple checks.
        
        Returns:
            {
                'category': ModerationCategory,
                'confidence': float,
                'flags': List[str],
                'should_block': bool,
                'requires_human_review': bool
            }
        """
        logger.info(f"Moderating content: {content[:50]}...")
        
        results = {
            'category': ModerationCategory.SAFE,
            'confidence': 0.0,
            'flags': [],
            'should_block': False,
            'requires_human_review': False,
            'scores': {}
        }
        
        # 1. Keyword filtering (fast, deterministic)
        keyword_result = self.keyword_filter.check(content)
        if keyword_result['flagged']:
            results['flags'].extend(keyword_result['matched_keywords'])
            results['should_block'] = keyword_result['block']
            results['category'] = keyword_result['category']
        
        # 2. ML classification
        if not results['should_block']:
            ml_result = await self.ml_classifier.classify(content)
            results['scores'].update(ml_result['scores'])
            
            # Check thresholds
            for category, score in ml_result['scores'].items():
                if score > 0.8:  # High confidence harmful
                    results['should_block'] = True
                    results['category'] = ModerationCategory(category)
                elif score > 0.5:  # Uncertain, needs review
                    results['requires_human_review'] = True
        
        # 3. External API (Perspective API for toxicity)
        if not results['should_block'] and content_type == "text":
            external_result = await self.external_api.analyze(content)
            results['scores']['toxicity'] = external_result.get('TOXICITY', 0.0)
            
            if external_result.get('TOXICITY', 0) > 0.9:
                results['should_block'] = True
                results['category'] = ModerationCategory.HATE_SPEECH
        
        # 4. Determine final action
        if results['should_block']:
            results['confidence'] = max(results['scores'].values()) if results['scores'] else 1.0
        elif results['requires_human_review']:
            results['category'] = ModerationCategory.REQUIRES_REVIEW
        
        logger.info(f"Moderation result: {results['category'].value}, block={results['should_block']}")
        
        return results
    
    async def moderate_image(self, image_url: str) -> Dict[str, Any]:
        """Moderate image content."""
        # Use external service like AWS Rekognition, Google Vision API
        # or Clarifai for image moderation
        return {
            'category': ModerationCategory.SAFE,
            'confidence': 0.0,
            'should_block': False
        }


class KeywordFilter:
    """Simple keyword-based filtering."""
    
    def __init__(self):
        self.hate_keywords = self._load_hate_keywords()
        self.spam_patterns = self._load_spam_patterns()
        self.violence_keywords = self._load_violence_keywords()
    
    def check(self, content: str) -> Dict[str, Any]:
        """Check content against keyword lists."""
        content_lower = content.lower()
        result = {
            'flagged': False,
            'block': False,
            'matched_keywords': [],
            'category': ModerationCategory.SAFE
        }
        
        # Check hate speech
        for keyword in self.hate_keywords:
            if keyword in content_lower:
                result['flagged'] = True
                result['block'] = True
                result['matched_keywords'].append(keyword)
                result['category'] = ModerationCategory.HATE_SPEECH
                return result
        
        # Check violence
        for keyword in self.violence_keywords:
            if keyword in content_lower:
                result['flagged'] = True
                result['matched_keywords'].append(keyword)
                result['category'] = ModerationCategory.VIOLENCE
        
        # Check spam patterns
        for pattern in self.spam_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                result['flagged'] = True
                result['matched_keywords'].append('spam_pattern')
                result['category'] = ModerationCategory.SPAM
        
        return result
    
    def _load_hate_keywords(self) -> List[str]:
        """Load hate speech keywords."""
        # In production, load from database or config file
        return [
            # Common hate speech terms (placeholder)
            # Real implementation would have comprehensive list
        ]
    
    def _load_spam_patterns(self) -> List[str]:
        """Load spam regex patterns."""
        return [
            r'click here.{0,20}(?:http|www)',
            r'buy now',
            r'limited time offer',
            r'(?:viagra|cialis)',
        ]
    
    def _load_violence_keywords(self) -> List[str]:
        """Load violence-related keywords."""
        return [
            'graphic violence',
            'gore',
        ]


class MLContentClassifier:
    """ML-based content classification."""
    
    def __init__(self):
        # Load pre-trained model
        # Could be Hugging Face model or custom trained
        self.model = None
    
    async def classify(self, content: str) -> Dict[str, Any]:
        """Classify content using ML model."""
        # Placeholder for ML classification
        # Real implementation would use:
        # - Hugging Face transformers
        # - OpenAI moderation API
        # - Custom trained model
        
        scores = {
            'hate_speech': 0.0,
            'violence': 0.0,
            'spam': 0.0,
            'sexual_content': 0.0
        }
        
        # Simple heuristic for demo
        content_lower = content.lower()
        if 'spam' in content_lower:
            scores['spam'] = 0.7
        
        return {'scores': scores}


class PerspectiveAPIClient:
    """Client for Google Perspective API."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or "YOUR_PERSPECTIVE_API_KEY"
        self.base_url = "https://commentanalyzer.googleapis.com/v1alpha1"
    
    async def analyze(self, text: str) -> Dict[str, float]:
        """Analyze text toxicity using Perspective API."""
        # Placeholder - real implementation would call API
        # import aiohttp
        # async with aiohttp.ClientSession() as session:
        #     payload = {
        #         'comment': {'text': text},
        #         'requestedAttributes': {'TOXICITY': {}}
        #     }
        #     async with session.post(f"{self.base_url}/comments:analyze", json=payload) as resp:
        #         result = await resp.json()
        
        return {
            'TOXICITY': 0.0,
            'SEVERE_TOXICITY': 0.0,
            'IDENTITY_ATTACK': 0.0,
            'INSULT': 0.0,
            'PROFANITY': 0.0,
            'THREAT': 0.0
        }


# Human review queue
class HumanReviewQueue:
    """Queue for content requiring human review."""
    
    def __init__(self, db):
        self.db = db
    
    async def add_to_queue(
        self,
        content_id: str,
        content_type: str,
        content: str,
        moderation_result: Dict[str, Any]
    ):
        """Add content to human review queue."""
        # Store in database for review
        review_item = {
            'content_id': content_id,
            'content_type': content_type,
            'content': content,
            'moderation_scores': moderation_result['scores'],
            'flags': moderation_result['flags'],
            'status': 'pending',
            'created_at': datetime.utcnow()
        }
        # self.db.add(ReviewQueueItem(**review_item))
        # self.db.commit()
    
    async def get_pending_reviews(self, limit: int = 50) -> List[Dict]:
        """Get items pending review."""
        # Query from database
        return []
    
    async def submit_review_decision(
        self,
        content_id: str,
        decision: str,
        reviewer_id: int,
        notes: Optional[str] = None
    ):
        """Submit human review decision."""
        # Update database
        pass


# API Integration
from fastapi import APIRouter, Depends
from pydantic import BaseModel

router = APIRouter(prefix="/moderation", tags=["Moderation"])


class ModerateRequest(BaseModel):
    content: str
    content_type: str = "text"


@router.post("/check")
async def moderate_content(request: ModerateRequest):
    """Check content for policy violations."""
    moderator = ContentModerator()
    result = await moderator.moderate_content(
        request.content,
        request.content_type
    )
    return result


@router.get("/review-queue")
async def get_review_queue(limit: int = 50):
    """Get items in human review queue."""
    # Requires admin/moderator role
    queue = HumanReviewQueue(None)
    items = await queue.get_pending_reviews(limit)
    return {"items": items}
