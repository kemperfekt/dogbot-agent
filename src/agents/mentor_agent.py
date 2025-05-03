# src/agents/mentor_agent.py

from src.agents.base_agent import BaseAgent

class MentorAgent(BaseAgent):
    def __init__(self):
        super().__init__("Mentor")

    def respond(self, *args, **kwargs) -> str:
        return "Der Mentor ist für diesen Durchlauf deaktiviert."
