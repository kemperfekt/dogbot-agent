# src/agents/coach_agent.py

from openai import OpenAI
from src.agents.base_agent import BaseAgent
from src.prompts.system_prompt_coach import system_prompt_coach
from src.services.retrieval import get_symptom_info, get_instinkt_rueckfrage
from src.services.instinct_classifier import classify_instincts

class CoachAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Coach")

    def build_prompt(self, symptom_info, session_history=None):
        """
        Baut den Prompt, basierend auf der Diagnosephase:
        - Wenn Instinkt unklar, stelle gezielte Rückfrage
        - Wenn Diagnose klar, fasse Diagnose zusammen
        """
        if not symptom_info.instinktvarianten:
            return "Ich konnte leider keine Instinktvarianten zu diesem Symptom finden."

        # Wähle die erste passende Instinktvariante für Rückfrage (vereinfachter MVP-Fall)
        instinktfrage = get_instinkt_rueckfrage(symptom_info.instinktvarianten)
        if instinktfrage:
            return instinktfrage

        # Fallback, falls keine passende Frage
        return f"Wie genau zeigt sich das Verhalten '{symptom_info.symptom_name}' bei deinem Hund?"

    def respond(self, session_id: str, user_input: str, client: OpenAI) -> str:
        symptom_info = get_symptom_info(user_input)
        prompt = self.build_prompt(symptom_info)
        return super().respond(prompt=prompt, system_prompt=system_prompt_coach)
