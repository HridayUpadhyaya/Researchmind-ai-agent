# ResearchMind AI

A beginner-friendly, portfolio-ready multi-step research agent with:

- FastAPI backend
- React frontend
- Live web search via DuckDuckGo
- Page fetching and text extraction
- Research planning, source ranking, confidence scoring, and citation-backed reporting
- Free by default

## What it does

1. Takes a topic/question from the user
2. Splits it into research angles
3. Searches the web
4. Fetches and extracts the best source pages
5. Produces a structured report with citations and a confidence score
6. Shows progress in the UI so the workflow looks like a real agent

## Setup

### Backend
```bash
cd backend
python -m venv .venv
# activate the venv, then:
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Open the frontend URL printed by Vite.

## Notes

- This MVP is free to run.
- It works best on clear, researchable questions.
- Some websites block scraping; the app will skip those and continue.
