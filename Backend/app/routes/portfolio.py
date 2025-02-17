from fastapi import APIRouter
from typing import List  # Ensure List is imported
from models import Asset, Portfolio, RiskAssessment, DiversificationSuggestion, PlotlyJSONSchema
from services.portfolio import analyze_portfolio, plotly_data

router = APIRouter()

# @router.post("/analysis", response_model=RiskAssessment)
# async def portfolio_analysis(portfolio: Portfolio):
#     return analyze_portfolio(portfolio.assets)

@router.post("/analysis")
async def portfolio_analysis(portfolio: Portfolio):
    return analyze_portfolio(portfolio.assets)

