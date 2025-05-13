// Portfolio and Asset Types
export interface Asset {
  ticker: string;
  quantity: number;
}

export interface Portfolio {
  assets: Asset[];
}

// API Response Types
export interface PortfolioAnalysisResponse {
  report: string;
  error: string;
  details: {
    riskScore?: number;
    categories?: Record<string, number>;
    recommendations?: string[];
    forecasts?: Record<string, any>;
    [key: string]: any;
  };
}

export interface SamplePortfolioResponse {
  assets: Asset[];
}

export interface PortfolioUploadResponse {
  message: string;
  extracted_data: Record<string, number>;
  assets: Asset[];
}

export interface StoredPortfolioResponse {
  assets: Asset[];
  raw_data: {
    extracted_text?: string;
    processed_data?: Record<string, any>;
    [key: string]: any;
  };
}

export interface ClearPortfolioResponse {
  message: string;
}

// API Request Types
export interface AnalysisRequest {
  portfolio?: Portfolio;
  goals?: string[];
} 