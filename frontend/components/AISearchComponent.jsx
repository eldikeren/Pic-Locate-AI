/**
 * AI Search Component for PicLocate
 * Implements ChatGPT-like image search with AI verification
 */

import React, { useState, useEffect } from 'react';
import './AISearchComponent.css';

const AISearchComponent = () => {
  const [query, setQuery] = useState('');
  const [lang, setLang] = useState('en');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const [trending, setTrending] = useState(null);
  const [stats, setStats] = useState(null);

  // Load trending searches and stats on component mount
  useEffect(() => {
    loadTrendingSearches();
    loadSearchStats();
  }, []);

  // Load search suggestions as user types
  useEffect(() => {
    if (query.length > 2) {
      loadSuggestions(query);
    } else {
      setSuggestions([]);
    }
  }, [query]);

  const loadTrendingSearches = async () => {
    try {
      const response = await fetch('/api/search/trending');
      const data = await response.json();
      setTrending(data);
    } catch (error) {
      console.error('Error loading trending searches:', error);
    }
  };

  const loadSearchStats = async () => {
    try {
      const response = await fetch('/api/search/stats');
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Error loading search stats:', error);
    }
  };

  const loadSuggestions = async (partialQuery) => {
    try {
      const response = await fetch(`/api/search/suggestions?q=${encodeURIComponent(partialQuery)}`);
      const data = await response.json();
      setSuggestions(data.suggestions || []);
    } catch (error) {
      console.error('Error loading suggestions:', error);
    }
  };

  const handleSearch = async (searchQuery = query) => {
    if (!searchQuery.trim()) return;

    setLoading(true);
    try {
      const response = await fetch('/api/search/production', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: searchQuery,
          lang: lang,
          limit: 24
        }),
      });

      if (!response.ok) {
        throw new Error(`Search failed: ${response.statusText}`);
      }

      const data = await response.json();
      setResults(data.results || []);
    } catch (error) {
      console.error('Search error:', error);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setQuery(suggestion);
    handleSearch(suggestion);
  };

  const getConfidenceBadge = (confidence) => {
    if (confidence >= 0.9) {
      return { color: 'green', text: 'High Confidence', icon: '✓' };
    } else if (confidence >= 0.7) {
      return { color: 'yellow', text: 'Medium Confidence', icon: '⚠' };
    } else {
      return { color: 'red', text: 'Low Confidence', icon: '?' };
    }
  };

  const formatEvidence = (evidence) => {
    const parts = [];
    
    if (evidence.objects && evidence.objects.length > 0) {
      parts.push(`Objects: ${evidence.objects.join(', ')}`);
    }
    
    if (evidence.colors && Object.keys(evidence.colors).length > 0) {
      const colorDesc = Object.entries(evidence.colors)
        .map(([obj, color]) => `${obj}=${color}`)
        .join(', ');
      parts.push(`Colors: ${colorDesc}`);
    }
    
    if (evidence.materials && Object.keys(evidence.materials).length > 0) {
      const materialDesc = Object.entries(evidence.materials)
        .map(([obj, material]) => `${obj}=${material}`)
        .join(', ');
      parts.push(`Materials: ${materialDesc}`);
    }
    
    return parts;
  };

  return (
    <div className="ai-search-container">
      {/* Header */}
      <div className="search-header">
        <h1>AI-Powered Image Search</h1>
        <p>Search like ChatGPT - AI analyzes images and gives final verdict</p>
      </div>

      {/* Search Form */}
      <div className="search-form">
        <div className="search-input-container">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={lang === 'he' ? 'חפש תמונות...' : 'Search images...'}
            className="search-input"
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          />
          <button 
            onClick={() => handleSearch()} 
            className="search-button"
            disabled={loading}
          >
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>
        
        <div className="search-options">
          <label>
            <input
              type="radio"
              value="en"
              checked={lang === 'en'}
              onChange={(e) => setLang(e.target.value)}
            />
            English
          </label>
          <label>
            <input
              type="radio"
              value="he"
              checked={lang === 'he'}
              onChange={(e) => setLang(e.target.value)}
            />
            עברית
          </label>
        </div>
      </div>

      {/* Suggestions */}
      {suggestions.length > 0 && (
        <div className="suggestions">
          <h3>Suggestions:</h3>
          <div className="suggestion-tags">
            {suggestions.map((suggestion, index) => (
              <button
                key={index}
                className="suggestion-tag"
                onClick={() => handleSuggestionClick(suggestion)}
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Trending Searches */}
      {trending && (
        <div className="trending">
          <h3>Trending Searches:</h3>
          <div className="trending-content">
            <div className="trending-section">
              <h4>Popular Rooms:</h4>
              {trending.trending_rooms.map((item, index) => (
                <span key={index} className="trending-item">
                  {item.room} ({item.count})
                </span>
              ))}
            </div>
            <div className="trending-section">
              <h4>Popular Objects:</h4>
              {trending.trending_objects.map((item, index) => (
                <span key={index} className="trending-item">
                  {item.object} ({item.count})
                </span>
              ))}
            </div>
            <div className="trending-section">
              <h4>Popular Colors:</h4>
              {trending.trending_colors.map((item, index) => (
                <span key={index} className="trending-item">
                  {item.color} ({item.count})
                </span>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Search Results */}
      {results.length > 0 && (
        <div className="search-results">
          <h3>AI-Verified Results ({results.length})</h3>
          <div className="results-grid">
            {results.map((result, index) => {
              const badge = getConfidenceBadge(result.vlm_confidence);
              const evidence = formatEvidence(result.evidence);
              
              return (
                <div key={result.image_id} className="result-card">
                  <div className="result-image">
                    <img 
                      src={`https://drive.google.com/uc?id=${result.image_id}`}
                      alt={result.file_name}
                      onError={(e) => {
                        e.target.src = '/placeholder-image.png';
                      }}
                    />
                    <div className={`confidence-badge ${badge.color}`}>
                      <span className="badge-icon">{badge.icon}</span>
                      <span className="badge-text">{badge.text}</span>
                      <span className="badge-score">{(result.vlm_confidence * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                  
                  <div className="result-info">
                    <h4 className="result-title">{result.file_name}</h4>
                    <p className="result-folder">{result.folder_path}</p>
                    
                    <div className="result-evidence">
                      <div className="evidence-section">
                        <strong>Room:</strong> {result.room}
                      </div>
                      {evidence.map((item, idx) => (
                        <div key={idx} className="evidence-section">
                          <strong>{item.split(':')[0]}:</strong> {item.split(':')[1]}
                        </div>
                      ))}
                    </div>
                    
                    <div className="result-notes">
                      <strong>AI Analysis:</strong> {result.ai_notes}
                    </div>
                    
                    <div className="result-scores">
                      <div className="score-item">
                        <span>VLM Confidence:</span>
                        <span>{(result.vlm_confidence * 100).toFixed(1)}%</span>
                      </div>
                      <div className="score-item">
                        <span>Final Score:</span>
                        <span>{(result.final_score * 100).toFixed(1)}%</span>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* No Results */}
      {!loading && results.length === 0 && query && (
        <div className="no-results">
          <h3>No Results Found</h3>
          <p>Try different keywords or be more specific in your search.</p>
        </div>
      )}

      {/* Stats */}
      {stats && (
        <div className="search-stats">
          <h3>Search Engine Stats</h3>
          <div className="stats-grid">
            <div className="stat-item">
              <span className="stat-label">Total Images:</span>
              <span className="stat-value">{stats.total_images}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Total Objects:</span>
              <span className="stat-value">{stats.total_objects}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">AI Search:</span>
              <span className={`stat-value ${stats.search_engine_available ? 'available' : 'unavailable'}`}>
                {stats.search_engine_available ? 'Available' : 'Unavailable'}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AISearchComponent;
