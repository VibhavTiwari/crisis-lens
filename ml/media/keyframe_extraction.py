"""
Real Keyframe Extraction Service

Uses ffmpeg to extract meaningful keyframes from video content.
"""
import os
import subprocess
import ffmpeg
import numpy as np
import cv2
from typing import List, Dict, Any
from config import settings
from services.observability import observability_service

class KeyframeExtractor:
    """Extracts keyframes from video files using FFmpeg"""
    
    def __init__(self):
        self.output_dir = os.path.join(settings.MEDIA_ROOT, "keyframes")
        os.makedirs(self.output_dir, exist_ok=True)
        
    def get_video_info(self, video_path: str) -> Dict[str, Any]:
        """Get video metadata using ffprobe"""
        try:
            probe = ffmpeg.probe(video_path)
            video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
            
            if not video_stream:
                return {}
                
            return {
                'width': int(video_stream['width']),
                'height': int(video_stream['height']),
                'duration': float(video_stream['duration']),
                'codec': video_stream['codec_name'],
                'fps': eval(video_stream['r_frame_rate'])
            }
        except Exception as e:
            observability_service.log_error(f"Failed to probe video: {e}")
            return {}

    def extract_keyframes(self, video_path: str, method: str = "scene_change") -> List[str]:
        """
        Extract keyframes from video.
        
        Args:
            video_path: Path to video file
            method: 'uniform' (every N sec) or 'scene_change' (content adaptive)
            
        Returns:
            List of paths to extracted keyframe images
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
            
        video_id = os.path.splitext(os.path.basename(video_path))[0]
        output_pattern = os.path.join(self.output_dir, f"{video_id}_%03d.jpg")
        
        extracted_files = []
        
        try:
            if method == "scene_change":
                # Extract frames where scene changes (greater than 30% difference)
                # select='gt(scene,0.3)'
                (
                    ffmpeg
                    .input(video_path)
                    .filter('select', 'gt(scene,0.3)')
                    .output(output_pattern, vsync='vfr', frame_pts=True)
                    .run(capture_stdout=True, capture_stderr=True)
                )
            else:
                # Uniform extraction (1 frame every 5 seconds)
                (
                    ffmpeg
                    .input(video_path)
                    .filter('fps', fps=1/5)
                    .output(output_pattern, vsync='vfr')
                    .run(capture_stdout=True, capture_stderr=True)
                )
                
            # Collect generated files
            import glob
            extracted_files = sorted(glob.glob(os.path.join(self.output_dir, f"{video_id}_*.jpg")))
            
            observability_service.log_info(f"Extracted {len(extracted_files)} keyframes from {video_id}")
            
        except ffmpeg.Error as e:
            observability_service.log_error(f"FFmpeg error: {e.stderr.decode('utf8')}")
            raise
            
        return extracted_files

# Singleton instance
keyframe_extractor = KeyframeExtractor()
