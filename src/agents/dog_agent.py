# src/agents/dog_agent.py

from src.agents.base_agent import BaseAgent
from src.prompts.prompt_hundliche_wahrnehmung import hundliche_wahrnehmung
from src.services.retrieval import get_hundewissen

class DogAgent(BaseAgent):
    def __init__(self):
        super().__init__("🐾 Hund")

    def build_prompt(self, symptom: str) -> str:
        # Weaviate-Retrieval: relevante Inhalte aus Sicht des Hundes
        chunks = get_hundewissen(symptom)
        fachwissen = "\n".join(f"- {c}" for c in chunks)

        return (
            f"{hundliche_wahrnehmung}\n\n"
            f"Das hier sind Eindrücke, die du als Hund kennst:\n"
            f"{fachwissen}\n\n"
            f"Die menschliche Beschreibung war: '{symptom}'. "
            f"Formuliere jetzt aus deiner Sicht als Hund, wie du dich in dieser konkreten Situation gefühlt hast. "
            f"Beziehe dich auf das Verhalten, das beschrieben wurde. "
            f"Sei instinktnah, klar, freundlich – aber nicht unterwürfig. "
            f"Stelle zum Schluss die Frage, ob der Mensch mehr über die Ursachen wissen möchte."
)

