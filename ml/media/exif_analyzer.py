import exifread
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from typing import Dict, Any, Optional
from datetime import datetime
import requests
from io import BytesIO
from services.observability import observability_service

class EXIFAnalyzer:
    """Analyze EXIF metadata from images"""
    
    @staticmethod
    def extract_exif(image_path_or_url: str) -> Dict[str, Any]:
        """
        Extract EXIF data from image
        
        Args:
            image_path_or_url: Path or URL to image
            
        Returns:
            Dict of EXIF metadata
        """
        try:
            # Load image
            if image_path_or_url.startswith(('http://', 'https://')):
                response = requests.get(image_path_or_url)
                image_file = BytesIO(response.content)
            else:
                image_file = open(image_path_or_url, 'rb')
            
            # Extract EXIF using exifread
            tags = exifread.process_file(image_file, details=False)
            
            image_file.close() if hasattr(image_file, 'close') else None
            
            # Convert to dict
            exif_data = {}
            for tag, value in tags.items():
                exif_data[tag] = str(value)
            
            return exif_data
            
        except Exception as e:
            observability_service.log_error(f"EXIF extraction failed: {e}")
            return {}
    
    @staticmethod
    def extract_exif_pil(image_path_or_url: str) -> Dict[str, Any]:
        """Extract EXIF using PIL (alternative method)"""
        try:
            if image_path_or_url.startswith(('http://', 'https://')):
                response = requests.get(image_path_or_url)
                image = Image.open(BytesIO(response.content))
            else:
                image = Image.open(image_path_or_url)
            
            exif_data = {}
            
            if hasattr(image, '_getexif') and image._getexif():
                exif = image._getexif()
                
                for tag_id, value in exif.items():
                    tag = TAGS.get(tag_id, tag_id)
                    exif_data[tag] = str(value)
            
            return exif_data
            
        except Exception as e:
            observability_service.log_error(f"PIL EXIF extraction failed: {e}")
            return {}
    
    @staticmethod
    def parse_gps(exif_data: Dict[str, Any]) -> Optional[Dict[str, float]]:
        """
        Parse GPS coordinates from EXIF
        
        Returns:
            Dict with latitude and longitude, or None
        """
        try:
            # Look for GPS tags
            gps_latitude = exif_data.get('GPS GPSLatitude')
            gps_latitude_ref = exif_data.get('GPS GPSLatitudeRef')
            gps_longitude = exif_data.get('GPS GPSLongitude')
            gps_longitude_ref = exif_data.get('GPS GPSLongitudeRef')
            
            if not all([gps_latitude, gps_latitude_ref, gps_longitude, gps_longitude_ref]):
                return None
            
            # Parse coordinates
            def parse_coord(coord_str):
                # Format: [degrees, minutes, seconds]
                parts = coord_str.strip('[]').split(', ')
                degrees = float(parts[0])
                minutes = float(parts[1])
                seconds = float(parts[2])
                return degrees + minutes/60 + seconds/3600
            
            lat = parse_coord(gps_latitude)
            lon = parse_coord(gps_longitude)
            
            # Apply direction
            if gps_latitude_ref == 'S':
                lat = -lat
            if gps_longitude_ref == 'W':
                lon = -lon
            
            return {'latitude': lat, 'longitude': lon}
            
        except Exception as e:
            observability_service.log_error(f"GPS parsing failed: {e}")
            return None
    
    @staticmethod
    def detect_manipulation_signs(exif_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect potential signs of image manipulation
        
        Returns:
            Dict with manipulation indicators
        """
        indicators = {
            'missing_exif': len(exif_data) == 0,
            'software_edited': False,
            'exif_stripped': False,
            'date_inconsistency': False,
            'suspicious_software': []
        }
        
        # Check for editing software
        software = exif_data.get('Image Software', '') or exif_data.get('Software', '')
        editing_tools = ['Photoshop', 'GIMP', 'Lightroom', 'Snapseed', 'Pixlr']
        
        for tool in editing_tools:
            if tool.lower() in software.lower():
                indicators['software_edited'] = True
                indicators['suspicious_software'].append(tool)
        
        # Check if key EXIF fields are missing (possibly stripped)
        required_fields = ['Image Make', 'Image Model', 'DateTime']
        missing = sum(1 for field in required_fields if field not in exif_data)
        
        if missing >= 2:
            indicators['exif_stripped'] = True
        
        # Check date consistency
        datetime_original = exif_data.get('EXIF DateTimeOriginal')
        datetime_digitized = exif_data.get('EXIF DateTimeDigitized')
        
        if datetime_original and datetime_digitized and datetime_original != datetime_digitized:
            indicators['date_inconsistency'] = True
        
        return indicators
    
    @staticmethod
    def analyze_image(image_path_or_url: str) -> Dict[str, Any]:
        """
        Comprehensive image analysis
        
        Returns:
            Dict with EXIF, GPS, and manipulation indicators
        """
        exif_data = EXIFAnalyzer.extract_exif(image_path_or_url)
        
        analysis = {
            'has_exif': len(exif_data) > 0,
            'exif_data': exif_data,
            'camera_make': exif_data.get('Image Make', 'Unknown'),
            'camera_model': exif_data.get('Image Model', 'Unknown'),
            'datetime_original': exif_data.get('EXIF DateTimeOriginal'),
            'gps_coordinates': EXIFAnalyzer.parse_gps(exif_data),
            'manipulation_indicators': EXIFAnalyzer.detect_manipulation_signs(exif_data)
        }
        
        observability_service.log_info(
            f"EXIF analysis: {analysis['camera_make']} {analysis['camera_model']}, "
            f"GPS: {analysis['gps_coordinates'] is not None}"
        )
        
        return analysis

# Singleton
exif_analyzer = EXIFAnalyzer()
