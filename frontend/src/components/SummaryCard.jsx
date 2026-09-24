import React from 'react';

export default function SummaryCard({ summary }) {
  return (
    <div className="card">
      <h3 style={{ marginBottom: '1rem' }}>Review Summary</h3>
      <div style={{ whiteSpace: 'pre-wrap', color: 'var(--text-secondary)' }}>
        {summary || 'No summary available.'}
      </div>
    </div>
  );
}
