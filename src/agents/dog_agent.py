# agents/dog_agent.py

from agents.base_agent import BaseAgent

class DogAgent(BaseAgent):
    def __init__(self):
        super().__init__("🐾 Hund")

    def build_prompt(self, symptom: str) -> str:
        return (
            f"Stell dir vor, du bist ein Hund und beschreibst, was du erlebt hast, aus deiner Perspektive.\n"
            f"Die menschliche Beschreibung lautet: '{symptom}'\n"
            "Wie fühlt sich das für dich an? Was hast du wahrgenommen? Nutze dabei deine Sinne, dein Instinktverhalten und deine Emotionen."
        )
