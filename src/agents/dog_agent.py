# src/agents/dog_agent.py

from src.agents.base_agent import BaseAgent
from src.prompts.prompt_hundliche_wahrnehmung import hundliche_wahrnehmung
from src.services.retrieval import get_hundewissen

class DogAgent(BaseAgent):
    def __init__(self):
        super().__init__("Hund")

    def build_prompt(self, symptom: str) -> str:
        # Inhalte aus Weaviate holen (z. B. chunks zur Hundeperspektive)
        fachwissen = get_hundewissen(symptom)

        return (
            f"{hundliche_wahrnehmung}\n\n"
            f"Das hier sind Eindrücke, die du als Hund kennst:\n"
            f"{fachwissen}\n\n"
            f"Formuliere aus der Sicht eines Hundes, basierend auf seiner Wahrnehmung. "
            f"Sei kurz, deutlich und freundlich, aber nicht unterwürfig. "
            f"Stelle zum Schluss die Frage, ob der Mensch mehr über die Ursachen deines Verhaltens wissen will."
        )

    def respond(self, symptom: str) -> str:
        prompt = self.build_prompt(symptom=symptom)
        return super().respond(system_prompt=hundliche_wahrnehmung, prompt=prompt)
