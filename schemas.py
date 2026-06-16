from pydantic import BaseModel, Field
from typing import List

class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str = ""

class ResearchStep(BaseModel):
    title: str
    status: str
    detail: str

class SourceEvidence(BaseModel):
    title: str
    url: str
    snippet: str
    extracted_facts: List[str] = Field(default_factory=list)
    reliability_note: str = ""

class ResearchResponse(BaseModel):
    query: str
    plan: List[str]
    steps: List[ResearchStep]
    summary: str
    key_findings: List[str]
    contradictions: List[str]
    recommendations: List[str]
    confidence_score: int
    sources: List[SourceEvidence]
