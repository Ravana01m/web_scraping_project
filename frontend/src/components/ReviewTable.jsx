import React, { useState, useMemo } from 'react';
import CharacterViewer from './CharacterViewer';
import { getDownloadUrl } from '../services/api';

export default function ReviewTable({ reviews, jobId }) {
  const [search, setSearch] = useState('');
  const [filterRating, setFilterRating] = useState('All');
  const [sortOrder, setSortOrder] = useState('Newest');
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedReview, setSelectedReview] = useState(null);
  
  const itemsPerPage = 10;

  const filteredAndSorted = useMemo(() => {
    let result = [...reviews];
    
    // Filter by search — use 'review' field (from Python API)
    if (search) {
      const lowerSearch = search.toLowerCase();
      result = result.filter(r => 
        (r.review && r.review.toLowerCase().includes(lowerSearch))
      );
    }
    
    // Filter by rating
    if (filterRating !== 'All') {
      const target = parseInt(filterRating);
      result = result.filter(r => {
        const rating = parseFloat(r.rating);
        return !isNaN(rating) && Math.floor(rating) === target;
      });
    }

    // Sort
    if (sortOrder === 'Highest Rating') {
      result.sort((a, b) => (parseFloat(b.rating) || 0) - (parseFloat(a.rating) || 0));
    } else if (sortOrder === 'Lowest Rating') {
      result.sort((a, b) => (parseFloat(a.rating) || 0) - (parseFloat(b.rating) || 0));
    }

    return result;
  }, [reviews, search, filterRating, sortOrder]);

  const totalPages = Math.ceil(filteredAndSorted.length / itemsPerPage);
  const paginatedData = filteredAndSorted.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  // Reset page when filters change
  React.useEffect(() => {
    setCurrentPage(1);
  }, [search, filterRating, sortOrder]);

  const handleDownload = () => {
    window.location.href = getDownloadUrl(jobId);
  };

  return (
    <div className="card">
      <h3 style={{ marginBottom: '1rem' }}>Reviews</h3>
      <div className="table-controls">
        <input 
          type="text" 
          placeholder="Search reviews..." 
          className="form-control search-bar"
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
        
        <div className="filters">
          {['All', '5', '4', '3', '2', '1'].map(r => (
            <button 
              key={r}
              className={`filter-btn ${filterRating === r ? 'active' : ''}`}
              onClick={() => setFilterRating(r)}
            >
              {r === 'All' ? 'All' : `${r}⭐`}
            </button>
          ))}
        </div>

        <select 
          className="form-control" 
          style={{ width: 'auto' }}
          value={sortOrder}
          onChange={e => setSortOrder(e.target.value)}
        >
          <option>Newest</option>
          <option>Highest Rating</option>
          <option>Lowest Rating</option>
        </select>

        {jobId && (
          <button className="btn btn-secondary" onClick={handleDownload}>
            ⬇ Download CSV
          </button>
        )}
      </div>

      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Rating</th>
              <th>Review</th>
              <th>Likes</th>
              <th>Dislikes</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {paginatedData.map((review, i) => {
              const globalIndex = (currentPage - 1) * itemsPerPage + i + 1;
              const reviewText = review.review || '';
              const snippet = reviewText.length > 200 ? reviewText.substring(0, 200) + '...' : reviewText;
              
              return (
                <tr key={i}>
                  <td>{globalIndex}</td>
                  <td>{review.rating ? `${review.rating}⭐` : '-'}</td>
                  <td>{snippet}</td>
                  <td>{review.likes ?? '-'}</td>
                  <td>{review.dislikes ?? '-'}</td>
                  <td>
                    <button 
                      className="btn btn-secondary"
                      style={{ padding: '0.25rem 0.5rem', fontSize: '0.875rem' }}
                      onClick={() => setSelectedReview(review)}
                    >
                      View Characters
                    </button>
                  </td>
                </tr>
              );
            })}
            {paginatedData.length === 0 && (
              <tr>
                <td colSpan="6" style={{ textAlign: 'center' }}>No reviews found</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && (
        <div className="pagination">
          <button 
            className="btn btn-secondary" 
            disabled={currentPage === 1}
            onClick={() => setCurrentPage(p => p - 1)}
          >
            Previous
          </button>
          <span>Page {currentPage} of {totalPages}</span>
          <button 
            className="btn btn-secondary" 
            disabled={currentPage === totalPages}
            onClick={() => setCurrentPage(p => p + 1)}
          >
            Next
          </button>
        </div>
      )}

      {selectedReview && (
        <CharacterViewer 
          characters={selectedReview.review_characters || Array.from(selectedReview.review || '')}
          review={selectedReview.review || ''}
          onClose={() => setSelectedReview(null)}
        />
      )}
    </div>
  );
}
