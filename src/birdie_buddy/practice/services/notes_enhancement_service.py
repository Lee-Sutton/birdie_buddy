import logging
from typing import Optional

from django.conf import settings
from openai import OpenAI


logger = logging.getLogger(__name__)


class NotesEnhancementService:
    """Service for enhancing practice session notes using OpenAI's API."""
    
    def __init__(self, client=None):
        self.api_key = settings.OPENAI_API_KEY
        self.client = client or OpenAI(api_key=self.api_key)
        self.model = "gpt-3.5-turbo"
        self.max_retries = 3
    
    def enhance_notes(self, notes: str, practice_type: str = "") -> Optional[str]:
        """
        Enhance practice session notes using LLM.
        
        Args:
            notes: Original notes from the user
            practice_type: Type of practice session (Full Swing, Short Game, Putting)
            
        Returns:
            Enhanced notes or None if enhancement fails
        """
        if not notes or not notes.strip():
            return notes
            
        if not self.client:
            logger.warning("OpenAI API key not configured")
            return notes
            
        prompt = self._build_prompt(notes, practice_type)
        
        try:
            response = self._call_api(prompt)
            if response:
                return self._extract_enhanced_notes(response)
        except Exception as e:
            logger.error(f"LLM API call failed: {e}")
                    
        return notes
    
    def _build_prompt(self, notes: str, practice_type: str) -> str:
        """Build the prompt for the LLM."""
        practice_context = ""
        if practice_type:
            practice_context = f"This was a {practice_type.lower()} practice session. "
            
        return f"""You are a golf coach helping a player improve their practice session notes. 
{practice_context}Please enhance the following notes by:

1. Improving clarity and adding proper golf terminology
2. Adding relevant coaching insights and observations
3. Structuring the information for better readability
4. Maintaining the original meaning and key observations
5. Keeping it concise but informative

Original notes:
{notes}

Enhanced notes:"""
    
    def _call_api(self, prompt: str) -> Optional[dict]:
        """Make API call to OpenAI using Responses API."""
        response = self.client.responses.create(
            model=self.model,
            instructions="You are a helpful golf coach assistant.",
            input=prompt,
            temperature=0.7,
        )
        return response
    
    def _extract_enhanced_notes(self, response) -> str:
        """Extract enhanced notes from API response."""
        try:
            content = response.output_text
            return content.strip()
        except AttributeError as e:
            logger.error(f"Failed to extract content from response: {e}")
            raise ValueError("Invalid API response format")
