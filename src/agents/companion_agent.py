# src/agents/companion_agent.py

from src.agents.base_agent import BaseAgent

class CompanionAgent(BaseAgent):
    def __init__(self):
        super().__init__("Companion")

    def respond(self, *args, **kwargs) -> str | None:
        return None  # Companion bleibt im Hintergrund
