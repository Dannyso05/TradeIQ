from fastapi import APIRouter
from typing import List  # Ensure List is imported
from models import Asset, Portfolio, RiskAssessment, DiversificationSuggestion, PlotlyJSONSchema
from services.portfolio import analyze_portfolio, plotly_data

router = APIRouter()

# @router.post("/analysis", response_model=RiskAssessment)
# async def portfolio_analysis(portfolio: Portfolio):
#     return analyze_portfolio(portfolio.assets)

@router.get("/analysis")
async def portfolio_analysis():
    portfolio = [
        Asset(name="Apple Inc.", ticker="AZZZPL", total_price=1500.0),  # 10 shares at $150 each
        Asset(name="Tesla Inc.", ticker="TSLA", total_price=3500.0),  # 5 shares at $700 each
        Asset(name="Amazon.com Inc.", ticker="AMZN", total_price=6000.0)  # 2 shares at $3000 each
    ]
    return analyze_portfolio(portfolio)

@router.post("/recommendations", response_model=List[DiversificationSuggestion])
async def portfolio_recommendations(portfolio: Portfolio):
    # For simplicity, return a mock recommendation
    return [
        DiversificationSuggestion(suggested_asset="TSLA", suggested_percentage=20),
        DiversificationSuggestion(suggested_asset="SPY", suggested_percentage=15)
    ]

@router.get("/graph", response_model=PlotlyJSONSchema)
async def getgraphs(ticker):
    data = plotly_data(ticker)

