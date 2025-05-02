# src/agents/mentor_agent.py

from src.agents.base_agent import BaseAgent
from src.prompts.system_prompt_mentor import system_prompt_mentor


class MentorAgent(BaseAgent):
    def __init__(self):
        super().__init__("🧠 Mentor")

    def build_prompt(self, symptom: str, instinct_data: dict | None = None) -> str:
        return (
            f"Symptom: '{symptom}'\n"
            f"Instinktdaten: {instinct_data or {}}\n\n"
            f"Erkläre die Hintergründe des Verhaltens verständlich und anschaulich, so dass der Mensch es nachvollziehen kann."
        )

    def respond(self, symptom: str, instinct_data: dict | None = None) -> str:
        prompt = self.build_prompt(symptom, instinct_data)
        return super().respond(system_prompt=system_prompt_mentor, prompt=prompt)
