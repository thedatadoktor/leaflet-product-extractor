/**
 * Product table component with sorting and filtering
 */
import React, { useState, useMemo } from 'react';
import { Product } from '../types/product';

interface ProductTableProps {
  products: Product[];
  onProductClick: (product: Product) => void;
}

type SortField = 'name' | 'price' | 'confidence';
type SortDirection = 'asc' | 'desc';

const ProductTable: React.FC<ProductTableProps> = ({ products, onProductClick }) => {
  const [sortField, setSortField] = useState<SortField>('name');
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc');
  const [searchTerm, setSearchTerm] = useState('');

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const filteredAndSortedProducts = useMemo(() => {
    let filtered = products;

    // Apply search filter
    if (searchTerm) {
      filtered = products.filter((product) =>
        product.name.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Apply sorting
    const sorted = [...filtered].sort((a, b) => {
      let aValue: any = a[sortField];
      let bValue: any = b[sortField];

      if (typeof aValue === 'string') {
        aValue = aValue.toLowerCase();
        bValue = bValue.toLowerCase();
      }

      if (aValue < bValue) return sortDirection === 'asc' ? -1 : 1;
      if (aValue > bValue) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });

    return sorted;
  }, [products, sortField, sortDirection, searchTerm]);

  if (products.length === 0) {
    return (
      <div className="no-products">
        <p>No products extracted yet. Upload a leaflet image to get started.</p>
      </div>
    );
  }

  return (
    <div className="product-table-container">
      <div className="table-header">
        <h2>Extracted Products ({filteredAndSortedProducts.length})</h2>
        <input
          type="text"
          placeholder="Search products..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="search-input"
        />
      </div>

      <table className="product-table">
        <thead>
          <tr>
            <th onClick={() => handleSort('name')} className="sortable">
              Product Name {sortField === 'name' && (sortDirection === 'asc' ? '↑' : '↓')}
            </th>
            <th>Description</th>
            <th onClick={() => handleSort('price')} className="sortable">
              Price {sortField === 'price' && (sortDirection === 'asc' ? '↑' : '↓')}
            </th>
            <th>Unit Price</th>
            <th>Special Offer</th>
            <th onClick={() => handleSort('confidence')} className="sortable">
              Confidence {sortField === 'confidence' && (sortDirection === 'asc' ? '↑' : '↓')}
            </th>
          </tr>
        </thead>
        <tbody>
          {filteredAndSortedProducts.map((product) => (
            <tr key={product.id} onClick={() => onProductClick(product)} className="clickable">
              <td className="product-name">{product.name}</td>
              <td>{product.description || '-'}</td>
              <td className="price">
                {product.currency} ${product.price.toFixed(2)}
              </td>
              <td className="unit-price">
                {product.unit_price ? `$${product.unit_price.toFixed(2)} ${product.unit}` : '-'}
              </td>
              <td>
                {product.special_offer && (
                  <span className="badge badge-offer">{product.special_offer}</span>
                )}
              </td>
              <td>
                <span className={`confidence confidence-${Math.floor(product.confidence * 10)}`}>
                  {(product.confidence * 100).toFixed(0)}%
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ProductTable;
