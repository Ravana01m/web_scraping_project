import React, { useEffect, useState } from 'react';

export default function LoadingState({ status }) {
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => setElapsed(s => s + 1), 1000);
    return () => clearInterval(interval);
  }, []);

  const getStatusText = () => {
    switch (status) {
      case 'queued': return 'Job queued, waiting to start...';
      case 'scraping': return 'Scraping reviews... Please wait.';
      case 'analyzing': return 'Analyzing reviews...';
      default: return 'Processing...';
    }
  };

  return (
    <div className="card loading-container">
      <div className="spinner"></div>
      <div className="loading-text">{getStatusText()}</div>
      <div className="loading-time">Elapsed time: {elapsed}s</div>
    </div>
  );
}
