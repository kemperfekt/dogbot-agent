# agents/base_agent.py

from abc import ABC, abstractmethod

class BaseAgent(ABC):
    """Basisklasse für alle DogBot-Agentenrollen (🐾🧠🛠💛)"""

    def __init__(self, role_name: str):
        self.role_name = role_name

    @abstractmethod
    def build_prompt(self, **kwargs) -> str:
        """Jeder Agent muss seinen GPT-Prompt selbst definieren"""
        pass

    def respond(self, **kwargs) -> str:
        """Standard-GPT-Aufruf (hier noch Dummy-Ausgabe)"""
        prompt = self.build_prompt(**kwargs)
        return f"[{self.role_name}] {prompt}"
