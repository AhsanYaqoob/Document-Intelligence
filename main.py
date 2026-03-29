import os
import asyncio
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv

load_dotenv()

# Create required directories at startup
os.makedirs(os.getenv("UPLOAD_DIR", "./data/uploads"), exist_ok=True)
os.makedirs(os.getenv("VECTOR_DB_DIR", "./data/vector_db"), exist_ok=True)

app = FastAPI(title="AI Document Intelligence Backend")

# Serve frontend static assets (css, js)
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Security: Check for X-API-KEY in headers
async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != os.getenv("APP_API_KEY"):
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return x_api_key

# Quick health check without requiring embedding model
@app.get("/health-quick")
async def quick_health():
    return {"status": "online", "version": "1.0"}

@app.get("/health", dependencies=[Depends(verify_api_key)])
async def health_check():
    return {"status": "online", "engine": "Groq AI"}

# Warm up embeddings in background (non-blocking)
@app.on_event("startup")
async def startup_warmup():
    """Load embeddings after app starts so port is detected immediately."""
    asyncio.create_task(warmup_embeddings())

async def warmup_embeddings():
    """Load embeddings asynchronously to avoid blocking startup."""
    try:
        from app.services.vector_store import VectorStoreService
        print("⏳ Warming up embedding model in background...")
        VectorStoreService.get_embeddings()
        print("✅ Embedding model ready for document processing!")
    except Exception as e:
        print(f"⚠️ Warmup error: {e}")

# Include our routes
from app.api.endpoints import router as api_router
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def home():
    return FileResponse("frontend/index.html")
