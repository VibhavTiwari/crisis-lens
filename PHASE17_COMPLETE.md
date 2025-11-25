# Phase 17: Advanced Media Processing - Complete!

## Components Implemented

### 1. Keyframe Extraction (`ml/media/keyframe_extraction.py`)
**Real ffmpeg-based implementation:**
- Scene detection with configurable threshold
- Automatic frame extraction at scene changes
- Thumbnail generation at specific timestamps
- Video metadata extraction (duration, resolution, codec, bitrate)
- Resize to 640px for efficiency
- Returns list of extracted keyframe paths

**Features:**
- `extract_keyframes()` - Extract N keyframes using scene detection
- `extract_thumbnail()` - Single frame at timestamp
- `get_video_info()` - Video metadata

### 2. Reverse Image Search (`ml/media/reverse_image.py`)
**Multiple search backends:**
- TinEye API integration (requires API key)
- Google Images search (via Custom Search API)
- Perceptual image hashing (imagehash)
- Local similarity search using Hamming distance
- Comprehensive multi-source search

**Features:**
- `calculate_image_hash()` - Perceptual hashing
- `find_similar_images_local()` - Local database search
- `comprehensive_search()` - Search all sources

### 3. EXIF Analyzer (`ml/media/exif_analyzer.py`)
**Comprehensive metadata extraction:**
- EXIF data extraction (exifread + PIL)
- GPS coordinate parsing (lat/lon from EXIF)
- Camera make/model identification
- Timestamp extraction
- Manipulation detection

**Manipulation Indicators:**
- Missing EXIF data (stripped metadata)
- Editing software detection (Photoshop, GIMP, etc.)
- Date inconsistencies
- Suspicious software signatures

**Features:**
- `extract_exif()` - Full EXIF extraction
- `parse_gps()` - GPS coordinates
- `detect_manipulation_signs()` - Forensic analysis
- `analyze_image()` - Complete analysis

### 4. Deepfake Detector (`ml/media/deepfake_detector.py`)
**Multi-modal deepfake detection:**
- Video deepfake detection (temporal analysis)
- Face swap detection (OpenCV)
- Audio deepfake detection (librosa)
- Frame consistency checking
- Spectral anomaly detection

**Note:** Simplified version for Phase 17. Production would use:
- FaceForensics++ models
- XceptionNet
- ASVspoof models for audio
- RawNet2

**Features:**
- `detect_video_deepfake()` - Video analysis
- `detect_face_swap()` - Image face manipulation
- `detect_audio_deepfake()` - Synthetic voice detection

### 5. Video Timeline Builder (`ml/media/timeline_builder.py`)
**Scene and event detection:**
- Scene change detection (scenedetect library)
- Motion-based segmentation
- Activity timeline construction
- Event sequencing

**Features:**
- `detect_scenes()` - Scene boundaries with timestamps
- `segment_by_motion()` - Motion level analysis
- `build_timeline()` - Complete event timeline

**Output:**
- Scene changes with start/end times
- High-motion segments
- Chronological event list

### 6. Audio Analyzer (`ml/media/audio_analyzer.py`)
**Advanced audio analysis with librosa:**
- Spectral features (centroid, rolloff)
- Rhythm analysis (tempo, beats)
- MFCC extraction (speaker characteristics)
- Energy analysis (RMS)
- Speaker diarization (simplified)
- Background noise analysis

**Features:**
- `analyze_audio()` - Full audio analysis
- `detect_speaker_diarization()` - Speaker segmentation
- `analyze_background_noise()` - Noise profiling, SNR

### 7. Keyframe Extraction Agent (`agents/digestion/keyframe_extraction.py`)
Agent wrapper for integrating into workflow

## Dependencies Added

```toml
# Media Processing
ffmpeg-python = "^0.2.0"
Pillow-HEIF = "^0.13.0"
exifread = "^3.0.0"
pydub = "^0.25.1"
scenedetect = {extras = ["opencv"], version = "^0.6.0"}
opencv-python = "^4.8.0"
librosa = "^0.10.0"
```

## System Requirements

