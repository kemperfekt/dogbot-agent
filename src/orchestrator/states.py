# src/orchestrator/states.py

from enum import Enum

class DialogState(Enum):
    START = "start"               # Flow beginnt – Hund reagiert
    DOG_RESPONDED = "dog"         # Hund hat geantwortet, Mentor folgt
    MENTOR_RESPONDED = "mentor"   # Mentor hat erklärt, Coach folgt
    COACH_RESPONDED = "coach"     # Coach hat beraten, Companion folgt
    COMPANION_RESPONDED = "companion"  # Companion rundet ab
    DONE = "done"                 # Flow abgeschlossen
