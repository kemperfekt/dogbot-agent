# agents/coach_agent.py

from agents.base_agent import BaseAgent
from services.instinct_classifier import classify_instincts
from openai import OpenAI
from prompts.blocks import diagnose_rueckfrage_generisch

class CoachAgent(BaseAgent):
    def __init__(self, client: OpenAI):
        super().__init__("🛠 Coach")
        self.client = client

    def build_prompt(self, symptom: str, instinct_data: dict | None = None) -> str:
        if instinct_data is None:
            return diagnose_rueckfrage_generisch.replace("{{symptom}}", symptom)
        else:
            # z. B. Später spezifische Rückfragen formulieren basierend auf Instinkten
            return f"Du beschreibst: '{symptom}'. Ich vermute folgende Instinkte: {instinct_data}"

    def respond(self, symptom: str, client: OpenAI) -> str:
        instincts = classify_instincts(symptom, client)
        instinct_data = instincts.model_dump(exclude={"kommentar"})
        return super().respond(symptom=symptom, instinct_data=instinct_data)
