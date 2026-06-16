import React, { useMemo, useState } from 'react'
import { runResearch } from './api'

const sampleQueries = [
  'Should India invest more in nuclear energy?',
  'What are the best ways to prepare for an AI internship?',
  'Is remote work more productive than office work?',
]

function Step({ step }) {
  return (
    <div className={`step step-${step.status}`}>
      <div className="step-badge">{step.status === 'done' ? '✓' : '•'}</div>
      <div>
        <div className="step-title">{step.title}</div>
        <div className="step-detail">{step.detail}</div>
      </div>
    </div>
  )
}

function SourceCard({ source }) {
  return (
    <a className="source-card" href={source.url} target="_blank" rel="noreferrer">
      <div className="source-title">{source.title}</div>
      <div className="source-url">{source.url}</div>
      <div className="source-snippet">{source.snippet}</div>
      {source.extracted_facts?.length > 0 && (
        <ul className="fact-list">
          {source.extracted_facts.slice(0, 3).map((fact, idx) => (
            <li key={idx}>{fact}</li>
          ))}
        </ul>
      )}
    </a>
  )
}

export default function App() {
  const [query, setQuery] = useState(sampleQueries[0])
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const progress = useMemo(() => {
    if (!data?.steps?.length) return 0
    const done = data.steps.filter(s => s.status === 'done').length
    return Math.round((done / data.steps.length) * 100)
  }, [data])

  async function handleRun(e) {
    e.preventDefault()
    setLoading(true)
    setError('')
    setData(null)
    try {
      const result = await runResearch(query)
      setData(result)
    } catch (err) {
      setError(err.message || 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app-shell">
      <header className="hero">
        <div className="hero-copy">
          <div className="eyebrow">Portfolio Project</div>
          <h1>ResearchMind AI</h1>
          <p>
            A multi-step research agent that searches the web, compares evidence,
            and writes a citation-backed report with a confidence score.
          </p>
        </div>

        <form className="search-box" onSubmit={handleRun}>
          <label htmlFor="query">Ask anything</label>
          <textarea
            id="query"
            rows="4"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter a research question..."
          />
          <div className="quick-queries">
            {sampleQueries.map((q) => (
              <button key={q} type="button" onClick={() => setQuery(q)} className="chip">
                {q}
              </button>
            ))}
          </div>
          <button className="primary-btn" type="submit" disabled={loading}>
            {loading ? 'Researching...' : 'Run Research Agent'}
          </button>
        </form>
      </header>

      {error && <div className="error-box">{error}</div>}

      {loading && (
        <div className="panel">
          <div className="panel-title">Working on it</div>
          <p>The agent is planning, searching, reading, and comparing evidence.</p>
          <div className="progress">
            <div className="progress-bar" style={{ width: '65%' }} />
          </div>
        </div>
      )}

      {data && (
        <>
          <section className="grid two-col">
            <div className="panel">
              <div className="panel-title">Research plan</div>
              <ol className="numbered-list">
                {data.plan.map((item, idx) => (
                  <li key={idx}>{item}</li>
                ))}
              </ol>
            </div>

            <div className="panel score-panel">
              <div className="panel-title">Confidence score</div>
              <div className="score">{data.confidence_score}</div>
              <div className="score-label">out of 100</div>
              <div className="progress">
                <div className="progress-bar" style={{ width: `${progress}%` }} />
              </div>
              <div className="small-note">
                Higher score means more sources, more evidence, and fewer conflicts.
              </div>
            </div>
          </section>

          <section className="panel">
            <div className="panel-title">Agent steps</div>
            <div className="steps">
              {data.steps.map((step, idx) => (
                <Step step={step} key={idx} />
              ))}
            </div>
          </section>

          <section className="grid two-col">
            <div className="panel">
              <div className="panel-title">Summary</div>
              <p className="summary-text">{data.summary}</p>
            </div>

            <div className="panel">
              <div className="panel-title">Contradictions / caveats</div>
              {data.contradictions.length ? (
                <ul className="bullet-list">
                  {data.contradictions.map((item, idx) => (
                    <li key={idx}>{item}</li>
                  ))}
                </ul>
              ) : (
                <p>No major contradictions detected.</p>
              )}
            </div>
          </section>

          <section className="panel">
            <div className="panel-title">Key findings</div>
            <ul className="bullet-list">
              {data.key_findings.map((item, idx) => (
                <li key={idx}>{item}</li>
              ))}
            </ul>
          </section>

          <section className="panel">
            <div className="panel-title">Recommendations</div>
            <ul className="bullet-list">
              {data.recommendations.map((item, idx) => (
                <li key={idx}>{item}</li>
              ))}
            </ul>
          </section>

          <section className="panel">
            <div className="panel-title">Sources</div>
            <div className="source-grid">
              {data.sources.map((source, idx) => (
                <SourceCard key={idx} source={source} />
              ))}
            </div>
          </section>
        </>
      )}

      <footer className="footer">
        Built with FastAPI + React. Free by default. Designed for portfolio demos.
      </footer>
    </div>
  )
}
