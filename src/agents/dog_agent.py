# agents/dog_agent.py

from src.agents.base_agent import BaseAgent
from src.prompts.prompt_hundliche_wahrnehmung import hundliche_wahrnehmung

class DogAgent(BaseAgent):
    def __init__(self):
        super().__init__("🐾 Hund")

    def build_prompt(self, symptom: str) -> str:
        return f"{hundliche_wahrnehmung}\n\nDie menschliche Beschreibung lautet: '{symptom}'"
