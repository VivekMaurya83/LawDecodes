# Test script to verify installation
import sys
import os

def test_imports():
    try:
        import langchain
        print("✓ LangChain imported successfully")
        
        import langchain_google_genai
        print("✓ LangChain Google GenAI imported successfully")
        
        import sentence_transformers
        print("✓ Sentence Transformers imported successfully")
        
        import faiss
        print("✓ FAISS imported successfully")
        
        import numpy as np
        print(f"✓ NumPy {np.__version__} imported successfully")
        
        from rank_bm25 import BM25Okapi
        print("✓ BM25 imported successfully")
        
        print("\n🎉 All packages installed correctly!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_api_key():
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key and api_key != "your_google_api_key_here":
        print("✓ Google API key found in .env file")
        return True
    else:
        print("❌ Google API key not found or not set properly")
        print("Please add your API key to the .env file")
        return False

if __name__ == "__main__":
    print("Testing Legal RAG Chatbot Installation...")
    print("=" * 50)
    
    imports_ok = test_imports()
    api_key_ok = test_api_key()
    
    if imports_ok and api_key_ok:
        print("\n🚀 Ready to run your Legal RAG Chatbot!")
    else:
        print("\n⚠️ Please fix the issues above before proceeding")
