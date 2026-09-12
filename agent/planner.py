import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


QUERY_CATEGORIES = (
    "comparison",
    "how_to",
    "causal",
    "opinion",
    "definition",
    "recent",
    "factual",
)


def classify_query(query: str) -> str:
    """Classify a research query using transparent keyword rules."""

    lower = query.lower()

    if any(
        word in lower
        for word in [
            "best",
            "compare",
            "vs",
            "versus",
            "which",
        ]
    ):
        return "comparison"

    if any(
        word in lower
        for word in [
            "how",
            "steps",
            "process",
            "build",
            "make",
            "guide",
        ]
    ):
        return "how_to"

    if any(
        word in lower
        for word in [
            "why",
            "cause",
            "because",
            "reason",
            "impact",
        ]
    ):
        return "causal"

    if any(
        word in lower
        for word in [
            "should",
            "worth",
            "better",
            "opinion",
        ]
    ):
        return "opinion"

    if any(
        word in lower
        for word in [
            "what is",
            "define",
            "meaning",
        ]
    ):
        return "definition"

    if any(
        word in lower
        for word in [
            "2024",
            "2025",
            "2026",
            "latest",
            "recent",
        ]
    ):
        return "recent"

    return "factual"


def build_research_plan(query: str) -> List[str]:
    """Build a numbered research plan based on query type."""

    clean_query = query.strip().rstrip("?")
    category = classify_query(query)

    plan = [
        f"1. Understand the core question: {clean_query}",
        "2. Find multiple sources with different perspectives",
    ]

    if category == "comparison":
        plan.append(
            "3. Compare options, tradeoffs, and decision criteria"
        )

    elif category == "how_to":
        plan.append(
            "3. Break the topic into actionable sub-questions"
        )

    elif category == "causal":
        plan.append(
            "3. Search for explanations, causes, and evidence"
        )

    elif category == "recent":
        plan.append(
            "3. Prioritize the most recent evidence available"
        )

    elif category == "opinion":
        plan.append(
            "3. Gather diverse perspectives and expert opinions"
        )

    elif category == "definition":
        plan.append(
            "3. Establish clear definitions and context"
        )

    else:
        plan.append(
            "3. Identify the main facts, claims, and context"
        )

    plan.extend(
        [
            "4. Extract facts, claims, and numbers",
            "5. Compare agreement and disagreement across sources",
            "6. Write a balanced answer with citations and caveats",
        ]
    )

    return plan


def build_search_queries(query: str) -> List[str]:
    """Generate a diverse set of up to six search queries."""

    base = query.strip().rstrip("?")
    category = classify_query(query)

    queries = [base]

    if category == "comparison":
        queries.extend(
            [
                f"{base} pros cons",
                f"{base} comparison",
            ]
        )

    elif category == "how_to":
        queries.extend(
            [
                f"{base} step by step guide",
                f"{base} tutorial",
            ]
        )

    elif category == "recent":
        queries.extend(
            [
                f"{base} latest 2026",
                f"{base} recent news",
            ]
        )

    elif category == "causal":
        queries.extend(
            [
                f"{base} causes evidence",
                f"{base} research findings",
            ]
        )

    queries.extend(
        [
            f"{base} overview",
            f"{base} expert opinion",
            f"{base} statistics data",
            f"{base} research study",
        ]
    )

    seen = set()
    output = []

    for item in queries:

        key = item.lower().strip()

        if key in seen:
            continue

        seen.add(key)
        output.append(item)

        if len(output) >= 6:
            break

    return output


def estimate_complexity(
    query: str,
) -> Dict[str, object]:
    """Estimate source depth needed for the question."""

    category = classify_query(query)

    shallow = category in (
        "factual",
        "definition",
    )

    return {
        "word_count": len(query.split()),
        "category": category,
        "estimated_sources_needed": (
            3 if shallow else 5
        ),
        "search_depth": (
            "shallow" if shallow else "deep"
        ),
    }
