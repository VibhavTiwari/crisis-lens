from openai import OpenAI
from anthropic import Anthropic
from typing import List, Dict, Any, Optional, Literal
from config import settings
from services.observability import observability_service

class LLMService:
    """Service for LLM interactions (OpenAI, Anthropic)"""
    
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        
    def _get_openai_client(self):
        """Lazy load OpenAI client"""
        if self.openai_client is None:
            if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY.startswith("dummy"):
                raise ValueError("OpenAI API key not configured")
            self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        return self.openai_client
    
    def _get_anthropic_client(self):
        """Lazy load Anthropic client"""
        if self.anthropic_client is None:
            if not hasattr(settings, 'ANTHROPIC_API_KEY') or settings.ANTHROPIC_API_KEY.startswith("dummy"):
                raise ValueError("Anthropic API key not configured")
            self.anthropic_client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        return self.anthropic_client
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4-turbo-preview",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        provider: Literal["openai", "anthropic"] = "openai"
    ) -> str:
        """
        Chat completion
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model name
            temperature: Sampling temperature
            max_tokens: Max response tokens
            provider: LLM provider
            
        Returns:
            Response text
        """
        observability_service.log_info(f"LLM request to {provider}: {model}")
        
        if provider == "openai":
            client = self._get_openai_client()
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
            
        elif provider == "anthropic":
            client = self._get_anthropic_client()
            # Convert messages to Anthropic format
            system_msg = next((m["content"] for m in messages if m["role"] == "system"), None)
            user_messages = [m for m in messages if m["role"] != "system"]
            
            response = client.messages.create(
                model=model or "claude-3-sonnet-20240229",
                system=system_msg,
                messages=user_messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.content[0].text
        
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    def draft_advisory(
        self,
        item_title: str,
        item_text: str,
        verified_claims: List[str],
        debunked_claims: List[str]
    ) -> Dict[str, str]:
        """
        Draft an advisory using LLM
        
        Returns:
            Dict with advisory fields
        """
        prompt = f"""You are a crisis information analyst. Draft a clear, concise advisory.

INCIDENT: {item_title}

DETAILS:
{item_text}

VERIFIED FACTS:
{chr(10).join(f"- {claim}" for claim in verified_claims)}

FALSE CLAIMS TO DEBUNK:
{chr(10).join(f"- {claim}" for claim in debunked_claims)}

Generate an advisory with these sections:
1. SUMMARY: 2-3 sentence overview
2. WHAT HAPPENED: Factual description of events
3. WHAT WE VERIFIED: Confirmed information
4. RECOMMENDED ACTIONS: What people should do

Be factual, clear, and avoid speculation."""

        messages = [
            {"role": "system", "content": "You are a crisis information analyst drafting public advisories."},
            {"role": "user", "content": prompt}
        ]
        
        response = self.chat(messages, temperature=0.3)
        
        # Parse response (simplified)
        sections = {}
        current_section = None
        current_content = []
        
        for line in response.split('\n'):
            line = line.strip()
            if line.startswith('SUMMARY:') or line.startswith('1.'):
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = 'summary'
                current_content = [line.split(':', 1)[-1].strip()]
            elif line.startswith('WHAT HAPPENED:') or line.startswith('2.'):
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = 'what_happened'
                current_content = [line.split(':', 1)[-1].strip()]
            elif line.startswith('WHAT WE VERIFIED:') or line.startswith('3.'):
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = 'verified'
                current_content = [line.split(':', 1)[-1].strip()]
            elif line.startswith('RECOMMENDED ACTIONS:') or line.startswith('4.'):
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = 'actions'
                current_content = [line.split(':', 1)[-1].strip()]
            elif line and current_section:
                current_content.append(line)
        
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections

# Singleton instance
llm_service = LLMService()
