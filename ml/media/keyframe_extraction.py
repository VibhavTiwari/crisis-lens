import ffmpeg
import os
from typing import List, Dict, Any
from PIL import Image
import tempfile
from services.observability import observability_service

class KeyframeExtractor:
    """Extract keyframes from videos using ffmpeg"""
    
    @staticmethod
    def extract_keyframes(
        video_path: str,
        output_dir: str = None,
        max_frames: int = 10,
        scene_threshold: float = 0.4
    ) -> List[str]:
        """
        Extract keyframes from video
        
        Args:
            video_path: Path to video file
            output_dir: Directory to save frames (temp if None)
            max_frames: Maximum number of frames to extract
            scene_threshold: Scene detection threshold (0-1)
            
        Returns:
            List of paths to extracted keyframes
        """
        if output_dir is None:
            output_dir = tempfile.mkdtemp()
        
        os.makedirs(output_dir, exist_ok=True)
        
        try:
            # Get video info
            probe = ffmpeg.probe(video_path)
            video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
            duration = float(video_info.get('duration', 0))
            
            observability_service.log_info(f"Extracting keyframes from video (duration: {duration}s)")
            
            # Extract keyframes using scene detection
            output_pattern = os.path.join(output_dir, 'frame_%04d.jpg')
            
            (
                ffmpeg
                .input(video_path)
                .filter('select', f'gt(scene,{scene_threshold})')
                .filter('scale', 640, -1)  # Resize to 640px width
                .output(output_pattern, vsync='vfr', frame_pts=True)
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            
            # Get extracted frames
            frames = sorted([
                os.path.join(output_dir, f)
                for f in os.listdir(output_dir)
                if f.startswith('frame_') and f.endswith('.jpg')
            ])
            
            # Limit to max_frames
            if len(frames) > max_frames:
                # Keep evenly spaced frames
                step = len(frames) // max_frames
                frames = frames[::step][:max_frames]
            
            observability_service.log_info(f"Extracted {len(frames)} keyframes")
            
            return frames
            
        except ffmpeg.Error as e:
            observability_service.log_error(f"FFmpeg error: {e.stderr.decode()}")
            return []
    
    @staticmethod
    def extract_thumbnail(video_path: str, timestamp: float = 1.0) -> str:
        """
        Extract a single thumbnail from video at specific timestamp
        
        Args:
            video_path: Path to video
            timestamp: Time in seconds
            
        Returns:
            Path to thumbnail image
        """
        output_path = tempfile.mktemp(suffix='.jpg')
        
        try:
            (
                ffmpeg
                .input(video_path, ss=timestamp)
                .filter('scale', 640, -1)
                .output(output_path, vframes=1)
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            
            return output_path
            
        except ffmpeg.Error as e:
            observability_service.log_error(f"Thumbnail extraction failed: {e.stderr.decode()}")
            return None
    
    @staticmethod
    def get_video_info(video_path: str) -> Dict[str, Any]:
        """Get video metadata"""
        try:
            probe = ffmpeg.probe(video_path)
            video_stream = next(s for s in probe['streams'] if s['codec_type'] == 'video')
            
            return {
                'duration': float(video_stream.get('duration', 0)),
                'width': int(video_stream.get('width', 0)),
                'height': int(video_stream.get('height', 0)),
                'fps': eval(video_stream.get('r_frame_rate', '0/1')),
                'codec': video_stream.get('codec_name'),
                'bitrate': int(probe['format'].get('bit_rate', 0))
            }
            
        except Exception as e:
            observability_service.log_error(f"Failed to get video info: {e}")
            return {}

# Singleton
keyframe_extractor = KeyframeExtractor()
