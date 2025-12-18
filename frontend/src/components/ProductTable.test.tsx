import React from 'react';
import { render, screen } from '@testing-library/react';
import ProductTable from './ProductTable';
import { Product } from '../types/product';

const mockProducts: Product[] = [
  {
    id: 'test-1',
    name: 'Test Product',
    price: 3.49,
    currency: 'AUD',
    confidence: 0.95
  }
];

describe('ProductTable Component', () => {
  test('renders product table with data', () => {
    const mockOnClick = jest.fn();
    render(<ProductTable products={mockProducts} onProductClick={mockOnClick} />);
    expect(screen.getByText('Test Product')).toBeInTheDocument();
  });

  test('shows no products message when empty', () => {
    const mockOnClick = jest.fn();
    render(<ProductTable products={[]} onProductClick={mockOnClick} />);
    expect(screen.getByText(/No products extracted/i)).toBeInTheDocument();
  });

  test('displays product count', () => {
    const mockOnClick = jest.fn();
    render(<ProductTable products={mockProducts} onProductClick={mockOnClick} />);
    expect(screen.getByText(/Extracted Products \(1\)/i)).toBeInTheDocument();
  });
});
