import os
from langchain.agents import initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv
from app.agents.tools.search import searchtool
from langchain.prompts import PromptTemplate
from models import SearchResult, SearchResponse

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

search_prompt = PromptTemplate(
    input_variables=["context"],
    template=(
        """You are an Market Researcher. Use the following context to retrieved search 
        results to assit our financial consultant to help our customer.\n\n"""
        "Context:\n{context}\n\n"
        "Response:"
    ),
)

def RunSearchAgent(context):
    search_tool = searchtool()
    llm = ChatOpenAI(model_name="gpt-4o-mini", openai_api_key=OPENAI_API_KEY)
    agent = initialize_agent([search_tool], llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)
    # user_query = "Which ETF should I buy if I wanna invest into SPY 500? I dont want to buy expensive ones like qqq"
    # response = agent.invoke({"input": user_query})
    prompt = search_prompt.format(context=context)
    response = agent.run(prompt)    
    print("AI Response:", response["output"])
    return {
        "Response" : response["output"]
    }
