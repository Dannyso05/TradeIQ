import axios from 'axios';
import type { 
  Asset, 
  Portfolio, 
  PortfolioAnalysisResponse, 
  SamplePortfolioResponse,
  PortfolioUploadResponse,
  StoredPortfolioResponse,
  ClearPortfolioResponse,
  AnalysisRequest
} from '../models/types';

// Create axios instance with base URL
const api = axios.create({
  baseURL: 'http://localhost:3000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Portfolio API functions
export const portfolioAPI = {
  // Get a sample portfolio
  getSamplePortfolio: async (): Promise<SamplePortfolioResponse> => {
    const response = await api.get<SamplePortfolioResponse>('/portfolio/sample');
    return response.data;
  },

  // Get the stored portfolio
  getStoredPortfolio: async (): Promise<StoredPortfolioResponse> => {
    const response = await api.get<StoredPortfolioResponse>('/portfolio/stored-portfolio');
    return response.data;
  },

  // Upload a portfolio image
  uploadPortfolio: async (file: File): Promise<PortfolioUploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post<PortfolioUploadResponse>(
      '/portfolio/upload-portfolio',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    
    return response.data;
  },

  // Analyze a portfolio
  analyzePortfolio: async (data: AnalysisRequest): Promise<PortfolioAnalysisResponse> => {
    const response = await api.post<PortfolioAnalysisResponse>('/portfolio/analyze', data);
    return response.data;
  },

  // Clear the stored portfolio
  clearPortfolio: async (): Promise<ClearPortfolioResponse> => {
    const response = await api.delete<ClearPortfolioResponse>('/portfolio/clear-portfolio');
    return response.data;
  }
};

export default api; 