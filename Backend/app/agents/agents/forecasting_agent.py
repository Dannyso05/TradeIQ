from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.runnables import Runnable
from typing import Dict, Any, List
from app.agents.base_agent import BaseAgent
from app.agents.tools.forecasting_tools import ForecastingTools

class ForecastingAgent(BaseAgent):
    """Agent for forecasting stock prices using ML models."""
    
    def __init__(self, llm: BaseLanguageModel):
        """Initialize the Forecasting Agent."""
        super().__init__(llm)
        
        # Create tools
        self.tools = [
            ForecastingTools.create_stock_forecast_tool(),
            ForecastingTools.create_comparative_forecast_tool()
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
        You are an expert financial forecasting analyst specialized in using machine learning models
        to predict stock price movements.
        
        Your responsibilities include:
        1. Forecasting stock prices using XGBoost models
        2. Comparing stock forecasts with market indices (S&P 500, NASDAQ)
        3. Analyzing forecast results and providing insights
        4. Explaining forecast uncertainties and limitations
        
        Carefully analyze the input to determine what forecasting task is needed, and use the appropriate
        tools to generate forecasts and visualizations.
        
        {input}
        """)
        
        return prompt
    
    def _create_chain(self) -> Runnable:
        """Create the chain for the agent."""
        return self.agent_executor
    
    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Run the agent with the given inputs."""
        # Ensure we have a ticker to forecast
        if 'ticker' not in inputs:
            return {"error": "Stock ticker is required"}
        
        # Set default forecast days if not provided
        if 'forecast_days' not in inputs:
            inputs['forecast_days'] = 30
        
        # Process the input
        result = self.chain.invoke(inputs)
        
        return result 