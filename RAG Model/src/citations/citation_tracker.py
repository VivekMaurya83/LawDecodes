# import re
# from typing import List, Dict, Any, Tuple
# from langchain.schema import Document
# import difflib

# class CitationTracker:
#     def __init__(self):
#         self.citation_pattern = r'"([^"]+)"'
#         self.min_similarity = 0.8
    
#     def extract_citations_from_response(self, response: str, source_documents: List[Document]) -> Dict[str, Any]:
#         """Extract and validate citations from AI response"""
#         quotes = re.findall(self.citation_pattern, response)
#         validated_citations = []
        
#         for quote in quotes:
#             citation_info = self._validate_quote(quote, source_documents)
#             if citation_info:
#                 validated_citations.append(citation_info)
        
#         return {
#             "response": response,
#             "citations": validated_citations,
#             "citation_count": len(validated_citations),
#             "confidence_score": self._calculate_confidence(validated_citations)
#         }
    
#     # def _validate_quote(self, quote: str, source_documents: List[Document]) -> Dict[str, Any]:
#     #     """Validate if quote exists in source documents"""
#     #     best_match = None
#     #     best_similarity = 0
        
#     #     for i, doc in enumerate(source_documents):
#     #         content = doc.page_content
            
#     #         # Direct substring match
#     #         if quote.lower() in content.lower():
#     #             return self._create_citation(doc, quote, 1.0, "exact_match")
            
#     #         # Fuzzy matching for paraphrases
#     #         similarity = difflib.SequenceMatcher(None, quote.lower(), content.lower()).ratio()
#     #         if similarity > best_similarity and similarity > self.min_similarity:
#     #             best_similarity = similarity
#     #             best_match = doc
        
#     #     if best_match:
#     #         return self._create_citation(best_match, quote, best_similarity, "fuzzy_match")
        
#     #     return None

#     def _validate_quote(self, quote: str, source_documents: List[Document]) -> Dict[str, Any]:
#         """Validate if quote exists in source documents"""
#         best_match = None
#         best_similarity = 0
        
#         for i, doc in enumerate(source_documents):
#             content = doc.page_content
            
#             # Ensure content is a string
#             if not isinstance(content, str):
#                 content = str(content)
            
#             # Direct substring match
#             if quote.lower() in content.lower():
#                 return self._create_citation(doc, quote, 1.0, "exact_match")
            
#             # Fuzzy matching for paraphrases
#             similarity = difflib.SequenceMatcher(None, quote.lower(), content.lower()).ratio()
#             if similarity > best_similarity and similarity > self.min_similarity:
#                 best_similarity = similarity
#                 best_match = doc
        
#         if best_match:
#             return self._create_citation(best_match, quote, best_similarity, "fuzzy_match")
        
#         return None
    
#     def _create_citation(self, document: Document, quote: str, similarity: float, match_type: str) -> Dict[str, Any]:
#         """Create citation dictionary"""
#         metadata = document.metadata
        
#         return {
#             "quote": quote,
#             "document_title": metadata.get("source", "Unknown Document"),
#             "page_number": metadata.get("page", "N/A"),
#             "section": metadata.get("section", "N/A"),
#             "chunk_id": metadata.get("chunk_id", "N/A"),
#             "similarity_score": similarity,
#             "match_type": match_type,
#             "source_content": document.page_content[:200] + "..." if len(document.page_content) > 200 else document.page_content
#         }
    
#     def _calculate_confidence(self, citations: List[Dict]) -> float:
#         """Calculate overall confidence score for citations"""
#         if not citations:
#             return 0.0
        
#         total_score = sum(citation["similarity_score"] for citation in citations)
#         return min(total_score / len(citations), 1.0)
    
#     def format_citations_for_display(self, citations: List[Dict]) -> str:
#         """Format citations for user display"""
#         if not citations:
#             return "No sources cited."
        
