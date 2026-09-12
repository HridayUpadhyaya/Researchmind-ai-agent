import React from "react";
import ReactDOM from "react-dom/client";

import App from "./App";
import "./styles.css";


class ErrorBoundary
  extends React.Component {

  constructor(props) {

    super(props);

    this.state = {
      hasError: false,
      error: null,
    };
  }


  static getDerivedStateFromError(
    error
  ) {

    return {
      hasError: true,
      error,
    };
  }


  componentDidCatch(
    error,
    errorInfo
  ) {

    console.error(
      "Uncaught error in ResearchMind AI:",
      error,
      errorInfo
    );
  }


  render() {

    if (
      this.state.hasError
    ) {

      return (
        <div
          style={{
            minHeight:
              "100vh",

            display:
              "grid",

            placeItems:
              "center",

            padding:
              "2rem",

            fontFamily:
              "Inter, sans-serif",
          }}
        >

          <div
            style={{
              maxWidth: 600,
              textAlign:
                "center",
            }}
          >

            <h1>
              Something went wrong.
            </h1>

            <p
              style={{
                color:
                  "#cf222e",
              }}
            >
              {
                this.state.error
                  ?.toString() ||
                "Unknown application error"
              }
            </p>

            <button
              type="button"
              onClick={() =>
                window.location.reload()
              }
              style={{
                padding:
                  "0.6rem 1rem",
                cursor:
                  "pointer",
              }}
            >
              Reload Page
            </button>

          </div>

        </div>
      );
    }


    return this.props.children;
  }
}


console.log(
  "ResearchMind AI v2.0.0 initializing..."
);


ReactDOM.createRoot(
  document.getElementById(
    "root"
  )
).render(

  <React.StrictMode>

    <ErrorBoundary>

      <App />

    </ErrorBoundary>

  </React.StrictMode>
);
