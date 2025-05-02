# agents/companion_agent.py

from src.agents.base_agent import BaseAgent
from src.prompts.system_prompt_companion import companion_prompt

class CompanionAgent(BaseAgent):
    def __init__(self):
        super().__init__("💛 Beziehungsbegleiter")

    def build_prompt(self, previous_messages: list[str] | None = None) -> str:
        base = companion_prompt
        if previous_messages:
            joined = "\n".join(previous_messages[-3:])
            return f"{base}\nHier die letzten Aussagen:\n{joined}"
        return base
