# agents/mentor_agent.py

from src.agents.base_agent import BaseAgent
from src.prompts.system_prompt_mentor import mentor_prompt

class MentorAgent(BaseAgent):
    def __init__(self):
        super().__init__("🧠 Mentor")

    def build_prompt(self, symptom: str, instinct_data: dict | None = None) -> str:
        if instinct_data:
            instinkte = ", ".join([f"{k}: {v}%" for k, v in instinct_data.items()])
            return (
                f"{mentor_prompt}\n\n"
                f"Symptom: {symptom}\n"
                f"Erkannte Instinkte: {instinkte}"
            )
        else:
            return (
                f"{mentor_prompt}\n\n"
                f"Symptom: {symptom}\n"
                "Ich erkläre dir, welche Instinkte bei Hunden grundsätzlich eine Rolle spielen."
            )
