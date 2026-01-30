import os
from fastapi import FastAPI, Depends, HTTPException, Header
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="AI Document Intelligence Backend")

# Security: Check for X-API-KEY in headers
async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != os.getenv("APP_API_KEY"):
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return x_api_key

@app.get("/health", dependencies=[Depends(verify_api_key)])
async def health_check():
    return {"status": "online", "engine": "Groq AI"}

# Include our routes
from app.api.endpoints import router as api_router
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def home():
    return {"message": "Server is running. Use /api/v1/upload to start."}
