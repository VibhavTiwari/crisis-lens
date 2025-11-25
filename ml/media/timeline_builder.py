from scenedetect import VideoManager, SceneManager
from scenedetect.detectors import ContentDetector
from typing import List, Dict, Any
from datetime import timedelta
from services.observability import observability_service
import cv2

class VideoTimelineBuilder:
    """Build timeline of events from video"""
    
    @staticmethod
    def detect_scenes(video_path: str, threshold: float = 30.0) -> List[Dict[str, Any]]:
        """
        Detect scene changes in video
        
        Args:
            video_path: Path to video
            threshold: Scene detection threshold
            
        Returns:
            List of scenes with start/end times
        """
        try:
            # Create video manager
            video_manager = VideoManager([video_path])
            scene_manager = SceneManager()
            
            # Add detector
            scene_manager.add_detector(ContentDetector(threshold=threshold))
            
            # Start video and detect scenes
            video_manager.start()
            scene_manager.detect_scenes(frame_source=video_manager)
            
            # Get scene list
            scene_list = scene_manager.get_scene_list()
            
            scenes = []
            for i, (start_time, end_time) in enumerate(scene_list):
                scenes.append({
                    'scene_number': i + 1,
                    'start_time': start_time.get_seconds(),
                    'end_time': end_time.get_seconds(),
                    'duration': (end_time - start_time).get_seconds(),
                    'start_frame': start_time.get_frames(),
                    'end_frame': end_time.get_frames()
                })
            
            video_manager.release()
            
            observability_service.log_info(f"Detected {len(scenes)} scenes in video")
            
            return scenes
            
        except Exception as e:
            observability_service.log_error(f"Scene detection failed: {e}")
            return []
    
    @staticmethod
    def segment_by_motion(video_path: str) -> List[Dict[str, Any]]:
        """
        Segment video by motion/activity
        
        Returns:
            List of segments with motion levels
        """
        segments = []
        
        try:
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            ret, frame1 = cap.read()
            prev_gray = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
            
            frame_count = 0
            motion_scores = []
            
            while cap.isOpened():
                ret, frame2 = cap.read()
                if not ret:
                    break
                
                # Calculate motion
                gray = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
                diff = cv2.absdiff(prev_gray, gray)
                motion_score = diff.mean()
                
                motion_scores.append({
                    'frame': frame_count,
                    'time': frame_count / fps,
                    'motion': motion_score
                })
                
                prev_gray = gray
                frame_count += 1
                
                # Limit processing
                if frame_count > 1000:
                    break
            
            cap.release()
            
            # Group by motion levels
            current_segment = {'start': 0, 'motion_level': 'low'}
            motion_threshold = 20.0
            
            for i, score in enumerate(motion_scores):
                level = 'high' if score['motion'] > motion_threshold else 'low'
                
                if level != current_segment['motion_level']:
                    current_segment['end'] = score['time']
                    segments.append(current_segment.copy())
                    current_segment = {'start': score['time'], 'motion_level': level}
            
            # Add final segment
            if motion_scores:
                current_segment['end'] = motion_scores[-1]['time']
                segments.append(current_segment)
            
        except Exception as e:
            observability_service.log_error(f"Motion segmentation failed: {e}")
        
        return segments
    
    @staticmethod
    def build_timeline(video_path: str) -> Dict[str, Any]:
        """
        Build comprehensive timeline of video
        
        Returns:
            Dict with scenes, segments, and event timeline
        """
        timeline = {
            'video_path': video_path,
            'scenes': VideoTimelineBuilder.detect_scenes(video_path),
            'motion_segments': VideoTimelineBuilder.segment_by_motion(video_path),
            'events': []
        }
        
        # Construct event sequence
        for scene in timeline['scenes']:
            timeline['events'].append({
                'type': 'scene_change',
                'time': scene['start_time'],
                'description': f"Scene {scene['scene_number']} begins"
            })
        
        # Add high-motion events
        for segment in timeline['motion_segments']:
            if segment['motion_level'] == 'high':
                timeline['events'].append({
                    'type': 'high_activity',
                    'time': segment['start'],
                    'duration': segment.get('end', 0) - segment['start'],
                    'description': 'High motion detected'
                })
        
        # Sort events by time
        timeline['events'].sort(key=lambda x: x['time'])
        
        observability_service.log_info(f"Built timeline with {len(timeline['events'])} events")
        
        return timeline

# Singleton
timeline_builder = VideoTimelineBuilder()
