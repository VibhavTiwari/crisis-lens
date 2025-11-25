import requests
from typing import List, Dict, Any, Optional
from PIL import Image
from io import BytesIO
import hashlib
from services.observability import observability_service
from config import settings

class ReverseImageSearch:
    """Reverse image search using multiple services"""
    
    @staticmethod
    def search_tineye(image_url: str) -> List[Dict[str, Any]]:
        """
        Search TinEye for similar images
        
        Note: Requires TinEye API key (paid service)
        Returns mock results for demo
        """
        # In production, integrate with TinEye API
        # https://services.tineye.com/developers/tineyeapi/
        
        tineye_api_key = getattr(settings, 'TINEYE_API_KEY', None)
        
        if not tineye_api_key or tineye_api_key.startswith('dummy'):
            observability_service.log_warning("TinEye API not configured, returning mock results")
            return []
        
        # Mock implementation
        observability_service.log_info(f"Searching TinEye for: {image_url}")
        return []
    
    @staticmethod
    def search_google_images(image_url: str) -> List[Dict[str, Any]]:
        """
        Search Google Images (simplified)
        
        Note: Google doesn't have a direct reverse image search API
        This is a simplified version using custom search
        """
        # In production, use Google Custom Search API with image search
        # or integrate with SerpAPI for reverse image search
        
        google_api_key = getattr(settings, 'GOOGLE_SEARCH_API_KEY', None)
        
        if not google_api_key or google_api_key.startswith('dummy'):
            observability_service.log_warning("Google Search API not configured")
            return []
        
        observability_service.log_info(f"Searching Google Images for: {image_url}")
        return []
    
    @staticmethod
    def calculate_image_hash(image_path_or_url: str) -> str:
        """Calculate perceptual hash of image"""
        import imagehash
        
        try:
            if image_path_or_url.startswith(('http://', 'https://')):
                response = requests.get(image_path_or_url)
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
    def find_similar_images_local(
        query_hash: str,
        stored_hashes: List[Dict[str, str]],
        threshold: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find similar images in local database using perceptual hashing
        
        Args:
            query_hash: Hash of query image
            stored_hashes: List of {hash, url, metadata} dicts
            threshold: Hamming distance threshold
            
        Returns:
            List of matching images
        """
        import imagehash
        
        matches = []
        query_hash_obj = imagehash.hex_to_hash(query_hash)
        
        for stored in stored_hashes:
            try:
                stored_hash_obj = imagehash.hex_to_hash(stored['hash'])
                distance = query_hash_obj - stored_hash_obj
                
                if distance <= threshold:
                    matches.append({
                        'url': stored['url'],
                        'similarity': 1 - (distance / 64),  # Normalize to 0-1
                        'metadata': stored.get('metadata', {})
                    })
            except:
                continue
        
        # Sort by similarity
        matches.sort(key=lambda x: x['similarity'], reverse=True)
        
        return matches
    
    @staticmethod
    def comprehensive_search(image_url: str) -> Dict[str, Any]:
        """
        Search multiple sources for an image
        
        Returns:
            Dict with results from all sources
        """
        results = {
            'image_url': image_url,
            'image_hash': ReverseImageSearch.calculate_image_hash(image_url),
            'tineye_results': ReverseImageSearch.search_tineye(image_url),
            'google_results': ReverseImageSearch.search_google_images(image_url),
            'found_elsewhere': False
        }
        
        # Determine if image was found on other sites
        total_results = len(results['tineye_results']) + len(results['google_results'])
        results['found_elsewhere'] = total_results > 0
        
        return results

# Singleton
reverse_image_search = ReverseImageSearch()
