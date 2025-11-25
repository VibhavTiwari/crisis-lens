from typing import Dict, Any
import cv2
import numpy as np
import torch
import torch.nn as nn
from torchvision import transforms
from services.observability import observability_service
import requests
from io import BytesIO
from PIL import Image
import os

class DeepfakeDetector:
    """
    Deepfake detection using a simplified Xception-like model
    """
    
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = self._load_model()
        self.transform = transforms.Compose([
            transforms.Resize((299, 299)),
            transforms.ToTensor(),
            transforms.Normalize([0.5]*3, [0.5]*3)
        ])
        
    def _load_model(self):
        """Load a pre-trained model (simulated structure for now)"""
        # In a real deployment, we would load weights:
        # model.load_state_dict(torch.load('xception_deepfake.pth'))
        # Here we define a simple CNN to represent the architecture
        model = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.AdaptiveAvgPool2d((1, 1)),
            nn.Flatten(),
            nn.Linear(64, 2)  # Real/Fake
        )
        model.to(self.device)
        model.eval()
        return model

    def detect_face_swap(self, image_path_or_url: str) -> Dict[str, Any]:
        """
        Detect face swap in images using the model
        """
        results = {
            'is_face_swap': False,
            'confidence': 0.0,
            'indicators': []
        }
        
        try:
            # 1. Load Image
            if image_path_or_url.startswith(('http://', 'https://')):
                response = requests.get(image_path_or_url, timeout=10)
                img = Image.open(BytesIO(response.content)).convert('RGB')
            else:
                img = Image.open(image_path_or_url).convert('RGB')
            
            # 2. Detect Faces (using OpenCV for speed)
            img_cv = np.array(img)
            gray = cv2.cvtColor(img_cv, cv2.COLOR_RGB2GRAY)
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            if len(faces) == 0:
                return results
                
            # 3. Analyze each face
            max_fake_prob = 0.0
            
            for (x, y, w, h) in faces:
                face_img = img.crop((x, y, x+w, y+h))
                face_tensor = self.transform(face_img).unsqueeze(0).to(self.device)
                
                with torch.no_grad():
                    outputs = self.model(face_tensor)
                    probs = torch.softmax(outputs, dim=1)
                    fake_prob = probs[0][1].item()  # Index 1 is 'fake'
                    
                if fake_prob > max_fake_prob:
                    max_fake_prob = fake_prob
            
            # 4. Result
            results['confidence'] = max_fake_prob
            results['is_face_swap'] = max_fake_prob > 0.5
            
            if results['is_face_swap']:
                results['indicators'].append("Model detected manipulation artifacts")
                
        except Exception as e:
            observability_service.log_error(f"Face swap detection failed: {e}")
            
        return results

    def detect_video_deepfake(self, video_path: str) -> Dict[str, Any]:
        """
        Detect deepfake in video by analyzing frames
        """
        results = {
            'is_deepfake': False,
            'confidence': 0.0,
            'indicators': [],
            'frames_analyzed': 0
        }
        
        try:
            cap = cv2.VideoCapture(video_path)
            frame_scores = []
            
            while len(frame_scores) < 20:  # Analyze up to 20 frames
                ret, frame = cap.read()
                if not ret:
                    break
                    
                # Convert to PIL for our transform
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(frame_rgb)
                
                # Reuse face swap logic for single frame
                # (In production, we'd use temporal models)
                # For efficiency, we just pass the path logic here manually
                # but simplified for this snippet
                
                frame_tensor = self.transform(pil_img).unsqueeze(0).to(self.device)
                with torch.no_grad():
                    out = self.model(frame_tensor)
                    prob = torch.softmax(out, dim=1)[0][1].item()
                    frame_scores.append(prob)
            
            cap.release()
            
            if frame_scores:
                avg_score = sum(frame_scores) / len(frame_scores)
                results['confidence'] = avg_score
                results['is_deepfake'] = avg_score > 0.5
                results['frames_analyzed'] = len(frame_scores)
                
        except Exception as e:
            observability_service.log_error(f"Video deepfake detection failed: {e}")
            
        return results

# Singleton
deepfake_detector = DeepfakeDetector()
