import openai
import os
from typing import List
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI
from langchain.utilities import GoogleSearchAPIWrapper
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def google_search(query: str, num_results: int = 3) -> List[str]:
    """Uses Google Search API to fetch top search results."""
    search = GoogleSearchAPIWrapper()
    results = search.results(query, num_results)
    return [result["snippet"] for result in results]

def generate_response(query: str, retrieved_docs: List[str]) -> str:
    """Generates a response using OpenAI's API with the retrieved context."""
    context = "\n".join(retrieved_docs)
    prompt = f"""You are an AI assistant. Use the following retrieved search results to answer the query.\n\nContext:\n{context}\n\nQuery: {query}\nResponse:"""
    
    llm = ChatOpenAI(model_name="gpt-4o-mini", openai_api_key=OPENAI_API_KEY)
    response = llm.invoke(prompt)
    return response.content

def main():
    """Main function to demonstrate Google Search RAG agentic system."""
    search_tool = Tool(name="Google Search", func=google_search, description="Searches Google for relevant information.")
    llm = ChatOpenAI(model_name="gpt-4o-mini", openai_api_key=OPENAI_API_KEY)
    agent = initialize_agent([search_tool], llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)
    
    user_query = "Which ETF should I buy if I wanna invest into SPY 500? I dont want to buy expensive ones like qqq"
    response = agent.invoke({"input": user_query})
    print("AI Response:", response["output"])

if __name__ == "__main__":
    main()
