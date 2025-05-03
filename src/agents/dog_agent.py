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
            f"{system_prompt_dog}\n\n"
            f"Das hier sind Eindrücke, die du als Hund kennst:\n"
            f"{fachwissen}\n\n"
            f"Formuliere aus der Sicht eines Hundes, basierend auf seiner Wahrnehmung. "
            f"Sei kurz, deutlich und freundlich, aber nicht unterwürfig. "
            f"Stelle zum Schluss die Frage, ob der Mensch mehr über die Ursachen deines Verhaltens wissen will."
        )

    def respond(self, symptom: str, client: OpenAI) -> str:
        prompt = self.build_prompt(symptom=symptom)
        message = super().respond(system_prompt=system_prompt_dog, prompt=prompt, client=client)
        return message.text or ""