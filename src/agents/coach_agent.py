# src/agents/coach_agent.py

from openai import OpenAI
from src.agents.base_agent import BaseAgent
from src.models.symptom_models import SymptomInfo
from src.prompts.system_prompt_coach import system_prompt_coach, build_coach_prompt


class CoachAgent(BaseAgent):
    def __init__(self):
        super().__init__("🚀 Coach")

    def build_prompt(self, symptom_info: SymptomInfo) -> str:
        return build_coach_prompt(
            symptom=symptom_info.symptom_name,
            instinktvarianten=symptom_info.instinktvarianten
        )

    def respond(self, session_id: str, symptom_info: SymptomInfo, client: OpenAI) -> str:
        prompt = self.build_prompt(symptom_info)
        return super().respond(
            system_prompt=system_prompt_coach,
            prompt=prompt
        )
