import yfinance as yf
import pandas as pd
import numpy as np
from typing import List, Dict, Any
from langchain.tools import Tool
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

class PortfolioTools:
    """Tools for analyzing and assessing investment portfolios."""
    
    # Stock categories mapping (simplified)
    STOCK_CATEGORIES = {
        # Technology
        'AAPL': 'Technology', 'MSFT': 'Technology', 'GOOGL': 'Technology', 'GOOG': 'Technology', 
        'META': 'Technology', 'AMZN': 'Technology', 'NVDA': 'Technology', 'TSLA': 'Technology',
        'AMD': 'Technology', 'INTC': 'Technology', 'IBM': 'Technology', 'CSCO': 'Technology',
        'ORCL': 'Technology', 'CRM': 'Technology', 'ADBE': 'Technology',
        
        # Healthcare
        'JNJ': 'Healthcare', 'PFE': 'Healthcare', 'MRK': 'Healthcare', 'ABT': 'Healthcare',
        'UNH': 'Healthcare', 'ABBV': 'Healthcare', 'BMY': 'Healthcare', 'TMO': 'Healthcare',
        'DHR': 'Healthcare', 'AMGN': 'Healthcare',
        
        # Finance
        'JPM': 'Finance', 'BAC': 'Finance', 'WFC': 'Finance', 'GS': 'Finance', 'MS': 'Finance',
        'C': 'Finance', 'AXP': 'Finance', 'BLK': 'Finance', 'SCHW': 'Finance',
        
        # Consumer
        'KO': 'Consumer', 'PEP': 'Consumer', 'PG': 'Consumer', 'WMT': 'Consumer', 'MCD': 'Consumer',
        'SBUX': 'Consumer', 'NKE': 'Consumer', 'DIS': 'Consumer', 'HD': 'Consumer', 'COST': 'Consumer',
        
        # Energy
        'XOM': 'Energy', 'CVX': 'Energy', 'COP': 'Energy', 'EOG': 'Energy', 'SLB': 'Energy',
        'OXY': 'Energy',
        
        # Telecoms
        'VZ': 'Telecommunications', 'T': 'Telecommunications', 'TMUS': 'Telecommunications',
        
        # Real Estate
        'AMT': 'Real Estate', 'EQIX': 'Real Estate', 'PLD': 'Real Estate', 'CCI': 'Real Estate',
        
        # Industry
        'GE': 'Industrial', 'MMM': 'Industrial', 'HON': 'Industrial', 'CAT': 'Industrial',
        'BA': 'Industrial', 'LMT': 'Industrial', 'RTX': 'Industrial',
        
        # ETFs
        'SPY': 'ETF', 'QQQ': 'ETF', 'IWM': 'ETF', 'DIA': 'ETF', 'VTI': 'ETF',
        'VOO': 'ETF', 'VEA': 'ETF', 'VWO': 'ETF', 'BND': 'ETF', 'AGG': 'ETF',
        'VNQ': 'ETF', 'GLD': 'ETF', 'SLV': 'ETF'
    }
    
    # Default ETF recommendations for each risk profile
    DEFAULT_RECOMMENDATIONS = {
        'low_risk': [
            {'ticker': 'BND', 'name': 'Vanguard Total Bond Market ETF', 'allocation': 40},
            {'ticker': 'VTI', 'name': 'Vanguard Total Stock Market ETF', 'allocation': 30},
            {'ticker': 'VEA', 'name': 'Vanguard FTSE Developed Markets ETF', 'allocation': 20},
            {'ticker': 'VTIP', 'name': 'Vanguard Short-Term Inflation-Protected Securities ETF', 'allocation': 10},
        ],
        'moderate_risk': [
            {'ticker': 'VTI', 'name': 'Vanguard Total Stock Market ETF', 'allocation': 45},
            {'ticker': 'VEA', 'name': 'Vanguard FTSE Developed Markets ETF', 'allocation': 25},
            {'ticker': 'BND', 'name': 'Vanguard Total Bond Market ETF', 'allocation': 20},
            {'ticker': 'VWO', 'name': 'Vanguard FTSE Emerging Markets ETF', 'allocation': 10},
        ],
        'high_risk': [
            {'ticker': 'VTI', 'name': 'Vanguard Total Stock Market ETF', 'allocation': 50},
            {'ticker': 'VWO', 'name': 'Vanguard FTSE Emerging Markets ETF', 'allocation': 25},
            {'ticker': 'VEA', 'name': 'Vanguard FTSE Developed Markets ETF', 'allocation': 15},
            {'ticker': 'ARKK', 'name': 'ARK Innovation ETF', 'allocation': 10},
        ]
    }
    
    @staticmethod
    def _get_category(ticker: str) -> str:
        """Get the category for a given ticker."""
        return PortfolioTools.STOCK_CATEGORIES.get(ticker, 'Other')
    
    @staticmethod
    def _get_stock_data(tickers: List[str], period: str = '1y') -> Dict[str, pd.DataFrame]:
        """Get historical stock data for a list of tickers."""
        data = {}
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                data[ticker] = stock.history(period=period)
            except Exception as e:
                data[ticker] = None
        return data
    
    @staticmethod
    def _calculate_portfolio_metrics(portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate various portfolio metrics."""
        assets = portfolio_data['assets']
        
        # Get all ticker symbols
        tickers = [asset['ticker'] for asset in assets]
        
        # Retrieve price data
        stock_data = PortfolioTools._get_stock_data(tickers)
        
        # Calculate total portfolio value
        total_value = 0
        asset_values = []
        
        for asset in assets:
            ticker = asset['ticker']
            quantity = asset['quantity']
            
            if ticker in stock_data and stock_data[ticker] is not None and not stock_data[ticker].empty:
                price = stock_data[ticker]['Close'].iloc[-1]
                value = price * quantity
                total_value += value
                asset_values.append({
                    'ticker': ticker,
                    'quantity': quantity,
                    'price': price,
                    'value': value,
                    'category': PortfolioTools._get_category(ticker)
                })
        
        # Calculate allocation percentages
        for asset in asset_values:
            asset['allocation'] = (asset['value'] / total_value) * 100 if total_value > 0 else 0
        
        # Calculate category allocations
        categories = {}
        for asset in asset_values:
            category = asset['category']
            if category not in categories:
                categories[category] = 0
            categories[category] += asset['allocation']
        
        category_allocation = [{'category': cat, 'allocation': alloc} for cat, alloc in categories.items()]
        
        # Calculate returns (1 month, 3 months, 1 year)
        returns = {}
        if all(ticker in stock_data and stock_data[ticker] is not None and not stock_data[ticker].empty for ticker in tickers):
            # Initialize portfolio values at different time points
            portfolio_hist = pd.DataFrame()
            
            for asset in assets:
                ticker = asset['ticker']
                quantity = asset['quantity']
                
                # Get adjusted close prices
                asset_hist = stock_data[ticker]['Close']
                
                # Calculate asset value over time
                asset_value = asset_hist * quantity
                
                # Add to portfolio value
                if portfolio_hist.empty:
                    portfolio_hist = asset_value.to_frame(name=ticker)
                else:
                    portfolio_hist[ticker] = asset_value
            
            # Calculate total portfolio value over time
            portfolio_hist['Total'] = portfolio_hist.sum(axis=1)
            
            # Calculate returns
            if len(portfolio_hist) > 0:
                latest_value = portfolio_hist['Total'].iloc[-1]
                
                # 1 month return
                if len(portfolio_hist) >= 30:
                    month_ago_idx = -min(30, len(portfolio_hist))
                    month_ago_value = portfolio_hist['Total'].iloc[month_ago_idx]
                    returns['1m'] = ((latest_value / month_ago_value) - 1) * 100
                
                # 3 month return
                if len(portfolio_hist) >= 90:
                    three_month_ago_idx = -min(90, len(portfolio_hist))
                    three_month_ago_value = portfolio_hist['Total'].iloc[three_month_ago_idx]
                    returns['3m'] = ((latest_value / three_month_ago_value) - 1) * 100
                
                # 1 year return
                if len(portfolio_hist) >= 252:
                    year_ago_idx = -min(252, len(portfolio_hist))
                    year_ago_value = portfolio_hist['Total'].iloc[year_ago_idx]
                    returns['1y'] = ((latest_value / year_ago_value) - 1) * 100
                    
                # Annualized volatility
                if len(portfolio_hist) > 1:
                    daily_returns = portfolio_hist['Total'].pct_change().dropna()
                    annualized_vol = daily_returns.std() * np.sqrt(252) * 100  # in percentage
                    returns['volatility'] = annualized_vol
        
        result = {
            'total_value': total_value,
            'assets': asset_values,
            'category_allocation': category_allocation,
            'returns': returns
        }
        
        return result
    
    @staticmethod
    def create_portfolio_visualization_tool() -> Tool:
        """Create a tool for visualizing portfolio allocation."""
        
        def visualize_portfolio(portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
            """Visualize portfolio allocation using Plotly."""
            metrics = PortfolioTools._calculate_portfolio_metrics(portfolio_data)
            
            # Create pie chart for asset allocation
            asset_fig = px.pie(
                metrics['assets'], 
                values='allocation', 
                names='ticker',
                title='Portfolio Asset Allocation',
                hover_data=['value', 'category']
            )
            asset_fig.update_traces(textposition='inside', textinfo='percent+label')
            
            # Create pie chart for category allocation
            category_fig = px.pie(
                metrics['category_allocation'], 
                values='allocation', 
                names='category',
                title='Portfolio Category Allocation'
            )
            category_fig.update_traces(textposition='inside', textinfo='percent+label')
            
            # Create bar chart for returns
            if metrics['returns']:
                returns_data = [{'period': period, 'return': value} for period, value in metrics['returns'].items()]
                returns_fig = px.bar(
                    returns_data,
                    x='period',
                    y='return',
                    title='Portfolio Returns',
                    labels={'return': 'Return (%)', 'period': 'Time Period'}
                )
            else:
                returns_fig = go.Figure()
                returns_fig.update_layout(title='Portfolio Returns (Insufficient Data)')
            
            return {
                'metrics': metrics,
                'asset_allocation_chart': asset_fig.to_json(),
                'category_allocation_chart': category_fig.to_json(),
                'returns_chart': returns_fig.to_json()
            }
        
        return Tool(
            name="PortfolioVisualization",
            func=visualize_portfolio,
            description="Visualizes portfolio allocation and returns using Plotly charts."
        )
    
    @staticmethod
    def create_risk_assessment_tool() -> Tool:
        """Create a tool for assessing portfolio risk."""
        
        def assess_risk(portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
            """Assess portfolio risk and provide a risk profile."""
            metrics = PortfolioTools._calculate_portfolio_metrics(portfolio_data)
            
            # Calculate risk factors
            risk_factors = {
                'diversification': 0,
                'volatility': 0,
                'category_concentration': 0
            }
            
            # 1. Diversification - based on number of assets
            num_assets = len(metrics['assets'])
            if num_assets < 5:
                risk_factors['diversification'] = 3  # High risk
            elif num_assets < 10:
                risk_factors['diversification'] = 2  # Medium risk
            else:
                risk_factors['diversification'] = 1  # Low risk
            
            # 2. Volatility - if available
            if 'volatility' in metrics['returns']:
                volatility = metrics['returns']['volatility']
                if volatility > 25:
                    risk_factors['volatility'] = 3  # High risk
                elif volatility > 15:
                    risk_factors['volatility'] = 2  # Medium risk
                else:
                    risk_factors['volatility'] = 1  # Low risk
            else:
                # Estimate risk based on category allocation
                category_risk_weights = {
                    'Technology': 3,
                    'Healthcare': 2,
                    'Finance': 2.5,
                    'Consumer': 1.5,
                    'Energy': 3,
                    'Telecommunications': 1.5,
                    'Real Estate': 2,
                    'Industrial': 2,
                    'ETF': 1,
                    'Other': 2.5
                }
                
                weighted_risk = 0
                total_allocation = 0
                
                for cat_alloc in metrics['category_allocation']:
                    category = cat_alloc['category']
                    allocation = cat_alloc['allocation']
                    risk_weight = category_risk_weights.get(category, 2.5)
                    
                    weighted_risk += allocation * risk_weight
                    total_allocation += allocation
                
                avg_risk = weighted_risk / total_allocation if total_allocation > 0 else 2
                
                if avg_risk > 2.5:
                    risk_factors['volatility'] = 3  # High risk
                elif avg_risk > 1.8:
                    risk_factors['volatility'] = 2  # Medium risk
                else:
                    risk_factors['volatility'] = 1  # Low risk
            
            # 3. Category concentration
            category_allocations = [cat['allocation'] for cat in metrics['category_allocation']]
            max_allocation = max(category_allocations) if category_allocations else 100
            
            if max_allocation > 60:
                risk_factors['category_concentration'] = 3  # High risk
            elif max_allocation > 40:
                risk_factors['category_concentration'] = 2  # Medium risk
            else:
                risk_factors['category_concentration'] = 1  # Low risk
            
            # Calculate average risk score
            avg_risk_score = sum(risk_factors.values()) / len(risk_factors)
            
            # Determine overall risk level
            if avg_risk_score > 2.3:
                risk_level = 'High Risk'
                profile = 'high_risk'
            elif avg_risk_score > 1.7:
                risk_level = 'Moderate Risk'
                profile = 'moderate_risk'
            else:
                risk_level = 'Low Risk'
                profile = 'low_risk'
            
            # Provide recommendations based on risk profile
            recommendations = PortfolioTools.DEFAULT_RECOMMENDATIONS[profile]
            
            return {
                'risk_assessment': {
                    'risk_level': risk_level,
                    'risk_score': avg_risk_score,
                    'risk_factors': risk_factors,
                },
                'profile': profile,
                'recommendations': recommendations,
                'metrics': metrics
            }
        
        return Tool(
            name="RiskAssessment",
            func=assess_risk,
            description="Assesses portfolio risk and provides a risk profile and recommendations."
        )
    
    @staticmethod
    def create_category_assessment_tool() -> Tool:
        """Create a tool for assessing portfolio categories."""
        
        def assess_categories(portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
            """Assess portfolio stock categories and their allocations."""
            metrics = PortfolioTools._calculate_portfolio_metrics(portfolio_data)
            
            # Analyze category allocations
            categories = {cat['category']: cat['allocation'] for cat in metrics['category_allocation']}
            
            # Identify dominant categories (>20%)
            dominant_categories = [cat for cat, alloc in categories.items() if alloc > 20]
            
            # Identify missing major categories
            all_major_categories = ['Technology', 'Healthcare', 'Finance', 'Consumer', 'Energy', 'Industrial', 'ETF']
            missing_categories = [cat for cat in all_major_categories if cat not in categories or categories[cat] < 5]
            
            # Create category diversification score
            num_categories = len(categories)
            if num_categories >= 6:
                diversification_level = 'Highly Diversified'
            elif num_categories >= 4:
                diversification_level = 'Well Diversified'
            elif num_categories >= 2:
                diversification_level = 'Moderately Diversified'
            else:
                diversification_level = 'Poorly Diversified'
            
            # Calculate Herfindahl-Hirschman Index (HHI) for concentration
            hhi = sum([(alloc/100)**2 for alloc in categories.values()]) * 10000
            
            if hhi > 3000:
                concentration_level = 'Highly Concentrated'
            elif hhi > 1800:
                concentration_level = 'Moderately Concentrated'
            else:
                concentration_level = 'Not Concentrated'
            
            return {
                'category_metrics': metrics['category_allocation'],
                'dominant_categories': dominant_categories,
                'missing_categories': missing_categories,
                'diversification_level': diversification_level,
                'concentration_level': concentration_level,
                'hhi': hhi,
                'num_categories': num_categories
            }
        
        return Tool(
            name="CategoryAssessment",
            func=assess_categories,
            description="Assesses portfolio stock categories and their allocations."
        )
    
    @staticmethod
    def create_investment_advisor_tool(llm) -> Tool:
        """Create a tool for investment advice based on goals."""
        
        def provide_investment_advice(portfolio_data: Dict[str, Any], goal: str) -> Dict[str, Any]:
            """Provides investment advice based on portfolio and financial goals."""
            # First, get risk assessment
            risk_tool = PortfolioTools.create_risk_assessment_tool()
            risk_assessment = risk_tool.func(portfolio_data)
            
            # Map goals to target profiles
            goal_mappings = {
                'retirement': {
                    'High Risk': 'moderate_risk',
                    'Moderate Risk': 'moderate_risk',
                    'Low Risk': 'low_risk'
                },
                'home_purchase': {
                    'High Risk': 'low_risk',
                    'Moderate Risk': 'low_risk',
                    'Low Risk': 'low_risk'
                },
                'aggressive_growth': {
                    'High Risk': 'high_risk',
                    'Moderate Risk': 'high_risk',
                    'Low Risk': 'moderate_risk'
                }
            }
            
            # Determine which goal is closest to the provided goal
            goal_keywords = {
                'retirement': ['retirement', 'retire', 'pension'],
                'home_purchase': ['home', 'house', 'property', 'real estate', 'mortgage'],
                'aggressive_growth': ['aggressive', 'growth', 'risky', 'high return']
            }
            
            matched_goal = 'retirement'  # Default
            for g, keywords in goal_keywords.items():
                if any(keyword in goal.lower() for keyword in keywords):
                    matched_goal = g
                    break
            
            current_risk = risk_assessment['risk_assessment']['risk_level']
            target_profile = goal_mappings.get(matched_goal, {}).get(current_risk, 'moderate_risk')
            
            # Generate advice using LLM
            current_profile = risk_assessment['profile']
            metrics = risk_assessment['metrics']
            
            prompt = f"""
            As a financial advisor, provide personalized investment advice based on the following information:

            Current Portfolio:
            - Total Value: ${metrics['total_value']:.2f}
            - Current Risk Profile: {current_risk}
            - Major Categories: {', '.join([f"{cat['category']} ({cat['allocation']:.1f}%)" for cat in metrics['category_allocation']])}
            - Number of Assets: {len(metrics['assets'])}

            User's Goal: {goal}
            Target Risk Profile: {target_profile.replace('_', ' ').title()}

            Provide the following advice:
            1. Overall assessment of the portfolio alignment with the goal
            2. 3-4 specific recommendations for portfolio adjustments (be specific about which types of assets to add or reduce)
            3. Timeline considerations
            4. A recommended allocation model (stocks/bonds/cash percentages)

            Format your response as a structured JSON with the following keys:
            - assessment (string)
            - recommendations (array of strings)
            - timeline (string)
            - allocation_model (object with keys for stocks, bonds, cash, and other percentages)
            - additional_notes (string)
            """
            
            response = llm.invoke(prompt)
            
            try:
                import json
                advice = json.loads(response.content)
            except:
                # Fallback if LLM doesn't return proper JSON
                advice = {
                    "assessment": "Unable to analyze portfolio properly.",
                    "recommendations": [
                        "Consider consulting with a professional financial advisor.",
                        "Review your portfolio allocation between stocks and bonds.",
                        "Ensure your investments align with your time horizon."
                    ],
                    "timeline": "Your timeline will depend on your specific goals and risk tolerance.",
                    "allocation_model": {
                        "stocks": 60,
                        "bonds": 30,
                        "cash": 10,
                        "other": 0
                    },
                    "additional_notes": "This is general advice. Please consult a professional for personalized recommendations."
                }
            
            return {
                "goal": goal,
                "matched_goal_category": matched_goal,
                "current_risk_profile": current_risk,
                "target_risk_profile": target_profile.replace('_', ' ').title(),
                "advice": advice,
                "default_recommendations": PortfolioTools.DEFAULT_RECOMMENDATIONS[target_profile]
            }
        
        return Tool(
            name="InvestmentAdvisor",
            func=provide_investment_advice,
            description="Provides investment advice based on portfolio and financial goals."
        ) 