**FFmpeg must be installed:**
- Windows: Download from ffmpeg.org
- Linux: `sudo apt-get install ffmpeg`
- Mac: `brew install ffmpeg`

## Usage Examples

### Keyframe Extraction
```python
from ml.media.keyframe_extraction import keyframe_extractor

# Extract keyframes
keyframes = keyframe_extractor.extract_keyframes(
    video_path="video.mp4",
    max_frames=10,
    scene_threshold=0.4
)

# Get single thumbnail
thumbnail = keyframe_extractor.extract_thumbnail("video.mp4", timestamp=5.0)

# Video info
info = keyframe_extractor.get_video_info("video.mp4")
print(f"Duration: {info['duration']}s, Resolution: {info['width']}x{info['height']}")
```

### Reverse Image Search
```python
from ml.media.reverse_image import reverse_image_search

# Calculate hash
image_hash = reverse_image_search.calculate_image_hash("image.jpg")

# Search
results = reverse_image_search.comprehensive_search("https://example.com/image.jpg")
print(f"Found elsewhere: {results['found_elsewhere']}")
```

### EXIF Analysis
```python
from ml.media.exif_analyzer import exif_analyzer

# Full analysis
analysis = exif_analyzer.analyze_image("photo.jpg")

print(f"Camera: {analysis['camera_make']} {analysis['camera_model']}")
print(f"GPS: {analysis['gps_coordinates']}")
print(f"Manipulation: {analysis['manipulation_indicators']}")
```

### Deepfake Detection
```python
from ml.media.deepfake_detector import deepfake_detector

# Video deepfake
result = deepfake_detector.detect_video_deepfake("video.mp4")
print(f"Deepfake: {result['is_deepfake']}, Confidence: {result['confidence']}")

# Face swap
result = deepfake_detector.detect_face_swap("image.jpg")

# Audio
result = deepfake_detector.detect_audio_deepfake("audio.mp3")
```

### Video Timeline
```python
from ml.media.timeline_builder import timeline_builder

# Build timeline
timeline = timeline_builder.build_timeline("video.mp4")

for event in timeline['events']:
    print(f"{event['time']:.1f}s: {event['description']}")
```

### Audio Analysis
```python
from ml.media.audio_analyzer import audio_analyzer

# Analyze
analysis = audio_analyzer.analyze_audio("audio.wav")
print(f"Tempo: {analysis['tempo']} BPM")
print(f"SNR: {analysis.get('snr_db', 0):.1f} dB")

# Speaker diarization
segments = audio_analyzer.detect_speaker_diarization("audio.wav")
```

## Integration with Workflow

Media processing can be added to the verification workflow:

```python
# In verification_workflow.py
async def process_media_node(state: WorkflowState) -> WorkflowState:
    """Process media attachments"""
    from ml.media.exif_analyzer import exif_analyzer
    from ml.media.deepfake_detector import deepfake_detector
    
    for media in state.get('media_items', []):
        if media['type'] == 'image':
            # EXIF analysis
            exif_results = exif_analyzer.analyze_image(media['url'])
            media['exif'] = exif_results
            
            # Check for face manipulation
            deepfake_results = deepfake_detector.detect_face_swap(media['url'])
            media['deepfake_check'] = deepfake_results
    
    return state
```

## Limitations & Production Notes

1. **Deepfake Detection:** Current implementation is simplified
   - **Production:** Use FaceForensics++, XceptionNet, specialized models
   
2. **Speaker Diarization:** Basic energy-based segmentation
   - **Production:** Use pyannote.audio or similar

3. **Reverse Image Search:** Requires API keys
   - TinEye: Paid API
   - Google: Custom Search API (limited free tier)

4. **FFmpeg:** Must be installed separately

5. **Performance:** Video processing is CPU/GPU intensive
   - Consider async processing
   - Use task queues (Celery) for large videos

## Next Steps (Phase 18)

Deploy to Kubernetes with production infrastructure:
- Helm charts
- Ingress configuration
- Prometheus monitoring
- Grafana dashboards
- Auto-scaling
- ELK stack
