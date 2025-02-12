from pydantic import BaseModel, JsonValue
from typing import List, Optional

class StockPrice(BaseModel):
    symbol: str
    current_price: float

class Asset(BaseModel):
    name: str
    ticker: str
    total_price: float

# class Asset(BaseModel):
#     name: str
#     amount: float
#     price_per_unit: float


class Portfolio(BaseModel):
    assets: List[Asset]

class RiskAssessment(BaseModel):
    risk_level: str
    diversification: str
    asset_concentration: float

class DiversificationSuggestion(BaseModel):
    suggested_asset: str
    suggested_percentage: float


class PlotlyJSONSchema(BaseModel):
    data: JsonValue
    layout: JsonValue


# from typing import List

# class StockPrice:
#     def __init__(self, symbol: str, current_price: float):
#         self.symbol = symbol
#         self.current_price = current_price

# class Asset:
#     def __init__(self, name: str, amount: float, price_per_unit: float):
#         self.name = name
#         self.amount = amount
#         self.price_per_unit = price_per_unit

# class Portfolio:
#     def __init__(self, assets: List[Asset]):
#         self.assets = assets

# class RiskAssessment:
#     def __init__(self, risk_level: str, diversification: str, asset_concentration: float):
#         self.risk_level = risk_level
#         self.diversification = diversification
#         self.asset_concentration = asset_concentration

# class DiversificationSuggestion:
#     def __init__(self, suggested_asset: str, suggested_percentage: float):
#         self.suggested_asset = suggested_asset
#         self.suggested_percentage = suggested_percentage