import logging
import time
from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed,
)
from datetime import datetime, timezone
from urllib.parse import urlparse

from .fetcher import (
    extract_text,
    extract_title,
    fetch_html,
)
from .planner import (
    build_research_plan,
    build_search_queries,
    classify_query,
)
from .report import (
    build_report,
    extract_facts,
    keyword_list,
)
from .schemas import (
    ResearchResponse,
    ResearchStep,
    SourceEvidence,
    StepStatus,
)
from .search import search_with_fallback

logger = logging.getLogger(__name__)


def _reliability_score(
    domain: str,
) -> tuple[float, str]:
    """Apply a simple domain-based reliability heuristic."""

    normalized = (
        domain.lower()
        .removeprefix("www.")
    )

    if (
        normalized.endswith(".gov")
        or normalized.endswith(".edu")
    ):
        return (
            0.9,
            "High heuristic score because "
            "the domain is .gov or .edu.",
        )

    if normalized.endswith(".org"):
        return (
            0.7,
            "Medium heuristic score because "
            "the domain is .org.",
        )

    return (
        0.5,
        "Baseline heuristic score; verify "
        "the source independently.",
    )


def run_research(
    query: str,
    max_sources: int = 5,
    max_results_per_query: int = 5,
) -> ResearchResponse:
    """Run the complete ResearchMind pipeline."""

    start_time = time.perf_counter()

    clean_query = query.strip()

    steps: list[ResearchStep] = []

    def add_step(
        title: str,
        detail: str,
        status: StepStatus = StepStatus.DONE,
    ) -> None:

        steps.append(
            ResearchStep(
                title=title,
                status=status,
                detail=detail,
                timestamp=(
                    datetime.now(
                        timezone.utc
                    ).isoformat()
                ),
            )
        )

    add_step(
        "Planning",
        (
            "Classifying query and building "
            f"a plan for: {clean_query}"
        ),
    )

    category = classify_query(
        clean_query
    )

    plan = build_research_plan(
        clean_query
    )

    queries = build_search_queries(
        clean_query
    )

    keywords = keyword_list(
        clean_query
    )

    add_step(
        "Searching",
        (
            f"Running {len(queries)} "
            f"search queries for a "
            f"{category} question."
        ),
        StepStatus.DONE,
    )

    all_results = []

    for search_query in queries:

        all_results.extend(
            search_with_fallback(
                search_query,
                max_results=max_results_per_query,
            )
        )

    seen_urls = set()
    unique_results = []

    for result in all_results:

        if result.url in seen_urls:
            continue

        seen_urls.add(result.url)
        unique_results.append(result)

    total_found = len(
        unique_results
    )

    if not unique_results:

        add_step(
            "Search failed",
            (
                "No search results were returned. "
                "Try a broader or more specific query."
            ),
            StepStatus.FAILED,
        )

        duration = (
            time.perf_counter()
            - start_time
        )

        return ResearchResponse(
            query=clean_query,
            plan=plan,
            steps=steps,
            summary="No search results found.",
            key_findings=[],
            contradictions=[],
            recommendations=[
                "Try broadening or rephrasing the query."
            ],
            confidence_score=0,
            sources=[],
            total_sources_found=0,
            total_sources_used=0,
            research_duration_seconds=duration,
        )

    add_step(
        "Fetching",
        (
            f"Fetching up to {max_sources} "
            "usable sources in parallel."
        ),
    )

    def fetch_and_process(result):

        try:

            html = fetch_html(
                result.url
            )

            if not html:
                return None

            text, word_count = extract_text(
                html
            )

            if word_count < 50:
                return None

            facts = extract_facts(
                text,
                keywords,
            )

            title = (
                extract_title(html)
                or result.title
            )

            domain = (
                result.domain
                or urlparse(
                    result.url
                ).netloc
            )

            (
                reliability_score,
                reliability_note,
            ) = _reliability_score(
                domain
            )

            return SourceEvidence(
                title=title,
                url=result.url,
                snippet=result.snippet,
                extracted_facts=facts,
                domain=domain,
                word_count=word_count,
                reliability_score=(
                    reliability_score
                ),
                reliability_note=(
                    reliability_note
                ),
            )

        except Exception as exc:

            logger.warning(
                "Failed to process %s: %s",
                result.url,
                exc,
            )

            return None

    sources: list[SourceEvidence] = []

    candidates = unique_results[
        :max(
            max_sources * 3,
            max_sources,
        )
    ]

    with ThreadPoolExecutor(
        max_workers=3
    ) as executor:

        futures = {
            executor.submit(
                fetch_and_process,
                result,
            ): result
            for result in candidates
        }

        for future in as_completed(
            futures
        ):

            source = future.result()

            if source:
                sources.append(source)

            if len(sources) >= max_sources:
                break

    add_step(
        "Reporting",
        (
            "Synthesizing findings from "
            f"{len(sources)} usable sources."
        ),
    )

    (
        summary,
        findings,
        contradictions,
        recommendations,
        confidence,
    ) = build_report(
        clean_query,
        sources,
    )

    duration = (
        time.perf_counter()
        - start_time
    )

    add_step(
        "Complete",
        (
            f"Research finished in "
            f"{duration:.2f} seconds."
        ),
    )

    return ResearchResponse(
        query=clean_query,
        plan=plan,
        steps=steps,
        summary=summary,
        key_findings=findings,
        contradictions=contradictions,
        recommendations=recommendations,
        confidence_score=confidence,
        sources=sources,
        total_sources_found=total_found,
        total_sources_used=len(sources),
        research_duration_seconds=duration,
    )
