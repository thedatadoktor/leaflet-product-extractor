/**
 * Main application component
 */
import React, { useState } from 'react';
import UploadForm from './components/UploadForm';
import ProductTable from './components/ProductTable';
import ProductDetails from './components/ProductDetails';
import { ExtractionResponse, Product } from './types/product';
import './App.css';

const App: React.FC = () => {
  const [extractionData, setExtractionData] = useState<ExtractionResponse | null>(null);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);

  const handleExtractionComplete = (data: ExtractionResponse) => {
    setExtractionData(data);
  };

  const handleProductClick = (product: Product) => {
    setSelectedProduct(product);
  };

  const handleCloseModal = () => {
    setSelectedProduct(null);
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>🛒 Leaflet Product Extractor</h1>
        <p className="subtitle">AI-powered product extraction from grocery store leaflets</p>
      </header>

      <main className="app-main">
        <UploadForm onExtractionComplete={handleExtractionComplete} />

        {extractionData && (
          <div className="extraction-results">
            <div className="results-header">
              <h3>Extraction Results</h3>
              <div className="extraction-stats">
                <span className="stat">
                  <strong>Products:</strong> {extractionData.total_products}
                </span>
                <span className="stat">
                  <strong>Processing Time:</strong> {extractionData.processing_time_seconds}s
                </span>
                {extractionData.json_file && (
                  <span className="stat">
                    <strong>Export:</strong> {extractionData.json_file.split('/').pop()}
                  </span>
                )}
              </div>
            </div>

            <ProductTable
              products={extractionData.products}
              onProductClick={handleProductClick}
            />
          </div>
        )}
      </main>

      <ProductDetails product={selectedProduct} onClose={handleCloseModal} />

      <footer className="app-footer">
        <p>
          Built with ❤️ using FastAPI, React, and EasyOCR |{' '}
          <a href="/docs" target="_blank" rel="noopener noreferrer">
            API Documentation
          </a>
        </p>
      </footer>
    </div>
  );
};

export default App;
