from langchain_core.language_models import BaseLanguageModel
from typing import Dict, Any, List, TypedDict, Annotated, Literal
from enum import Enum
from langgraph.graph import StateGraph, END
from app.agents.finance_advisor_agent import FinanceAdvisorAgent
from app.agents.market_analysis_agent import MarketAnalysisAgent
from app.agents.forecasting_agent import ForecastingAgent

# Define the state
class AgentState(TypedDict):
    portfolio_data: Dict[str, Any]
    goals: List[str]
    risk_assessment: Dict[str, Any]
    category_analysis: Dict[str, Any]
    market_analysis: Dict[str, Any]
    forecasting: Dict[str, Any]
    investment_advice: Dict[str, Any]
    error: str
    final_report: str
    next: str

# Define agent identifiers
class AgentType(str, Enum):
    FINANCE_ADVISOR = "finance_advisor"
    MARKET_ANALYSIS = "market_analysis"
    FORECASTING = "forecasting"
    REPORT_GENERATOR = "report_generator"

def create_agent_graph(llm: BaseLanguageModel) -> StateGraph:
    """Create a graph of agents for financial analysis."""
    
    # Initialize agents
    finance_advisor_agent = FinanceAdvisorAgent(llm)
    market_analysis_agent = MarketAnalysisAgent(llm)
    forecasting_agent = ForecastingAgent(llm)
    
    # Define state graph
    workflow = StateGraph(AgentState)
    
    # Risk Assessment & Category Analysis Node
    def risk_assessment_node(state: AgentState) -> AgentState:
        """Assess portfolio risk and categories."""
        try:
            result = finance_advisor_agent.run({
                'portfolio_data': state['portfolio_data'],
                'input': 'Analyze this portfolio to assess its risk level and categorize the stocks.'
            })
            
            # Extract risk assessment and category analysis
            return {
                **state,
                'risk_assessment': result.get('risk_assessment', {}),
                'category_analysis': result.get('category_analysis', {})
            }
        except Exception as e:
            return {**state, 'error': f"Risk assessment failed: {str(e)}"}
    
    # Market Analysis Node
    def market_analysis_node(state: AgentState) -> AgentState:
        """Analyze market sentiment and relevant articles."""
        try:
            # Find the largest holding in the portfolio
            largest_ticker = None
            if 'category_analysis' in state and 'assets' in state['category_analysis']:
                assets = state['category_analysis']['assets']
                if assets:
                    largest_ticker = max(assets, key=lambda x: x.get('allocation', 0))['ticker']
            
            # Get categories from portfolio for market research
            categories = []
            if 'category_analysis' in state and 'category_metrics' in state['category_analysis']:
                categories = [cat['category'] for cat in state['category_analysis']['category_metrics']]
            
            # Run market analysis
            result = market_analysis_agent.run({
                'ticker': largest_ticker,
                'categories': categories,
                'input': f'Research market sentiment and relevant articles for {largest_ticker} and these categories: {", ".join(categories)}'
            })
            
            return {**state, 'market_analysis': result}
        except Exception as e:
            return {**state, 'error': f"Market analysis failed: {str(e)}"}
    
    # Forecasting Node
    def forecasting_node(state: AgentState) -> AgentState:
        """Forecast largest holding and compare with indices."""
        try:
            # Find the largest holding in the portfolio
            largest_ticker = None
            if 'category_analysis' in state and 'assets' in state['category_analysis']:
                assets = state['category_analysis']['assets']
                if assets:
                    largest_ticker = max(assets, key=lambda x: x.get('allocation', 0))['ticker']
            
            if not largest_ticker:
                return {**state, 'error': "Could not determine largest holding for forecasting"}
            
            # Run forecasting
            result = forecasting_agent.run({
                'ticker': largest_ticker,
                'forecast_days': 30,
                'input': f'Forecast {largest_ticker} price for the next month using XGBoost and compare with market indices.'
            })
            
            return {**state, 'forecasting': result}
        except Exception as e:
            return {**state, 'error': f"Forecasting failed: {str(e)}"}
    
    # Investment Advice Node
    def investment_advice_node(state: AgentState) -> AgentState:
        """Generate investment advice for different goals."""
        try:
            advice = {}
            for goal in state['goals']:
                result = finance_advisor_agent.run({
                    'portfolio_data': state['portfolio_data'],
                    'goal': goal,
                    'input': f'Provide investment advice for this portfolio with the goal: {goal}'
                })
                advice[goal] = result.get('investment_advice', {})
            
            return {**state, 'investment_advice': advice}
        except Exception as e:
            return {**state, 'error': f"Investment advice generation failed: {str(e)}"}
    
    # Report Generator Node
    def report_generator_node(state: AgentState) -> AgentState:
        """Generate final comprehensive report."""
        try:
            # Prompt for report generation
            prompt = f"""
            You are a professional financial advisor. Create a comprehensive report based on the following analysis:
            
            1. Risk Assessment: {state.get('risk_assessment', {})}
            
            2. Portfolio Categories: {state.get('category_analysis', {})}
            
            3. Market Analysis: {state.get('market_analysis', {})}
            
            4. Forecasting Results: {state.get('forecasting', {})}
            
            5. Investment Advice:
            {state.get('investment_advice', {})}
            
            Create a well-structured, professional report that summarizes all these findings
            in a clear, concise, and actionable format for the client.
            Include visual references where appropriate (mention which charts would be displayed).
            """
            
            # Generate report using the LLM
            final_report = llm.invoke(prompt).content
            
            return {**state, 'final_report': final_report}
        except Exception as e:
            return {**state, 'error': f"Report generation failed: {str(e)}"}
    
    # Define router based on "next" field
    def router(state: AgentState) -> Literal["risk_assessment", "market_analysis", "forecasting", "investment_advice", "report_generator", "END"]:
        if 'error' in state and state['error']:
            return END
            
        return state.get('next', END)
    
    # Add nodes to graph
    workflow.add_node("risk_assessment", risk_assessment_node)
    workflow.add_node("market_analysis", market_analysis_node)
    workflow.add_node("forecasting", forecasting_node)
    workflow.add_node("investment_advice", investment_advice_node)
    workflow.add_node("report_generator", report_generator_node)
    
    # Set edges
    workflow.set_entry_point("risk_assessment")
    workflow.add_edge("risk_assessment", "market_analysis")
    workflow.add_edge("market_analysis", "forecasting")
    workflow.add_edge("forecasting", "investment_advice")
    workflow.add_edge("investment_advice", "report_generator")
    workflow.add_edge("report_generator", END)
    
    # Compile the graph
    return workflow.compile()


def run_financial_analysis(llm: BaseLanguageModel, portfolio_data: Dict[str, Any], goals: List[str] = None) -> Dict[str, Any]:
    """Run the complete financial analysis workflow."""
    if goals is None:
        goals = ['retirement', 'home_purchase', 'aggressive_growth']
    
    # Create the graph
    graph = create_agent_graph(llm)
    
    # Initialize the state
    initial_state = {
        'portfolio_data': portfolio_data,
        'goals': goals,
        'risk_assessment': {},
        'category_analysis': {},
        'market_analysis': {},
        'forecasting': {},
        'investment_advice': {},
        'error': '',
        'final_report': '',
        'next': 'risk_assessment'
    }
    
    # Run the graph
    result = graph.invoke(initial_state)
    
    # Return results
    return {
        'report': result.get('final_report', ''),
        'error': result.get('error', ''),
        'details': {
            'risk_assessment': result.get('risk_assessment', {}),
            'category_analysis': result.get('category_analysis', {}),
            'market_analysis': result.get('market_analysis', {}),
            'forecasting': result.get('forecasting', {}),
            'investment_advice': result.get('investment_advice', {})
        }
    } 