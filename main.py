from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from agent.pipeline import run_research
from agent.schemas import ResearchResponse

app = FastAPI(title="ResearchMind AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ResearchRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=500)
    max_sources: int = Field(default=5, ge=1, le=10)
    max_results_per_query: int = Field(default=5, ge=1, le=10)

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "ResearchMind AI"}

@app.post("/api/research", response_model=ResearchResponse)
def research(payload: ResearchRequest):
    return run_research(
        query=payload.query,
        max_sources=payload.max_sources,
        max_results_per_query=payload.max_results_per_query,
    )
