# agents/mentor_agent.py

from agents.base_agent import BaseAgent

class MentorAgent(BaseAgent):
    def __init__(self):
        super().__init__("🧠 Mentor")

    def build_prompt(self, symptom: str, instinct_data: dict | None = None) -> str:
        if instinct_data:
            instinkte = ", ".join([f"{k}: {v}%" for k, v in instinct_data.items()])
            return (
                f"Basierend auf dem beschriebenen Verhalten ('{symptom}') wurden folgende Instinkte erkannt: {instinkte}.\n"
                "Ich erkläre dir nun, was diese Instinkte bedeuten und wie du damit umgehen kannst."
            )
        else:
            return (
                f"Du hast beschrieben: '{symptom}'.\n"
                "Ich erkläre dir, welche Instinkte bei Hunden grundsätzlich eine Rolle spielen und worauf du achten kannst."
            )