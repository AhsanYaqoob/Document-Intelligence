import os
import pickle
from langchain_community.retrievers import BM25Retriever

VECTOR_DB_DIR = os.getenv("VECTOR_DB_DIR", "./data/vector_db")


class VectorStoreService:
    """
    BM25-based document store.
    - Pure Python keyword search (rank_bm25)
    - No embedding model, no PyTorch, no external API
    - Documents saved as pickle files — works on 512MB free tier
    """

    def _doc_path(self, doc_id: str) -> str:
        return os.path.join(VECTOR_DB_DIR, f"{doc_id}.pkl")

    def save_index(self, chunks, doc_id: str):
        """Saves document chunks to disk as a pickle file."""
        os.makedirs(VECTOR_DB_DIR, exist_ok=True)
        path = self._doc_path(doc_id)
        with open(path, "wb") as f:
            pickle.dump(chunks, f)
        print(f"✅ Saved {len(chunks)} chunks for '{doc_id}'")
        return path

    def load_index(self, doc_id: str):
        """Loads a BM25Retriever for a specific document."""
        path = self._doc_path(doc_id)
        if not os.path.exists(path):
            return None
        with open(path, "rb") as f:
            chunks = pickle.load(f)
        retriever = BM25Retriever.from_documents(chunks, k=5)
        return retriever

