import yfinance as yf
import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error
from datetime import datetime, timedelta
import plotly.graph_objects as go
from typing import Dict, Any, List, Tuple
from langchain.tools import Tool

class ForecastingTools:
    """Tools for forecasting stock prices using ML models."""
    
    @staticmethod
    def _prepare_stock_data(ticker: str, period: str = "2y") -> pd.DataFrame:
        """
        Prepare stock data for forecasting.
        
        Args:
            ticker (str): Stock ticker symbol
            period (str): Period to fetch data for (default: "2y")
            
        Returns:
            pd.DataFrame: Processed dataframe with features
        """
        # Fetch data
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        
        if df.empty:
            raise ValueError(f"No data found for ticker {ticker}")
        
        # Create features
        df['Return'] = df['Close'].pct_change()
        df['MA5'] = df['Close'].rolling(window=5).mean()
        df['MA20'] = df['Close'].rolling(window=20).mean()
        df['MA50'] = df['Close'].rolling(window=50).mean()
        df['Volatility'] = df['Return'].rolling(window=20).std()
        df['RSI'] = ForecastingTools._calculate_rsi(df['Close'])
        df['Target'] = df['Close'].shift(-1)  # Next day's close price
        
        # Drop NaN values
        df = df.dropna()
        
        return df
    
    @staticmethod
    def _calculate_rsi(prices, window=14):
        """Calculate RSI technical indicator."""
        delta = prices.diff()
        gain = delta.where(delta > 0, 0).rolling(window=window).mean()
        loss = -delta.where(delta < 0, 0).rolling(window=window).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def _train_and_forecast(df: pd.DataFrame, forecast_days: int = 30) -> Tuple[pd.DataFrame, Dict]:
        """
        Train XGBoost model and make forecast.
        
        Args:
            df (pd.DataFrame): Prepared dataframe
            forecast_days (int): Number of days to forecast
            
        Returns:
            Tuple[pd.DataFrame, Dict]: Forecast dataframe and metrics
        """
        # Select features
        features = ['Return', 'MA5', 'MA20', 'MA50', 'Volatility', 'RSI', 'Volume']
        features = [f for f in features if f in df.columns]  # Filter in case some features are missing
        
        # Split data
        train_size = int(len(df) * 0.8)
        train_data = df.iloc[:train_size]
        test_data = df.iloc[train_size:]
        
        # Train model
        model = XGBRegressor(
            n_estimators=100,
            learning_rate=0.05,
            max_depth=5,
            random_state=42
        )
        
        model.fit(
            train_data[features], 
            train_data['Target'],
            eval_set=[(test_data[features], test_data['Target'])],
            verbose=False
        )
        
        # Evaluate
        predictions = model.predict(test_data[features])
        mae = mean_absolute_error(test_data['Target'], predictions)
        
        # Prepare for future prediction
        last_row = df.iloc[-1:].copy()
        forecast_dates = [df.index[-1] + timedelta(days=i+1) for i in range(forecast_days)]
        forecast_df = pd.DataFrame(index=forecast_dates, columns=['Close'])
        
        # Make future predictions
        for i in range(forecast_days):
            # Use last known features
            future_features = last_row[features].values
            # Predict next close price
            next_close = model.predict(future_features)[0]
            
            # Store prediction
            forecast_df.iloc[i]['Close'] = next_close
            
            # Update last row for next prediction
            last_row['Close'] = next_close
            last_row['Return'] = (next_close / last_row['Close'].values[0]) - 1 if i > 0 else last_row['Return']
            last_row['MA5'] = (df['Close'].iloc[-4:].sum() + next_close) / 5 if i == 0 else \
                              (forecast_df['Close'].iloc[max(0, i-4):i].sum() + next_close) / min(i+1, 5)
            last_row['MA20'] = (df['Close'].iloc[-19:].sum() + next_close) / 20 if i == 0 else \
                               (df['Close'].iloc[-(19-i):].sum() + forecast_df['Close'].iloc[:i].sum() + next_close) / 20
            # Simplify volatility and RSI calculation for forecasting
            last_row['Volatility'] = df['Volatility'].iloc[-1]
            last_row['RSI'] = df['RSI'].iloc[-1]
            last_row['Volume'] = df['Volume'].mean() if 'Volume' in df.columns else 0
        
        metrics = {
            "mae": mae,
            "last_actual_close": df['Close'].iloc[-1],
            "forecast_end_price": forecast_df['Close'].iloc[-1],
            "percent_change": ((forecast_df['Close'].iloc[-1] / df['Close'].iloc[-1]) - 1) * 100
        }
        
        return forecast_df, metrics
    
    @staticmethod
    def _create_forecast_plot(ticker: str, historical_df: pd.DataFrame, forecast_df: pd.DataFrame) -> Dict:
        """
        Create a Plotly plot of historical prices and forecast.
        
        Args:
            ticker (str): Stock ticker symbol
            historical_df (pd.DataFrame): Historical price data
            forecast_df (pd.DataFrame): Forecast data
            
        Returns:
            Dict: Plotly figure as JSON
        """
        # Use only the last 90 days of historical data for better visualization
        historical_df = historical_df.iloc[-90:]
        
        # Create figure
        fig = go.Figure()
        
        # Add historical prices
        fig.add_trace(go.Scatter(
            x=historical_df.index,
            y=historical_df['Close'],
            mode='lines',
            name='Historical',
            line=dict(color='blue')
        ))
        
        # Add forecast
        fig.add_trace(go.Scatter(
            x=forecast_df.index,
            y=forecast_df['Close'],
            mode='lines',
            name='Forecast',
            line=dict(color='red', dash='dash')
        ))
        
        # Add confidence interval (simplified)
        std_dev = historical_df['Close'].std() * 0.5
        fig.add_trace(go.Scatter(
            x=forecast_df.index,
            y=forecast_df['Close'] + std_dev,
            mode='lines',
            line=dict(width=0),
            showlegend=False,
            hoverinfo='none'
        ))
        
        fig.add_trace(go.Scatter(
            x=forecast_df.index,
            y=forecast_df['Close'] - std_dev,
            mode='lines',
            line=dict(width=0),
            fillcolor='rgba(255, 0, 0, 0.1)',
            fill='tonexty',
            showlegend=False,
            hoverinfo='none'
        ))
        
        # Update layout
        fig.update_layout(
            title=f'{ticker} Stock Price Forecast (XGBoost)',
            xaxis_title='Date',
            yaxis_title='Price',
            hovermode='x unified',
            legend=dict(y=0.99, x=0.01),
            template='plotly_white'
        )
        
        return fig.to_json()
    
    @staticmethod
    def create_stock_forecast_tool() -> Tool:
        """Create a tool for forecasting stock prices."""
        
        def forecast_stock(ticker: str, forecast_days: int = 30) -> Dict[str, Any]:
            """Forecast stock prices using XGBoost."""
            try:
                # Prepare data
                df = ForecastingTools._prepare_stock_data(ticker)
                
                # Train model and get forecast
                forecast_df, metrics = ForecastingTools._train_and_forecast(df, forecast_days)
                
                # Create plot
                plot_json = ForecastingTools._create_forecast_plot(ticker, df, forecast_df)
                
                return {
                    "ticker": ticker,
                    "forecast_days": forecast_days,
                    "metrics": metrics,
                    "plot": plot_json,
                    "forecast_data": forecast_df.reset_index().to_dict(orient='records')
                }
            
            except Exception as e:
                return {"error": str(e)}
        
        return Tool(
            name="StockForecast",
            func=forecast_stock,
            description="Forecasts stock prices using XGBoost. Provide a ticker symbol and optional number of days to forecast."
        )
    
    @staticmethod
    def create_comparative_forecast_tool() -> Tool:
        """Create a tool for comparing stock forecasts with market indices."""
        
        def compare_forecasts(ticker: str, forecast_days: int = 30) -> Dict[str, Any]:
            """Compare stock forecast with SPY and NASDAQ-100 (QQQ) indices."""
            try:
                indices = ['SPY', 'QQQ']  # SPY for S&P 500, QQQ for NASDAQ-100
                results = {}
                
                # Forecast user's stock
                stock_df = ForecastingTools._prepare_stock_data(ticker)
                stock_forecast, stock_metrics = ForecastingTools._train_and_forecast(stock_df, forecast_days)
                results[ticker] = {
                    "forecast": stock_forecast,
                    "metrics": stock_metrics
                }
                
                # Forecast indices
                for index in indices:
                    index_df = ForecastingTools._prepare_stock_data(index)
                    index_forecast, index_metrics = ForecastingTools._train_and_forecast(index_df, forecast_days)
                    results[index] = {
                        "forecast": index_forecast,
                        "metrics": index_metrics
                    }
                
                # Create comparative plot
                fig = go.Figure()
                
                # Normalize to percentage change from start
                for symbol, data in results.items():
                    start_price = data["forecast"]["Close"].iloc[0]
                    normalized_forecast = (data["forecast"]["Close"] / start_price - 1) * 100
                    
                    fig.add_trace(go.Scatter(
                        x=data["forecast"].index,
                        y=normalized_forecast,
                        mode='lines',
                        name=f'{symbol} (forecast)',
                        line=dict(dash='dash' if symbol != ticker else None)
                    ))
                
                # Update layout
                fig.update_layout(
                    title=f'Comparative Forecast: {ticker} vs Market Indices (XGBoost)',
                    xaxis_title='Date',
                    yaxis_title='Percentage Change (%)',
                    hovermode='x unified',
                    legend=dict(y=0.99, x=0.01),
                    template='plotly_white'
                )
                
                # Calculate correlation with indices
                correlations = {}
                for index in indices:
                    # Calculate correlation of percentage changes
                    stock_pct = stock_forecast['Close'].pct_change().iloc[1:]
                    index_pct = results[index]["forecast"]['Close'].pct_change().iloc[1:]
                    correlations[index] = stock_pct.corr(index_pct)
                
                return {
                    "ticker": ticker,
                    "forecast_days": forecast_days,
                    "stock_metrics": stock_metrics,
                    "index_metrics": {idx: results[idx]["metrics"] for idx in indices},
                    "correlations": correlations,
                    "plot": fig.to_json()
                }
            
            except Exception as e:
                return {"error": str(e)}
        
        return Tool(
            name="ComparativeStockForecast",
            func=compare_forecasts,
            description="Compares a stock's forecast with market indices (S&P 500 and NASDAQ-100) using XGBoost."
        ) 