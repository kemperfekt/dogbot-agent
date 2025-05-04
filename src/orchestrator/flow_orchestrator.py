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

    def has_agent_spoken(self, session_id: str, agent: str) -> bool:
        history = get_history(session_id)
        return any(m.sender == agent for m in history)

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

        # Coach
        messages = []
        if not self.has_agent_spoken(session_id, "coach"):
            coach_intro = AgentMessage(sender="coach", text=self.coach.intro_text)
            append_message(session_id, coach_intro)
            messages.append(coach_intro)

        return {
            "session_id": session_id,
            "messages": messages
        }

        # Der Coach antwortet später auf Eingabe
        # coach_msg = self.coach.respond(session_id, user_answer, self.client)
        # coach_question = AgentMessage(sender="coach", text=self.coach.question_text)

        # append_message(session_id, coach_msg)
        # append_message(session_id, coach_question)

        # Companion (vorerst deaktiviert)
        # companion_intro = AgentMessage(sender="companion", text=self.companion.intro_text)
        # companion_responses = self.companion.respond(session_id, self.client)

        # if len(companion_responses) < 2:
        #     raise ValueError("CompanionAgent lieferte weniger als 2 Nachrichten zurück.")

        # companion_msg = companion_responses[1]
        # companion_question = companion_responses[2] if len(companion_responses) > 2 else None

        # append_message(session_id, companion_intro)
        # append_message(session_id, companion_msg)
        # if companion_question:
        #     append_message(session_id, companion_question)

        # return {
        #     "session_id": session_id,
        #     "messages": [
        #         coach_intro,
        #         coach_msg,
        #         coach_question,
        #         companion_intro,
        #         companion_msg,
        #         companion_question,
        #     ] if companion_question else [
        #         coach_intro,
        #         coach_msg,
        #         coach_question,
        #         companion_intro,
        #         companion_msg,
        #     ]
        # }
