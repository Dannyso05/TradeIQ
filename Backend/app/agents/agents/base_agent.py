from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod

class BaseAgent(ABC):
    """Base class for all agents in the system."""
    
    def __init__(self, llm: BaseLanguageModel):
        """Initialize the agent with an LLM."""
        self.llm = llm
        self.tools = []
        self.prompt = self._create_prompt()
        self.chain = self._create_chain()
    
    @abstractmethod
    def _create_prompt(self) -> ChatPromptTemplate:
        """Create the prompt template for the agent."""
        pass
    
    @abstractmethod
    def _create_chain(self) -> Runnable:
        """Create the chain for the agent."""
        pass
    
    @abstractmethod
    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Run the agent with the given inputs."""
        pass 