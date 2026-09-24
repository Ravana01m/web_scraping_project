import React, { useState } from 'react';

export default function ScraperForm({ onSubmit, loading }) {
  const [platform, setPlatform] = useState('croma');
  const [url, setUrl] = useState('');
  const [maxReviews, setMaxReviews] = useState(50);
  const [error, setError] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!url.trim()) {
      setError('URL is required');
      return;
    }
    if (platform === 'croma' && !url.includes('croma.com')) {
      setError('URL must be a valid Croma link containing "croma.com"');
      return;
    }
    if (platform === 'imdb' && !url.includes('imdb.com')) {
      setError('URL must be a valid IMDb link containing "imdb.com"');
      return;
    }
    setError('');
    onSubmit({ platform, url, maxReviews: Number(maxReviews) });
  };

  return (
    <div className="card">
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Platform</label>
          <select 
            className="form-control" 
            value={platform} 
            onChange={(e) => setPlatform(e.target.value)}
            disabled={loading}
          >
            <option value="croma">Croma</option>
            <option value="imdb">IMDb</option>
          </select>
        </div>
        
        <div className="form-group">
          <label>Product/Movie URL</label>
          <input 
            type="url" 
            className="form-control"
            value={url}
            onChange={(e) => {
              setUrl(e.target.value);
              setError('');
            }}
            placeholder={platform === 'croma' ? 'https://www.croma.com/...' : 'https://www.imdb.com/title/...'}
            disabled={loading}
          />
          {error && <div className="error-message">{error}</div>}
        </div>

        <div className="form-group">
          <label>Max Reviews to Collect</label>
          <select 
            className="form-control" 
            value={maxReviews} 
            onChange={(e) => setMaxReviews(e.target.value)}
            disabled={loading}
          >
            <option value={25}>25</option>
            <option value={50}>50</option>
            <option value={100}>100</option>
            <option value={200}>200</option>
            <option value={500}>500</option>
          </select>
        </div>

        <button type="submit" className="btn" disabled={loading}>
          🚀 Start Scraping
        </button>
      </form>
    </div>
  );
}
