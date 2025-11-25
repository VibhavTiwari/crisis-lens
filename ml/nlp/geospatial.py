from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from typing import List, Dict, Any, Tuple, Optional
import re
from services.observability import observability_service

class GeospatialAnalyzer:
    """Geospatial analysis and location extraction"""
    
    def __init__(self):
        self.geocoder = Nominatim(user_agent="crisislen")
    
    def extract_locations(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract location mentions from text
        
        Uses spaCy NER for location entities
        """
        import spacy
        
        try:
            nlp = spacy.load("en_core_web_sm")
            doc = nlp(text)
            
            locations = []
            for ent in doc.ents:
                if ent.label_ in ['GPE', 'LOC', 'FAC']:  #Geo-political entity, location, facility
                    locations.append({
                        'text': ent.text,
                        'type': ent.label_,
                        'start': ent.start_char,
                        'end': ent.end_char
                    })
            
            return locations
            
        except Exception as e:
            observability_service.log_error(f"Location extraction failed: {e}")
            return []
    
    def geocode_location(self, location_name: str) -> Optional[Dict[str, Any]]:
        """
        Geocode a location name to coordinates
        
        Args:
            location_name: Name of location
            
        Returns:
            Dict with latitude, longitude, and address
        """
        try:
            location = self.geocoder.geocode(location_name)
            
            if location:
                return {
                    'location_name': location_name,
                    'latitude': location.latitude,
                    'longitude': location.longitude,
                    'address': location.address,
                    'raw': location.raw
                }
            else:
                return None
                
        except Exception as e:
            observability_service.log_error(f"Geocoding failed for {location_name}: {e}")
            return None
    
    def calculate_distance(
        self,
        coord1: Tuple[float, float],
        coord2: Tuple[float, float]
    ) -> Dict[str, float]:
        """
        Calculate distance between two coordinates
        
        Args:
            coord1: (latitude, longitude)
            coord2: (latitude, longitude)
            
        Returns:
            Distance in km and miles
        """
        distance_km = geodesic(coord1, coord2).kilometers
        distance_mi = geodesic(coord1, coord2).miles
        
        return {
            'km': distance_km,
            'miles': distance_mi,
            'meters': distance_km * 1000
        }
    
    def find_nearby_locations(
        self,
        center: Tuple[float, float],
        locations: List[Dict[str, Any]],
        radius_km: float = 10.0
    ) -> List[Dict[str, Any]]:
        """
        Find locations within radius of center point
        
        Args:
            center: (latitude, longitude)
            locations: List of location dicts with 'latitude', 'longitude'
            radius_km: Radius in kilometers
            
        Returns:
            List of locations within radius with distances
        """
        nearby = []
        
        for loc in locations:
            if 'latitude' in loc and 'longitude' in loc:
                coords = (loc['latitude'], loc['longitude'])
                distance = self.calculate_distance(center, coords)
                
                if distance['km'] <= radius_km:
                    nearby.append({
                        **loc,
                        'distance_km': distance['km'],
                        'distance_miles': distance['miles']
                    })
        
        # Sort by distance
        nearby.sort(key=lambda x: x['distance_km'])
        
        return nearby
    
    def cluster_locations(
        self,
        locations: List[Dict[str, Any]],
        max_distance_km: float = 5.0
    ) -> List[List[Dict[str, Any]]]:
        """
        Cluster locations that are close to each other
        
        Args:
            locations: List of location dicts
            max_distance_km: Maximum distance for same cluster
            
        Returns:
            List of location clusters
        """
        if not locations:
            return []
        
        clusters = []
        used = set()
        
        for i, loc in enumerate(locations):
            if i in used or 'latitude' not in loc:
                continue
            
            cluster = [loc]
            coord1 = (loc['latitude'], loc['longitude'])
            
            for j, other in enumerate(locations[i+1:], start=i+1):
                if j in used or 'latitude' not in other:
                    continue
                
                coord2 = (other['latitude'], other['longitude'])
                distance = self.calculate_distance(coord1, coord2)
                
                if distance['km'] <= max_distance_km:
                    cluster.append(other)
                    used.add(j)
            
            clusters.append(cluster)
        
        return clusters
    
    def analyze_spatial_distribution(
        self,
        locations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze spatial distribution of locations
        
        Returns:
            Dict with center, spread, bounding box
        """
        if not locations:
            return {}
        
        # Filter valid coordinates
        valid_locs = [
            loc for loc in locations
            if 'latitude' in loc and 'longitude' in loc
        ]
        
        if not valid_locs:
            return {}
        
        # Calculate center (centroid)
        avg_lat = sum(loc['latitude'] for loc in valid_locs) / len(valid_locs)
        avg_lon = sum(loc['longitude'] for loc in valid_locs) / len(valid_locs)
        
        # Bounding box
        min_lat = min(loc['latitude'] for loc in valid_locs)
        max_lat = max(loc['latitude'] for loc in valid_locs)
        min_lon = min(loc['longitude'] for loc in valid_locs)
        max_lon = max(loc['longitude'] for loc in valid_locs)
        
        # Calculate spread (max distance from center)
        center = (avg_lat, avg_lon)
        max_distance = 0
        for loc in valid_locs:
            coords = (loc['latitude'], loc['longitude'])
            dist = self.calculate_distance(center, coords)
            max_distance = max(max_distance, dist['km'])
        
        return {
            'center': {'latitude': avg_lat, 'longitude': avg_lon},
            'spread_km': max_distance,
            'bounding_box': {
                'min_lat': min_lat,
                'max_lat': max_lat,
                'min_lon': min_lon,
                'max_lon': max_lon
            },
            'location_count': len(valid_locs)
        }

# Singleton
geospatial_analyzer = GeospatialAnalyzer()
