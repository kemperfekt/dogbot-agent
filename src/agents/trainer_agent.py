# agents/trainer_agent.py

from pydantic import BaseModel
from typing import List
from src.agents.base_agent import BaseAgent 
from src.prompts.system_prompt_trainer import trainer_prompt

class TrainingPlan(BaseModel):
    plan: str
    tips: List[str]

class TrainerAgent(BaseAgent):
    def __init__(self):
        super().__init__("🏋️‍♂️ Trainer")

    def build_prompt(self, history: list[str], mentor_summary: str) -> str:
        joined = "\n".join(history[-3:])
        return (
            f"{trainer_prompt}\n"
            f"Zusammenfassung des MentorAgent: {mentor_summary}\n"
            f"Letzter Gesprächsverlauf:\n{joined}\n"
            "Formuliere daraus einen Trainingsplan mit Ziel und 3 alltagstauglichen Tipps."
        )
