import requests
from models import StockPrice

def process_extracted_text(text: str) -> dict:
    stock_data = {}
    lines = text.splitlines()
    for line in lines:
        if ":" in line:
            symbol, price = line.split(":")
            stock_data[symbol.strip()] = price.strip()
    return stock_data