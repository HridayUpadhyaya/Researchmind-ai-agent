import logging
import os
import sys
import time
from contextlib import asynccontextmanager

from fastapi import (
    FastAPI,
    HTTPException,
    Request,
)
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from agent.pipeline import run_research
from agent.planner import (
    build_research_plan,
    build_search_queries,
)
from agent.schemas import ResearchResponse


logging.basicConfig(
    level=os.getenv(
        "LOG_LEVEL",
        "INFO",
    ),
    format=(
        "%(asctime)s | "
        "%(name)s | "
        "%(levelname)s | "
        "%(message)s"
    ),
)

logger = logging.getLogger(__name__)

START_TIME = time.time()


default_origins = (
    "http://localhost:5173,"
    "http://127.0.0.1:5173"
)

ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS",
        default_origins,
    ).split(",")
    if origin.strip()
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(
        "Starting ResearchMind AI server..."
    )

    yield

    logger.info(
        "Shutting down ResearchMind AI server..."
    )


app = FastAPI(
    title="ResearchMind AI",
    version="2.0.0",
    description=(
        "Autonomous multi-step research agent "
        "with evidence-backed reporting and "
        "confidence scoring."
    ),
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(
    request: Request,
    call_next,
):
    started = time.perf_counter()

    response = await call_next(
        request
    )

    process_time = (
        time.perf_counter()
        - started
    )

    response.headers[
        "X-Process-Time"
    ] = f"{process_time:.4f}"

    logger.info(
        "%s %s completed in %.4fs",
        request.method,
        request.url.path,
        process_time,
    )

    return response


class ResearchRequest(BaseModel):

    query: str = Field(
        ...,
        min_length=3,
        max_length=500,
    )

    max_sources: int = Field(
        default=5,
        ge=1,
        le=10,
    )

    max_results_per_query: int = Field(
        default=5,
        ge=1,
        le=10,
    )


class ResearchPreviewRequest(BaseModel):

    query: str = Field(
        ...,
        min_length=3,
        max_length=500,
    )


@app.get("/")
def root():
    return {
        "service": "ResearchMind AI",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/api/health",
    }


@app.get("/api/health")
def health():

    return {
        "status": "ok",
        "service": "ResearchMind AI",
        "version": "2.0.0",
        "uptime_seconds": (
            time.time()
            - START_TIME
        ),
        "python_version": sys.version,
    }


@app.post("/api/research/preview")
def research_preview(
    payload: ResearchPreviewRequest,
):
    """Return the plan and queries without executing research."""

    clean_query = payload.query.strip()

    return {
        "query": clean_query,
        "plan": build_research_plan(
            clean_query
        ),
        "queries": build_search_queries(
            clean_query
        ),
    }


@app.post(
    "/api/research",
    response_model=ResearchResponse,
)
def research(
    payload: ResearchRequest,
):
    """Execute the full research pipeline."""

    clean_query = payload.query.strip()

    try:

        return run_research(
            query=clean_query,
            max_sources=payload.max_sources,
            max_results_per_query=(
                payload.max_results_per_query
            ),
        )

    except Exception as exc:

        logger.exception(
            "Research failure"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                f"Research process failed: "
                f"{exc}"
            ),
        ) from exc
