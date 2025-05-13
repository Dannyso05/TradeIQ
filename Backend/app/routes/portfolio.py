from fastapi import APIRouter, HTTPException, status, Depends, File, UploadFile
from typing import List, Optional
from Backend.app.Models.models import (
    Portfolio, Asset, PortfolioAnalysisResponse, SamplePortfolioResponse,
    PortfolioUploadResponse, StoredPortfolioResponse, ClearPortfolioResponse
)
from app.agents.agent_graph import run_financial_analysis
from langchain_openai import ChatOpenAI
from app.config import get_settings, Settings, portfolio_store
from fastapi.responses import JSONResponse
import pytesseract
import cv2
import numpy as np
import io
from PIL import Image
import re

router = APIRouter()

def preprocess_image(image_bytes):
    # Convert uploaded bytes to OpenCV image
    image = np.array(Image.open(io.BytesIO(image_bytes)))

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Noise removal
    denoised = cv2.fastNlMeansDenoising(gray, h=30)

    # Adaptive thresholding for better contrast
    binary = cv2.adaptiveThreshold(denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    # Deskewing (straighten tilted text)
    coords = cv2.findNonZero(binary)
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = binary.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    deskewed = cv2.warpAffine(binary, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    return deskewed

def process_extracted_text(text: str) -> dict:
    """Process extracted text into portfolio data."""
    stock_data = {}
    # Pattern to match stock symbols (assumed to be 1-5 uppercase letters) and quantities
    pattern = r'([A-Z]{1,5})[:\s]+(\d+(?:\.\d+)?)'
    
    matches = re.findall(pattern, text)
    for match in matches:
        symbol, quantity = match
        try:
            stock_data[symbol.strip()] = float(quantity.strip())
        except ValueError:
            continue  # Skip if quantity can't be converted to float
            
    return stock_data

@router.post("/upload-portfolio", response_model=PortfolioUploadResponse, summary="Upload portfolio image")
async def upload_portfolio(file: UploadFile = File(...)):
    """
    Upload an image of a portfolio statement and extract stock data.
    
    This endpoint processes an uploaded image using OCR to extract stock ticker symbols 
    and quantities. The extracted data is stored for use in portfolio analysis.
    """
    try:
        # Read the uploaded image file
        image_bytes = await file.read()

        # Preprocess the image with OpenCV
        preprocessed = preprocess_image(image_bytes)

        # Use OCR to extract text
        extracted_text = pytesseract.image_to_string(preprocessed, config="--psm 6")
        print(f"Extracted text: {extracted_text}")

        # Process the extracted text to fetch stock symbols and quantities
        stock_data = process_extracted_text(extracted_text)
        
        # Convert to assets format and store in portfolio_store
        assets = [{"ticker": ticker, "quantity": quantity} for ticker, quantity in stock_data.items()]
        portfolio_store.store_portfolio(assets)
        portfolio_store.store_raw_data({"extracted_text": extracted_text, "processed_data": stock_data})
        
        return {
            "message": "Portfolio successfully extracted and stored", 
            "extracted_data": stock_data,
            "assets": assets
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process portfolio image: {str(e)}"
        )

def get_llm(settings: Settings = Depends(get_settings)):
    """Get the language model instance."""
    try:
        return ChatOpenAI(
            model=settings.llm_model,
            temperature=settings.llm_temperature,
            openai_api_key=settings.openai_api_key
        )
    except Exception as e:
        print(f"Error initializing LLM: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize language model: {str(e)}"
        )

@router.post("/analyze", response_model=PortfolioAnalysisResponse, summary="Analyze portfolio")
async def analyze_portfolio(
    portfolio: Optional[Portfolio] = None,
    goals: Optional[List[str]] = None,
    settings: Settings = Depends(get_settings)
):
    """
    Analyze a portfolio using the multi-agent system.
    
    This endpoint performs a comprehensive analysis of the provided portfolio, including:
    - Risk assessment and categorization
    - Market sentiment and news analysis
    - Price forecasting with XGBoost models
    - Custom investment advice based on financial goals
    
    If no portfolio is provided, it will use the last uploaded portfolio from the image upload endpoint.
    
    Args:
        portfolio: The portfolio to analyze (optional if you've already uploaded via image)
        goals: Optional list of investment goals (default: retirement, home purchase, aggressive growth)
        
    Returns:
        PortfolioAnalysisResponse: A comprehensive financial report and detailed analysis
    """
    try:
        # Get LLM instance
        llm = get_llm(settings)
        
        # If no portfolio is provided, use the stored portfolio
        if portfolio is None:
            stored_assets = portfolio_store.get_portfolio()
            if not stored_assets:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No portfolio provided and no uploaded portfolio found. Please upload a portfolio first."
                )
            
            # Format portfolio data for agents
            portfolio_data = {"assets": stored_assets}
        else:
            # Format provided portfolio data for agents
            portfolio_data = {
                "assets": [
                    {"ticker": asset.ticker, "quantity": asset.quantity}
                    for asset in portfolio.assets
                ]
            }
        
        # Set default goals if not provided
        if not goals:
            goals = ['retirement', 'home_purchase', 'aggressive_growth']
        
        # Run the analysis
        result = run_financial_analysis(llm, portfolio_data, goals)
        
        return {
            "report": result.get('report', ''),
            "error": result.get('error', ''),
            "details": result.get('details', {})
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Portfolio analysis failed: {str(e)}"
        )

@router.get("/stored-portfolio", response_model=StoredPortfolioResponse, summary="Get stored portfolio")
async def get_stored_portfolio():
    """
    Retrieve the portfolio data that was extracted from the last uploaded image.
    
    Returns:
        The stored portfolio data and raw extraction information
    """
    assets = portfolio_store.get_portfolio()
    raw_data = portfolio_store.get_raw_data()
    
    if not assets:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No portfolio data found. Please upload a portfolio image first."
        )
    
    return {
        "assets": assets,
        "raw_data": raw_data
    }

@router.get("/sample", response_model=SamplePortfolioResponse, summary="Get sample portfolio")
async def get_sample_portfolio():
    """
    Get a sample portfolio for testing.
    
    Returns a pre-configured portfolio with a diversified set of assets 
    that can be used to test the analysis functionality.
    """
    return {
        "assets": [
            {"ticker": "AAPL", "quantity": 10},
            {"ticker": "MSFT", "quantity": 15},
            {"ticker": "GOOGL", "quantity": 5},
            {"ticker": "AMZN", "quantity": 8},
            {"ticker": "JNJ", "quantity": 12},
            {"ticker": "JPM", "quantity": 20},
            {"ticker": "VTI", "quantity": 30}
        ]
    }

@router.delete("/clear-portfolio", response_model=ClearPortfolioResponse, summary="Clear stored portfolio")
async def clear_portfolio():
    """
    Clear the stored portfolio data.
    
    This is useful when you want to start fresh with a new portfolio upload.
    """
    portfolio_store.clear()
    return {"message": "Portfolio data cleared successfully"}

