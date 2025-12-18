/**
 * Product details modal component
 */
import React from 'react';
import { Product } from '../types/product';

interface ProductDetailsProps {
  product: Product | null;
  onClose: () => void;
}

const ProductDetails: React.FC<ProductDetailsProps> = ({ product, onClose }) => {
  if (!product) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Product Details</h2>
          <button className="close-button" onClick={onClose}>
            ×
          </button>
        </div>

        <div className="modal-body">
          <div className="detail-row">
            <label>Product Name:</label>
            <span>{product.name}</span>
          </div>

          {product.description && (
            <div className="detail-row">
              <label>Description:</label>
              <span>{product.description}</span>
            </div>
          )}

          <div className="detail-row">
            <label>Price:</label>
            <span className="price-large">
              {product.currency} ${product.price.toFixed(2)}
            </span>
          </div>

          {product.unit_price && (
            <div className="detail-row">
              <label>Unit Price:</label>
              <span>
                ${product.unit_price.toFixed(2)} {product.unit}
              </span>
            </div>
          )}

          {product.special_offer && (
            <div className="detail-row">
              <label>Special Offer:</label>
              <span className="badge badge-offer-large">{product.special_offer}</span>
            </div>
          )}

          <div className="detail-row">
            <label>Confidence:</label>
            <span>
              {(product.confidence * 100).toFixed(1)}%
              <div className="confidence-bar">
                <div
                  className="confidence-fill"
                  style={{ width: `${product.confidence * 100}%` }}
                ></div>
              </div>
            </span>
          </div>

          {product.position && (
            <div className="detail-row">
              <label>Position in Image:</label>
              <span>
                ({product.position.x}, {product.position.y}) - {product.position.width}x
                {product.position.height}px
              </span>
            </div>
          )}

          <div className="detail-row">
            <label>Product ID:</label>
            <span className="product-id">{product.id}</span>
          </div>
        </div>

        <div className="modal-footer">
          <button className="btn-secondary" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProductDetails;
