from openai import OpenAI
from src.agents.base_agent import BaseAgent
from src.prompts.system_prompt_companion import system_prompt_companion
from src.services.retrieval import get_breed_info
from src.state.session_store import get_history
from src.logic.context_analyzer import extract_breed_from_history


class CompanionAgent(BaseAgent):
    def __init__(self):
        super().__init__("companion")

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

    def respond(self, session_id: str, client: OpenAI):
        prompt = self.build_prompt(session_id)
        return super().respond_with_intro_and_question(
            system_prompt=system_prompt_companion,
            prompt=prompt,
            client=client,
            intro="Ich bin dein treuer Begleiter auf diesem Weg.",
            question="Willst du diesen Weg gemeinsam mit mir weitergehen?"
        )