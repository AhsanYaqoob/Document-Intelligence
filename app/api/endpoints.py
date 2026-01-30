from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Header
import os
from app.services.file_storage import FileStorageService
from app.core.orchestrator import DocumentOrchestrator  # The Brain
from app.models.schemas import DocumentResponse

router = APIRouter()

# Global orchestrator instance
orchestrator = DocumentOrchestrator()

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != os.getenv("APP_API_KEY"):
        raise HTTPException(status_code=403, detail="Invalid API Key")

@router.post("/upload", response_model=DocumentResponse, dependencies=[Depends(verify_api_key)])
async def upload_document(file: UploadFile = File(...)):
    # 1. Save file to disk
    try:
        file_path = FileStorageService.save_file(file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File save failed: {str(e)}")
    
    # 2. Trigger the Multi-Agent Workflow
    try:
        # This one call handles Ingestion AND Indexing
        result = await orchestrator.process_document(file_path, file.filename)
        
        return DocumentResponse(
            filename=file.filename,
            status="Success",
            message=f"Agent workflow complete. Indexed {result['chunks_created']} chunks.",
            doc_id=file.filename # Using filename as ID for simplicity
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent processing failed: {str(e)}")

# Global QA Agent instance
from app.agents.qa_agent import QAAgent
from app.models.schemas import QuestionRequest, AnswerResponse

qa_agent = QAAgent()

@router.post("/ask/{doc_id}", response_model=AnswerResponse, dependencies=[Depends(verify_api_key)])
async def ask_question(doc_id: str, request: QuestionRequest):
    """
    Asks a question based on a specific document ID (the filename).
    """
    try:
        # The QA Agent handles the retrieval and Groq generation
        answer = qa_agent.answer(request.question, doc_id)
        
        return AnswerResponse(
            answer=answer,
            sources=[doc_id]  # In a multi-doc system, this would list all relevant docs
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"QA Agent failed: {str(e)}")
