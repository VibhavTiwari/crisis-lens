import requests
from typing import List, Dict, Any, Optional
from PIL import Image
from io import BytesIO
import hashlib
from services.observability import observability_service
from config import settings

class ReverseImageSearch:
    """Reverse image search using real APIs"""
    
    @staticmethod
    def search_tineye(image_url: str) -> List[Dict[str, Any]]:
        """
        Search TinEye API for similar images
        """
        api_key = getattr(settings, 'TINEYE_API_KEY', None)
        if not api_key or api_key.startswith('dummy'):
            return []
            
        try:
            # Real TinEye API call
            response = requests.get(
                'https://api.tineye.com/rest/search/',
                params={
                    'image_url': image_url,
                    'api_key': api_key,
                    'limit': 10
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return [
                    {
                        'url': match['backlinks'][0]['url'] if match['backlinks'] else match['image_url'],
                        'score': match['score'],
                        'source': 'tineye'
                    }
                    for match in data.get('matches', [])
                ]
        except Exception as e:
            observability_service.log_error(f"TinEye search failed: {e}")
            
        return []
    
    @staticmethod
    def search_google_images(image_url: str) -> List[Dict[str, Any]]:
        """
        Search Google Custom Search API (CSE)
        Requires CSE ID configured with 'Image search' enabled
        """
        api_key = getattr(settings, 'GOOGLE_SEARCH_API_KEY', None)
        cse_id = getattr(settings, 'GOOGLE_CSE_ID', None)
        
        if not api_key or not cse_id or api_key.startswith('dummy'):
            return []
            
        try:
            # Real Google CSE API call
            response = requests.get(
                'https://www.googleapis.com/customsearch/v1',
                params={
                    'key': api_key,
                    'cx': cse_id,
                    'searchType': 'image',
                    'q': image_url,  # Searching by URL as query often finds the image
                    'num': 5
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return [
                    {
                        'url': item['link'],
                        'title': item['title'],
                        'context_link': item['image']['contextLink'],
                        'source': 'google'
                    }
                    for item in data.get('items', [])
                ]
        except Exception as e:
            observability_service.log_error(f"Google Image search failed: {e}")
            
        return []
    
    @staticmethod
    def calculate_image_hash(image_path_or_url: str) -> str:
        """Calculate perceptual hash of image"""
        import imagehash
        
        try:
            if image_path_or_url.startswith(('http://', 'https://')):
                response = requests.get(image_path_or_url, timeout=10)
                image = Image.open(BytesIO(response.content))
            else:
                image = Image.open(image_path_or_url)
            
            # Calculate average hash
            avg_hash = str(imagehash.average_hash(image))
            return avg_hash
            
        except Exception as e:
            observability_service.log_error(f"Image hash calculation failed: {e}")
            return ""
    
    @staticmethod
    def comprehensive_search(image_url: str) -> Dict[str, Any]:
        """Search multiple sources for an image"""
        
        tineye_results = ReverseImageSearch.search_tineye(image_url)
        google_results = ReverseImageSearch.search_google_images(image_url)
        
        return {
            'image_url': image_url,
            'image_hash': ReverseImageSearch.calculate_image_hash(image_url),
            'tineye_results': tineye_results,
            'google_results': google_results,
            'found_elsewhere': (len(tineye_results) + len(google_results)) > 0,
            'match_count': len(tineye_results) + len(google_results)
        }

# Singleton
reverse_image_search = ReverseImageSearch()
