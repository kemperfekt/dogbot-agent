from openai import OpenAI
from src.agents.base_agent import BaseAgent
from src.prompts.system_prompt_companion import system_prompt_companion
from src.state.session_store import get_history
from src.logic.context_analyzer import extract_breed_from_history
from src.models.agent_models import AgentMessage


class CompanionAgent(BaseAgent):
    def __init__(self):
        super().__init__("companion")
        self.intro_text = "Ich bin dein treuer Begleiter auf diesem Weg."
        self.question_text = "Willst du diesen Weg gemeinsam mit mir weitergehen?"

    def introduce(self) -> AgentMessage:
        return AgentMessage(
            sender=self.name,
            text=self.intro_text
        )

    def build_prompt(self, session_id: str) -> str:
        history = get_history(session_id)
        breed = extract_breed_from_history(history)
        breed_info = get_breed_info(breed) if breed else None

        info_text = (
            f"Rasse: {breed_info.rasse}\n"
            f"Beschreibung: {breed_info.beschreibung}\n"
            f"Erziehung: {breed_info.erziehung}\n"
            f"Herkunft: {breed_info.herkunft}\n"
        ) if breed_info else "(keine rassespezifischen Infos gefunden)"

        return (
            f"Hier ist der letzte Abschnitt des Gesprächs. Kontext: {info_text}\n"
            f"Formuliere eine warmherzige, abschließende Nachricht, die Mensch und Hund motiviert."
        )

    def respond(self, session_id: str, client: OpenAI) -> list[AgentMessage]:
        prompt = self.build_prompt(session_id)
        return super().respond(
            system_prompt=system_prompt_companion,
            prompt=prompt,
            client=client,
            include_greeting=False  # Begrüßung wird manuell über intro_text gesteuert
        )