const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

export async function runResearch(query) {
  const res = await fetch(`${API_BASE}/api/research`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, max_sources: 5, max_results_per_query: 5 }),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || 'Failed to run research');
  }

  return res.json();
}
