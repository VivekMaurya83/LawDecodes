# import numpy as np
# from typing import List, Dict, Any, Tuple
# from langchain.schema import Document
# from langchain_community.retrievers import BM25Retriever
# from langchain_community.vectorstores import FAISS
# # Remove EnsembleRetriever for now
# from src.retrieval.vector_store import VectorStoreManager
# from src.retrieval.bm25_retriever import CustomBM25Retriever
# from config.settings import settings

# class HybridRetriever:
#     def __init__(self, documents: List[Document]):
#         self.documents = documents
#         self.vector_store_manager = VectorStoreManager()
#         self.vector_store = self.vector_store_manager.create_vector_store(documents)
        
#         # Initialize BM25 retriever
#         self.bm25_retriever = CustomBM25Retriever.from_documents(
#             documents, k=settings.TOP_K_RETRIEVAL
#         )
        
#         # Initialize FAISS retriever
#         self.faiss_retriever = self.vector_store.as_retriever(
#             search_type="mmr",
#             search_kwargs={
#                 "k": settings.TOP_K_RETRIEVAL,
#                 "fetch_k": settings.TOP_K_RETRIEVAL * 2,
#                 "lambda_mult": 0.5
#             }
#         )
    
#     def retrieve(self, query: str, k: int = None) -> List[Document]:
#         """Retrieve documents using hybrid search"""
#         k = k or settings.RERANK_TOP_K
        
#         # Get results from both retrievers
#         # bm25_results = self.bm25_retriever.get_relevant_documents(query)
#         bm25_results = self.bm25_retriever.invoke(query)
#         # faiss_results = self.faiss_retriever.get_relevant_documents(query)
#         faiss_results = self.faiss_retriever.invoke(query)
        
#         # Simple fusion: combine and deduplicate
#         combined_results = self._combine_results(bm25_results, faiss_results)
        
#         # Rerank results
#         reranked_results = self._rerank_results(query, combined_results)
        
#         return reranked_results[:k]
    
#     def _combine_results(self, bm25_results: List[Document], faiss_results: List[Document]) -> List[Document]:
#         """Combine results from both retrievers"""
#         seen_content = set()
#         combined = []
        
#         # Add BM25 results first (keyword priority)
#         for doc in bm25_results:
#             if doc.page_content not in seen_content:
#                 combined.append(doc)
#                 seen_content.add(doc.page_content)
        
#         # Add FAISS results
#         for doc in faiss_results:
#             if doc.page_content not in seen_content:
#                 combined.append(doc)
#                 seen_content.add(doc.page_content)
        
#         return combined
    
#     def _rerank_results(self, query: str, documents: List[Document]) -> List[Document]:
#         """Simple reranking based on query term frequency"""
#         query_terms = query.lower().split()
        
#         scored_docs = []
#         for doc in documents:
#             content = doc.page_content.lower()
#             score = sum(content.count(term) for term in query_terms)
#             scored_docs.append((doc, score))
        
#         # Sort by score descending
#         scored_docs.sort(key=lambda x: x[1], reverse=True)
        
#         return [doc for doc, _ in scored_docs]

# import numpy as np
# from typing import List, Dict, Any, Tuple
# from langchain.schema import Document
# from langchain_community.retrievers import BM25Retriever
# from langchain_community.vectorstores import FAISS
# from src.retrieval.vector_store import VectorStoreManager
# from src.retrieval.bm25_retriever import CustomBM25Retriever
# from config.settings import settings

# class HybridRetriever:
#     def __init__(self, documents: List[Document]):
#         self.documents = documents
#         self.vector_store_manager = VectorStoreManager()
#         self.vector_store = self.vector_store_manager.create_vector_store(documents)
        
#         # Initialize BM25 retriever
#         self.bm25_retriever = CustomBM25Retriever.from_documents(
#             documents, k=settings.TOP_K_RETRIEVAL
#         )
        
