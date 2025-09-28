'use client'

import { useState, useEffect } from 'react'
import { Search, Upload, Database, Image as ImageIcon, Loader2 } from 'lucide-react'
import axios from 'axios'

const API_BASE = 'http://localhost:6000'

interface SearchResult {
  file_id: string
  name: string
  score: number
  objects: string[]
  colors: number[][]
  semantic_score: number
  object_score: number
  color_score: number
}

interface Requirements {
  location?: string
  style: string[]
  required_objects: string[]
  required_colors: number[][]
  raw_text?: string
}

export default function Home() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isIndexing, setIsIndexing] = useState(false)
  const [indexStats, setIndexStats] = useState<any>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [requiredObjects, setRequiredObjects] = useState<string[]>([])
  const [requiredColors, setRequiredColors] = useState<number[][]>([])
  const [searchResults, setSearchResults] = useState<SearchResult[]>([])
  const [isSearching, setIsSearching] = useState(false)
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)
  const [parsedRequirements, setParsedRequirements] = useState<Requirements | null>(null)
  const [isParsing, setIsParsing] = useState(false)

  // Check authentication status
  useEffect(() => {
    checkAuthStatus()
  }, [])

  const checkAuthStatus = async () => {
    try {
      const response = await axios.get(`${API_BASE}/health`)
      setIsAuthenticated(response.data.authenticated)
    } catch (error) {
      console.error('Auth check failed:', error)
    }
  }

  const handleAuth = async () => {
    try {
      window.open(`${API_BASE}/auth`, '_blank')
      // Wait a bit then check auth status
      setTimeout(checkAuthStatus, 3000)
    } catch (error) {
      console.error('Auth failed:', error)
    }
  }

  const handleIndex = async () => {
    setIsIndexing(true)
    try {
      const response = await axios.post(`${API_BASE}/index`)
      setIndexStats(response.data)
      setIsIndexing(false)
    } catch (error) {
      console.error('Indexing failed:', error)
      setIsIndexing(false)
    }
  }

  const handleSearch = async () => {
    if (!searchQuery.trim()) return
    
    setIsSearching(true)
    try {
      const response = await axios.post(`${API_BASE}/search`, {
        query: searchQuery,
        required_objects: requiredObjects,
        required_colors: requiredColors,
        top_k: 10
      })
      setSearchResults(response.data)
    } catch (error) {
      console.error('Search failed:', error)
    } finally {
      setIsSearching(false)
    }
  }

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    setUploadedFile(file)
    setIsParsing(true)

    try {
      const formData = new FormData()
      formData.append('file', file)
      
      const response = await axios.post(`${API_BASE}/parse_requirements`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      
      setParsedRequirements(response.data.requirements)
      
      // Auto-populate search fields
      if (response.data.requirements.required_objects.length > 0) {
        setRequiredObjects(response.data.requirements.required_objects)
      }
      if (response.data.requirements.required_colors.length > 0) {
        setRequiredColors(response.data.requirements.required_colors)
      }
      if (response.data.requirements.location) {
        setSearchQuery(`modern ${response.data.requirements.location}`)
      }
    } catch (error) {
      console.error('File parsing failed:', error)
    } finally {
      setIsParsing(false)
    }
  }

  const addObject = (object: string) => {
    if (!requiredObjects.includes(object)) {
      setRequiredObjects([...requiredObjects, object])
    }
  }

  const removeObject = (object: string) => {
    setRequiredObjects(requiredObjects.filter(o => o !== object))
  }

  const addColor = (color: number[]) => {
    if (!requiredColors.some(c => c.every((val, i) => val === color[i]))) {
      setRequiredColors([...requiredColors, color])
    }
  }

  const removeColor = (color: number[]) => {
    setRequiredColors(requiredColors.filter(c => !c.every((val, i) => val === color[i])))
  }

  const rgbToHex = (rgb: number[]) => {
    return `#${rgb.map(x => x.toString(16).padStart(2, '0')).join('')}`
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Google Drive AI Visual Search
        </h1>
        <p className="text-lg text-gray-600">
          Find images in your Google Drive using natural language, object detection, and color matching
        </p>
      </div>

      {/* Authentication Section */}
      <div className="card mb-8">
        <h2 className="text-2xl font-semibold mb-4 flex items-center">
          <Database className="mr-2" />
          Setup
        </h2>
        
        {!isAuthenticated ? (
          <div className="text-center">
            <p className="text-gray-600 mb-4">
              Connect to your Google Drive to start searching
            </p>
            <button onClick={handleAuth} className="btn-primary">
              Connect Google Drive
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center text-green-600">
              <Database className="mr-2" />
              <span>Connected to Google Drive</span>
            </div>
            
            <div className="flex items-center space-x-4">
              <button 
                onClick={handleIndex} 
                disabled={isIndexing}
                className="btn-primary flex items-center"
              >
                {isIndexing ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <Database className="mr-2 h-4 w-4" />
                )}
                {isIndexing ? 'Indexing...' : 'Index Drive Images'}
              </button>
              
              {indexStats && (
                <span className="text-sm text-gray-600">
                  {indexStats.total_images} images indexed
                </span>
              )}
            </div>
          </div>
        )}
      </div>

      {/* File Upload Section */}
      <div className="card mb-8">
        <h2 className="text-2xl font-semibold mb-4 flex items-center">
          <Upload className="mr-2" />
          Upload Requirements
        </h2>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Upload Storyboard or PDF
            </label>
            <input
              type="file"
              accept=".pdf,.txt,.doc,.docx"
              onChange={handleFileUpload}
              className="input-field"
            />
          </div>
          
          {isParsing && (
            <div className="flex items-center text-blue-600">
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              <span>Parsing requirements...</span>
            </div>
          )}
          
          {parsedRequirements && (
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-medium mb-2">Extracted Requirements:</h3>
              <div className="space-y-2 text-sm">
                {parsedRequirements.location && (
                  <p><strong>Location:</strong> {parsedRequirements.location}</p>
                )}
                {parsedRequirements.style.length > 0 && (
                  <p><strong>Style:</strong> {parsedRequirements.style.join(', ')}</p>
                )}
                {parsedRequirements.required_objects.length > 0 && (
                  <p><strong>Objects:</strong> {parsedRequirements.required_objects.join(', ')}</p>
                )}
                {parsedRequirements.required_colors.length > 0 && (
                  <p><strong>Colors:</strong> {parsedRequirements.required_colors.length} colors detected</p>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Search Section */}
      <div className="card mb-8">
        <h2 className="text-2xl font-semibold mb-4 flex items-center">
          <Search className="mr-2" />
          Search Images
        </h2>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Search Query
            </label>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="e.g., modern kitchen with purple island"
              className="input-field"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Required Objects
            </label>
            <div className="flex flex-wrap gap-2 mb-2">
              {requiredObjects.map(obj => (
                <span
                  key={obj}
                  className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-sm flex items-center"
                >
                  {obj}
                  <button
                    onClick={() => removeObject(obj)}
                    className="ml-1 text-blue-600 hover:text-blue-800"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
            <div className="flex flex-wrap gap-2">
              {['island', 'bed', 'sofa', 'table', 'chair', 'stove', 'sink', 'lamp'].map(obj => (
                <button
                  key={obj}
                  onClick={() => addObject(obj)}
                  className="bg-gray-200 text-gray-700 px-2 py-1 rounded text-sm hover:bg-gray-300"
                >
                  + {obj}
                </button>
              ))}
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Required Colors
            </label>
            <div className="flex flex-wrap gap-2 mb-2">
              {requiredColors.map((color, i) => (
                <span
                  key={i}
                  className="flex items-center px-2 py-1 rounded-full text-sm"
                  style={{ backgroundColor: rgbToHex(color), color: 'white' }}
                >
                  {rgbToHex(color)}
                  <button
                    onClick={() => removeColor(color)}
                    className="ml-1 hover:bg-black hover:bg-opacity-20 rounded"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
            <div className="flex flex-wrap gap-2">
              {[
                { name: 'Red', rgb: [255, 0, 0] },
                { name: 'Blue', rgb: [0, 0, 255] },
                { name: 'Green', rgb: [0, 128, 0] },
                { name: 'Purple', rgb: [128, 0, 128] },
                { name: 'Pink', rgb: [255, 192, 203] },
                { name: 'Orange', rgb: [255, 165, 0] }
              ].map(color => (
                <button
                  key={color.name}
                  onClick={() => addColor(color.rgb)}
                  className="px-2 py-1 rounded text-sm text-white hover:opacity-80"
                  style={{ backgroundColor: rgbToHex(color.rgb) }}
                >
                  + {color.name}
                </button>
              ))}
            </div>
          </div>
          
          <button
            onClick={handleSearch}
            disabled={isSearching || !searchQuery.trim()}
            className="btn-primary flex items-center"
          >
            {isSearching ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <Search className="mr-2 h-4 w-4" />
            )}
            {isSearching ? 'Searching...' : 'Search Images'}
          </button>
        </div>
      </div>

      {/* Results Section */}
      {searchResults.length > 0 && (
        <div className="card">
          <h2 className="text-2xl font-semibold mb-4 flex items-center">
            <ImageIcon className="mr-2" />
            Search Results ({searchResults.length})
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {searchResults.map((result, index) => (
              <div key={result.file_id} className="bg-white border rounded-lg p-4 shadow-sm">
                <div className="aspect-video bg-gray-200 rounded-lg mb-3 flex items-center justify-center">
                  <ImageIcon className="h-12 w-12 text-gray-400" />
                </div>
                
                <h3 className="font-medium text-sm mb-2 truncate">{result.name}</h3>
                
                <div className="space-y-2 text-xs">
                  <div className="flex justify-between">
                    <span>Overall Score:</span>
                    <span className="font-medium">{result.score.toFixed(3)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Semantic:</span>
                    <span>{result.semantic_score.toFixed(3)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Objects:</span>
                    <span>{result.object_score.toFixed(3)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Colors:</span>
                    <span>{result.color_score.toFixed(3)}</span>
                  </div>
                </div>
                
                {result.objects.length > 0 && (
                  <div className="mt-2">
                    <p className="text-xs text-gray-600 mb-1">Objects:</p>
                    <div className="flex flex-wrap gap-1">
                      {result.objects.slice(0, 3).map(obj => (
                        <span key={obj} className="bg-blue-100 text-blue-800 px-1 py-0.5 rounded text-xs">
                          {obj}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                
                {result.colors.length > 0 && (
                  <div className="mt-2">
                    <p className="text-xs text-gray-600 mb-1">Colors:</p>
                    <div className="flex gap-1">
                      {result.colors.slice(0, 3).map((color, i) => (
                        <div
                          key={i}
                          className="w-4 h-4 rounded border"
                          style={{ backgroundColor: rgbToHex(color) }}
                          title={rgbToHex(color)}
                        />
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

