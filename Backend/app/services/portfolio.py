from typing import List
import yfinance as yf
from models import Asset
import plotly.express as px
from utils.exceptions import StockNotFound

def load_stockinfo(assets: List[Asset]) -> List[yf.Ticker]:
    tickers = []
    for asset in assets:
        ticker_symbol = asset.ticker
        try:
            ticker = yf.Ticker(ticker_symbol)
            if ticker.history(period='1d').empty:  # Check if the stock data is valid
                raise StockNotFound(ticker_symbol)
            tickers.append(ticker)
        except StockNotFound as snf:
            print(f"Stock not found: {snf.ticker_symbol}")  # Log the custom error message
            # Optionally, you can choose to raise the exception again if you want to stop processing
            raise  # Uncomment this line if you want to stop processing on error
        
        except Exception as e:  # Catching all other exceptions
            print(f"Error fetching ticker data: {e}")  # Log the error or handle it appropriately
    return tickers

def analyze_portfolio(assets: List[Asset]) -> dict:
    try:
        tickers = load_stockinfo(assets=assets)

    
    # If no exceptions were raised, proceed with analysis
        

    except StockNotFound as snf:
        for tic in tickers:
            print(tic.history(period="1d"))
        
        print(f"Stock not found: {snf.ticker_symbol}")  # Log the custom error message
        return {
            "risk_level": "Moderate",
            "diversification": None,
            "asset_concentration": None,
        }
    except Exception as e:  # Catching all other exceptions
        print(f"An error occurred while loading stock info: {e}")
        return {
            "risk_level": "Moderate",
            "diversification": None,
            "asset_concentration": None,
        }

    return {
        "risk_level": "Moderate",
        "diversification": None,
        "asset_concentration": None
    }

def plotly_data(ticker):
    df = px.data.gapminder().query("continent == 'Oceania'")
    fig = px.line(df, x='year', y='lifeExp', color='country', markers=True)
    this_plot_data = fig.to_json(pretty=True, engine="json")
    this_plot_data = json.loads(this_plot_data)
    return PlotlyJSONSchema(data=this_plot_data["data"], layout=this_plot_data["layout"])
    # return Response(content=this_plot_data, media_type="application/json")