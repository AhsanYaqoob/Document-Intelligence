import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

VECTOR_DB_DIR = os.getenv("VECTOR_DB_DIR", "./data/vector_db")

class VectorStoreService:
    def __init__(self):
        # Initialize the embedding model once
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    def save_index(self, chunks, doc_id: str):
        """Creates a FAISS index from chunks and saves it to disk."""
        if not os.path.exists(VECTOR_DB_DIR):
            os.makedirs(VECTOR_DB_DIR)
            
        doc_path = os.path.join(VECTOR_DB_DIR, doc_id)
        
        # Create vector store
        db = FAISS.from_documents(chunks, self.embeddings)
        
        # Save locally
        db.save_local(doc_path)
        return doc_path

    def load_index(self, doc_id: str):
        """Loads a FAISS index for a specific document."""
        doc_path = os.path.join(VECTOR_DB_DIR, doc_id)
        
        if not os.path.exists(doc_path):
            return None
            
        # Security warning: Only allow dangerous deserialization for trusted local files
        return FAISS.load_local(doc_path, self.embeddings, allow_dangerous_deserialization=True)
