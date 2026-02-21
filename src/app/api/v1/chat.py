from fastapi import APIRouter, UploadFile, File
from app.services.ai_service import ai_service

router = APIRouter()

@router.post("/ingest")
async def ingest_knowledge(file: UploadFile = File(...)):
    """
    Upload a PDF to train the AI.
    """
    return await ai_service.ingest_document(file)

@router.post("/ask")
async def ask_ai(query: str):
    """
    Ask a question to the AI about the uploaded PDF.
    """
    response = await ai_service.ask_question(query)
    return {"answer": response}