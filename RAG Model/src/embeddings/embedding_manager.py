import os
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Union
import pickle
from config.settings import settings

class EmbeddingManager:
    def __init__(self):
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
        self.cache_path = os.path.join(settings.CACHE_PATH, "embeddings.pkl")
        self.embedding_cache = self._load_cache()
    
    def _load_cache(self) -> dict:
        """Load embedding cache from disk"""
        if os.path.exists(self.cache_path):
            with open(self.cache_path, 'rb') as f:
                return pickle.load(f)
        return {}
    
    def _save_cache(self):
        """Save embedding cache to disk"""
        os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
        with open(self.cache_path, 'wb') as f:
            pickle.dump(self.embedding_cache, f)
    
    def embed_documents(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for documents with caching"""
        embeddings = []
        new_embeddings = []
        
        for text in texts:
            text_hash = hash(text)
            if text_hash in self.embedding_cache:
                embeddings.append(self.embedding_cache[text_hash])
            else:
                # Use encode method instead of embed_documents
                embedding = self.model.encode(text)
                embeddings.append(embedding)
                self.embedding_cache[text_hash] = embedding
                new_embeddings.append(text)
        
        if new_embeddings:
            self._save_cache()
        
        # Convert to numpy array with explicit dtype for NumPy 2.x compatibility
        return np.array(embeddings, dtype=np.float32)
    
    def embed_query(self, query: str) -> np.ndarray:
        """Generate embedding for a single query"""
        return self.model.encode(query).astype(np.float32)
