# src/orchestrator/flow_orchestrator.py

import os
from openai import OpenAI
from src.agents.dog_agent import DogAgent
from src.agents.mentor_agent import MentorAgent
from src.agents.coach_agent import CoachAgent
from src.agents.companion_agent import CompanionAgent
from src.agents.trainer_agent import TrainerAgent
from src.services.instinct_classifier import InstinctClassification, classify_instincts
from src.state.session_store import (
    create_session,
    append_message,
    get_last_message,
    get_state,
    set_state,
)
from src.orchestrator.states import DialogState

class FlowOrchestrator:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_APIKEY"))
        self.dog = DogAgent()
        self.mentor = MentorAgent()
        self.coach = CoachAgent(self.client)
        self.companion = CompanionAgent()
        self.trainer = TrainerAgent()

    def run_initial_flow(self, symptom: str) -> dict:
        session_id = create_session()

        # Hund antwortet (Symptomvalidierung, Perspektive, Übergabefrage)
        dog_response = self.dog.respond(symptom=symptom)
        append_message(session_id, "dog", dog_response)
        set_state(session_id, DialogState.DOG_RESPONDED)

        return {
            "session_id": session_id,
            "messages": [{"sender": "dog", "text": dog_response}]
        }

    def run_continued_flow(self, session_id: str, user_answer: str) -> dict:
        append_message(session_id, "user", user_answer)
        state = get_state(session_id)
        messages = []

        if state == DialogState.DOG_RESPONDED:
            if self._is_positive(user_answer):
                # Mensch will Analyse → Coach beginnt mit Rückfragen
                coach_reply = self.coach.respond(symptom=user_answer, session_id=session_id)
                append_message(session_id, "coach", coach_reply)
                set_state(session_id, DialogState.COACH_RESPONDED)
                messages.append({"sender": "coach", "text": coach_reply})
            else:
                messages.append({"sender": "dog", "text": "Magst du mir sagen, ob du möchtest, dass mein Coach hilft?"})

        elif state == DialogState.COACH_RESPONDED:
            # Coach stellt weitere Rückfragen, solange nötig
            coach_reply = self.coach.respond(symptom=user_answer, session_id=session_id)
            append_message(session_id, "coach", coach_reply)
            messages.append({"sender": "coach", "text": coach_reply})
            # (Optional: Bei Erreichen aller Fragen Zustand wechseln)

        elif state == DialogState.MENTOR_RESPONDED:
            mentor_reply = self.mentor.respond(symptom=user_answer)
            append_message(session_id, "mentor", mentor_reply)
            set_state(session_id, DialogState.MENTOR_RESPONDED)
            messages.append({"sender": "mentor", "text": mentor_reply})

        elif state == DialogState.MENTOR_RESPONDED:
            trainer_reply = self.trainer.respond(symptom=user_answer)
            append_message(session_id, "trainer", trainer_reply)
            set_state(session_id, DialogState.DONE)
            messages.append({"sender": "trainer", "text": trainer_reply})

        elif state == DialogState.DONE:
            messages.append({"sender": "system", "text": "Der Flow ist abgeschlossen."})

        else:
            messages.append({"sender": "system", "text": "Ungültiger Zustand."})

        return {
            "session_id": session_id,
            "messages": messages
        }

    def _classify_only(self, text: str) -> InstinctClassification:
        return classify_instincts(text, self.client)

    def _is_positive(self, text: str) -> bool:
        text_lower = text.strip().lower()
        return any(kw in text_lower for kw in ["ja", "gerne", "bitte", "ok", "klar"])
