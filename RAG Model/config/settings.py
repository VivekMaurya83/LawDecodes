# import os
# from dotenv import load_dotenv

# load_dotenv()

# class Settings:
#     # API Keys
#     GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    
#     # Model Configuration
#     EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
#     LLM_MODEL = "gemini-2.5-pro"
#     EMBEDDING_DIMENSION = 384
    
#     # Retrieval Configuration
#     CHUNK_SIZE = 400
#     CHUNK_OVERLAP = 80
#     TOP_K_RETRIEVAL = 15
#     RERANK_TOP_K = 5
    
#     # Hybrid Search Weights
#     BM25_WEIGHT = 0.4
#     SEMANTIC_WEIGHT = 0.6
    
#     # Memory Configuration
#     MAX_MEMORY_TOKENS = 2000
#     MEMORY_SUMMARY_THRESHOLD = 1500
    
#     # File Paths
#     DATA_PATH = "data/"
#     RAW_DATA_PATH = "data/raw/"
#     PROCESSED_DATA_PATH = "data/processed/"
#     VECTOR_STORE_PATH = "data/vector_stores/"
#     CACHE_PATH = "cache/"
#     LOGS_PATH = "logs/"
    
#     # Citation Configuration
#     MIN_CITATION_SCORE = 0.7
#     MAX_SOURCES_PER_RESPONSE = 5

# settings = Settings()

import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # API Keys
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    
    # Model Configuration
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    LLM_MODEL = "gemini-2.5-flash"
    EMBEDDING_DIMENSION = 384
    
    # Retrieval Configuration - UPDATED FOR BETTER PERFORMANCE
    CHUNK_SIZE = 800  # Increased from 400
    CHUNK_OVERLAP = 200  # Increased from 80
    TOP_K_RETRIEVAL = 10  # Reduced from 15
    RERANK_TOP_K = 5
    
    # Hybrid Search Weights
    BM25_WEIGHT = 0.6  # Increased for exact keyword matching
    SEMANTIC_WEIGHT = 0.4
    
    # Memory Configuration
    MAX_MEMORY_TOKENS = 2000
    MEMORY_SUMMARY_THRESHOLD = 1500
    
    # File Paths
    DATA_PATH = "data/"
    RAW_DATA_PATH = "data/raw/"
    PROCESSED_DATA_PATH = "data/processed/"
    VECTOR_STORE_PATH = "data/vector_stores/"
    CACHE_PATH = "cache/"
    LOGS_PATH = "logs/"
    
    # Citation Configuration
    MIN_CITATION_SCORE = 0.5  # Reduced for better matches
    MAX_SOURCES_PER_RESPONSE = 3  # Reduced for cleaner output

settings = Settings()
