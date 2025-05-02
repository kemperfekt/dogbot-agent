# src/orchestrator/flow_orchestrator.py

import os
from src.agents.dog_agent import DogAgent
from src.agents.mentor_agent import MentorAgent
from src.agents.coach_agent import CoachAgent
from src.agents.companion_agent import CompanionAgent
from src.agents.trainer_agent import TrainerAgent
from src.services.instinct_classifier import InstinctClassification, classify_instincts
from openai import OpenAI

class FlowOrchestrator:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_APIKEY"))
        self.dog = DogAgent()
        self.mentor = MentorAgent()
        self.coach = CoachAgent(self.client)
        self.companion = CompanionAgent()
        self.trainer = TrainerAgent()

    def run_initial_flow(self, symptom: str) -> dict:
        """Initialer Einstieg: Hund reagiert auf menschliche Beschreibung."""
        dog_response = self.dog.respond(symptom=symptom)
        return {
            "messages": [
                {"sender": "dog", "text": dog_response}
            ]
        }

    def continue_flow(self, symptom: str, step: str) -> dict:
        """Setzt den Dialog mit einem bestimmten Agenten fort."""
        if step == "mentor":
            instincts = self._classify_only(symptom)
            mentor_response = self.mentor.respond(symptom=symptom, instinct_data=instincts.model_dump())
            return {"messages": [{"sender": "mentor", "text": mentor_response}]}
        elif step == "coach":
            coach_response = self.coach.respond(symptom=symptom, client=self.client)
            return {"messages": [{"sender": "coach", "text": coach_response}]}
        elif step == "companion":
            # Platzhalter: Companion kann später aus vorherigen Messages schöpfen
            companion_response = self.companion.respond(previous_messages=[symptom])
            return {"messages": [{"sender": "companion", "text": companion_response}]}
        else:
            return {"messages": [{"sender": "error", "text": "Unbekannter Schritt"}]}

    def _classify_only(self, text: str) -> InstinctClassification:
        return classify_instincts(text, self.client)
