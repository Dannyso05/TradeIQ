from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.runnables import Runnable
from typing import Dict, Any, List
from app.agents.base_agent import BaseAgent
from app.agents.finance_advisor_agent import FinanceAdvisorAgent
from app.agents.market_analysis_agent import MarketAnalysisAgent
from app.agents.forecasting_agent import ForecastingAgent
from app.agents.tools.portfolio_tools import PortfolioTools
import json

class SupervisorAgent(BaseAgent):
    """Supervisor agent that coordinates all other agents to generate a comprehensive financial report."""
    
    def __init__(self, llm: BaseLanguageModel):
        """Initialize the Supervisor Agent."""
        # Initialize sub-agents
        self.finance_advisor_agent = FinanceAdvisorAgent(llm)
        self.market_analysis_agent = MarketAnalysisAgent(llm)
        self.forecasting_agent = ForecastingAgent(llm)
        
        # Initialize base class
        super().__init__(llm)
        
        # Create tools for portfolio visualization
        self.tools = [
            PortfolioTools.create_portfolio_visualization_tool()
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
        You are the lead financial advisor tasked with creating a comprehensive financial report for a client's portfolio.
        
        Your report must include:
        1. A detailed risk assessment of the portfolio
        2. Analysis of the categories of stocks held in the portfolio
        3. Current market sentiment and summaries of relevant articles
        4. Forecasting results for the portfolio's largest holding
        5. Personalized investment advice based on the client's goals
        
        Use the tools available to generate this report. Break down complex financial concepts into understandable terms.
        
        {input}
        """)
        
        return prompt
    
    def _create_chain(self) -> Runnable:
        """Create the chain for the agent."""
        return self.agent_executor
    
    def _find_largest_holding(self, portfolio_data: Dict[str, Any]) -> str:
        """Find the ticker with the largest holding in the portfolio."""
        # Calculate portfolio metrics to find largest holding
        visualization_tool = PortfolioTools.create_portfolio_visualization_tool()
        metrics = visualization_tool.func(portfolio_data)['metrics']
        
        # Sort assets by allocation percentage
        sorted_assets = sorted(metrics['assets'], key=lambda x: x['allocation'], reverse=True)
        
        # Return ticker of largest holding
        return sorted_assets[0]['ticker'] if sorted_assets else None
    
    def _generate_financial_report(self, portfolio_data: Dict[str, Any], goals: List[str]) -> Dict[str, Any]:
        """Generate a comprehensive financial report by coordinating sub-agents."""
        report = {}
        
        # Step 1: Risk assessment and category analysis
        finance_advisor_result = self.finance_advisor_agent.run({
            'portfolio_data': portfolio_data,
            'input': 'Analyze this portfolio to assess its risk level and categorize the stocks.'
        })
        
        report['risk_assessment'] = finance_advisor_result.get('risk_assessment', {})
        report['category_analysis'] = finance_advisor_result.get('category_analysis', {})
        
        # Step 2: Find portfolio's largest holding
        largest_ticker = self._find_largest_holding(portfolio_data)
        
        # Step 3: Market sentiment and article analysis
        # Get categories from portfolio for market research
        categories = []
        if 'category_analysis' in report and 'category_metrics' in report['category_analysis']:
            categories = [cat['category'] for cat in report['category_analysis']['category_metrics']]
        
        market_analysis_result = self.market_analysis_agent.run({
            'ticker': largest_ticker,
            'categories': categories,
            'input': f'Research market sentiment and relevant articles for {largest_ticker} and these categories: {", ".join(categories)}'
        })
        
        report['market_analysis'] = market_analysis_result
        
        # Step 4: Forecasting for largest holding
        forecasting_result = self.forecasting_agent.run({
            'ticker': largest_ticker,
            'forecast_days': 30,
            'input': f'Forecast {largest_ticker} price for the next month using XGBoost and compare with market indices.'
        })
        
        report['forecasting'] = forecasting_result
        
        # Step 5: Investment advice for different goals
        advice = {}
        for goal in goals:
            advice_result = self.finance_advisor_agent.run({
                'portfolio_data': portfolio_data,
                'goal': goal,
                'input': f'Provide investment advice for this portfolio with the goal: {goal}'
            })
            advice[goal] = advice_result.get('investment_advice', {})
        
        report['investment_advice'] = advice
        
        return report
    
    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Run the agent with the given inputs."""
        # Ensure portfolio data is properly formatted
        if 'portfolio_data' not in inputs:
            return {"error": "Portfolio data is required"}
        
        # Set default goals if not provided
        goals = inputs.get('goals', ['retirement', 'home_purchase', 'aggressive_growth'])
        
        # Generate financial report
        report = self._generate_financial_report(inputs['portfolio_data'], goals)
        
        # Let the agent summarize and format the report
        formatted_report = self.chain.invoke({
            'input': f'Create a formatted financial report from this data: {json.dumps(report)}'
        })
        
        return {
            'report': formatted_report,
            'raw_data': report
        } 