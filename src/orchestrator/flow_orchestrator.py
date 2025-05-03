import os
from openai import OpenAI

from src.agents.dog_agent import DogAgent
from src.agents.mentor_agent import MentorAgent
from src.agents.coach_agent import CoachAgent
from src.agents.companion_agent import CompanionAgent
from src.agents.trainer_agent import TrainerAgent

from src.services.retrieval import get_symptom_info
from src.state.session_store import (
    create_session,
    append_message,
    get_last_message,
)


class FlowOrchestrator:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAIAPIKEY"))
        self.dog = DogAgent()
        self.mentor = MentorAgent()
        self.coach = CoachAgent()
        self.companion = CompanionAgent(self.client)  # OpenAI-Client wird korrekt übergeben
        self.trainer = TrainerAgent()

    def run_initial_flow(self, symptom: str) -> dict:
        session_id = create_session()

        # Hund antwortet
        dog_response = self.dog.respond(symptom)
        append_message(session_id, "dog", dog_response)

        return {
            "session_id": session_id,
            "messages": [
                {"sender": "dog", "text": dog_response}
            ]
        }

    def run_continued_flow(self, session_id: str, user_answer: str) -> dict:
        append_message(session_id, "user", user_answer)

        # Coach fragt nach oder erstellt Diagnose
        coach_reply = self.coach.respond(session_id, user_answer, self.client)
        append_message(session_id, "coach", coach_reply)

        if "diagnosis" not in coach_reply:
            return {
                "session_id": session_id,
                "messages": [
                    {"sender": "coach", "text": coach_reply}
                ]
            }

        # Mentor erklärt die Diagnose
        diagnosis = coach_reply["diagnosis"]
        mentor_reply = self.mentor.respond(diagnosis, user_answer)
        append_message(session_id, "mentor", mentor_reply)

        # Trainingsplan von Trainer
        symptom_info = get_symptom_info(user_answer)
        trainer_reply = self.trainer.respond(symptom_info, diagnosis)
        append_message(session_id, "trainer", trainer_reply)

        # Companion reflektiert Beziehungsebene
        messages_so_far = [
            get_last_message(session_id, role)
            for role in ["dog", "coach", "mentor", "trainer"]
        ]
        messages_so_far = [m["text"] for m in messages_so_far if m]

        companion_reply = self.companion.respond(session_id, messages_so_far)
        if companion_reply:
            append_message(session_id, "companion", companion_reply)
            all_messages = [
                {"sender": "coach", "text": coach_reply},
                {"sender": "mentor", "text": mentor_reply},
                {"sender": "trainer", "text": trainer_reply},
                {"sender": "companion", "text": companion_reply}
            ]
        else:
            all_messages = [
                {"sender": "coach", "text": coach_reply},
                {"sender": "mentor", "text": mentor_reply},
                {"sender": "trainer", "text": trainer_reply}
            ]

        return {
            "session_id": session_id,
            "messages": all_messages
        }
