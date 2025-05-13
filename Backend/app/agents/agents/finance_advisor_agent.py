from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.runnables import Runnable
from typing import Dict, Any, List
from app.agents.base_agent import BaseAgent
from app.agents.tools.portfolio_tools import PortfolioTools
from app.agents.tools.research_tools import ResearchTools

class FinanceAdvisorAgent(BaseAgent):
    """Agent for financial portfolio risk assessment and recommendations."""
    
    def __init__(self, llm: BaseLanguageModel):
        """Initialize the Financial Advisor Agent."""
        super().__init__(llm)
        
        # Create tools
        self.tools = [
            PortfolioTools.create_risk_assessment_tool(),
            PortfolioTools.create_category_assessment_tool(),
            PortfolioTools.create_investment_advisor_tool(llm),
            ResearchTools.create_google_search_tool()
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
        You are an expert financial advisor tasked with analyzing investment portfolios and providing personalized advice.
        
        Your responsibilities include:
        1. Assessing portfolio risk levels
        2. Analyzing stock categories and diversification
        3. Researching market trends for relevant stock categories
        4. Providing recommendations based on different investment goals
        
        Use the tools available to analyze the portfolio data and provide detailed, actionable advice.
        
        {input}
        """)
        
        return prompt
    
    def _create_chain(self) -> Runnable:
        """Create the chain for the agent."""
        return self.agent_executor
    
    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Run the agent with the given inputs."""
        # Ensure portfolio data is properly formatted
        if 'portfolio_data' not in inputs:
            return {"error": "Portfolio data is required"}
        
        # Process the input
        result = self.chain.invoke(inputs)
        
        return result 