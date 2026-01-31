# AI Document Intelligence Backend

This project is a high-performance, Multi-Agent Retrieval-Augmented Generation (RAG) system built with FastAPI, LangChain, and Groq. It allows users to upload documents (PDF, Images) and ask intelligent questions about them.

## System Architecture

The system uses an **Agentic Orchestrator Pattern** to manage the document lifecycle:



1.  **Ingestion**: Documents are uploaded and processed by the Ingestion Agent.
2.  **Indexing**: Cleaned text is chunked and vectorized by the Indexing Agent.
3.  **Storage**: Vectors are stored locally using FAISS.
4.  **Retrieval & QA**: User questions trigger the QA Agent to retrieve context and generate answers using Groq's Llama 3 models.

### Agent Responsibilities

* **Ingestion Agent** (`app/agents/ingestion.py`):
    * Detects file type (PDF/Image).
    * Extracts text using `pypdf` or `pytesseract` (OCR).
    * Cleans and normalizes text for processing.

* **Indexing Agent** (`app/agents/indexing.py`):
    * Splits text into semantic chunks (defaults to 1000 chars).
    * Prepares documents for vectorization.

* **QA Agent** (`app/agents/qa_agent.py`):
    * The "Researcher" of the system.
    * Connects to the Groq API (Llama 3.3).
    * Performs similarity search in the local FAISS vector store.
    * Synthesizes the final answer.
## Setup Instructions (Local Development)

### Prerequisites
* Python 3.10+
* Tesseract-OCR (required only for image processing/OCR)

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
* **Endpoint**: `POST /api/v1/upload`
* **Body**: `multipart/form-data` with file
* **Curl**:
    ```bash
    curl -X POST "[http://127.0.0.1:8000/api/v1/upload](http://127.0.0.1:8000/api/v1/upload)" \
         -H "X-API-KEY: my_secret_key" \
         -F "file=@/path/to/contract.pdf"
    ```

### 2. Ask Question
* **Endpoint**: `POST /api/v1/ask/{doc_id}` (use filename as doc_id)
* **Body**: JSON `{"question": "..."}`
* **Curl**:
    ```bash
    curl -X POST "[http://127.0.0.1:8000/api/v1/ask/contract.pdf](http://127.0.0.1:8000/api/v1/ask/contract.pdf)" \
         -H "X-API-KEY: my_secret_key" \
         -H "Content-Type: application/json" \
         -d '{"question": "What is the summary?"}'
    ```

## Architectural Decisions

### Why Multi-Agent Architecture?
This system implements a **separation of concerns** pattern where each agent has a single, well-defined responsibility. This leads to better modularity, scalability, and maintainability.

### Key Design Choices
* **FAISS vs. Cloud Vector DB**: Chose **FAISS (CPU)** for a self-contained architecture without cloud dependencies.
* **Groq Llama 3.3**: Blazing fast inference speed for near real-time answers.
* **Orchestrator Pattern**: Centralized coordination of agent workflows.

### Trade-offs
* **Local FAISS**: Fast but doesn't scale to billions of vectors like cloud solutions.
* **Synchronous Processing**: Current implementation is sync; for production, a task queue (Celery) is recommended.




