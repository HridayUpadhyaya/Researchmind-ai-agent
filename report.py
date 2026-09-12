import logging
import re
from collections import Counter
from typing import List, Tuple

from .schemas import SourceEvidence

logger = logging.getLogger(__name__)


STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "that",
    "this",
    "from",
    "are",
    "was",
    "were",
    "you",
    "your",
    "has",
    "have",
    "had",
    "into",
    "about",
    "what",
    "when",
    "where",
    "which",
    "will",
    "would",
    "should",
    "could",
    "their",
    "there",
    "been",
    "them",
    "they",
    "than",
    "then",
    "over",
    "after",
    "before",
    "such",
    "more",
    "most",
    "some",
    "many",
    "much",
    "also",
    "not",
    "can",
    "may",
    "our",
    "one",
    "two",
    "just",
    "like",
    "other",
    "its",
    "does",
    "did",
    "but",
    "being",
    "only",
    "still",
    "very",
    "too",
    "each",
    "every",
    "any",
    "all",
    "both",
    "how",
    "why",
    "who",
    "whose",
    "whereas",
    "while",
    "through",
    "between",
    "within",
}


def tokenize(text: str) -> List[str]:
    """Tokenize text into lowercase alphanumeric words."""

    return [
        word.lower()
        for word in re.findall(
            r"[A-Za-z0-9']+",
            text,
        )
    ]


def keyword_list(
    query: str,
    limit: int = 6,
) -> List[str]:
    """Return the most useful non-stopword query terms."""

    words = [
        word
        for word in tokenize(query)
        if word not in STOPWORDS
        and len(word) > 2
    ]

    counts = Counter(words)

    return [
        word
        for word, _ in counts.most_common(limit)
    ]


def sentence_split(
    text: str,
) -> List[str]:
    """Split text into reasonably sized sentences."""

    chunks = re.split(
        r"(?<=[.!?])\s+",
        text.strip(),
    )

    return [
        chunk.strip()
        for chunk in chunks
        if len(chunk.strip()) > 30
    ]


def score_sentence(
    sentence: str,
    keywords: List[str],
) -> int:
    """Score a sentence for relevance and evidence density."""

    low = sentence.lower()

    score = sum(
        2
        for keyword in keywords
        if keyword in low
    )

    if re.search(
        r"\b\d+(?:\.\d+)?%?\b",
        sentence,
    ):
        score += 3

    if re.search(
        r"\b[A-Za-z]+,\s+\d{4}\b",
        sentence,
    ):
        score += 2

    if re.search(
        r"\b(study|research|report|survey|data|evidence|according|found)\b",
        low,
    ):
        score += 2

    if len(sentence) < 40:
        score -= 2

    return score


def summarize_text(
    text: str,
    keywords: List[str],
    max_sentences: int = 3,
) -> List[str]:
    """Extract the highest scoring sentences."""

    sentences = sentence_split(text)

    if not sentences:
        return []

    ranked = sorted(
        sentences,
        key=lambda sentence: score_sentence(
            sentence,
            keywords,
        ),
        reverse=True,
    )

    chosen: List[str] = []

    for sentence in ranked:

        if sentence not in chosen:
            chosen.append(sentence)

        if len(chosen) >= max_sentences:
            break

    return chosen


def extract_facts(
    text: str,
    keywords: List[str],
    max_facts: int = 5,
) -> List[str]:
    """Extract sentences that look fact-heavy or query-relevant."""

    facts: List[str] = []

    fact_keywords = [
        "study",
        "research",
        "found",
        "according",
        "report",
        "data",
        "evidence",
        "survey",
        "statistics",
    ]

    for sentence in sentence_split(text):

        low = sentence.lower()

        has_keyword = any(
            keyword in low
            for keyword in keywords
        )

        has_number = bool(
            re.search(
                r"\b\d+(?:\.\d+)?%?\b",
                sentence,
            )
        )

        has_fact_keyword = any(
            item in low
            for item in fact_keywords
        )

        if (
            has_keyword
            or has_number
            or has_fact_keyword
        ):
            facts.append(sentence)

        if len(facts) >= max_facts:
            break

    return facts[:max_facts]


