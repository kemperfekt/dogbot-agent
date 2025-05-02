# src/orchestrator/flow_orchestrator.py

import os
from openai import OpenAI
from src.agents.dog_agent import DogAgent
from src.agents.mentor_agent import MentorAgent
from src.agents.coach_agent import CoachAgent
from src.agents.companion_agent import CompanionAgent
from src.agents.trainer_agent import TrainerAgent
from src.services.instinct_classifier import InstinctClassification, classify_instincts
from src.state.session_store import create_session, append_message, get_last_message

class FlowOrchestrator:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_APIKEY"))
        self.dog = DogAgent()
        self.mentor = MentorAgent()
        self.coach = CoachAgent(self.client)
        self.companion = CompanionAgent()
        self.trainer = TrainerAgent()

    def run_initial_flow(self, symptom: str) -> dict:
        # Neue Session starten
        session_id = create_session()

        # 1. 🐾 Hund
        dog_response = self.dog.respond(symptom=symptom)
        append_message(session_id, "dog", dog_response)

        # 2. 🔮 Mentor
        instincts = self._classify_only(symptom)
        mentor_response = self.mentor.respond(
            symptom=symptom,
            instinct_data=instincts.model_dump()
        )
        append_message(session_id, "mentor", mentor_response)

        # 3. 🚀 Coach
        coach_response = self.coach.respond(
            symptom=symptom,
            client=self.client
        )
        append_message(session_id, "coach", coach_response)

        # 4. 💛 Companion (optional)
        companion_response = self.companion.respond(
            previous_messages=[dog_response, mentor_response, coach_response]
        )
        append_message(session_id, "companion", companion_response)

        return {
            "session_id": session_id,
            "messages": [
                {"sender": "dog", "text": dog_response},
                {"sender": "mentor", "text": mentor_response},
                {"sender": "coach", "text": coach_response},
                {"sender": "companion", "text": companion_response}
            ]
        }

    def run_continued_flow(self, session_id: str, user_answer: str) -> dict:
        # Nutzerantwort speichern
        append_message(session_id, "user", user_answer)

        # 🔮 Mentor antwortet
        mentor_reply = self.mentor.respond(symptom=user_answer)
        append_message(session_id, "mentor", mentor_reply)

        # 🚀 Coach antwortet
        coach_reply = self.coach.respond(symptom=user_answer, client=self.client)
        append_message(session_id, "coach", coach_reply)

        return {
            "session_id": session_id,
            "messages": [
                {"sender": "mentor", "text": mentor_reply},
                {"sender": "coach", "text": coach_reply}
            ]
        }

    def _classify_only(self, text: str) -> InstinctClassification:
        return classify_instincts(text, self.client)
