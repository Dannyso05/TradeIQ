
from typing import List
from langchain.utilities import GoogleSearchAPIWrapper
from dotenv import load_dotenv
from langchain.tools import Tool

load_dotenv()

def google_search(query: str, num_results: int = 3) -> List[str]:
    search = GoogleSearchAPIWrapper()
    results = search.results(query, num_results)
    return [result["snippet"] for result in results]

def searchtool():
    return Tool(name="Google Search", func=google_search, description="Searches Google for relevant information.")