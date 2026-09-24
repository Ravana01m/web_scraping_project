import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

export default function RatingChart({ ratingDistribution }) {
  if (!ratingDistribution) return null;

  const data = [1, 2, 3, 4, 5].map(rating => ({
    rating: `${rating} Star`,
    count: ratingDistribution[String(rating)] || ratingDistribution[rating] || 0
  }));

  const getBarColor = (ratingStr) => {
    if (ratingStr.startsWith('1') || ratingStr.startsWith('2')) return '#ef4444'; // Red
    if (ratingStr.startsWith('3')) return '#f59e0b'; // Yellow
    return '#10b981'; // Green
  };

  return (
    <div className="card">
      <h3 style={{ marginBottom: '1rem' }}>Rating Distribution</h3>
      <div style={{ height: 300, width: '100%' }}>
        <ResponsiveContainer>
          <BarChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <XAxis dataKey="rating" />
            <YAxis allowDecimals={false} />
            <Tooltip />
            <Bar dataKey="count" radius={[4, 4, 0, 0]}>
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={getBarColor(entry.rating)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
