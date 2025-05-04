# --- src/agents/coach_agent.py ---

from openai import OpenAI
from src.agents.base_agent import BaseAgent
from src.prompts.system_prompt_coach import system_prompt_coach
from src.models.agent_models import AgentMessage
from src.state.session_store import get_history
from src.services.retrieval import get_instinktwissen


class CoachAgent(BaseAgent):
    def __init__(self):
        super().__init__("coach")
        self.intro_text = (
            "Hallo! Ich bin Dein Coach und unterstütze Dich bei der Erziehung Deines Hundes. "
            "Zuerst erstelle ich die Diagnose, wollen wir loslegen?"
        )
        self.question_text = "Hast Du Lust, einen Blick auf den Trainingsplan zu werfen?"

    def build_prompt(self, symptom: str, hund_text: str, instinkte: list[dict]) -> str:
        varianten = "\n".join([
            f"- {item['instinkt'].capitalize()}: {item['beschreibung']}"
            for item in instinkte
        ])
        return (
            f"Symptom: {symptom}\n"
            f"Hundesicht: {hund_text}\n\n"
            f"Mögliche Instinktvarianten:\n{varianten}\n\n"
            f"Erkläre ruhig, welcher Instinkt oder welche Instinkte das Verhalten am besten erklären. "
            f"Formuliere verständlich und gib eine Einschätzung, wie der Mensch damit umgehen kann. "
            f"Biete abschließend an, eine passende Trainingsaufgabe zu formulieren."
        )

    def respond(self, session_id: str, user_input: str, client: OpenAI) -> list[AgentMessage]:
        history = get_history(session_id)

        # Ursprüngliches Symptom finden (erste user-Nachricht)
        symptom = next((m.text for m in history if m.sender == "user"), "")
        hund_text = next((m.text for m in history if m.sender == "dog"), "")

        instinkte = get_instinktwissen(symptom)
        prompt = self.build_prompt(symptom, hund_text, instinkte)

        return super().respond(
            system_prompt=system_prompt_coach,
            prompt=prompt,
            client=client,
            include_greeting=False
        )