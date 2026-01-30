from pydantic import BaseModel
from typing import Optional, List

class DocumentResponse(BaseModel):
    filename: str
    status: str
    message: str
    doc_id: Optional[str] = None

class QuestionRequest(BaseModel):
    question: str

class AnswerResponse(BaseModel):
    answer: str
    sources: List[str]
