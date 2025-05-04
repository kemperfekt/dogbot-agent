# src/models/agent_models.py

from pydantic import BaseModel
from typing import Literal


class AgentMessage(BaseModel):
    sender: Literal[
        "dog",        # aus Hundesicht
        "coach",      # erklärender Agent
        "companion",  # emotionaler Abschlussagent
        "user",       # Nutzereingabe
        "system",     # systeminterne Hinweise (z. B. "neu starten")
        "error",      # Fehler-Feedback
        "bot"         # optional für generische KI-Antworten
    ]
    text: str