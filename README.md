# 🧠 ResearchMind AI

ResearchMind AI is a multi-step research agent built with Python, FastAPI and React.

It plans a research task, searches the web, fetches accessible sources, extracts evidence, detects mixed signals and presents a structured report with a transparent confidence heuristic.

> This version is a rule-based research pipeline. It does not currently use an LLM to write the report.

---

## Architecture

```text
User
  │
  ▼
React + Vite frontend
  │
  │ HTTP / JSON
  ▼
FastAPI backend
  │
  ├── Query Planner
  ├── DuckDuckGo Search
  ├── URL Deduplication
  ├── Parallel Page Fetching
  ├── HTML Text Extraction
  ├── Fact Extraction
  ├── Contradiction Detection
  └── Confidence Calculation
  │
  ▼
Structured JSON response
