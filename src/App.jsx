import React, {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";

import {
  downloadResults,
  runResearch,
} from "./api";


const SAMPLE_QUERIES = [
  "Should India invest more in nuclear energy?",
  "What are the best ways to prepare for an AI internship?",
  "Is remote work more productive than office work?",
  "What is the future of quantum computing in healthcare?",
  "How does climate change affect global food security?",
];


function ThemeToggle({
  theme,
  toggleTheme,
}) {
  return (
    <button
      type="button"
      className="theme-toggle"
      onClick={toggleTheme}
      aria-label={
        `Switch to ${
          theme === "dark"
            ? "light"
            : "dark"
        } mode`
      }
      title={
        `Switch to ${
          theme === "dark"
            ? "light"
            : "dark"
        } mode`
      }
    >
      {theme === "dark"
        ? "☀️"
        : "🌙"}
    </button>
  );
}


function Step({ step }) {

  const icons = {
    done: "✓",
    running: "↻",
    failed: "✕",
    pending: "○",
  };

  return (
    <div
      className={`step step-${step.status}`}
    >
      <div
        className={
          `step-badge ${
            step.status === "running"
              ? "pulse"
              : ""
          }`
        }
        aria-hidden="true"
      >
        {icons[step.status] || "○"}
      </div>

      <div className="step-content">
        <div className="step-title">
          {step.title}
        </div>

        <div className="step-detail">
          {step.detail}
        </div>
      </div>
    </div>
  );
}


function reliabilityLabel(
  score = 0
) {
  if (score >= 0.8) {
    return "high";
  }

  if (score >= 0.6) {
    return "medium";
  }

  return "baseline";
}


function SourceCard({
  source,
}) {

  const domain = useMemo(() => {

    try {

      return new URL(
        source.url
      ).hostname.replace(
        /^www\./,
        ""
      );

    } catch {

      return source.domain || "";
    }

  }, [
    source.url,
    source.domain,
  ]);


  const reliability =
    reliabilityLabel(
      source.reliability_score
    );


  const reliabilityClass =
    reliability === "high"
      ? "green"
      : reliability === "medium"
      ? "yellow"
      : "red";


  return (
    <a
      className="source-card"
      href={source.url}
      target="_blank"
      rel="noreferrer"
    >

      <div className="source-header">

        <span className="source-domain">
          {domain}
        </span>

        <span
          className={
            `reliability-badge ${
              reliabilityClass
            }`
          }
        >
          {reliability}
        </span>

      </div>


      <div className="source-title">
        {source.title}
      </div>


      <div className="source-snippet">
        {source.snippet}
      </div>


      <div className="source-meta">

        {source.word_count > 0 && (
          <span>
            {source.word_count.toLocaleString()} words
          </span>
        )}

      </div>


      {source.reliability_note && (
        <div className="reliability-note">
          {source.reliability_note}
        </div>
      )}


      {source.extracted_facts?.length > 0 && (
        <ul className="fact-list">

          {source.extracted_facts
            .slice(0, 5)
            .map(
              (fact, index) => (
                <li
                  key={
                    `${source.url}-fact-${index}`
                  }
                >
                  {fact}
                </li>
              )
            )}

        </ul>
      )}

    </a>
  );
}


function ConfidenceGauge({
  score = 0,
}) {

  const safeScore =
    Math.max(
      0,
      Math.min(
        100,
        Number(score) || 0
      )
    );


  const colorClass =
    safeScore >= 70
      ? "green"
      : safeScore >= 40
      ? "yellow"
      : "red";


  const circumference =
    Math.PI * 80;


  const dashOffset =
    circumference *
    (1 - safeScore / 100);


  return (
    <div
      className={
        `confidence-gauge ${
          colorClass
        }`
      }
    >

      <svg
        className="gauge-svg"
        viewBox="0 0 100 55"
        role="img"
        aria-label={
          `Confidence score ${
            safeScore
          } out of 100`
        }
      >

        <path
          d="M 10 50 A 40 40 0 0 1 90 50"
          fill="none"
          stroke="currentColor"
          strokeOpacity="0.15"
          strokeWidth="10"
        />

        <path
          d="M 10 50 A 40 40 0 0 1 90 50"
          fill="none"
          stroke="currentColor"
          strokeWidth="10"
          strokeDasharray={
            circumference
          }
          strokeDashoffset={
            dashOffset
          }
          className="gauge-path"
          strokeLinecap="round"
        />

      </svg>


      <div className="gauge-score">
        {safeScore}
      </div>

    </div>
  );
}


function CopyButton({
  text,
}) {

  const [copied, setCopied] =
    useState(false);


  const handleCopy =
    useCallback(
      async () => {

        try {

          await navigator.clipboard.writeText(
            text || ""
          );

          setCopied(true);

          window.setTimeout(
            () => setCopied(false),
            2000
          );

        } catch {

          setCopied(false);

        }

      },
      [text]
    );


  return (
    <button
      type="button"
      className="copy-btn"
      onClick={handleCopy}
      aria-label="Copy summary"
    >
      {copied
        ? "Copied"
        : "📋"}
    </button>
  );
}


function ResearchMeta({
  data,
}) {

  if (!data) {
    return null;
  }


  return (
    <div className="meta-bar">

      <span>
        Completed in{" "}
        {(
          data.research_duration_seconds ||
          0
        ).toFixed(1)}
        s
      </span>

      <span>
        •{" "}
        {data.total_sources_used || 0}
        {" / "}
        {data.total_sources_found || 0}
        {" "}sources
      </span>

      {data.timestamp && (
        <span>
          •{" "}
          {new Date(
            data.timestamp
          ).toLocaleTimeString()}
        </span>
      )}

    </div>
  );
}


export default function App() {

  const [query, setQuery] =
    useState(
      SAMPLE_QUERIES[0]
    );

  const [data, setData] =
    useState(null);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  const [theme, setTheme] =
    useState(
      () =>
        localStorage.getItem(
          "researchmind-theme"
        ) || "dark"
    );


  const resultsRef =
    useRef(null);

  const abortControllerRef =
    useRef(null);


  useEffect(() => {

    document.documentElement.setAttribute(
      "data-theme",
      theme
    );

    localStorage.setItem(
      "researchmind-theme",
      theme
    );

  }, [theme]);


  useEffect(() => {

    if (
      data &&
      resultsRef.current
    ) {

      resultsRef.current.scrollIntoView(
        {
          behavior: "smooth",
          block: "start",
        }
      );

    }

  }, [data]);


  useEffect(() => {

    return () => {
      abortControllerRef.current?.abort();
    };

  }, []);


  const toggleTheme = () => {

    setTheme(
      (previous) =>
        previous === "dark"
          ? "light"
          : "dark"
    );

  };


  const progress =
    useMemo(() => {

      if (
        !data?.steps?.length
      ) {
        return 0;
      }

      const done =
        data.steps.filter(
          (step) =>
            step.status === "done"
        ).length;

      return Math.round(
        (done /
          data.steps.length) *
          100
      );

    }, [data]);


  const handleRun =
    async (event) => {

      event?.preventDefault();

      const cleanQuery =
        query.trim();


      if (
        cleanQuery.length < 3
      ) {

        setError(
          "Please enter a research question with at least 3 characters."
        );

        return;
      }


      abortControllerRef.current?.abort();


      const controller =
        new AbortController();


      abortControllerRef.current =
        controller;


      setLoading(true);
      setError("");
      setData(null);


      try {

        const result =
          await runResearch(
            cleanQuery,
            {
              signal:
                controller.signal,
            }
          );

        setData(result);

      } catch (err) {

        if (
          err.name !==
          "AbortError"
        ) {

          setError(
            err.message ||
            "Something went wrong."
          );

        }

      } finally {

        if (
          !controller.signal.aborted
        ) {

          setLoading(false);

        }
      }
    };


  const handleKeyDown =
    (event) => {

      if (
        event.key === "Enter" &&
        (event.ctrlKey ||
          event.metaKey)
      ) {

        handleRun(event);

      }
    };


  const handleExport = () => {

    if (data) {

      downloadResults(
        data,
        "research-results.json"
      );

    }
  };


  return (
    <div className="app-shell">

      <ThemeToggle
        theme={theme}
        toggleTheme={
          toggleTheme
        }
      />


      <main>

        <section className="hero">

          <div className="eyebrow">
            Portfolio Project
          </div>

          <h1>
            ResearchMind AI
          </h1>

          <p>
            A multi-step research agent
            that searches the web, compares
            evidence, identifies disagreements,
            and produces an evidence-backed
            report with a confidence score.
          </p>


          <form
            className="search-box"
            onSubmit={handleRun}
          >

            <label htmlFor="query">

              Ask anything{" "}

              <span className="muted">
                (Ctrl + Enter to run)
              </span>

            </label>


            <textarea
              id="query"
              rows="4"
              value={query}
              onChange={(event) =>
                setQuery(
                  event.target.value
                )
              }
              onKeyDown={
                handleKeyDown
              }
              placeholder="Enter a research question..."
              disabled={loading}
            />


            <div className="quick-queries">

              {SAMPLE_QUERIES.map(
                (sample) => (

                  <button
                    key={sample}
                    type="button"
                    className="chip"
                    onClick={() =>
                      setQuery(sample)
                    }
                    disabled={loading}
                  >
                    {sample}
                  </button>

                )
              )}

            </div>


            <button
              className="primary-btn"
              type="submit"
              disabled={loading}
            >

              {loading ? (

                <span className="loading-dots">
                  Researching
                  <span>.</span>
                  <span>.</span>
                  <span>.</span>
                </span>

              ) : (

                "Run Research Agent"

              )}

            </button>

          </form>

        </section>


        {error && (
          <div className="error-box fade-in">
            {error}
          </div>
        )}


        {loading && (

          <section
            className="panel fade-in skeleton"
          >

            <div className="panel-title">
              Working on it
            </div>

            <p>
              The agent is planning,
              searching, reading, and
              comparing evidence.
            </p>

            <div className="progress">
              <div
                className="progress-bar pulse"
                style={{
                  width: "65%",
                }}
              />
            </div>

          </section>

        )}


        {data && (

          <div
            className="results-container fade-in"
            ref={resultsRef}
          >

            <ResearchMeta
              data={data}
            />


            <section className="grid two-col">

              <div className="panel">

                <div className="panel-title">
                  Research plan
                </div>

                <ol className="numbered-list">

                  {data.plan?.map(
                    (item, index) => (

                      <li key={index}>
                        {item}
                      </li>

                    )
                  )}

                </ol>

              </div>


              <div className="panel score-panel">

                <div className="panel-title">
                  Confidence score
                </div>

                <ConfidenceGauge
                  score={
                    data.confidence_score
                  }
                />

                <div className="score-label">
                  out of 100
                </div>

                <div className="progress">

                  <div
                    className="progress-bar"
                    style={{
                      width:
                        `${progress}%`,
                    }}
                  />

                </div>

                <div className="small-note">
                  Based on source count,
                  evidence extraction,
                  domain diversity,
                  heuristic reliability,
                  and detected conflicts.
                </div>

              </div>

            </section>


            <section className="panel">

              <div className="panel-title">
                Agent steps
              </div>

              <div className="steps">

                {data.steps?.map(
                  (step, index) => (

                    <Step
                      step={step}
                      key={index}
                    />

                  )
                )}

              </div>

            </section>


            <section className="grid two-col">

              <div className="panel summary-panel">

                <div className="panel-title">

                  <span>
                    Summary
                  </span>

                  <CopyButton
                    text={
                      data.summary
                    }
                  />

                </div>

                <p className="summary-text">
                  {data.summary}
                </p>

              </div>


              <div className="panel">

                <div className="panel-title">
                  Contradictions / caveats
                </div>

                {data.contradictions?.length ? (

                  <ul className="bullet-list">

                    {data.contradictions.map(
                      (
                        item,
                        index
                      ) => (

                        <li key={index}>
                          {item}
                        </li>

                      )
                    )}

                  </ul>

                ) : (

                  <p className="muted">
                    No major contradictions detected.
                  </p>

                )}

              </div>

            </section>


            <section className="panel">

              <div className="panel-title">
                Key findings
              </div>

              <ul className="bullet-list">

                {data.key_findings?.map(
                  (
                    item,
                    index
                  ) => (

                    <li key={index}>
                      {item}
                    </li>

                  )
                )}

              </ul>

            </section>


            <section className="panel">

              <div className="panel-title">
                Recommendations
              </div>

              <ul className="bullet-list">

                {data.recommendations?.map(
                  (
                    item,
                    index
                  ) => (

                    <li key={index}>
                      {item}
                    </li>

                  )
                )}

              </ul>

            </section>


            <section className="panel">

              <div className="panel-title">
                Sources
              </div>

              <div className="source-grid">

                {data.sources?.map(
                  (
                    source,
                    index
                  ) => (

                    <SourceCard
                      key={index}
                      source={source}
                    />

                  )
                )}

              </div>

            </section>


            <div className="export-section">

              <button
                className="export-btn"
                onClick={
                  handleExport
                }
              >
                Download JSON Report
              </button>

            </div>

          </div>

        )}

      </main>


      <footer className="footer">

        <div>
          ResearchMind AI v2.0.0
          {" · "}
          Built with FastAPI + React
        </div>

        <a
          href="https://github.com/HridayUpadhyaya/Researchmind-ai-agent"
          target="_blank"
          rel="noreferrer"
        >
          View on GitHub
        </a>

      </footer>

    </div>
  );
}
