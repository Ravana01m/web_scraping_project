const rawApiUrl = import.meta.env.VITE_API_URL || '';
const API_BASE = rawApiUrl ? (rawApiUrl.endsWith('/api') ? rawApiUrl : `${rawApiUrl.replace(/\/$/, '')}/api`) : '/api';

export const startScraping = async ({ platform, url, maxReviews }) => {
  const res = await fetch(`${API_BASE}/scrape`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ platform, url, maxReviews })
  });
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.error || 'Failed to start scraping');
  }
  return res.json();
};

export const getJobStatus = async (jobId) => {
  const res = await fetch(`${API_BASE}/scrape/${jobId}`);
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.error || 'Failed to fetch job status');
  }
  return res.json();
};

export const getDownloadUrl = (jobId) => {
  return `${API_BASE}/scrape/${jobId}/download`;
};
