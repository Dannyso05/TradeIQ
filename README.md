# TradeIQ Multi-Agent Financial Analysis System

A sophisticated multi-agent system for comprehensive financial portfolio analysis using LangChain and LangGraph.

## Features

- **OCR Portfolio Import**: Upload images of portfolio statements to automatically extract stocks and quantities
- **Risk Assessment**: Evaluates portfolio diversification, volatility, and concentration
- **Category Analysis**: Identifies dominant sectors and diversification opportunities
- **Market Sentiment Analysis**: Researches current market trends and sentiment
- **ML Forecasting**: Uses XGBoost for stock price prediction
- **Goal-Based Advice**: Provides tailored recommendations for retirement, home purchase, or aggressive growth

## System Architecture

The system consists of four specialized agents coordinated through LangGraph:

1. **Finance Advisor Agent**: Assesses portfolio risk, analyzes stock categories, and provides investment recommendations.

2. **Market Analysis Agent**: Researches market sentiment and gathers information from online sources.

3. **Forecasting Agent**: Uses XGBoost to predict stock prices and compare forecasts with market indices.

4. **Supervisor Agent**: Coordinates all other agents to generate a comprehensive financial report.

## Getting Started

### Prerequisites

- Python 3.8+
- OpenAI API key
- Optional: Google API key and Custom Search Engine ID (for web search)
- Optional: Tesseract OCR (for portfolio image upload feature)

## API Endpoints

### Portfolio Analysis

- `POST /portfolio/analyze`: Analyze a portfolio and generate a comprehensive report
  - Accepts a JSON portfolio object or uses previously uploaded portfolio
  - Returns a detailed financial analysis and recommendations

### Portfolio Upload

- `POST /portfolio/upload-portfolio`: Upload an image of a portfolio statement
  - Accepts an image file and extracts stock data using OCR
  - Stores the extracted portfolio for later analysis

### Portfolio Management

- `GET /portfolio/stored-portfolio`: Retrieve the currently stored portfolio
- `DELETE /portfolio/clear-portfolio`: Clear the stored portfolio data
- `GET /portfolio/sample`: Get a sample portfolio for testing


## Architecture Diagram

```
┌──────────────────┐
│   Supervisor     │
│      Agent       │
└────────┬─────────┘
         │
         │ coordinates
         ▼
┌─────────────────────────────────────────────┐
│                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  │  Finance    │  │   Market    │  │ Forecasting │
│  │   Advisor   │  │  Analysis   │  │    Agent    │
│  │    Agent    │  │    Agent    │  │             │
│  └─────────────┘  └─────────────┘  └─────────────┘
│                                             │
└─────────────────────────────────────────────┘
```
