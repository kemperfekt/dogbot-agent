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

        # Begrüßung des Hundes (statisch, kein GPT)
        greeting = AgentMessage(sender="dog", text=self.dog.greeting_text)
        append_message(session_id, greeting)

        # Hund antwortet auf Symptom (GPT-generiert)
        dog_msg = self.dog.respond(symptom, self.client)
        append_message(session_id, dog_msg)

        # Abschlussfrage (statisch, kein GPT)
        question = AgentMessage(sender="dog", text=self.dog.question_text)
        append_message(session_id, question)

        return {
            "session_id": session_id,
            "messages": [greeting, dog_msg, question]
        }

    def run_continued_flow(self, session_id: str, user_answer: str) -> dict:
        append_message(session_id, AgentMessage(sender="user", text=user_answer))

        # Coach: Begrüßung → Antwort → Frage
        coach_intro = AgentMessage(sender="coach", text=self.coach.intro_text)
        append_message(session_id, coach_intro)

        coach_msg = self.coach.respond(session_id, user_answer, self.client)
        append_message(session_id, coach_msg)

        coach_question = AgentMessage(sender="coach", text=self.coach.question_text)
        append_message(session_id, coach_question)

        # Companion: Begrüßung → Antwort → Frage
        companion_intro = AgentMessage(sender="companion", text=self.companion.intro_text)
        append_message(session_id, companion_intro)

        companion_msg = self.companion.respond(session_id, self.client)
        append_message(session_id, companion_msg)

        companion_question = AgentMessage(sender="companion", text=self.companion.question_text)
        append_message(session_id, companion_question)

        return {
            "session_id": session_id,
            "messages": [
                coach_intro,
                coach_msg,
                coach_question,
                companion_intro,
                companion_msg,
                companion_question,
            ]
        }
