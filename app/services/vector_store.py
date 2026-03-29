import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings

VECTOR_DB_DIR = os.getenv("VECTOR_DB_DIR", "./data/vector_db")

class VectorStoreService:
    _embeddings = None  # Lazy load — only initialised on first use

    @classmethod
    def get_embeddings(cls):
        """Lazy-load ONNX-based embeddings (no PyTorch, ~150MB RAM)."""
        if cls._embeddings is None:
            print("🔄 Loading embedding model (ONNX)...")
            # BAAI/bge-small-en-v1.5: 384-dim, ~130MB model file, ONNX runtime
            cls._embeddings = FastEmbedEmbeddings(
                model_name="BAAI/bge-small-en-v1.5"
            )
            print("✅ Embedding model ready!")
        return cls._embeddings

    def save_index(self, chunks, doc_id: str):
        """Creates a FAISS index from chunks and saves it to disk."""
        os.makedirs(VECTOR_DB_DIR, exist_ok=True)
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