#         formatted = "\n**Sources:**\n"
#         for i, citation in enumerate(citations, 1):
#             formatted += f"{i}. {citation['document_title']}"
#             if citation['page_number'] != "N/A":
#                 formatted += f", page {citation['page_number']}"
#             if citation['section'] != "N/A":
#                 formatted += f", section {citation['section']}"
#             formatted += f"\n   Quote: \"{citation['quote']}\"\n"
#             formatted += f"   Confidence: {citation['similarity_score']:.2f}\n\n"
        
#         return formatted

import re
from typing import List, Dict, Any, Set
from langchain.schema import Document
import difflib

class CitationTracker:
    def __init__(self):
        self.citation_pattern = r'"([^"]+)"'
        self.min_similarity = 0.5
    
    def extract_citations_from_response(self, response: str, source_documents: List[Document]) -> Dict[str, Any]:
        """Extract and validate citations from AI response"""
        if not isinstance(response, str):
            response = str(response)
        
        # Clean up the response first
        cleaned_response = self._clean_response(response)
            
        quotes = re.findall(self.citation_pattern, cleaned_response)
        validated_citations = []
        seen_quotes = set()  # Prevent duplicates
        
        for quote in quotes:
            if quote not in seen_quotes and len(quote) > 10:  # Filter short quotes
                citation_info = self._validate_quote(quote, source_documents)
                if citation_info:
                    validated_citations.append(citation_info)
                    seen_quotes.add(quote)
        
        return {
            "response": cleaned_response,
            "citations": validated_citations[:3],  # Limit to top 3
            "citation_count": len(validated_citations),
            "confidence_score": self._calculate_confidence(validated_citations)
        }
    
    def _clean_response(self, response: str) -> str:
        """Clean up duplicated response content"""
        lines = response.split('\n')
        cleaned_lines = []
        seen_lines = set()
        
        for line in lines:
            line = line.strip()
            if line and line not in seen_lines:
                cleaned_lines.append(line)
                seen_lines.add(line)
        
        return '\n'.join(cleaned_lines)
    
    def _validate_quote(self, quote: str, source_documents: List[Document]) -> Dict[str, Any]:
        """Validate if quote exists in source documents"""
        best_match = None
        best_similarity = 0
        
        for doc in source_documents:
            content = str(doc.page_content)
            
            # Direct substring match
            if quote.lower() in content.lower():
                return self._create_citation(doc, quote, 1.0, "exact_match")
            
            # Fuzzy matching
            similarity = difflib.SequenceMatcher(None, quote.lower(), content.lower()).ratio()
            if similarity > best_similarity and similarity > self.min_similarity:
                best_similarity = similarity
                best_match = doc
        
        if best_match and best_similarity > 0.6:  # Higher threshold
            return self._create_citation(best_match, quote, best_similarity, "fuzzy_match")
        
        return None
    
    def _create_citation(self, document: Document, quote: str, similarity: float, match_type: str) -> Dict[str, Any]:
        """Create citation dictionary"""
        metadata = document.metadata
        
        return {
            "quote": quote[:100] + "..." if len(quote) > 100 else quote,  # Truncate long quotes
            "document_title": metadata.get("source", "Unknown Document"),
            "page_number": metadata.get("page", "N/A"),
            "section": metadata.get("section", "N/A"),
            "similarity_score": similarity,
            "match_type": match_type
        }
    
    def _calculate_confidence(self, citations: List[Dict]) -> float:
        """Calculate overall confidence score"""
        if not citations:
            return 0.0
        
        total_score = sum(citation["similarity_score"] for citation in citations)
        return min(total_score / len(citations), 1.0)
    
    def format_citations_for_display(self, citations: List[Dict]) -> str:
        """Format citations for user display"""
        if not citations:
            return "\n**Sources:** No specific sources cited."
        
        formatted = "\n**Sources:**"
        for i, citation in enumerate(citations, 1):
            formatted += f"\n{i}. {citation['document_title']}"
            if citation.get('section') != "N/A":
                formatted += f" - {citation['section']}"
            formatted += f"\n   Relevance: {citation['similarity_score']:.2f}"
        
        return formatted
