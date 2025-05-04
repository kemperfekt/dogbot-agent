from openai import OpenAI
from src.agents.base_agent import BaseAgent
from src.prompts.system_prompt_coach import system_prompt_coach
from src.models.agent_models import AgentMessage
from src.state.session_store import get_history
from src.services.retrieval import get_instinktwissen, get_erste_hilfe


class CoachAgent(BaseAgent):
    def __init__(self):
        super().__init__("coach")
        self.intro_text = (
            "Hallo! Ich bin Dein Coach und unterstütze Dich bei der Erziehung Deines Hundes. "
            "Zuerst erstelle ich die Diagnose, wollen wir loslegen?"
        )
        self.question_text = "Hast Du Lust, einen Blick auf den Trainingsplan zu werfen?"

    def introduce(self) -> AgentMessage:
        return AgentMessage(
            sender=self.name,
            text=self.intro_text
        )

    def respond(self, session_id: str, user_input: str, client: OpenAI) -> list[AgentMessage]:
        history = get_history(session_id)
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
        return [AgentMessage(sender=self.name, text=answer)]

    def give_training(self, session_id: str, user_input: str, client: OpenAI) -> list[AgentMessage]:
        history = get_history(session_id)
        symptom = self._extract_last_user_symptom(history)
        fachwissen = self._extract_last_dog_message(history)
        instinktvarianten = get_instinktwissen(symptom)

        # Führenden Instinkt wählen (hier einfach den ersten mit Inhalt)
        fuehrend = next((v["instinkt"] for v in instinktvarianten if v["beschreibung"]), "unbekannt")
        erste_hilfe = get_erste_hilfe(fuehrend, symptom)

        prompt = (
            f"Symptom: {symptom}\n"
            f"Fachwissen Hund: {fachwissen}\n"
            f"Führende Instinktvariante: {fuehrend}\n"
            f"Maßnahme aus Datenbank: {erste_hilfe}\n\n"
            "Wie kann ich diese Maßnahme verständlich und motivierend erklären?"
        )

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt_coach},
                {"role": "user", "content": prompt},
            ],
        )
        answer = response.choices[0].message.content.strip()
        return [AgentMessage(sender=self.name, text=answer)]

    def _extract_last_user_symptom(self, history: list[AgentMessage]) -> str:
        for msg in reversed(history):
            if msg.sender == "user":
                return msg.text.strip()
        return "(kein Symptom gefunden)"

    def _extract_last_dog_message(self, history: list[AgentMessage]) -> str:
        for msg in reversed(history):
            if msg.sender == "dog":
                return msg.text.strip()
        return "(keine Hundeperspektive gefunden)"

    def _build_prompt(self, symptom: str, instinktwissen: list[dict], fachwissen: str) -> str:
        jagd = next((v["beschreibung"] for v in instinktwissen if v["instinkt"] == "jagd"), "")
        rudel = next((v["beschreibung"] for v in instinktwissen if v["instinkt"] == "rudel"), "")
        territorial = next((v["beschreibung"] for v in instinktwissen if v["instinkt"] == "territorial"), "")
        sexual = next((v["beschreibung"] for v in instinktwissen if v["instinkt"] == "sexual"), "")

        return (
            f"Verschaffe Dir einen Eindruck aus Sicht des Menschen: {symptom}\n"
            f"Danach aus Sicht des Hundes: {fachwissen}\n\n"
            f"Instinktvariante jagd: {jagd}\n"
            f"Instinktvariante rudel: {rudel}\n"
            f"Instinktvariante territorial: {territorial}\n"
            f"Instinktvariante sexual: {sexual}\n\n"
            "Welche Variante passt am besten? Wenn zwei Varianten infrage kommen, nenne beide.\n"
            "Wenn keine passt, sage das offen.\n\n"
            "Gib in jedem Fall die passende Erste Hilfe aus."
        )
