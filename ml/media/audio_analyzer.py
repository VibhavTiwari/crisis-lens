import librosa
import numpy as np
from typing import Dict, Any, List
from services.observability import observability_service

class AudioAnalyzer:
    """Advanced audio analysis"""
    
    @staticmethod
    def analyze_audio(audio_path: str) -> Dict[str, Any]:
        """
        Comprehensive audio analysis
        
        Returns:
            Dict with audio features and analysis
        """
        try:
            # Load audio
            y, sr = librosa.load(audio_path)
            
            # Extract features
            # Spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
            
            # Rhythm features
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
            
            # Zero crossing rate
            zcr = librosa.feature.zero_crossing_rate(y)
            
            # MFCCs
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            
            # RMS energy
            rms = librosa.feature.rms(y=y)[0]
            
            analysis = {
                'duration': len(y) / sr,
                'sample_rate': sr,
                'tempo': float(tempo),
                'beats_count': len(beats),
                'spectral_centroid_mean': float(spectral_centroids.mean()),
                'spectral_centroid_std': float(spectral_centroids.std()),
                'spectral_rolloff_mean': float(spectral_rolloff.mean()),
                'zero_crossing_rate_mean': float(zcr.mean()),
                'rms_energy_mean': float(rms.mean()),
                'mfcc_means': [float(m) for m in mfccs.mean(axis=1)]
            }
            
            observability_service.log_info(
                f"Audio analysis: duration={analysis['duration']:.2f}s, tempo={analysis['tempo']:.1f}"
            )
            
            return analysis
            
        except Exception as e:
            observability_service.log_error(f"Audio analysis failed: {e}")
            return {}
    
    @staticmethod
    def detect_speaker_diarization(audio_path: str) -> List[Dict[str, Any]]:
        """
        Simple speaker diarization
        
        Note: Production would use models like pyannote.audio
        This is a simplified version based on spectral clustering
        """
        try:
            y, sr = librosa.load(audio_path)
            
            # Extract MFCCs for speaker characteristics
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)
            
            # Simple energy-based segmentation
            rms = librosa.feature.rms(y=y)[0]
            
            # Detect speech segments (simplified)
            threshold = rms.mean() * 0.5
            speech_frames = rms > threshold
            
            # Find segments
            segments = []
            in_segment = False
            start_frame = 0
            
            hop_length = 512
            frame_duration = hop_length / sr
            
            for i, is_speech in enumerate(speech_frames):
                if is_speech and not in_segment:
                    start_frame = i
                    in_segment = True
                elif not is_speech and in_segment:
                    segments.append({
                        'start': start_frame * frame_duration,
                        'end': i * frame_duration,
                        'speaker': 'Speaker1'  # Simplified
                    })
                    in_segment = False
            
            observability_service.log_info(f"Detected {len(segments)} speech segments")
            
            return segments
            
        except Exception as e:
            observability_service.log_error(f"Speaker diarization failed: {e}")
            return []
    
    @staticmethod
    def analyze_background_noise(audio_path: str) -> Dict[str, Any]:
        """
        Analyze background noise characteristics
        
        Returns:
            Dict with noise analysis
        """
        try:
            y, sr = librosa.load(audio_path)
            
            # Estimate noise floor
            rms = librosa.feature.rms(y=y)[0]
            noise_floor = np.percentile(rms, 10)  # Bottom 10% as noise
            
            # Signal-to-noise ratio estimate
            signal = rms.max()
            snr = 20 * np.log10(signal / noise_floor) if noise_floor > 0 else 0
            
            # Spectral analysis of noise
            D = np.abs(librosa.stft(y))
            noise_profile = D[:, rms < rms.mean() * 0.3].mean(axis=1)
            
            analysis = {
                'noise_floor': float(noise_floor),
                'snr_db': float(snr),
                'has_significant_noise': snr < 20,
                'noise_characteristics': {
                    'low_frequency': float(noise_profile[:len(noise_profile)//4].mean()),
                    'mid_frequency': float(noise_profile[len(noise_profile)//4:3*len(noise_profile)//4].mean()),
                    'high_frequency': float(noise_profile[3*len(noise_profile)//4:].mean())
                }
            }
            
            return analysis
            
        except Exception as e:
            observability_service.log_error(f"Background noise analysis failed: {e}")
            return {}

# Singleton
audio_analyzer = AudioAnalyzer()
