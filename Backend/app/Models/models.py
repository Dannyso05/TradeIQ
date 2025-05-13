from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union

# Input Models
class Asset(BaseModel):
    ticker: str = Field(..., description="Stock ticker symbol")
    quantity: float = Field(..., description="Number of shares owned", gt=0)

class Portfolio(BaseModel):
    assets: List[Asset] = Field(..., description="List of assets in the portfolio")

# Risk Assessment Models
class RiskFactor(BaseModel):
    diversification: int = Field(..., description="Risk factor for portfolio diversification (1=low, 2=medium, 3=high)")
    volatility: int = Field(..., description="Risk factor for volatility (1=low, 2=medium, 3=high)")
    category_concentration: int = Field(..., description="Risk factor for category concentration (1=low, 2=medium, 3=high)")

class RiskAssessment(BaseModel):
    risk_level: str = Field(..., description="Overall risk level assessment")
    risk_score: float = Field(..., description="Numerical risk score")
    risk_factors: RiskFactor = Field(..., description="Breakdown of risk factors")

# Category Analysis Models
class CategoryAllocation(BaseModel):
    category: str = Field(..., description="Asset category")
    allocation: float = Field(..., description="Percentage allocation", ge=0, le=100)

class CategoryAnalysis(BaseModel):
    category_metrics: List[CategoryAllocation] = Field(..., description="Allocation by category")
    dominant_categories: List[str] = Field(..., description="Categories with >20% allocation")
    missing_categories: List[str] = Field(..., description="Major categories with <5% allocation")
    diversification_level: str = Field(..., description="Category diversification assessment")
    concentration_level: str = Field(..., description="Concentration assessment")

# Market Analysis Models
class SentimentAnalysis(BaseModel):
    sentiment: str = Field(..., description="Sentiment (positive, negative, neutral)")
    confidence: float = Field(..., description="Confidence score", ge=0, le=1)
    key_points: List[str] = Field(..., description="Key points from the analysis")

class MarketAnalysis(BaseModel):
    ticker_sentiment: Optional[SentimentAnalysis] = Field(None, description="Sentiment analysis for primary ticker")
    category_sentiments: Dict[str, SentimentAnalysis] = Field(default_factory=dict, description="Sentiment by category")
    news_summary: str = Field(..., description="Summary of relevant news")

# Forecasting Models
class ForecastMetrics(BaseModel):
    mae: float = Field(..., description="Mean Absolute Error")
    last_actual_close: float = Field(..., description="Last known closing price")
    forecast_end_price: float = Field(..., description="Forecasted end price")
    percent_change: float = Field(..., description="Forecasted percent change")

class ForecastResult(BaseModel):
    ticker: str = Field(..., description="Stock ticker symbol")
    forecast_days: int = Field(..., description="Number of days forecasted")
    metrics: ForecastMetrics = Field(..., description="Forecast metrics")
    plot: Optional[str] = Field(None, description="Plotly chart JSON")

# Investment Advice Models
class AllocationModel(BaseModel):
    stocks: float = Field(..., description="Percentage allocated to stocks", ge=0, le=100)
    bonds: float = Field(..., description="Percentage allocated to bonds", ge=0, le=100)
    cash: float = Field(..., description="Percentage allocated to cash", ge=0, le=100)
    other: float = Field(..., description="Percentage allocated to other assets", ge=0, le=100)

class InvestmentAdvice(BaseModel):
    assessment: str = Field(..., description="Overall portfolio assessment")
    recommendations: List[str] = Field(..., description="Specific recommendations")
    timeline: str = Field(..., description="Timeline considerations")
    allocation_model: AllocationModel = Field(..., description="Recommended allocation model")
    additional_notes: Optional[str] = Field(None, description="Additional notes")

# Portfolio Upload Models
class ExtractedData(BaseModel):
    ticker: str = Field(..., description="Stock ticker symbol")
    quantity: float = Field(..., description="Quantity of shares")

class PortfolioUploadResponse(BaseModel):
    message: str = Field(..., description="Status message")
    extracted_data: Dict[str, float] = Field(..., description="Raw extracted data")
    assets: List[Dict[str, Any]] = Field(..., description="Formatted assets data")

class StoredPortfolioResponse(BaseModel):
    assets: List[Dict[str, Any]] = Field(..., description="Stored portfolio assets")
    raw_data: Dict[str, Any] = Field(..., description="Raw extracted data")

class ClearPortfolioResponse(BaseModel):
    message: str = Field(..., description="Status message")

# Response Models
class PortfolioAnalysisResponse(BaseModel):
    report: str = Field(..., description="Comprehensive financial report")
    error: str = Field("", description="Error message if any")
    details: Dict[str, Any] = Field(default_factory=dict, description="Detailed analysis results")

class SamplePortfolioResponse(BaseModel):
    assets: List[Asset] = Field(..., description="Sample portfolio assets") 