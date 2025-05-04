# --- src/orchestrator/flow_orchestrator.py ---

import os
from openai import OpenAI

from src.agents.dog_agent import DogAgent
from src.agents.coach_agent import CoachAgent
from src.agents.companion_agent import CompanionAgent
from src.models.agent_models import AgentMessage
from src.state.session_store import create_session, append_message, get_history


class FlowOrchestrator:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAIAPIKEY"))
        self.dog = DogAgent()
        self.coach = CoachAgent()
        self.companion = CompanionAgent()

    def run_intro_only(self) -> dict:
        session_id = create_session()
        greeting = AgentMessage(sender="dog", text=self.dog.greeting_text)
        append_message(session_id, greeting)
        return {
            "session_id": session_id,
            "messages": [greeting]
        }

    def run_initial_flow(self, symptom: str, session_id: str | None = None) -> dict:
        if session_id is None:
            session_id = create_session()

        dog_messages = self.dog.respond(symptom, self.client)

        for m in dog_messages:
            append_message(session_id, m)

        return {
            "session_id": session_id,
            "messages": dog_messages
        }

    def run_continued_flow(self, session_id: str, user_answer: str) -> dict:
        append_message(session_id, AgentMessage(sender="user", text=user_answer))

        history = get_history(session_id)
        coach_messages = [m for m in history if m.sender == "coach"]

        # Fall 1: Coach hat sich noch nicht gemeldet → Begrüßung senden
        if not coach_messages:
            intro_msg = AgentMessage(sender="coach", text=self.coach.intro_text)
            append_message(session_id, intro_msg)
            return {
                "session_id": session_id,
                "messages": [intro_msg]
            }

        # Fall 2: Coach hat begrüßt, wartet auf Zustimmung → prüfe Eingabe im respond()
        coach_msg = self.coach.respond(session_id=session_id, user_input=user_answer, client=self.client)
        append_message(session_id, coach_msg)

        return {
            "session_id": session_id,
            "messages": [coach_msg]
        }