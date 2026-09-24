import React, { useState, useEffect, useRef } from 'react';
import Header from './components/Header';
import ScraperForm from './components/ScraperForm';
import LoadingState from './components/LoadingState';
import StatsCards from './components/StatsCards';
import RatingChart from './components/RatingChart';
import SummaryCard from './components/SummaryCard';
import ReviewTable from './components/ReviewTable';
import { startScraping, getJobStatus } from './services/api';

function App() {
  const [jobId, setJobId] = useState(null);
  const [status, setStatus] = useState('idle');
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  
  const pollInterval = useRef(null);

  const handleSubmit = async (formData) => {
    try {
      setError(null);
      setJobId(null);
      setResults(null);
      setStatus('queued');
      
      const { jobId: newJobId } = await startScraping(formData);
      setJobId(newJobId);
    } catch (err) {
      setError(err.message);
      setStatus('idle');
    }
  };

  useEffect(() => {
    if (jobId && ['queued', 'scraping', 'analyzing'].includes(status)) {
      pollInterval.current = setInterval(async () => {
        try {
          const jobData = await getJobStatus(jobId);
          setStatus(jobData.status);
          
          if (jobData.status === 'completed' && jobData.data) {
            // jobData.data is the Python response with flat structure:
            // { reviews, totalReviews, averageRating, ratingDistribution, sentiment, summary }
            setResults(jobData.data);
            clearInterval(pollInterval.current);
          } else if (jobData.status === 'failed') {
            setError(jobData.error || 'Job failed');
            clearInterval(pollInterval.current);
          }
        } catch (err) {
          setError('Failed to get job status');
          setStatus('failed');
          clearInterval(pollInterval.current);
        }
      }, 2000);
    }

    return () => {
      if (pollInterval.current) clearInterval(pollInterval.current);
    };
  }, [jobId, status]);

  const handleReset = () => {
    setJobId(null);
    setStatus('idle');
    setResults(null);
    setError(null);
    if (pollInterval.current) clearInterval(pollInterval.current);
  };

  const isLoading = ['queued', 'scraping', 'analyzing'].includes(status);

  return (
    <div className="app-container">
      <Header />
      
      <main className="main-content">
        {error && (
          <div className="card" style={{ backgroundColor: '#fee2e2', borderLeft: '4px solid #ef4444' }}>
            <h3 style={{ color: '#b91c1c' }}>Error</h3>
            <p>{error}</p>
            <button className="btn" style={{ marginTop: '1rem' }} onClick={handleReset}>Try Again</button>
          </div>
        )}

        {status === 'idle' && !error && (
          <ScraperForm onSubmit={handleSubmit} loading={false} />
        )}

        {isLoading && (
          <LoadingState status={status} />
        )}

        {status === 'completed' && results && (
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
              <h2>Results Dashboard</h2>
              <button className="btn" onClick={handleReset}>New Scraping Job</button>
            </div>
            
            <StatsCards 
              totalReviews={results.totalReviews}
              averageRating={results.averageRating}
              sentiment={results.sentiment}
            />
            
            <div className="two-col">
              <RatingChart ratingDistribution={results.ratingDistribution} />
              <SummaryCard summary={results.summary} />
            </div>
            
            <ReviewTable reviews={results.reviews || []} jobId={jobId} />
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