def generate_executive_summary(
    query: str,
    sources: List[SourceEvidence],
    key_findings: List[str],
) -> str:
    """Create a short evidence-oriented executive summary."""

    if not sources:
        return (
            "Insufficient information was retrieved "
            f"to summarize: {query}"
        )

    first = (
        f"Research into '{query}' used "
        f"{len(sources)} accessible sources."
    )

    if key_findings:
        first += (
            f" A leading finding was: "
            f"{key_findings[0]}"
        )

    second = (
        "The evidence should be interpreted with "
        "the source quality, publication context, "
        "and disagreements between sources in mind."
    )

    return f"{first}\n\n{second}"


def build_recommendations(
    sources: List[SourceEvidence],
    num_contradictions: int,
    confidence: int,
) -> List[str]:
    """Produce conservative recommendations."""

    recommendations: List[str] = []

    if len(sources) < 3:

        recommendations.append(
            "Collect more sources before making "
            "a strong conclusion."
        )

    elif (
        confidence > 70
        and num_contradictions == 0
    ):

        recommendations.append(
            "Evidence is reasonably strong and "
            "internally consistent."
        )

    elif num_contradictions > 1:

        recommendations.append(
            "Evidence is mixed; verify the most "
            "important claims with primary sources."
        )

    recommendations.append(
        "Use the report as a starting point, then "
        "verify high-impact claims from the cited pages."
    )

    recommendations.append(
        "Prefer sources that provide numbers, dates, "
        "methods, or direct evidence."
    )

    return recommendations[:4]


def compute_confidence(
    sources: List[SourceEvidence],
    findings: List[str],
    contradictions: List[str],
) -> int:
    """Compute a transparent 0-100 confidence estimate."""

    score = 40

    score += min(
        len(sources) * 8,
        24,
    )

    score += min(
        len(findings) * 4,
        16,
    )

    if contradictions:

        score -= min(
            8 + (
                len(contradictions) - 1
            ) * 2,
            14,
        )

    unique_domains = len(
        {
            source.domain
            for source in sources
            if source.domain
        }
    )

    score += min(
        unique_domains * 2,
        10,
    )

    if sources:

        avg_reliability = sum(
            source.reliability_score
            for source in sources
        ) / len(sources)

        score += int(
            avg_reliability * 10
        )

    if len(sources) >= 5:
        score += 8

    return max(
        20,
        min(
            95,
            score,
        ),
    )


def build_report(
    query: str,
    sources: List[SourceEvidence],
) -> Tuple[
    str,
    List[str],
    List[str],
    List[str],
    int,
]:
    """Build all report components."""

    keywords = keyword_list(query)

    all_facts: List[str] = []

    for source in sources:
        all_facts.extend(
            source.extracted_facts
        )

    unique_findings: List[str] = []
    seen = set()

    for fact in all_facts:

        clean = fact.strip()
        key = clean.lower()

        if clean and key not in seen:

            seen.add(key)
            unique_findings.append(clean)

    contradictions: List[str] = []

    combined_text = " ".join(
        all_facts
    ).lower()

    cue_pairs = [
        ("increase", "decrease"),
        ("benefit", "risk"),
        ("good", "bad"),
        ("support", "oppose"),
        ("effective", "ineffective"),
        ("faster", "slower"),
        ("cheaper", "costly"),
        ("higher", "lower"),
        ("positive", "negative"),
        ("agree", "disagree"),
        ("safe", "dangerous"),
        ("growing", "declining"),
    ]

    for left, right in cue_pairs:

        if (
            left in combined_text
            and right in combined_text
        ):

            contradictions.append(
                f"Sources contain both '{left}' "
                f"and '{right}' language, indicating "
                "mixed evidence."
            )

    if (
        not contradictions
        and len(sources) >= 3
    ):

        contradictions.append(
            "Sources emphasize different angles, "
            "so the evidence should not be reduced "
            "to a single simplistic conclusion."
        )

    key_findings = (
        unique_findings[:5]
        if unique_findings
        else [
            f"No strong factual extraction found "
            f"for {query}."
        ]
    )

    confidence = compute_confidence(
        sources=sources,
        findings=unique_findings,
        contradictions=contradictions,
    )

    summary = generate_executive_summary(
        query=query,
        sources=sources,
        key_findings=key_findings,
    )

    recommendations = build_recommendations(
        sources=sources,
        num_contradictions=len(
            contradictions
        ),
        confidence=confidence,
    )

    return (
        summary,
        key_findings,
        contradictions,
        recommendations,
        confidence,
    )
