# agents/trainer_agent.py

from agents.base_agent import BaseAgent
from pydantic import BaseModel
from typing import List

class TrainingPlan(BaseModel):
    plan: str
    tips: List[str]

class TrainerAgent(BaseAgent):
    def __init__(self):
        super().__init__("🏋️‍♂️ Trainer")

    def build_prompt(self, history: list[str], mentor_summary: str) -> str:
        joined = "\n".join(history[-3:])
        return (
            f"Hier ist die Zusammenfassung des MentorAgent: {mentor_summary}\n"
            f"Und das Gespräch bisher:\n{joined}\n"
            "Formuliere nun einen konkreten Trainingsplan mit Ziel und 3 alltagstauglichen Tipps."
        )