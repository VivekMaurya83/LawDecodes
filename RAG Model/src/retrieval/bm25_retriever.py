# # from typing import List
# # from langchain.schema import Document
# # from langchain.retrievers import BM25Retriever
# # from rank_bm25 import BM25Okapi
# # import string

# from typing import List
# from langchain.schema import Document
# # Updated import
# from langchain_community.retrievers import BM25Retriever
# from rank_bm25 import BM25Okapi
# import string

# # Rest of the file remains the same...
# class CustomBM25Retriever(BM25Retriever):
#     def __init__(self, vectorizer, docs, k=4):
#         super().__init__(vectorizer=vectorizer, docs=docs, k=k)
    
#     @classmethod
#     def from_documents(cls, documents: List[Document], k=4):
#         """Create BM25Retriever from documents with legal text preprocessing"""
#         texts = [cls._preprocess_legal_text(doc.page_content) for doc in documents]
        
#         # Tokenize texts for BM25
#         tokenized_texts = [text.split() for text in texts]
        
#         # Create BM25 index
#         bm25 = BM25Okapi(tokenized_texts)
        
#         return cls(vectorizer=bm25, docs=documents, k=k)
    
#     @staticmethod
#     def _preprocess_legal_text(text: str) -> str:
#         """Preprocess legal text for better BM25 performance"""
#         # Convert to lowercase
#         text = text.lower()
        
#         # Remove punctuation except periods (for legal citations)
#         text = text.translate(str.maketrans('', '', string.punctuation.replace('.', '')))
        
#         # Handle legal citations and case names
#         # Add more sophisticated legal text preprocessing here
        
#         return text

from typing import List
from langchain.schema import Document
from langchain_community.retrievers import BM25Retriever
from rank_bm25 import BM25Okapi
import string
import re

class CustomBM25Retriever(BM25Retriever):
    def __init__(self, vectorizer, docs, k=4):
        super().__init__(vectorizer=vectorizer, docs=docs, k=k)
    
    @classmethod
    def from_documents(cls, documents: List[Document], k=4):
        """Create BM25Retriever from documents with legal text preprocessing"""
        texts = [cls._preprocess_legal_text(doc.page_content) for doc in documents]
        
        # Tokenize texts for BM25
        tokenized_texts = [text.split() for text in texts]
        
        # Create BM25 index
        bm25 = BM25Okapi(tokenized_texts)
        
        return cls(vectorizer=bm25, docs=documents, k=k)
    
    @staticmethod
    def _preprocess_legal_text(text: str) -> str:
        """Preprocess legal text for better BM25 performance"""
        # Convert to lowercase
        text = text.lower()
        
        # Enhanced date handling with raw strings
        try:
            # Add keyword variations for dates
            text = re.sub(r'effective\s+date', 'effective date effectivedate contract-date agreement-date', text)
            text = re.sub(r'(\d{1,2})\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+(\d{2,4})', 
                         r'\1 \2 \3 date effective-date contract-date', text)
            
            # Add company name variations
            text = re.sub(r'\bcompany\b', 'company entity corporation organization', text)
            
            # Add date-related terms
            text = re.sub(r'(\d{4})', r'\1 year date', text)
            
            # Remove excessive punctuation but keep important ones
            text = re.sub(r'[^\w\s\.\:\-\/]', ' ', text)
            
            # Normalize whitespace
            text = re.sub(r'\s+', ' ', text)
            
        except Exception as e:
            print(f"Regex error, falling back to simple preprocessing: {e}")
            # Fallback to simple replacements
            text = text.replace('effective date', 'effective date effectivedate contract-date agreement-date')
            text = text.replace('company', 'company entity corporation organization')
            text = text.replace('sep 2025', 'sep 2025 date effective-date september')
            text = text.replace('4 sep 2025', '4 sep 2025 date effective-date september contract-date')
            
            # Remove punctuation except periods and hyphens
            translator = str.maketrans('', '', string.punctuation.replace('.', '').replace('-', ''))
            text = text.translate(translator)
        
        return text.strip()
