# agents/coach_agent.py

from openai import OpenAI
from src.agents.base_agent import BaseAgent
from src.services.instinct_classifier import classify_instincts
from src.prompts.system_prompt_questions import diagnose_rueckfragen

class CoachAgent(BaseAgent):
    def __init__(self, client: OpenAI):
        super().__init__("🛠 Coach")
        self.client = client

    def build_prompt(self, symptom: str, instinct_data: dict | None = None) -> str:
        if instinct_data is None:
            return diagnose_rueckfrage_generisch.replace("{{symptom}}", symptom)
        else:
            return f"Du beschreibst: '{symptom}'. Ich vermute folgende Instinkte: {instinct_data}"

    def respond(self, symptom: str, client: OpenAI) -> str:
        instincts = classify_instincts(symptom, client)
        instinct_data = instincts.model_dump(exclude={"kommentar"})
        return super().respond(symptom=symptom, instinct_data=instinct_data)
