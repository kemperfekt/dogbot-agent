# orchestrator/flow_orchestrator.py

from agents.dog_agent import DogAgent
from agents.mentor_agent import MentorAgent
from agents.coach_agent import CoachAgent
from agents.companion_agent import CompanionAgent
from agents.trainer_agent import TrainerAgent
from services.instinct_classifier import InstinctClassification
from openai import OpenAI

class FlowOrchestrator:
    def __init__(self):
        self.client = OpenAI()
        self.dog = DogAgent()
        self.mentor = MentorAgent()
        self.coach = CoachAgent(self.client)
        self.companion = CompanionAgent()
        self.trainer = TrainerAgent()

    def run_initial_flow(self, symptom: str) -> dict:
        # 🐾 Hund: erlebt das Symptom aus seiner Sicht
        dog_response = self.dog.respond(symptom=symptom)

        # 🛠 Coach: klassifiziert Instinkte + reagiert
        coach_response = self.coach.respond(symptom=symptom, client=self.client)

        # 🧠 Mentor: erklärt das Instinktprofil
        instincts = self._classify_only(symptom)
        mentor_response = self.mentor.respond(symptom=symptom, instinct_data=instincts.model_dump())

        # 💛 Companion: reflektiert Beziehung
        companion_response = self.companion.respond(previous_messages=[dog_response, mentor_response, coach_response])

        return {
            "dog_response": dog_response,
            "mentor_response": mentor_response,
            "coach_question": coach_response,
            "companion_reflection": companion_response
        }

    def _classify_only(self, text: str) -> InstinctClassification:
        from services.instinct_classifier import classify_instincts
        return classify_instincts(text, self.client)