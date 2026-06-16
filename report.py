from typing import List, Tuple
import re
from collections import Counter

from .schemas import SourceEvidence

STOPWORDS = {
    "the", "and", "for", "with", "that", "this", "from", "are", "was", "were", "you", "your",
    "has", "have", "had", "into", "about", "what", "when", "where", "which", "will", "would",
    "should", "could", "their", "there", "been", "them", "they", "than", "then", "over", "after",
    "before", "such", "more", "most", "some", "many", "much", "also", "not", "can", "may", "our",
}

def tokenize(text: str):
    return [w.lower() for w in re.findall(r"[A-Za-z0-9']+", text)]

def keyword_list(query: str, limit: int = 6) -> List[str]:
    words = [w for w in tokenize(query) if w not in STOPWORDS and len(w) > 2]
    counts = Counter(words)
    return [w for w, _ in counts.most_common(limit)]

def sentence_split(text: str) -> List[str]:
    chunks = re.split(r"(?<=[.!?])\s+", text.strip())
    return [c.strip() for c in chunks if len(c.strip()) > 30]

def score_sentence(sentence: str, keywords: List[str]) -> int:
    low = sentence.lower()
    return sum(2 if kw in low else 0 for kw in keywords) + min(len(sentence) // 120, 2)

def summarize_text(text: str, keywords: List[str], max_sentences: int = 3) -> List[str]:
    sents = sentence_split(text)
    if not sents:
        return []
    ranked = sorted(sents, key=lambda s: score_sentence(s, keywords), reverse=True)
    chosen = []
    for s in ranked:
        if s not in chosen:
            chosen.append(s)
        if len(chosen) >= max_sentences:
            break
    return chosen

def extract_facts(text: str, keywords: List[str], max_facts: int = 5) -> List[str]:
    facts = []
    for s in sentence_split(text):
        low = s.lower()
        if any(k in low for k in keywords) or re.search(r"\b\d+(?:\.\d+)?%?\b", s):
            facts.append(s)
        if len(facts) >= max_facts:
            break
    return facts[:max_facts]

def build_report(query: str, sources: List[SourceEvidence]) -> Tuple[str, List[str], List[str], List[str], int]:
    keywords = keyword_list(query)
    all_facts = []
    for src in sources:
        all_facts.extend(src.extracted_facts)

    unique_findings = []
    for fact in all_facts:
        short = fact.strip()
        if short and short not in unique_findings:
            unique_findings.append(short)

    contradictions = []
    combined_text = " ".join(all_facts).lower()
    cue_pairs = [
        ("increase", "decrease"),
        ("benefit", "risk"),
        ("good", "bad"),
        ("support", "oppose"),
        ("effective", "ineffective"),
        ("faster", "slower"),
        ("cheaper", "costly"),
    ]
    for a, b in cue_pairs:
        if a in combined_text and b in combined_text:
            contradictions.append(
                f"Sources contain both '{a}' and '{b}' language, so the evidence is mixed rather than one-sided."
            )

    if not contradictions and len(sources) >= 3:
        contradictions.append("Different sources emphasize different angles, so a single headline answer would be too simplistic.")

    summary_sentences = []
    for src in sources[:2]:
        summary_sentences.extend(summarize_text(src.snippet, keywords, max_sentences=1))
        summary_sentences.extend(summarize_text(" ".join(src.extracted_facts), keywords, max_sentences=1))
    if summary_sentences:
        summary = " ".join(summary_sentences[:3])
    elif unique_findings:
        summary = " ".join(unique_findings[:3])
    else:
        summary = f"The research shows multiple perspectives on {query}."

    key_findings = unique_findings[:5] if unique_findings else [f"No strong factual extraction found for {query}."]
    recommendations = build_recommendations(sources)
    confidence = compute_confidence(sources, unique_findings, contradictions)
    return summary, key_findings, contradictions, recommendations, confidence

def build_recommendations(sources: List[SourceEvidence]) -> List[str]:
    recs = []
    if len(sources) < 3:
        recs.append("Collect more sources before making a strong conclusion.")
    else:
        recs.append("Use the report as a starting point, then verify the most important claims from the cited sources.")
    recs.append("Prefer sources that provide numbers, dates, and direct evidence instead of vague claims.")
    recs.append("Mix primary sources with high-quality explanatory sources for balance.")
    return recs[:4]

def compute_confidence(sources: List[SourceEvidence], findings: List[str], contradictions: List[str]) -> int:
    score = 40
    score += min(len(sources) * 8, 24)
    score += min(len(findings) * 4, 16)
    if contradictions:
        score -= 8
    if len(sources) >= 5:
        score += 8
    return max(20, min(95, score))
