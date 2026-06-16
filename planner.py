from typing import List

def build_research_plan(query: str) -> List[str]:
    q = query.strip().rstrip("?")
    lower = q.lower()

    plan = [
        f"Understand the core question: {q}",
        "Find multiple sources with different perspectives",
        "Extract facts, claims, and numbers",
        "Compare agreement and disagreement across sources",
        "Write a balanced answer with citations and caveats",
    ]

    if any(word in lower for word in ["best", "compare", "vs", "versus", "which"]):
        plan.insert(1, "Compare options, tradeoffs, and decision criteria")
    if any(word in lower for word in ["how", "steps", "process", "build", "make"]):
        plan.insert(1, "Break the topic into actionable sub-questions")
    if any(word in lower for word in ["why", "cause", "because", "reason"]):
        plan.insert(1, "Search for explanations, causes, and evidence")
    if any(word in lower for word in ["2024", "2025", "latest", "recent"]):
        plan.insert(1, "Prioritize the most recent evidence available")

    return plan

def build_search_queries(query: str) -> List[str]:
    base = query.strip().rstrip("?")
    queries = [
        base,
        f"{base} overview",
        f"{base} evidence",
        f"{base} pros cons",
    ]

    seen = set()
    out = []
    for q in queries:
        k = q.lower()
        if k not in seen:
            seen.add(k)
            out.append(q)
    return out
