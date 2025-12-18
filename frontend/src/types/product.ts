/**
 * TypeScript type definitions for products and API responses
 */

export interface Position {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface Product {
  id: string;
  name: string;
  description?: string;
  price: number;
  unit_price?: number;
  unit?: string;
  currency: string;
  special_offer?: string;
  position?: Position;
  confidence: number;
}

export interface ExtractionResponse {
  success: boolean;
  message: string;
  products: Product[];
  total_products: number;
  processing_time_seconds: number;
  json_file?: string;
  extraction_id?: string;
  timestamp?: string;
}

export interface ExtractionListItem {
  filename: string;
  filepath: string;
  extraction_id: string;
  timestamp: string;
  total_products: number;
  source_image: string;
}

export interface ErrorResponse {
  success: false;
  message: string;
  error_code?: string;
  details?: Record<string, any>;
}
