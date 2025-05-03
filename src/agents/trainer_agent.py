# src/agents/trainer_agent.py

from openai import OpenAI
from src.agents.base_agent import BaseAgent
from src.prompts.system_prompt_trainer import system_prompt_trainer
from src.services.retrieval import get_symptom_info


class TrainerAgent(BaseAgent):
    def __init__(self):
        super().__init__("Trainer")

    def build_prompt(self, symptom_info) -> str:
        """Baut den Prompt aus erster Hilfe und einem einfachen Übergang."""
        erste_hilfe = symptom_info.erste_hilfe.strip()

        return (
            f"Ich bin dein Trainer. Ich begleite dich mit konkreten Tipps, die du direkt im Alltag ausprobieren kannst.\n\n"
            f"Hier ist mein Vorschlag:\n\n"
            f"{erste_hilfe}\n\n"
            f"Wie geht es dir damit?"
        )

    def respond(self, symptom: str, client: OpenAI) -> str:
        """Holt die erste Hilfe aus Weaviate und erstellt den GPT-Dialog."""
        symptom_info = get_symptom_info(symptom)
        prompt = self.build_prompt(symptom_info)
        return super().respond(system_prompt=system_prompt_trainer, prompt=prompt)
