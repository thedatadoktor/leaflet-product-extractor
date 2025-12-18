import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

// Mock the API service to avoid axios issues
jest.mock('./services/api', () => ({
  apiService: {
    extractProducts: jest.fn(),
    listExtractions: jest.fn(),
    getExtraction: jest.fn(),
    healthCheck: jest.fn(),
  },
}));

describe('App Component', () => {
  test('renders main title', () => {
    render(<App />);
    expect(screen.getByText(/Leaflet Product Extractor/i)).toBeInTheDocument();
  });

  test('renders upload section', () => {
    render(<App />);
    expect(screen.getByText(/Upload Leaflet Image/i)).toBeInTheDocument();
  });

  test('renders footer', () => {
    render(<App />);
    expect(screen.getByText(/Built with/i)).toBeInTheDocument();
  });
});
