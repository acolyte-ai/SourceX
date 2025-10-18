from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import asyncio
import json
import os
from datetime import datetime

app = FastAPI(
    title="Crisis Fact-Check API",
    version="1.0.0",
    description="AI-powered news verification and fact-checking API",
    docs_url="/docs" if os.getenv("APP_ENV") != "production" else None,
    redoc_url="/redoc" if os.getenv("APP_ENV") != "production" else None
)

# Configure CORS based on environment
allowed_origins = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# ============================================================================
# PYDANTIC MODELS
# ============================================================================  
class FactCheckRequest(BaseModel):
    claim_text: str
    source_url: Optional[str] = None
    crisis_category: Optional[str] = "general"

class HealthCheck(BaseModel):
    status: str
    timestamp: str

# ============================================================================
# STREAMING GENERATOR
# ============================================================================


# ============================================================================
# API ENDPOINTS
# ============================================================================

from factcheck_code import FactCheckSystem

@app.post("/fact-check")
async def fact_check(request: FactCheckRequest):
    """Streaming endpoint for real-time fact-checking updates"""
    fact_checker = FactCheckSystem()
    result = fact_checker.check_claim(
        claim_text=request.claim_text,
        source_url=request.source_url
    )
    return result

@app.get("/stats")
async def get_stats():
    """Get system statistics"""
    from factcheck_code import Config
    
    return {
        "agents": {
            "active": 8,
            "total": 8
        },
        "model": {
            "provider": Config.DEFAULT_MODEL,
            "id": Config.ANTHROPIC_MODEL_ID if Config.DEFAULT_MODEL == "anthropic" else Config.OPENAI_MODEL_ID
        }
    }

@app.get("/health", response_model=HealthCheck)
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)