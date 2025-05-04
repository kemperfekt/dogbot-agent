# --- src/agents/dog_agent.py ---

from openai import OpenAI
from src.agents.base_agent import BaseAgent
from src.prompts.system_prompt_dog import system_prompt_dog
from src.services.retrieval import get_schnelldiagnose
from src.models.agent_models import AgentMessage


class DogAgent(BaseAgent):
    def __init__(self):
        super().__init__("dog")
        self.greeting_text = "Wuff! Schön, dass du hier bist. Beschreibe ein Verhalten von mir und ich erkläre es dir!"
        self.question_text = "Möchtest du erfahren, warum ich mich so verhalte und wie ich mein Verhalten ändern kann?"

    def build_prompt(self, symptom: str) -> str:
        schnelldiagnose = get_schnelldiagnose(symptom)
        return (
            f"Hier ist meine Sicht auf das, was passiert:\n"
            f"{schnelldiagnose}\n\n"
            f"Sprich in meiner Stimme – freundlich, emotional und nahbar. "
            f"Keine Fachbegriffe. Beschreibe, wie es sich für mich anfühlt. "
            f"Keine Besserwisserei. Formuliere höchstens zwei Absätze, aber stelle am Ende **keine Rückfrage.**"
        )

    def respond(self, symptom: str, client: OpenAI) -> list[AgentMessage]:
        prompt = self.build_prompt(symptom=symptom)
        return super().respond(
            system_prompt=system_prompt_dog,
            prompt=prompt,
            client=client,
            include_greeting=False
        )
