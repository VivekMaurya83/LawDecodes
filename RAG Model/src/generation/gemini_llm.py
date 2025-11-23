import os
from typing import Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from config.settings import settings

class GeminiLLM:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",  # Using available model
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0.1,  # Low temperature for legal accuracy
            max_output_tokens=2048,
            convert_system_message_to_human=True
        )
    
    def get_llm(self):
        """Get the LLM instance"""
        return self.llm
    
    def generate_response(self, prompt: str) -> str:
        """Generate response using Gemini"""
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def validate_api_key(self) -> bool:
        """Validate Gemini API key"""
        try:
            test_response = self.llm.invoke("Test")
            return True
        except Exception:
            return False