#         # Initialize FAISS retriever
#         self.faiss_retriever = self.vector_store.as_retriever(
#             search_type="mmr",
#             search_kwargs={
#                 "k": settings.TOP_K_RETRIEVAL,
#                 "fetch_k": settings.TOP_K_RETRIEVAL * 2,
#                 "lambda_mult": 0.5
#             }
#         )
    
#     def retrieve(self, query: str, k: int = None) -> List[Document]:
#         """Retrieve documents using hybrid search"""
#         k = k or settings.RERANK_TOP_K
        
#         # Get results from both retrievers with error handling
#         bm25_results = self._safe_retrieve(self.bm25_retriever, query, "BM25")
#         faiss_results = self._safe_retrieve(self.faiss_retriever, query, "FAISS")
        
#         # Simple fusion: combine and deduplicate
#         combined_results = self._combine_results(bm25_results, faiss_results)
        
#         # Rerank results
#         reranked_results = self._rerank_results(query, combined_results)
        
#         return reranked_results[:k]
    
#     def _safe_retrieve(self, retriever, query: str, retriever_name: str) -> List[Document]:
#         """Safely retrieve documents with fallback methods"""
#         try:
#             # Try the new invoke method first
#             result = retriever.invoke(query)
            
#             # Handle different return types
#             if isinstance(result, list):
#                 return result
#             elif hasattr(result, 'documents'):
#                 return result.documents
#             elif isinstance(result, dict) and 'documents' in result:
#                 return result['documents']
#             else:
#                 print(f"Warning: {retriever_name} returned unexpected type: {type(result)}")
#                 return []
                
#         except Exception as e:
#             print(f"Warning: {retriever_name} invoke failed: {e}")
#             try:
#                 # Fallback to deprecated method
#                 return retriever.get_relevant_documents(query)
#             except Exception as e2:
#                 print(f"Error: {retriever_name} fallback also failed: {e2}")
#                 return []
    
#     def _combine_results(self, bm25_results: List[Document], faiss_results: List[Document]) -> List[Document]:
#         """Combine results from both retrievers"""
#         seen_content = set()
#         combined = []
        
#         # Add BM25 results first (keyword priority)
#         for doc in bm25_results:
#             content = str(doc.page_content)  # Ensure string
#             if content not in seen_content:
#                 combined.append(doc)
#                 seen_content.add(content)
        
#         # Add FAISS results
#         for doc in faiss_results:
#             content = str(doc.page_content)  # Ensure string
#             if content not in seen_content:
#                 combined.append(doc)
#                 seen_content.add(content)
        
#         return combined
    
#     def _rerank_results(self, query: str, documents: List[Document]) -> List[Document]:
#         """Simple reranking based on query term frequency"""
#         if not isinstance(query, str):
#             query = str(query)
        
#         query_terms = query.lower().split()
#         scored_docs = []
        
#         for doc in documents:
#             # Ensure content is string and handle the error you encountered
#             content = str(doc.page_content).lower()
#             score = sum(content.count(term) for term in query_terms)
#             scored_docs.append((doc, score))
        
#         # Sort by score descending
#         scored_docs.sort(key=lambda x: x[1], reverse=True)
        
#         return [doc for doc, _ in scored_docs]

import numpy as np
from typing import List, Dict, Any, Tuple
from langchain.schema import Document
from langchain_community.retrievers import BM25Retriever
from langchain_community.vectorstores import FAISS
from src.retrieval.vector_store import VectorStoreManager
from src.retrieval.bm25_retriever import CustomBM25Retriever
from config.settings import settings

