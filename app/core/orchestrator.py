from app.agents.ingestion import IngestionAgent
from app.agents.indexing import IndexingAgent
from app.services.vector_store import VectorStoreService

class DocumentOrchestrator:
    def __init__(self):
        self.ingestion_agent = IngestionAgent()
        self.indexing_agent = IndexingAgent()
        self.vector_store = VectorStoreService()

    async def process_document(self, file_path: str, filename: str):
        """
        Orchestrates the flow:
        1. Ingestion Agent -> Extracts Text
        2. Indexing Agent -> Chunks Text
        3. Vector Store -> Embeds & Saves
        """
        # Step 1: Ingestion
        print(f"Orchestrator: Starting ingestion for {filename}...")
        raw_text = self.ingestion_agent.process(file_path)
        
        # Step 2: Indexing
        print(f"Orchestrator: Indexing {len(raw_text)} chars...")
        chunks = self.indexing_agent.process(raw_text)
        
        # Step 3: Storage
        print(f"Orchestrator: Saving {len(chunks)} chunks to Vector DB...")
        self.vector_store.save_index(chunks, filename)
        
        return {
            "extract_length": len(raw_text),
            "chunks_created": len(chunks)
        }
