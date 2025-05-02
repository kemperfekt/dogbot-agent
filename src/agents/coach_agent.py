# src/agents/coach_agent.py

from openai import OpenAI
from src.agents.base_agent import BaseAgent
from src.services.retrieval import get_symptom_info
from src.state.session_store import (
    get_diagnose_progress,
    set_diagnose_progress
)

class CoachAgent(BaseAgent):
    def __init__(self, client: OpenAI):
        super().__init__("🚀 Coach")
        self.client = client
        self.instinkte = ["jagdinstinkt", "rudelinstinkt", "territorialinstinkt", "sexualinstinkt"]

    def respond(self, symptom: str, session_id: str) -> str:
        # Lade Diagnose-Fortschritt
        progress = get_diagnose_progress(session_id)
        already_asked = progress.get("asked_instincts", [])
        remembered_symptom = progress.get("symptom")

        # Wenn Symptom sich geändert hat, Fortschritt zurücksetzen
        if remembered_symptom != symptom:
            progress = {"asked_instincts": [], "symptom": symptom}
            already_asked = []

        # Hole SymptomInfo
        try:
            info = get_symptom_info(symptom)
        except Exception:
            return "Ich brauche etwas mehr Information, um dir gute Fragen stellen zu können."

        # Finde nächste offene Instinkterklärung
        for instinkt in self.instinkte:
            if instinkt in already_asked:
                continue
            erklaerung = info.instinkterklaerungen.get(instinkt)
            if erklaerung and erklaerung.beschreibung:
                progress["asked_instincts"].append(instinkt)
                set_diagnose_progress(session_id, progress)
                return f"Trifft das auf dein Erlebnis zu? {erklaerung.beschreibung}"

        # Alle Instinkte durch → später GPT-Diagnose
        return "Ich habe dir nun alle Fragen gestellt, die mir helfen, dein Problem besser zu verstehen. Gib mir bitte kurz Bescheid, wenn du bereit für eine Einschätzung bist."
