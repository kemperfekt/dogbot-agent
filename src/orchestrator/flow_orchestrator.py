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

        # FSM-Zustand: START → Hund spricht
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
            instincts = self._classify_only(user_answer)
            mentor_reply = self.mentor.respond(
                symptom=user_answer,
                instinct_data=instincts.model_dump()
            )
            append_message(session_id, "mentor", mentor_reply)
            set_state(session_id, DialogState.MENTOR_RESPONDED)
            messages.append({"sender": "mentor", "text": mentor_reply})

        elif state == DialogState.MENTOR_RESPONDED:
            coach_reply = self.coach.respond(symptom=user_answer, client=self.client)
            append_message(session_id, "coach", coach_reply)
            set_state(session_id, DialogState.COACH_RESPONDED)
            messages.append({"sender": "coach", "text": coach_reply})

        elif state == DialogState.COACH_RESPONDED:
            history = get_history(session_id)
            last_msgs = [m["text"] for m in history if m["sender"] in {"dog", "mentor", "coach"}]
            companion_reply = self.companion.respond(previous_messages=last_msgs)
            append_message(session_id, "companion", companion_reply)
            set_state(session_id, DialogState.DONE)
            messages.append({"sender": "companion", "text": companion_reply})

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
