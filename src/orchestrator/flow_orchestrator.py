# src/orchestrator/flow_orchestrator.py

import os
from openai import OpenAI

from src.agents.dog_agent import DogAgent
from src.agents.coach_agent import CoachAgent
from src.agents.companion_agent import CompanionAgent
from src.models.agent_models import AgentMessage
from src.state.session_store import create_session, append_message


class FlowOrchestrator:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAIAPIKEY"))
        self.dog = DogAgent()
        self.coach = CoachAgent()
        self.companion = CompanionAgent()

    def run_initial_flow(self, symptom: str) -> dict:
        session_id = create_session()

        # Hund antwortet (nun als Liste von Messages)
        dog_messages = self.dog.respond(symptom, self.client)
        for msg in dog_messages:
            append_message(session_id, msg)

        return {
            "session_id": session_id,
            "messages": dog_messages
        }

    def run_continued_flow(self, session_id: str, user_answer: str) -> dict:
        # Nutzereingabe speichern
        append_message(session_id, AgentMessage(sender="user", text=user_answer))

        # Coach antwortet mit Rückfrage oder Diagnose
        coach_msg = self.coach.respond(session_id, user_answer, self.client)
        append_message(session_id, coach_msg)

        return {
            "session_id": session_id,
            "messages": [coach_msg]
        }