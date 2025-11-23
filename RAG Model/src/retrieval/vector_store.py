import os
import faiss
import pickle
from typing import List
from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from langchain.embeddings.base import Embeddings
from src.embeddings.embedding_manager import EmbeddingManager
from config.settings import settings

class VectorStoreManager:
    def __init__(self):
        self.embedding_manager = EmbeddingManager()
        self.vector_store_path = os.path.join(
            settings.VECTOR_STORE_PATH, "legal_faiss_store"
        )
    
    def create_vector_store(self, documents: List[Document]) -> FAISS:
        """Create or load FAISS vector store"""
        if self._vector_store_exists():
            return self._load_vector_store()
        else:
            return self._build_vector_store(documents)
    
    def _vector_store_exists(self) -> bool:
        """Check if vector store exists"""
        return os.path.exists(f"{self.vector_store_path}.faiss")
    
    def _load_vector_store(self) -> FAISS:
        """Load existing vector store"""
        # Create a wrapper for the embedding function
        embedding_wrapper = EmbeddingWrapper(self.embedding_manager)
        return FAISS.load_local(
            self.vector_store_path, 
            embedding_wrapper,
            allow_dangerous_deserialization=True
        )
    
    def _build_vector_store(self, documents: List[Document]) -> FAISS:
        """Build new vector store from documents"""
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        
        # Create a wrapper for the embedding function
        embedding_wrapper = EmbeddingWrapper(self.embedding_manager)
        
        # Create FAISS vector store
        vector_store = FAISS.from_texts(
            texts=texts,
            embedding=embedding_wrapper,
            metadatas=metadatas
        )
        
        # Save vector store
        os.makedirs(settings.VECTOR_STORE_PATH, exist_ok=True)
        vector_store.save_local(self.vector_store_path)
        
        return vector_store
    
    def add_documents(self, documents: List[Document]):
        """Add new documents to existing vector store"""
        vector_store = self._load_vector_store()
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        
        vector_store.add_texts(texts, metadatas)
        vector_store.save_local(self.vector_store_path)

class EmbeddingWrapper(Embeddings):
    """Wrapper to make EmbeddingManager compatible with LangChain"""
    
    def __init__(self, embedding_manager: EmbeddingManager):
        self.embedding_manager = embedding_manager
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed documents using the embedding manager"""
        embeddings = self.embedding_manager.embed_documents(texts)
        return embeddings.tolist()
    
    def embed_query(self, text: str) -> List[float]:
        """Embed a single query"""
        embedding = self.embedding_manager.embed_query(text)
        return embedding.tolist()
