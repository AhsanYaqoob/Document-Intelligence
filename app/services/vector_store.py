import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

VECTOR_DB_DIR = os.getenv("VECTOR_DB_DIR", "./data/vector_db")

class VectorStoreService:
    _embeddings = None  # Lazy load

    @classmethod
    def get_embeddings(cls):
        """Lazy-load embeddings on first use to avoid startup timeout."""
        if cls._embeddings is None:
            print("🔄 Downloading embedding model... (first time only)")
            # Smaller, faster model: 384-dim instead of 768-dim
            cls._embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True}
            )
            print("✅ Embedding model loaded!")
        return cls._embeddings

    def save_index(self, chunks, doc_id: str):
        """Creates a FAISS index from chunks and saves it to disk."""
        if not os.path.exists(VECTOR_DB_DIR):
            os.makedirs(VECTOR_DB_DIR)

        doc_path = os.path.join(VECTOR_DB_DIR, doc_id)
        embeddings = self.get_embeddings()
        db = FAISS.from_documents(chunks, embeddings)
        db.save_local(doc_path)
        return doc_path

    def load_index(self, doc_id: str):
        """Loads a FAISS index for a specific document."""
        doc_path = os.path.join(VECTOR_DB_DIR, doc_id)
        
        if not os.path.exists(doc_path):
            return None

        embeddings = self.get_embeddings()
        return FAISS.load_local(
            doc_path, embeddings, allow_dangerous_deserialization=True
        )
