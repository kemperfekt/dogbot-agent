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

    def respond(self, session_id: str, user_input: str, client: OpenAI) -> AgentMessage:
        # Prüfen, ob User erst begrüßt werden soll
        history = get_history(session_id)
        coach_messages = [m for m in history if m.sender == self.name]

        if not coach_messages:
            # Erste Nachricht vom Coach: nur Begrüßung
            return AgentMessage(sender=self.name, text=self.intro_text)

        if user_input.strip().lower() not in ["ja", "okay", "ok", "gern", "los", "klar"]:
            return AgentMessage(sender=self.name, text="Sag einfach Bescheid, wenn wir loslegen sollen.")

        # GPT-Antwort starten
        symptom = self._extract_last_user_symptom(history)
        fachwissen = self._extract_last_dog_message(history)
        instinktvarianten = get_instinktwissen(symptom)
        prompt = self._build_prompt(symptom, instinktvarianten, fachwissen)

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt_coach},
                {"role": "user", "content": prompt},
            ],
        )
        answer = response.choices[0].message.content.strip()
        full_answer = f"{answer}\n\n{self.question_text}"
        return AgentMessage(sender=self.name, text=full_answer)

    def _extract_last_user_symptom(self, history: list[AgentMessage]) -> str:
        user_msgs = [m.text for m in history if m.sender == "user"]
        return user_msgs[0] if user_msgs else "(kein Symptom gefunden)"

    def _extract_last_dog_message(self, history: list[AgentMessage]) -> str:
        dog_msgs = [m.text for m in history if m.sender == "dog"]
        return dog_msgs[-1] if dog_msgs else "(kein Hundetext gefunden)"

    def _build_prompt(self, symptom: str, instinktvarianten: dict, fachwissen: str) -> str:
        jagd = instinktvarianten.get("jagd", "")
        rudel = instinktvarianten.get("rudel", "")
        territorial = instinktvarianten.get("territorial", "")
        sexual = instinktvarianten.get("sexual", "")
        return (
            f"Das Symptom lautet: {symptom}\n\n"
            f"Hier ist der emotionale Hundetext:\n{fachwissen}\n\n"
            f"Instinkt-Wissen:\n"
            f"- Jagdtrieb: {jagd}\n"
            f"- Rudeltrieb: {rudel}\n"
            f"- Territorialtrieb: {territorial}\n"
            f"- Sexualtrieb: {sexual}\n\n"
            f"Bitte identifiziere den führenden Instinkt und erkläre ihn fachlich fundiert."
        )