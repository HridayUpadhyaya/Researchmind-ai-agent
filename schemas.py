from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class StepStatus(str, Enum):
    """Status of a research pipeline step."""

    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


class SearchResult(BaseModel):
    """A result returned by the web search provider."""

    title: str
    url: str
    snippet: str = ""
    domain: str = ""


class ResearchStep(BaseModel):
    """A discrete step executed by the research pipeline."""

    title: str
    status: StepStatus = StepStatus.PENDING
    detail: str
    timestamp: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class SourceEvidence(BaseModel):
    """Evidence extracted from a single web page."""

    title: str
    url: str
    snippet: str = ""
    extracted_facts: List[str] = Field(default_factory=list)
    reliability_note: str = ""
    domain: str = ""
    word_count: int = 0
    reliability_score: float = Field(default=0.0, ge=0.0, le=1.0)

    model_config = ConfigDict(from_attributes=True)


class ResearchResponse(BaseModel):
    """Final response returned by the research API."""

    query: str
    plan: List[str]
    steps: List[ResearchStep]
    summary: str
    key_findings: List[str]
    contradictions: List[str]
    recommendations: List[str]
    confidence_score: int = Field(ge=0, le=100)
    sources: List[SourceEvidence]

    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    total_sources_found: int = 0
    total_sources_used: int = 0
    research_duration_seconds: float = 0.0

    model_config = ConfigDict(from_attributes=True)
