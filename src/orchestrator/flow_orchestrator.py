# src/orchestrator/flow_orchestrator.py

import os
from openai import OpenAI

from src.agents.dog_agent import DogAgent
from src.agents.mentor_agent import MentorAgent
from src.agents.coach_agent import CoachAgent
from src.agents.companion_agent import CompanionAgent
from src.agents.trainer_agent import TrainerAgent

from src.services.instinct_classifier import InstinctClassification
from src.services.retrieval import get_symptom_info

from src.state.session_store import (
    create_session,
    append_message,
    get_last_message,
    session_exists
)


class FlowOrchestrator:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAIAPIKEY"))
        self.dog = DogAgent()
        self.mentor = MentorAgent()
        self.coach = CoachAgent()
        self.companion = CompanionAgent()
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
        if not session_exists(session_id):
            raise ValueError("Session-ID ist ungültig.")

        append_message(session_id, "user", user_answer)

        # 🛠 SymptomInfo-Objekt laden
        symptom_info = get_symptom_info(user_answer)

        # 🧠 Coach analysiert anhand der Weaviate-Daten + GPT
        coach_reply = self.coach.respond(session_id, symptom_info, self.client)

        messages = []

        if isinstance(coach_reply, dict):
            if "question" in coach_reply:
                question = coach_reply["question"]
                messages.append({
                "sender": "coach",
                "text": question 
                })
            elif "diagnosis" in coach_reply:
                diagnosis = coach_reply["diagnosis"]
                instinkt = diagnosis.get("instinkt", "unbekannt")
                messages.append({
                    "sender": "coach",
                    "text": f"Danke für deine Antworten. Ich vermute, dass der Instinkt '{instinkt}' eine zentrale Rolle spielt. Ich gebe weiter an den Mentor."
                })

                # Mentor erklärt Diagnose
                mentor_response = self.mentor.respond(
                    symptom=user_answer,
                    instinct_data=diagnosis
                )
                messages.append({
                    "sender": "mentor",
                    "text": mentor_response
                })

                # Trainer leitet daraus Hilfe ab
                trainer_response = self.trainer.respond(symptom_info)
                messages.append({
                    "sender": "trainer",
                    "text": trainer_response
                })

        else:
            # fallback für reine Textantwort
            messages.append({
                "sender": "coach",
                "text": coach_reply
            })

        for msg in messages:
            append_message(session_id, msg["sender"], msg["text"])

        return {
            "session_id": session_id,
            "messages": messages
        }
