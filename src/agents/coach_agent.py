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
        self.instinkte = ["jagd", "rudel", "territorial", "sexual"]

    def respond(self, symptom: str, session_id: str) -> str:
        progress = get_diagnose_progress(session_id)
        already_asked = progress.get("asked_instincts", [])
        remembered_symptom = progress.get("symptom")

        if remembered_symptom != symptom:
            progress = {"asked_instincts": [], "symptom": symptom}
            already_asked = []

        try:
            info = get_symptom_info(symptom)
        except Exception:
            return "Ich brauche etwas mehr Information, um dir gute Fragen stellen zu können."

        for instinkt in self.instinkte:
            if instinkt in already_asked:
                continue
            erklaerung = next(
                (v for v in info.instinktvarianten if v.instinkt == instinkt),
                None
            )
            if erklaerung and erklaerung.beschreibung:
                progress["asked_instincts"].append(instinkt)
                set_diagnose_progress(session_id, progress)
                return f"Trifft das auf dein Erlebnis zu? {erklaerung.beschreibung}"

        return "Ich habe dir nun alle Fragen gestellt, die mir helfen, dein Problem besser zu verstehen. Gib mir bitte kurz Bescheid, wenn du bereit für eine Einschätzung bist."

    def build_prompt(self, symptom: str) -> str:
        return "Coach verwendet direkten Flow, kein klassischer Prompt."
