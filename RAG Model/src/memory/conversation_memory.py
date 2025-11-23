# from typing import List, Dict, Any
# from langchain.memory import ConversationSummaryBufferMemory
# from langchain.schema import BaseMessage, HumanMessage, AIMessage
# from src.generation.gemini_llm import GeminiLLM
# from config.settings import settings
# from config.prompts import legal_prompts

# from typing import List, Dict, Any
# from langchain.memory import ConversationSummaryBufferMemory
# from langchain.schema import BaseMessage, HumanMessage, AIMessage
# # Updated import path
# from src.generation.gemini_llm import GeminiLLM
# from config.settings import settings
# from config.prompts import legal_prompts

# # Rest of the file remains the same...


# class LegalConversationMemory:
#     def __init__(self):
#         self.llm = GeminiLLM()
#         self.memory = ConversationSummaryBufferMemory(
#             llm=self.llm.get_llm(),
#             memory_key="chat_history",
#             return_messages=True,
#             max_token_limit=settings.MAX_MEMORY_TOKENS,
#             human_prefix="Legal Query",
#             ai_prefix="Legal Assistant",
#             summarize_step=settings.MEMORY_SUMMARY_THRESHOLD,
#             summary_message_cls=HumanMessage,
#             summarizer_prompt=legal_prompts.MEMORY_SUMMARIZATION_PROMPT
#         )
    
#     def add_interaction(self, human_input: str, ai_response: str, sources: List[Dict]):
#         """Add human-AI interaction to memory with source tracking"""
#         # Add the basic interaction
#         self.memory.chat_memory.add_user_message(human_input)
        
#         # Create enhanced AI response with sources
#         enhanced_response = self._create_enhanced_response(ai_response, sources)
#         self.memory.chat_memory.add_ai_message(enhanced_response)
    
#     def _create_enhanced_response(self, response: str, sources: List[Dict]) -> str:
#         """Create response with embedded source information for memory"""
#         if not sources:
#             return response
        
#         source_summary = "\n[Sources Referenced: "
#         source_summary += ", ".join([
#             f"{src.get('document_title', 'Unknown')} (p. {src.get('page_number', 'N/A')})"
#             for src in sources[:3]  # Keep only top 3 for memory efficiency
#         ])
#         source_summary += "]"
        
#         return response + source_summary
    
#     def get_conversation_history(self) -> str:
#         """Get formatted conversation history"""
#         return self.memory.buffer
    
#     def clear_memory(self):
#         """Clear conversation memory"""
#         self.memory.clear()
    
#     def get_memory_stats(self) -> Dict[str, Any]:
#         """Get memory usage statistics"""
#         messages = self.memory.chat_memory.messages
#         return {
#             "total_messages": len(messages),
#             "memory_size": len(self.memory.buffer),
#             "token_estimate": len(self.memory.buffer.split()),
#             "summary_active": hasattr(self.memory, 'moving_summary_buffer') and bool(self.memory.moving_summary_buffer)
#         }

from typing import List, Dict, Any
from langchain.memory import ConversationSummaryBufferMemory
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from src.generation.gemini_llm import GeminiLLM
from config.settings import settings
from config.prompts import legal_prompts

class LegalConversationMemory:
    def __init__(self):
        self.llm = GeminiLLM()
        self.memory = ConversationSummaryBufferMemory(
            llm=self.llm.get_llm(),
            memory_key="chat_history",
            return_messages=True,
            max_token_limit=settings.MAX_MEMORY_TOKENS,
            human_prefix="Legal Query",
            ai_prefix="Legal Assistant",
            summarize_step=settings.MEMORY_SUMMARY_THRESHOLD,
            summary_message_cls=HumanMessage,
        )
    
    def add_interaction(self, human_input: str, ai_response: str, sources: List[Dict]):
        """Add human-AI interaction to memory with source tracking"""
        # Ensure inputs are strings
        human_input = str(human_input) if not isinstance(human_input, str) else human_input
        ai_response = str(ai_response) if not isinstance(ai_response, str) else ai_response
        
        # Add the basic interaction
        self.memory.chat_memory.add_user_message(human_input)
        
        # Create enhanced AI response with sources
        enhanced_response = self._create_enhanced_response(ai_response, sources)
        self.memory.chat_memory.add_ai_message(enhanced_response)
    
    def _create_enhanced_response(self, response: str, sources: List[Dict]) -> str:
        """Create response with embedded source information for memory"""
        if not sources:
            return response
        
        source_summary = "\n[Sources Referenced: "
        source_summary += ", ".join([
            f"{src.get('document_title', 'Unknown')} (p. {src.get('page_number', 'N/A')})"
            for src in sources[:3]  # Keep only top 3 for memory efficiency
        ])
        source_summary += "]"
        
        return response + source_summary
    
    def get_conversation_history(self) -> str:
        """Get formatted conversation history"""
        try:
            history = self.memory.buffer
            return str(history) if history else ""
        except Exception as e:
            print(f"Warning: Could not retrieve conversation history: {e}")
            return ""
    
    def clear_memory(self):
        """Clear conversation memory"""
        self.memory.clear()
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory usage statistics"""
        try:
            messages = self.memory.chat_memory.messages
            buffer = self.get_conversation_history()
            return {
                "total_messages": len(messages),
                "memory_size": len(buffer),
                "token_estimate": len(buffer.split()),
                "summary_active": hasattr(self.memory, 'moving_summary_buffer') and bool(self.memory.moving_summary_buffer)
            }
        except Exception as e:
            print(f"Warning: Could not get memory stats: {e}")
            return {
                "total_messages": 0,
                "memory_size": 0,
                "token_estimate": 0,
                "summary_active": False
            }

