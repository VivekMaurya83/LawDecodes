# import os
# from typing import List
# from langchain.schema import Document
# from langchain.document_loaders import PyPDFLoader, TextLoader
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from config.settings import settings

import os
from typing import List
from langchain.schema import Document
# Updated imports
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from config.settings import settings

# Rest of the file remains the same...


class DocumentProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            separators=["\n\n", "\n", ".", " ", ""]
        )
    
    def process_documents(self, file_paths: List[str]) -> List[Document]:
        """Process multiple documents into chunks"""
        all_documents = []
        
        for file_path in file_paths:
            documents = self._load_document(file_path)
            chunks = self._chunk_documents(documents)
            all_documents.extend(chunks)
        
        return all_documents
    
    def _load_document(self, file_path: str) -> List[Document]:
        """Load a single document based on file type"""
        _, ext = os.path.splitext(file_path)
        
        if ext.lower() == '.pdf':
            loader = PyPDFLoader(file_path)
        elif ext.lower() == '.txt':
            loader = TextLoader(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
        
        documents = loader.load()
        
        # Add source metadata
        for doc in documents:
            doc.metadata.update({
                "source": os.path.basename(file_path),
                "file_path": file_path
            })
        
        return documents
    
    def _chunk_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into chunks with metadata preservation"""
        chunks = []
        
        for doc in documents:
            doc_chunks = self.text_splitter.split_documents([doc])
            
            # Add chunk-specific metadata
            for i, chunk in enumerate(doc_chunks):
                chunk.metadata.update({
                    "chunk_id": f"{doc.metadata.get('source', 'unknown')}_{i}",
                    "chunk_index": i,
                    "total_chunks": len(doc_chunks)
                })
                chunks.append(chunk)
        
        return chunks
    
    def process_text_files(self, directory_path: str) -> List[Document]:
        """Process all text files in a directory"""
        file_paths = []
        
        for file_name in os.listdir(directory_path):
            if file_name.endswith(('.txt', '.pdf')):
                file_paths.append(os.path.join(directory_path, file_name))
        
        return self.process_documents(file_paths)
