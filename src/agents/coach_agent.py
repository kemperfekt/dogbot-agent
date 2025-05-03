# src/agents/coach_agent.py

from openai import OpenAI
from src.agents.base_agent import BaseAgent
from src.services.retrieval import get_symptom_info
from src.prompts.system_prompt_coach import system_prompt_coach


class CoachAgent(BaseAgent):
    def __init__(self, client: OpenAI):
        super().__init__("Coach")
        self.client = client

    def build_prompt(self, symptom_info: dict) -> str:
        symptom_name = symptom_info.symptom_name
        variants = symptom_info.instinktvarianten

        prompt_lines = []
        for v in variants:
            frage = f"Wie verhält sich dein Hund in dieser Situation: {v.beschreibung.strip()}"
            prompt_lines.append(f"- {frage} (Instinkt: {v.instinkt})")

        prompt = "\n".join(prompt_lines)
        return prompt

    def respond(self, session_id: str, symptom: str, client: OpenAI) -> str:
        symptom_info = get_symptom_info(symptom)
        prompt = self.build_prompt(symptom_info)
        return super().respond(
            system_prompt=system_prompt_coach,
            prompt=prompt
        )
