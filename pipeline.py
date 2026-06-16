from typing import List
from .planner import build_research_plan, build_search_queries
from .search import web_search, dedupe_results
from .fetcher import fetch_html, extract_text
from .report import keyword_list, extract_facts, build_report
from .schemas import ResearchResponse, ResearchStep, SourceEvidence

def run_research(query: str, max_sources: int = 5, max_results_per_query: int = 5) -> ResearchResponse:
    steps: List[ResearchStep] = []
    plan = build_research_plan(query)
    steps.append(ResearchStep(title="Planning", status="done", detail="Built research plan and search angles."))

    queries = build_search_queries(query)
    steps.append(ResearchStep(title="Searching", status="running", detail="Searching the web for relevant sources."))

    raw_results = []
    for q in queries:
        raw_results.extend(web_search(q, max_results=max_results_per_query))
    results = dedupe_results(raw_results)
    steps.append(ResearchStep(title="Searching", status="done", detail=f"Found {len(results)} unique search results."))

    keywords = keyword_list(query)
    sources: List[SourceEvidence] = []

    steps.append(ResearchStep(title="Reading sources", status="running", detail="Fetching and extracting page content."))
    for result in results:
        if len(sources) >= max_sources:
            break

        html = fetch_html(result.url)
        if not html:
            continue

        text = extract_text(html)
        if len(text) < 200:
            continue

        facts = extract_facts(text, keywords, max_facts=5)
        reliability_note = "General web source"
        sources.append(
            SourceEvidence(
                title=result.title,
                url=result.url,
                snippet=result.snippet[:300] if result.snippet else text[:300],
                extracted_facts=facts[:5],
                reliability_note=reliability_note,
            )
        )

    steps.append(ResearchStep(title="Reading sources", status="done", detail=f"Extracted usable content from {len(sources)} sources."))

    steps.append(ResearchStep(title="Comparing evidence", status="running", detail="Looking for patterns, agreement, and disagreement."))
    summary, key_findings, contradictions, recommendations, confidence_score = build_report(query, sources)
    steps.append(ResearchStep(title="Comparing evidence", status="done", detail="Built report, findings, contradictions, and confidence score."))

    return ResearchResponse(
        query=query,
        plan=plan,
        steps=steps,
        summary=summary,
        key_findings=key_findings,
        contradictions=contradictions,
        recommendations=recommendations,
        confidence_score=confidence_score,
        sources=sources,
    )
