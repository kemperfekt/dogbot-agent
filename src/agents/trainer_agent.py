# src/agents/trainer_agent.py

from src.agents.base_agent import BaseAgent

class TrainerAgent(BaseAgent):
    def __init__(self):
        super().__init__("Trainer")

    def respond(self, *args, **kwargs) -> str:
        return "Der Trainer ist für diesen Durchlauf deaktiviert."
