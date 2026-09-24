import React from 'react';

export default function StatsCards({ totalReviews, averageRating, sentiment }) {
  const posPercentage = sentiment?.positive || 0;
  
  return (
    <div className="dashboard-grid">
      <div className="stat-card">
        <div className="stat-icon">📊</div>
        <div className="stat-content">
          <h3>Total Reviews</h3>
          <p>{totalReviews}</p>
        </div>
      </div>
      <div className="stat-card">
        <div className="stat-icon">⭐</div>
        <div className="stat-content">
          <h3>Average Rating</h3>
          <p>{typeof averageRating === 'number' ? averageRating.toFixed(2) : 'N/A'}</p>
        </div>
      </div>
      <div className="stat-card">
        <div className="stat-icon">😊</div>
        <div className="stat-content">
          <h3>Positive Reviews</h3>
          <p>{posPercentage.toFixed(1)}%</p>
        </div>
      </div>
    </div>
  );
}
