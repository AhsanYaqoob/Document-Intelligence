import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings

VECTOR_DB_DIR = os.getenv("VECTOR_DB_DIR", "./data/vector_db")

class VectorStoreService:
    _embeddings = None  # Lazy load — only initialised on first use

    @classmethod
    def get_embeddings(cls):
        """
        Use HuggingFace Inference API for embeddings.
        - No local model download
        - No PyTorch, no Rust
        - Free HF token required (hf.co -> Settings -> Tokens)
        """
        if cls._embeddings is None:
            hf_token = os.getenv("HF_TOKEN")
            if not hf_token:
                raise RuntimeError(
                    "HF_TOKEN env variable is missing. "
                    "Get a free token at https://huggingface.co/settings/tokens"
                )
            print("🔄 Initialising HuggingFace Inference API embeddings...")
            cls._embeddings = HuggingFaceInferenceAPIEmbeddings(
                api_key=hf_token,
                model_name="sentence-transformers/all-MiniLM-L6-v2",
            )
            print("✅ Embeddings ready!")
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
