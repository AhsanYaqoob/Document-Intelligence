# AI Document Intelligence Backend

This project is a high-performance, Multi-Agent Retrieval-Augmented Generation (RAG) system built with FastAPI, LangChain, and Groq. It allows users to upload documents (PDF, Images) and ask intelligent questions about them.

## System Architecture

The system uses an **Agentic Orchestrator Pattern** to manage the document lifecycle:

1.  **Ingestion**: Documents are uploaded and processed by the Ingestion Agent.
2.  **Indexing**: Cleaned text is chunked and vectorized by the Indexing Agent.
3.  **Storage**: Vectors are stored locally using FAISS.
4.  **Retrieval & QA**: User questions trigger the QA Agent to retrieve context and generate answers using Groq's Llama 3 models.

### Agent Responsibilities

*   **Ingestion Agent** (`app/agents/ingestion.py`):
    *   Detects file type (PDF/Image).
    *   Extracts text using `pypdf` or `pytesseract` (OCR).
    *   Cleans and normalizes text for processing.

*   **Indexing Agent** (`app/agents/indexing.py`):
    *   Splits text into semantic chunks (defaults to 1000 chars).
    *   Prepares documents for vectorization.

*   **QA Agent** (`app/agents/qa_agent.py`):
    *   The "Researcher" of the system.
    *   Connects to the Groq API (Llama 3.3).
    *   Performs similarity search in the local FAISS vector store.
    *   Synthesizes the final answer.

## Running with Docker

**The easiest way to run the entire multi-agent system:**

```bash
docker-compose up --build
```

This single command will:
- Build the Docker image with all dependencies
- Start the FastAPI server on port 8000
- Persist uploaded files and vector databases to your local machine
- Automatically restart on failures

Access the API at: `http://127.0.0.1:8000/docs`

> **Note**: While the system is optimized for local development using the provided setup instructions below, I have included a Docker configuration for production-ready deployment. This ensures the environment remains consistent across different stages of the development lifecycle and simplifies deployment to cloud platforms.

## Setup Instructions (Local Development)

### Prerequisites
*   Python 3.10+
*   Tesseract-OCR (for image processing)

### Installation

1.  **Create Virtual Environment**:
    ```bash
    python -m venv venv
    .\venv\Scripts\activate  # Windows
    # source venv/bin/activate  # Mac/Linux
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Environment Variables**:
    Create a `.env` file in the root directory:
    ```ini
    GROQ_API_KEY=your_groq_key
    GROQ_MODEL_NAME=llama-3.3-70b-versatile
    APP_API_KEY=my_secret_key
    ```

4.  **Run the Server**:
    ```bash
    uvicorn main:app --reload
    ```

## API Guide

### Authentication
All requests require the header: `X-API-KEY: my_secret_key`

### 1. Upload Document
*   **Endpoint**: `POST /api/v1/upload`
*   **Body**: `multipart/form-data` with file
*   **Curl**:
    ```bash
    curl -X POST "http://127.0.0.1:8000/api/v1/upload" \
         -H "X-API-KEY: my_secret_key" \
         -F "file=@/path/to/contract.pdf"
    ```

### 2. Ask Question
*   **Endpoint**: `POST /api/v1/ask/{doc_id}` (use filename as doc_id)
*   **Body**: JSON `{"question": "..."}`
*   **Curl**:
    ```bash
    curl -X POST "http://127.0.0.1:8000/api/v1/ask/contract.pdf" \
         -H "X-API-KEY: my_secret_key" \
         -H "Content-Type: application/json" \
         -d '{"question": "What is the summary?"}'
    ```

## Architectural Decisions

### Why Multi-Agent Architecture?

This system implements a **separation of concerns** pattern where each agent has a single, well-defined responsibility:

1.  **Modularity**: Each agent can be tested, updated, or replaced independently without affecting others.
2.  **Scalability**: Agents can be distributed across different services or containers in production.
3.  **Maintainability**: Clear boundaries make debugging and feature additions straightforward.

### Key Design Choices

*   **FAISS vs. Cloud Vector DB**: We chose **FAISS (CPU)** for this implementation to keep the architecture self-contained and easy to deploy locally without external cloud dependencies (like Pinecone). It offers extremely fast retrieval for small-to-medium datasets and eliminates API costs.

*   **Groq Llama 3.3**: We utilize Groq for its blazing fast token inference speed (up to 10x faster than traditional cloud LLMs), ensuring near real-time answers. The 70B parameter model provides high-quality reasoning without sacrificing performance.

*   **Local Processing**: All ingestion and chunking happen locally, ensuring data privacy before the retrieval step. Sensitive documents never leave your infrastructure until the final QA step (which only sends relevant context, not entire documents).

*   **Orchestrator Pattern**: The `DocumentOrchestrator` acts as the "brain" that coordinates agent workflows, making it easy to add new agents (e.g., summarization, translation) or modify the processing pipeline without touching individual agents.

### Trade-offs

*   **Local FAISS**: While excellent for prototypes and small-to-medium datasets, FAISS doesn't scale to billions of vectors like cloud solutions. For production at scale, consider migrating to Pinecone or Weaviate.
*   **Synchronous Processing**: Current implementation processes documents synchronously. For production, consider adding a task queue (Celery/Redis) for background processing of large files.
*   **Single-Document Scope**: Each query targets one document. Future enhancement could implement cross-document search and synthesis.
