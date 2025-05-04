from openai import OpenAI
from src.agents.dog_agent import DogAgent
from src.agents.coach_agent import CoachAgent
from src.agents.companion_agent import CompanionAgent
from src.models.flow_models import FlowIntroResponse, FlowStartRequest, FlowStartResponse, FlowContinueRequest, FlowContinueResponse
from src.models.agent_models import AgentMessage
from src.state.session_store import save_messages
from src.state.session_store import create_session


class FlowOrchestrator:
    def __init__(self):
        self.dog = DogAgent()
        self.coach = CoachAgent()
        self.companion = CompanionAgent()
        self.client = OpenAI()

    def run_intro(self, session_id: str) -> FlowIntroResponse:
        create_session(session_id)
        dog_msg = self.dog.introduce()
        messages = [dog_msg]
        save_messages(session_id, messages)
        return FlowIntroResponse(session_id=session_id, messages=messages)

    def run_start_flow(self, request: FlowStartRequest) -> FlowStartResponse:
        session_id = request.session_id or "sess_" + self._generate_session_id()
        dog_msgs = self.dog.respond(symptom=request.symptom, client=self.client)

        save_messages(session_id, dog_msgs)
        return FlowStartResponse(session_id=session_id, messages=dog_msgs)

    def run_continued_flow(self, session_id: str, user_answer: str) -> FlowContinueResponse:
        messages = []
        # Schritt 1: statische Begrüßung durch Coach
        intro_msg = self.coach.introduce()
        messages.append(intro_msg)
        save_messages(session_id, [intro_msg])

        # Schritt 2: GPT-generierte Diagnose
        diagnosis_msgs = self.coach.respond(session_id=session_id, user_input=user_answer, client=self.client)
        messages.extend(diagnosis_msgs)
        save_messages(session_id, diagnosis_msgs)
        return FlowContinueResponse(messages=messages)

    def _generate_session_id(self) -> str:
        import uuid
        return uuid.uuid4().hex[:8]