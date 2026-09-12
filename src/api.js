export const API_BASE = (
  import.meta.env.VITE_API_BASE || ""
).replace(/\/$/, "");


const DEFAULT_TIMEOUT =
  30_000;


async function fetchWithTimeout(
  resource,
  options = {}
) {

  const {
    timeout = DEFAULT_TIMEOUT,
    signal: externalSignal,
    ...fetchOptions
  } = options;


  const controller =
    new AbortController();


  const timeoutId =
    window.setTimeout(
      () =>
        controller.abort(),
      timeout
    );


  const abortHandler = () =>
    controller.abort();


  externalSignal?.addEventListener(
    "abort",
    abortHandler,
    {
      once: true,
    }
  );


  try {

    return await fetch(
      resource,
      {
        ...fetchOptions,
        signal:
          controller.signal,
      }
    );

  } finally {

    window.clearTimeout(
      timeoutId
    );

    externalSignal?.removeEventListener(
      "abort",
      abortHandler
    );

  }
}


async function fetchWithRetry(
  url,
  options = {},
  retries = 2,
  backoffMs = 300
) {

  try {

    const response =
      await fetchWithTimeout(
        url,
        options
      );


    if (!response.ok) {

      let message =
        `Request failed with status ${response.status}`;


      try {

        const payload =
          await response.json();


        if (payload?.detail) {

          message =
            payload.detail;

        } else if (
          payload?.message
        ) {

          message =
            payload.message;

        }

      } catch {

        const text =
          await response.text()
            .catch(
              () => ""
            );

        if (text) {
          message = text;
        }

      }


      throw new Error(
        message
      );
    }


    return await response.json();

  } catch (error) {

    if (
      error.name ===
        "AbortError" ||
      retries <= 0
    ) {

      throw error;

    }


    await new Promise(
      (resolve) =>
        window.setTimeout(
          resolve,
          backoffMs
        )
    );


    return fetchWithRetry(
      url,
      options,
      retries - 1,
      backoffMs * 2
    );
  }
}


export async function runResearch(
  query,
  options = {}
) {

  return fetchWithRetry(
    `${API_BASE}/api/research`,
    {
      method: "POST",

      headers: {
        "Content-Type":
          "application/json",
      },

      body: JSON.stringify({
        query,
        max_sources: 5,
        max_results_per_query: 5,
      }),

      ...options,
    }
  );
}


export async function checkHealth() {

  try {

    const response =
      await fetchWithTimeout(
        `${API_BASE}/api/health`,
        {
          timeout: 5000,
        }
      );


    if (!response.ok) {

      return {
        status: "error",
        message:
          "API is not healthy.",
      };
    }


    return await response.json();

  } catch (error) {

    return {
      status: "offline",
      message:
        error.message ||
        "API is unreachable.",
    };
  }
}


export async function getResearchPreview(
  query
) {

  return fetchWithRetry(
    `${API_BASE}/api/research/preview`,
    {
      method: "POST",

      headers: {
        "Content-Type":
          "application/json",
      },

      body: JSON.stringify({
        query,
      }),
    }
  );
}


export function downloadResults(
  data,
  filename = "results.json"
) {

  const blob =
    new Blob(
      [
        JSON.stringify(
          data,
          null,
          2
        ),
      ],
      {
        type: "application/json",
      }
    );


  const url =
    URL.createObjectURL(
      blob
    );


  const anchor =
    document.createElement(
      "a"
    );


  anchor.href = url;
  anchor.download = filename;

  document.body.appendChild(
    anchor
  );

  anchor.click();
  anchor.remove();

  URL.revokeObjectURL(
    url
  );
}