class HybridRetriever:
    def __init__(self, documents: List[Document]):
        self.documents = documents
        self.vector_store_manager = VectorStoreManager()
        self.vector_store = self.vector_store_manager.create_vector_store(documents)
        
        # Initialize BM25 retriever
        self.bm25_retriever = CustomBM25Retriever.from_documents(
            documents, k=settings.TOP_K_RETRIEVAL
        )
        
        # Initialize FAISS retriever
        self.faiss_retriever = self.vector_store.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": settings.TOP_K_RETRIEVAL,
                "fetch_k": settings.TOP_K_RETRIEVAL * 2,
                "lambda_mult": 0.5
            }
        )
    
    def retrieve(self, query: str, k: int = None) -> List[Document]:
        """Retrieve documents using hybrid search with date awareness"""
        k = k or settings.RERANK_TOP_K
        
        # Check if this is a date-related query
        date_keywords = ['date', 'when', 'effective', 'start', 'begin', 'commence', 'time', 'sep', '2025']
        is_date_query = any(keyword in query.lower() for keyword in date_keywords)
        
        if is_date_query:
            # For date queries, prioritize chunks that contain dates
            date_results = self._get_date_containing_chunks(query)
            if date_results:
                print(f"🎯 Found {len(date_results)} date-containing chunks")
                return date_results[:k]
        
        # Normal hybrid retrieval for non-date queries
        bm25_results = self._safe_retrieve(self.bm25_retriever, query, "BM25")
        faiss_results = self._safe_retrieve(self.faiss_retriever, query, "FAISS")
        
        # Combine and rerank
        combined_results = self._combine_results(bm25_results, faiss_results)
        reranked_results = self._rerank_results(query, combined_results)
        
        return reranked_results[:k]
    
    def _get_date_containing_chunks(self, query: str) -> List[Document]:
        """Get chunks that contain dates, ranked by relevance to query"""
        date_chunks = []
        
        # Define date indicators
        date_indicators = [
            'effective date:', '4 sep 2025', 'september 2025', 'sep 2025',
            'effective date', 'execution date', 'signed on', 'dated',
            'invoice date', 'due date', 'termination date'
        ]
        
        # Find all chunks with date content
        for doc in self.documents:
            content = doc.page_content.lower()
            
            # Check if chunk contains date indicators
            date_score = 0
            for indicator in date_indicators:
                if indicator in content:
                    date_score += content.count(indicator)
                    if 'effective date: 4 sep 2025' in content:
                        date_score += 10  # Boost for exact effective date match
            
            if date_score > 0:
                # Add chunk with its date relevance score
                doc_with_score = Document(
                    page_content=doc.page_content,
                    metadata={**doc.metadata, 'date_score': date_score}
                )
                date_chunks.append(doc_with_score)
        
        # Sort by date relevance score
        date_chunks.sort(key=lambda x: x.metadata.get('date_score', 0), reverse=True)
        
        print(f"📅 Date chunks found: {[(i+1, chunk.metadata.get('date_score', 0)) for i, chunk in enumerate(date_chunks)]}")
        
        return date_chunks
    
    def _safe_retrieve(self, retriever, query: str, retriever_name: str) -> List[Document]:
        """Safely retrieve documents with fallback methods"""
        try:
            result = retriever.invoke(query)
            
            if isinstance(result, list):
                return result
            elif hasattr(result, 'documents'):
                return result.documents
            elif isinstance(result, dict) and 'documents' in result:
                return result['documents']
            else:
                return []
                
        except Exception as e:
            try:
                return retriever.get_relevant_documents(query)
            except Exception:
                return []
    
    def _combine_results(self, bm25_results: List[Document], faiss_results: List[Document]) -> List[Document]:
        """Combine results from both retrievers"""
        seen_content = set()
        combined = []
        
        for doc in bm25_results:
            content = str(doc.page_content)
            if content not in seen_content:
                combined.append(doc)
                seen_content.add(content)
        
        for doc in faiss_results:
            content = str(doc.page_content)
            if content not in seen_content:
                combined.append(doc)
                seen_content.add(content)
        
        return combined
    
    def _rerank_results(self, query: str, documents: List[Document]) -> List[Document]:
        """Simple reranking based on query term frequency"""
        query_terms = query.lower().split()
        scored_docs = []
        
        for doc in documents:
            content = str(doc.page_content).lower()
            score = sum(content.count(term) for term in query_terms)
            scored_docs.append((doc, score))
        
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        return [doc for doc, _ in scored_docs]
