# src/agents/trainer_agent.py

from src.agents.base_agent import BaseAgent
from src.models.symptom_models import SymptomInfo
from src.prompts.system_prompt_trainer import system_prompt_trainer, build_trainer_prompt


class TrainerAgent(BaseAgent):
    def __init__(self):
        super().__init__("🛠 Trainer")

    def build_prompt(self, info: SymptomInfo) -> str:
        return build_trainer_prompt(
            symptom_name=info.symptom_name,
            erste_hilfe=getattr(info, "erste_hilfe", ""),
            hypothese_zuhause=getattr(info, "hypothese_zuhause", None)
        )

    def respond(self, symptom_info: SymptomInfo) -> str:
        prompt = self.build_prompt(symptom_info)
        return super().respond(system_prompt=system_prompt_trainer, prompt=prompt)
