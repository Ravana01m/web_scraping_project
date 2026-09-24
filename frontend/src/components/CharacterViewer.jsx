import React, { useState } from 'react';

export default function CharacterViewer({ characters, review, onClose }) {
  const [showAll, setShowAll] = useState(false);
  
  const displayChars = showAll ? characters : characters.slice(0, 100);

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Character View ({characters.length} chars)</h2>
          <button className="close-btn" onClick={onClose}>&times;</button>
        </div>
        <div className="modal-body">
          <div style={{ marginBottom: '1.5rem', padding: '1rem', backgroundColor: 'var(--bg-color)', borderRadius: 'var(--border-radius)' }}>
            <strong>Original Text:</strong>
            <p style={{ marginTop: '0.5rem', fontSize: '0.875rem' }}>{review}</p>
          </div>
          
          <strong>Characters Array:</strong>
          <div className="char-grid">
            {displayChars.map((char, i) => (
              <span key={i} className="char-item">
                '{char === ' ' ? ' ' : char}'
              </span>
            ))}
          </div>
          
          {!showAll && characters.length > 100 && (
            <div style={{ textAlign: 'center', marginTop: '1rem' }}>
              <button className="btn btn-secondary" onClick={() => setShowAll(true)}>
                Show All {characters.length} Characters
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
