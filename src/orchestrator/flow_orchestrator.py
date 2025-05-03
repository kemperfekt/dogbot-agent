import os
from openai import OpenAI

from src.agents.dog_agent import DogAgent
from src.agents.coach_agent import CoachAgent
from src.services.retrieval import get_symptom_info
from src.state.session_store import create_session, append_message
from src.models.agent_models import AgentMessage

class FlowOrchestrator:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAIAPIKEY"))
        self.dog = DogAgent()
        self.coach = CoachAgent()

    def run_initial_flow(self, symptom: str) -> dict:
        session_id = create_session()

        # Hund antwortet auf Symptom
        dog_response = self.dog.respond(symptom)
        append_message(session_id, "dog", dog_response)

        return {
            "session_id": session_id,
            "messages": [
                AgentMessage(sender="dog", text=dog_response)
            ]
        }

    def run_continued_flow(self, session_id: str, user_answer: str) -> dict:
        append_message(session_id, "user", user_answer)

        # Coach antwortet mit Rückfrage oder Diagnose
        coach_reply = self.coach.respond(session_id, user_answer, self.client)
        append_message(session_id, "coach", coach_reply)

        try:
            parsed = AgentMessage.model_validate_json(coach_reply)
        except Exception:
            parsed = AgentMessage(sender="coach", text=coach_reply)

        return {
            "session_id": session_id,
            "messages": [parsed]
        }