from langchain.tools import Tool
from langchain.utilities import GoogleSearchAPIWrapper
import requests
from bs4 import BeautifulSoup
import os
from typing import List, Dict, Any
from app.config import get_settings

class ResearchTools:
    """Tools for online research and sentiment analysis."""
    
    @staticmethod
    def create_google_search_tool() -> Tool:
        """Creates a tool for Google search."""
        settings = get_settings()
        search = GoogleSearchAPIWrapper(
            google_api_key=settings.google_api_key,
            google_cse_id=settings.google_cse_id
        )
        
        def google_search(query: str, num_results: int = 5) -> List[Dict[str, str]]:
            """Search Google for information about stocks or market trends."""
            results = search.results(query, num_results)
            return [{"title": r["title"], "snippet": r["snippet"], "link": r["link"]} for r in results]
        
        return Tool(
            name="GoogleSearch",
            func=google_search,
            description="Useful for searching information about stocks, market trends, and investment advice online."
        )
    
    @staticmethod
    def create_web_scraping_tool() -> Tool:
        """Creates a tool for web scraping."""
        
        def scrape_webpage(url: str) -> str:
            """Scrape the content of a webpage."""
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            try:
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract text from paragraphs
                paragraphs = soup.find_all('p')
                text = ' '.join([p.get_text().strip() for p in paragraphs])
                
                # Limit text length
                return text[:5000] + ("..." if len(text) > 5000 else "")
            
            except Exception as e:
                return f"Error scraping webpage: {str(e)}"
        
        return Tool(
            name="WebScraper",
            func=scrape_webpage,
            description="Useful for scraping the content of a webpage to gather detailed information about stocks or market analysis."
        )
    
    @staticmethod
    def create_sentiment_analysis_tool(llm) -> Tool:
        """Creates a tool for sentiment analysis using an LLM."""
        
        def analyze_sentiment(text: str) -> Dict[str, Any]:
            """Analyze the sentiment of text about stocks or market trends."""
            prompt = f"""
            Analyze the sentiment in the following text related to stock market or a specific stock.
            Return your analysis as a JSON with the following keys:
            - sentiment: 'positive', 'negative', or 'neutral'
            - confidence: a number between 0 and 1
            - key_points: a list of key points from the text
            
            Text: {text}
            
            Analysis:
            """
            
            response = llm.invoke(prompt)
            
            # The response should be a JSON string
            try:
                import json
                return json.loads(response.content)
            except:
                # Fallback if LLM doesn't return proper JSON
                return {
                    "sentiment": "neutral",
                    "confidence": 0.5,
                    "key_points": ["Unable to parse sentiment analysis results"]
                }
        
        return Tool(
            name="SentimentAnalyzer",
            func=analyze_sentiment,
            description="Useful for analyzing the sentiment of text about stocks or market trends."
        ) 