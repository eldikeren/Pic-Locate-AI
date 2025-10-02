/**
 * PicLocate V4 Integrated Frontend
 * Complete end-to-end solution with V4 indexing and AI search
 */

import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import styles from '../styles/Home.module.css';

const API_BASE = 'http://localhost:8000';

export default function Home() {
  // State management
  const [searchQuery, setSearchQuery] = useState('');
  const [searchLang, setSearchLang] = useState('en');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [systemStatus, setSystemStatus] = useState(null);
  const [indexingStatus, setIndexingStatus] = useState(null);
  const [systemStats, setSystemStats] = useState(null);
  const [activeTab, setActiveTab] = useState('search');

  // Load system status on component mount
  useEffect(() => {
    loadSystemStatus();
    loadIndexingStatus();
    loadSystemStats();
    
    // Refresh status every 30 seconds
    const interval = setInterval(() => {
      loadSystemStatus();
      loadIndexingStatus();
      loadSystemStats();
    }, 30000);
    
    return () => clearInterval(interval);
  }, []);

  const loadSystemStatus = async () => {
    try {
      const response = await fetch(`${API_BASE}/health`);
      const data = await response.json();
      setSystemStatus(data);
    } catch (error) {
      console.error('Error loading system status:', error);
    }
  };

  const loadIndexingStatus = async () => {
    try {
      const response = await fetch(`${API_BASE}/indexing/status`);
      const data = await response.json();
      setIndexingStatus(data);
    } catch (error) {
      console.error('Error loading indexing status:', error);
    }
  };

  const loadSystemStats = async () => {
    try {
      const response = await fetch(`${API_BASE}/stats/overview`);
      const data = await response.json();
      setSystemStats(data);
    } catch (error) {
      console.error('Error loading system stats:', error);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    setIsSearching(true);
    try {
      const response = await fetch(`${API_BASE}/api/search/production`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: searchQuery,
          lang: searchLang,
          limit: 24
        }),
      });

      if (!response.ok) {
        throw new Error(`Search failed: ${response.statusText}`);
      }

      const data = await response.json();
      setSearchResults(data.results || []);
    } catch (error) {
      console.error('Search error:', error);
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  const startIndexing = async () => {
    try {
      const response = await fetch(`${API_BASE}/indexing/start`, {
        method: 'POST',
      });
      const data = await response.json();
      
      if (data.status === 'started') {
        alert('V4 indexing started! Check the status tab for progress.');
        loadIndexingStatus();
      } else {
        alert(`Failed to start indexing: ${data.message || data.error}`);
      }
    } catch (error) {
      console.error('Error starting indexing:', error);
      alert('Failed to start indexing');
    }
  };

  const getConfidenceBadge = (confidence) => {
    if (confidence >= 0.9) {
      return { color: 'green', text: 'High', icon: '✓' };
    } else if (confidence >= 0.7) {
      return { color: 'yellow', text: 'Medium', icon: '⚠' };
    } else {
      return { color: 'red', text: 'Low', icon: '?' };
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
    <div className={styles.container}>
      <Head>
        <title>PicLocate V4 - AI-Powered Image Search</title>
        <meta name="description" content="Advanced image search with AI verification" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className={styles.main}>
        {/* Header */}
        <div className={styles.header}>
          <h1 className={styles.title}>PicLocate V4</h1>
          <p className={styles.description}>
            AI-Powered Image Search with V4 Indexing
          </p>
        </div>

        {/* System Status */}
        {systemStatus && (
          <div className={styles.statusBar}>
            <div className={styles.statusItem}>
              <span className={styles.statusLabel}>System:</span>
              <span className={`${styles.statusValue} ${systemStatus.status === 'healthy' ? styles.healthy : styles.unhealthy}`}>
                {systemStatus.status}
              </span>
            </div>
            <div className={styles.statusItem}>
              <span className={styles.statusLabel}>V4 Backend:</span>
              <span className={styles.statusValue}>Running</span>
            </div>
            <div className={styles.statusItem}>
              <span className={styles.statusLabel}>AI Search:</span>
              <span className={`${styles.statusValue} ${systemStatus.components?.production_search === 'available' ? styles.available : styles.unavailable}`}>
                {systemStatus.components?.production_search || 'Unknown'}
              </span>
            </div>
            <div className={styles.statusItem}>
              <span className={styles.statusLabel}>Database:</span>
              <span className={`${styles.statusValue} ${systemStatus.components?.supabase === 'connected' ? styles.connected : styles.disconnected}`}>
                {systemStatus.components?.supabase || 'Unknown'}
              </span>
            </div>
          </div>
        )}

        {/* Navigation Tabs */}
        <div className={styles.tabs}>
          <button 
            className={`${styles.tab} ${activeTab === 'search' ? styles.activeTab : ''}`}
            onClick={() => setActiveTab('search')}
          >
            🔍 AI Search
          </button>
          <button 
            className={`${styles.tab} ${activeTab === 'indexing' ? styles.activeTab : ''}`}
            onClick={() => setActiveTab('indexing')}
          >
            ⚙️ V4 Indexing
          </button>
          <button 
            className={`${styles.tab} ${activeTab === 'stats' ? styles.activeTab : ''}`}
            onClick={() => setActiveTab('stats')}
          >
            📊 Statistics
          </button>
        </div>

        {/* Search Tab */}
        {activeTab === 'search' && (
          <div className={styles.tabContent}>
            <div className={styles.searchSection}>
              <h2>AI-Powered Image Search</h2>
              <p>Search with ChatGPT-like accuracy - AI analyzes images and gives final verdict</p>
              
              <div className={styles.searchForm}>
                <div className={styles.searchInputContainer}>
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder={searchLang === 'he' ? 'חפש תמונות...' : 'Search images...'}
                    className={styles.searchInput}
                    onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                  />
                  <button 
                    onClick={handleSearch} 
                    className={styles.searchButton}
                    disabled={isSearching}
                  >
                    {isSearching ? 'Searching...' : 'Search'}
                  </button>
                </div>
                
                <div className={styles.searchOptions}>
                  <label>
                    <input
                      type="radio"
                      value="en"
                      checked={searchLang === 'en'}
                      onChange={(e) => setSearchLang(e.target.value)}
                    />
                    English
                  </label>
                  <label>
                    <input
                      type="radio"
                      value="he"
                      checked={searchLang === 'he'}
                      onChange={(e) => setSearchLang(e.target.value)}
                    />
                    עברית
                  </label>
                </div>
              </div>

              {/* Search Results */}
              {searchResults.length > 0 && (
                <div className={styles.resultsSection}>
                  <h3>AI-Verified Results ({searchResults.length})</h3>
                  <div className={styles.resultsGrid}>
                    {searchResults.map((result, index) => {
                      const badge = getConfidenceBadge(result.vlm_confidence);
                      const evidence = formatEvidence(result.evidence);
                      
                      return (
                        <div key={result.image_id} className={styles.resultCard}>
                          <div className={styles.resultImage}>
                            <img 
                              src={`https://drive.google.com/uc?id=${result.image_id}`}
                              alt={result.file_name}
                              onError={(e) => {
                                e.target.src = '/placeholder-image.png';
                              }}
                            />
                            <div className={`${styles.confidenceBadge} ${styles[badge.color]}`}>
                              <span className={styles.badgeIcon}>{badge.icon}</span>
                              <span className={styles.badgeText}>{badge.text}</span>
                              <span className={styles.badgeScore}>{(result.vlm_confidence * 100).toFixed(0)}%</span>
                            </div>
                          </div>
                          
                          <div className={styles.resultInfo}>
                            <h4 className={styles.resultTitle}>{result.file_name}</h4>
                            <p className={styles.resultFolder}>{result.folder_path}</p>
                            
                            <div className={styles.resultEvidence}>
                              <div className={styles.evidenceSection}>
                                <strong>Room:</strong> {result.room}
                              </div>
                              {evidence.map((item, idx) => (
                                <div key={idx} className={styles.evidenceSection}>
                                  <strong>{item.split(':')[0]}:</strong> {item.split(':')[1]}
                                </div>
                              ))}
                            </div>
                            
                            <div className={styles.resultNotes}>
                              <strong>AI Analysis:</strong> {result.ai_notes}
                            </div>
                            
                            <div className={styles.resultScores}>
                              <div className={styles.scoreItem}>
                                <span>VLM Confidence:</span>
                                <span>{(result.vlm_confidence * 100).toFixed(1)}%</span>
                              </div>
                              <div className={styles.scoreItem}>
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
              {!isSearching && searchResults.length === 0 && searchQuery && (
                <div className={styles.noResults}>
                  <h3>No Results Found</h3>
                  <p>Try different keywords or be more specific in your search.</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Indexing Tab */}
        {activeTab === 'indexing' && (
          <div className={styles.tabContent}>
            <div className={styles.indexingSection}>
              <h2>V4 Indexing Status</h2>
              <p>Advanced AI pipeline for processing images with object detection, room classification, and embeddings</p>
              
              {indexingStatus && (
                <div className={styles.indexingStatus}>
                  <div className={styles.statusCard}>
                    <h3>Current Status</h3>
                    <div className={styles.statusGrid}>
                      <div className={styles.statusItem}>
                        <span className={styles.statusLabel}>Running:</span>
                        <span className={`${styles.statusValue} ${indexingStatus.is_running ? styles.running : styles.stopped}`}>
                          {indexingStatus.is_running ? 'Yes' : 'No'}
                        </span>
                      </div>
                      <div className={styles.statusItem}>
                        <span className={styles.statusLabel}>Started:</span>
                        <span className={styles.statusValue}>
                          {indexingStatus.started_at ? new Date(indexingStatus.started_at).toLocaleString() : 'Never'}
                        </span>
                      </div>
                      <div className={styles.statusItem}>
                        <span className={styles.statusLabel}>Processed:</span>
                        <span className={styles.statusValue}>{indexingStatus.processed_count}</span>
                      </div>
                      <div className={styles.statusItem}>
                        <span className={styles.statusLabel}>Total:</span>
                        <span className={styles.statusValue}>{indexingStatus.total_count}</span>
                      </div>
                      <div className={styles.statusItem}>
                        <span className={styles.statusLabel}>Progress:</span>
                        <span className={styles.statusValue}>{indexingStatus.progress_percentage.toFixed(1)}%</span>
                      </div>
                    </div>
                    
                    {indexingStatus.current_file && (
                      <div className={styles.currentFile}>
                        <strong>Current File:</strong> {indexingStatus.current_file}
                      </div>
                    )}
                    
                    {indexingStatus.errors.length > 0 && (
                      <div className={styles.errors}>
                        <strong>Errors:</strong>
                        <ul>
                          {indexingStatus.errors.map((error, idx) => (
                            <li key={idx}>{error}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                  
                  <div className={styles.progressBar}>
                    <div 
                      className={styles.progressFill}
                      style={{ width: `${indexingStatus.progress_percentage}%` }}
                    ></div>
                  </div>
                  
                  <button 
                    onClick={startIndexing}
                    className={styles.startButton}
                    disabled={indexingStatus.is_running}
                  >
                    {indexingStatus.is_running ? 'Indexing in Progress...' : 'Start V4 Indexing'}
                  </button>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Statistics Tab */}
        {activeTab === 'stats' && (
          <div className={styles.tabContent}>
            <div className={styles.statsSection}>
              <h2>System Statistics</h2>
              <p>Overview of indexed images, objects, and system performance</p>
              
              {systemStats && (
                <div className={styles.statsGrid}>
                  <div className={styles.statCard}>
                    <h3>Database Statistics</h3>
                    <div className={styles.statItems}>
                      <div className={styles.statItem}>
                        <span className={styles.statLabel}>Total Images:</span>
                        <span className={styles.statValue}>{systemStats.database_stats?.total_images || 0}</span>
                      </div>
                      <div className={styles.statItem}>
                        <span className={styles.statLabel}>Total Objects:</span>
                        <span className={styles.statValue}>{systemStats.database_stats?.total_objects || 0}</span>
                      </div>
                      <div className={styles.statItem}>
                        <span className={styles.statLabel}>Total Captions:</span>
                        <span className={styles.statValue}>{systemStats.database_stats?.total_captions || 0}</span>
                      </div>
                      <div className={styles.statItem}>
                        <span className={styles.statLabel}>Total Tags:</span>
                        <span className={styles.statValue}>{systemStats.database_stats?.total_tags || 0}</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className={styles.statCard}>
                    <h3>Room Distribution</h3>
                    <div className={styles.distributionList}>
                      {Object.entries(systemStats.distributions?.rooms || {}).map(([room, count]) => (
                        <div key={room} className={styles.distributionItem}>
                          <span className={styles.distributionLabel}>{room}:</span>
                          <span className={styles.distributionValue}>{count}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  <div className={styles.statCard}>
                    <h3>Top Objects</h3>
                    <div className={styles.distributionList}>
                      {Object.entries(systemStats.distributions?.objects || {}).map(([obj, count]) => (
                        <div key={obj} className={styles.distributionItem}>
                          <span className={styles.distributionLabel}>{obj}:</span>
                          <span className={styles.distributionValue}>{count}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  <div className={styles.statCard}>
                    <h3>Top Colors</h3>
                    <div className={styles.distributionList}>
                      {Object.entries(systemStats.distributions?.colors || {}).map(([color, count]) => (
                        <div key={color} className={styles.distributionItem}>
                          <span className={styles.distributionLabel}>{color}:</span>
                          <span className={styles.distributionValue}>{count}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
