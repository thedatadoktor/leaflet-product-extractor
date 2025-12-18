/**
 * API service for communicating with the backend
 */
import axios, { AxiosInstance } from 'axios';
import { ExtractionResponse, ExtractionListItem } from '../types/product';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 120000, // 2 minutes for large file processing
    });
  }

  /**
   * Extract products from an uploaded image
   */
  async extractProducts(file: File): Promise<ExtractionResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await this.client.post<ExtractionResponse>(
      '/api/v1/extract',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );

    return response.data;
  }

  /**
   * Get list of recent extractions
   */
  async listExtractions(limit: number = 10): Promise<ExtractionListItem[]> {
    const response = await this.client.get('/api/v1/extractions', {
      params: { limit },
    });

    return response.data.extractions;
  }

  /**
   * Get a specific extraction by ID
   */
  async getExtraction(extractionId: string): Promise<any> {
    const response = await this.client.get(`/api/v1/extractions/${extractionId}`);
    return response.data.extraction;
  }

  /**
   * Check API health
   */
  async healthCheck(): Promise<{ status: string; version: string }> {
    const response = await this.client.get('/health');
    return response.data;
  }
}

export const apiService = new ApiService();
export default apiService;
