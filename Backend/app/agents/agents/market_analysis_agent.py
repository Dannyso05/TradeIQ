from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.runnables import Runnable
from typing import Dict, Any, List
from app.agents.base_agent import BaseAgent
from app.agents.tools.research_tools import ResearchTools

class MarketAnalysisAgent(BaseAgent):
    """Agent for analyzing market sentiment and researching online articles about stocks."""
    
    def __init__(self, llm: BaseLanguageModel):
        """Initialize the Market Analysis Agent."""
        super().__init__(llm)
        
        # Create tools
        self.tools = [
            ResearchTools.create_google_search_tool(),
            ResearchTools.create_web_scraping_tool(),
            ResearchTools.create_sentiment_analysis_tool(llm)
        ]
        
        # Create agent
        self.agent_executor = AgentExecutor.from_agent_and_tools(
            agent=create_openai_tools_agent(self.llm, self.tools, self.prompt),
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True
        )
    
    def _create_prompt(self) -> ChatPromptTemplate:
        """Create the prompt template for the agent."""
        prompt = ChatPromptTemplate.from_template("""
        You are an expert market analyst tasked with researching market sentiment and gathering information 
        about stocks or stock categories from online sources.
        
        Your responsibilities include:
        1. Researching public sentiment towards individual stocks or stock categories
        2. Finding and analyzing relevant news articles and reports
        3. Summarizing market trends and investor sentiment
        4. Identifying key factors affecting stock performance
        
        First, determine what stocks or categories you need to research based on the input.
        Then use the tools available to gather information, analyze sentiment, and compile a comprehensive report.
        
        {input}
        """)
        
        return prompt
    
    def _create_chain(self) -> Runnable:
        """Create the chain for the agent."""
        return self.agent_executor
    
    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Run the agent with the given inputs."""
        # Ensure we have either a stock ticker, list of tickers, or category to research
        if not any(key in inputs for key in ['ticker', 'tickers', 'category', 'categories']):
            return {"error": "At least one of ticker, tickers, category, or categories is required"}
        
        # Process the input
        result = self.chain.invoke(inputs)
        
        return result 