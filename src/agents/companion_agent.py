# agents/companion_agent.py

from agents.base_agent import BaseAgent

class CompanionAgent(BaseAgent):
    def __init__(self):
        super().__init__("💛 Beziehungsbegleiter")

    def build_prompt(self, previous_messages: list[str] | None = None) -> str:
        base = (
            "Zum Abschluss möchtest du dem Menschen helfen, die Beziehung zum Hund zu stärken.\n"
            "Formuliere einen Gedanken oder Impuls, der Vertrauen, Achtsamkeit oder Verbindung fördert."
        )
        if previous_messages:
            joined = "\n".join(previous_messages[-3:])  # letzte 3 Messages als Kontext
            return base + f"\nHier die letzten Aussagen: \n{joined}"
        return base