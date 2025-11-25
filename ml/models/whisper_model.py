import whisper
from typing import Dict, Any
from config import settings
from services.observability import observability_service
import os

class WhisperModel:
    """OpenAI Whisper for speech-to-text"""
    
    def __init__(self, model_size: str = "base"):
        """
        Initialize Whisper model
        
        Args:
            model_size: tiny, base, small, medium, large
        """
        self.model_size = model_size
        self.model = None
        
    def load(self):
        """Load the model"""
        if self.model is None:
            observability_service.log_info(f"Loading Whisper model: {self.model_size}")
            
            # Set download root
            download_root = os.path.join(settings.MODEL_CACHE_DIR, "whisper")
            os.makedirs(download_root, exist_ok=True)
            
            self.model = whisper.load_model(
                self.model_size,
                download_root=download_root
            )
            
            observability_service.log_info(f"Whisper model loaded: {self.model_size}")
    
    def transcribe(
        self,
        audio_path: str,
        language: str = None,
        task: str = "transcribe"
    ) -> Dict[str, Any]:
        """
        Transcribe audio file
        
        Args:
            audio_path: Path to audio file
            language: Language code (auto-detect if None)
            task: 'transcribe' or 'translate' (to English)
            
        Returns:
            Dict with 'text', 'segments', and 'language'
        """
        self.load()
        
        observability_service.log_info(f"Transcribing: {audio_path}")
        
        result = self.model.transcribe(
            audio_path,
            language=language,
            task=task,
            fp16=False  # Use FP32 on CPU
        )
        
        return {
            "text": result["text"],
            "language": result["language"],
            "segments": [
                {
                    "start": seg["start"],
                    "end": seg["end"],
                    "text": seg["text"]
                }
                for seg in result["segments"]
            ]
        }
    
    def detect_language(self, audio_path: str) -> str:
        """Detect the language of audio"""
        self.load()
        
        # Load audio and pad/trim it
        audio = whisper.load_audio(audio_path)
        audio = whisper.pad_or_trim(audio)
        
        # Make log-Mel spectrogram
        mel = whisper.log_mel_spectrogram(audio).to(self.model.device)
        
        # Detect language
        _, probs = self.model.detect_language(mel)
        detected_language = max(probs, key=probs.get)
        
        return detected_language

# Singleton instance
whisper_model = WhisperModel()
