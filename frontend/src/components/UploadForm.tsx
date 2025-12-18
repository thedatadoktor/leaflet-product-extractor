/**
 * File upload form component with drag-and-drop support
 */
import React, { useState, useCallback } from 'react';
import { ExtractionResponse } from '../types/product';
import apiService from '../services/api';

interface UploadFormProps {
  onExtractionComplete: (data: ExtractionResponse) => void;
}

const UploadForm: React.FC<UploadFormProps> = ({ onExtractionComplete }) => {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
      setError(null);
    }
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError(null);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!file) {
      setError('Please select a file');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const result = await apiService.extractProducts(file);
      onExtractionComplete(result);
      setFile(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Extraction failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="upload-form">
      <h2>Upload Leaflet Image</h2>

      <form onSubmit={handleSubmit}>
        <div
          className={`drop-zone ${dragActive ? 'drag-active' : ''}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <input
            type="file"
            id="file-upload"
            accept=".jpg,.jpeg,.png,.pdf"
            onChange={handleChange}
            disabled={loading}
          />
          <label htmlFor="file-upload">
            {file ? (
              <p className="file-selected">
                <strong>Selected:</strong> {file.name}
              </p>
            ) : (
              <p>
                Drag and drop your leaflet image here, or click to select
                <br />
                <small>Supported formats: JPG, PNG, PDF (max 10MB)</small>
              </p>
            )}
          </label>
        </div>

        {error && <div className="error-message">{error}</div>}

        <button type="submit" disabled={!file || loading}>
          {loading ? 'Processing...' : 'Extract Products'}
        </button>

        {loading && (
          <div className="loading-indicator">
            <div className="spinner"></div>
            <p>Extracting products from image... This may take a minute.</p>
          </div>
        )}
      </form>
    </div>
  );
};

export default UploadForm;
