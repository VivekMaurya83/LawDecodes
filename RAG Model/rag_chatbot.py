import os
import sys
from typing import List, Dict, Any
from src.preprocessing.document_processor import DocumentProcessor
from src.retrieval.hybrid_retriever import HybridRetriever
from src.memory.conversation_memory import LegalConversationMemory
from src.generation.gemini_llm import GeminiLLM
from src.citations.citation_tracker import CitationTracker
from config.settings import settings
from config.prompts import legal_prompts

class LegalRAGChatbot:
    def __init__(self, documents_path: str):
        print("Initializing Legal RAG Chatbot...")
        
        # Initialize components
        self.document_processor = DocumentProcessor()
        self.memory = LegalConversationMemory()
        self.llm = GeminiLLM()
        self.citation_tracker = CitationTracker()
        
        # Process documents and create retriever
        print("Processing documents...")
        self.documents = self._load_documents(documents_path)
        print(f"Loaded {len(self.documents)} document chunks")
        # Add this line after "Loaded X document chunks"
        # self.debug_chunks()  # Remove this after debugging
        self.retriever = HybridRetriever(self.documents)
        print("Chatbot initialized successfully!")
    
    def _load_documents(self, documents_path: str) -> List:
        """Load and process documents from path"""
        if os.path.isfile(documents_path):
            return self.document_processor.process_documents([documents_path])
        elif os.path.isdir(documents_path):
            return self.document_processor.process_text_files(documents_path)
        else:
            raise ValueError(f"Invalid documents path: {documents_path}")
    
    def debug_chunks(self):
        """Debug function to see what's in the chunks"""
        print("\n" + "="*60)
        print("DEBUG: Document Chunks Analysis")
        print("="*60)
        
        for i, doc in enumerate(self.documents):
            content = doc.page_content[:300]  # First 300 chars
            print(f"\n--- Chunk {i+1} ---")
            print(f"Content: {content}...")
            print(f"Metadata: {doc.metadata}")
            
            # Check if this chunk contains dates
            if any(date_term in content.lower() for date_term in ['sep', '2025', 'effective', 'date']):
                print(f"🎯 DATE FOUND IN CHUNK {i+1}")
        
        print("\n" + "="*60 + "\n")

    def chat(self, user_query: str) -> Dict[str, Any]:
        """Main chat interface"""
        try:
            # Retrieve relevant documents
            relevant_docs = self.retriever.retrieve(user_query)
            
            # Prepare context
            context = self._prepare_context(relevant_docs)
            chat_history = self.memory.get_conversation_history()
            
            # Generate response
            prompt = self._create_prompt(user_query, context, chat_history)
            response = self.llm.generate_response(prompt)
            
            # Extract and validate citations
            citation_info = self.citation_tracker.extract_citations_from_response(
                response, relevant_docs
            )
            
            # Update memory
            self.memory.add_interaction(
                user_query, 
                response, 
                citation_info["citations"]
            )
            
            # Format response
            formatted_response = self._format_response(
                citation_info, 
                relevant_docs
            )
            
            return formatted_response
            
        except Exception as e:
            return {
                "response": f"Error processing query: {str(e)}",
                "sources": [],
                "confidence": 0.0,
                "memory_stats": self.memory.get_memory_stats()
            }
    
    def _prepare_context(self, documents: List) -> str:
        """Prepare context from retrieved documents"""
        context_parts = []
        for i, doc in enumerate(documents):
            source_info = f"[Source {i+1}: {doc.metadata.get('source', 'Unknown')}]"
            context_parts.append(f"{source_info}\n{doc.page_content}\n")
        
        return "\n".join(context_parts)
    
    def _create_prompt(self, query: str, context: str, chat_history: str) -> str:
        """Create the final prompt for the LLM"""
        return legal_prompts.LEGAL_QA_PROMPT.format(
            context=context,
            question=query,
            chat_history=chat_history
        )
    
    # def _format_response(self, citation_info: Dict, source_docs: List) -> Dict[str, Any]:
    #     """Format the final response"""
    #     formatted_sources = self.citation_tracker.format_citations_for_display(
    #         citation_info["citations"]
    #     )
        
    #     return {
    #         "response": citation_info["response"],
    #         "sources": formatted_sources,
    #         "confidence": citation_info["confidence_score"],
    #         "citation_count": citation_info["citation_count"],
    #         "retrieved_docs": len(source_docs),
    #         "memory_stats": self.memory.get_memory_stats()
    #     }

    def _format_response(self, citation_info: Dict, source_docs: List) -> Dict[str, Any]:
        """Format the final response"""
        # Ensure response is a string
        response = citation_info.get("response", "")
        if not isinstance(response, str):
            response = str(response)
        
        formatted_sources = self.citation_tracker.format_citations_for_display(
            citation_info["citations"]
        )
        
        return {
            "response": response,
            "sources": formatted_sources,
            "confidence": citation_info["confidence_score"],
            "citation_count": citation_info["citation_count"],
            "retrieved_docs": len(source_docs),
            "memory_stats": self.memory.get_memory_stats()
        }

    
    def clear_conversation(self):
        """Clear conversation memory"""
        self.memory.clear_memory()

def main():
    # Check if documents path is provided
    if len(sys.argv) < 2:
        documents_path = input("Enter path to legal documents (file or directory): ")
    else:
        documents_path = sys.argv[1]
    
    # Initialize chatbot
    try:
        chatbot = LegalRAGChatbot(documents_path)
    except Exception as e:
        print(f"Error initializing chatbot: {e}")
        return
    
    # Interactive chat loop
    print("\n" + "="*50)
    print("Legal RAG Chatbot Ready!")
    print("Type 'exit' to quit, 'clear' to clear memory")
    print("="*50 + "\n")
    
    while True:
        try:
            user_input = input("\nYour question related to reports: ").strip()
            
            if user_input.lower() == 'exit':
                print("Thank you for using Legal RAG Chatbot!")
                break
            elif user_input.lower() == 'clear':
                chatbot.clear_conversation()
                print("Conversation memory cleared.")
                continue
            elif not user_input:
                continue
            
            print("\nProcessing your question...")
            result = chatbot.chat(user_input)
            
            print(f"\n📋 Legal Analysis:")
            print(result["response"])
            print(f"\n{result['sources']}")
            print(f"🎯 Confidence: {result['confidence']:.2f}")
            print(f"📊 Citations: {result['citation_count']}, Retrieved: {result['retrieved_docs']}")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
