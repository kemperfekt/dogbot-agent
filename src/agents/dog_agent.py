# src/agents/dog_agent.py

from openai import OpenAI
from src.agents.base_agent import BaseAgent
from src.prompts.system_prompt_dog import system_prompt_dog
from src.services.retrieval import get_hundewissen
from src.models.agent_models import AgentMessage

class DogAgent(BaseAgent):
    def __init__(self):
        super().__init__("dog")

    def build_prompt(self, symptom: str) -> str:
        fachwissen = get_hundewissen(symptom)
        return (
            f"Wuff! Schön, dass du hier bist. Beschreibe ein Verhalten von mir und ich erkläre es dir!\n\n"
            f"Hier sind ein paar Eindrücke aus meiner Sicht als Hund, wie ich Situationen erlebe:\n"
            f"{fachwissen}\n\n"
            f"Sprich in meiner Stimme – freundlich, emotional und nahbar. Beschreibe, wie sich die Situation für mich anfühlt – mit Gerüchen, Geräuschen, Körpergefühlen.\n"
            f"Keine Fachbegriffe, keine Erklärungen wie ein Mensch. Kein Besserwissen.\n"
            f"Erkläre nicht, warum ich etwas tue – beschreibe einfach, wie es sich für mich anfühlt.\n"
            f"Beende NICHT mit einer Frage. Ich übernehme die Frage separat."
        )

    def respond(self, symptom: str, client: OpenAI) -> list[AgentMessage]:
        prompt = self.build_prompt(symptom=symptom)
        response_text = super().respond(
            system_prompt=system_prompt_dog,
            prompt=prompt,
            client=client
        ).text

        return [
            AgentMessage(sender="dog", text=response_text),
            AgentMessage(
                sender="dog",
                question="Möchtest du erfahren, warum ich mich so verhalte und wie ich mein Verhalten ändern kann?"
            )
        ]