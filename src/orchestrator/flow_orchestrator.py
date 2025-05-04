# --- src/orchestrator/flow_orchestrator.py ---

from openai import OpenAI
from src.agents.dog_agent import DogAgent
from src.agents.coach_agent import CoachAgent
from src.agents.companion_agent import CompanionAgent
from src.models.flow_models import FlowIntroResponse, FlowStartRequest, FlowStartResponse, FlowContinueRequest, FlowContinueResponse
from src.models.agent_models import AgentMessage
from src.state.session_store import save_messages


class FlowOrchestrator:
    def __init__(self):
        self.dog = DogAgent()
        self.coach = CoachAgent()
        self.companion = CompanionAgent()
        self.client = OpenAI()

    def run_intro(self, session_id: str) -> FlowIntroResponse:
        dog_msg = self.dog.introduce()
        coach_msg = self.coach.introduce()
        companion_msg = self.companion.introduce()

        messages = [dog_msg, coach_msg, companion_msg]
        save_messages(session_id, messages)
        return FlowIntroResponse(session_id=session_id, messages=messages)

    def run_start_flow(self, request: FlowStartRequest) -> FlowStartResponse:
        session_id = request.session_id or "sess_" + self._generate_session_id()
        dog_msgs = self.dog.respond(symptom=request.symptom)

        save_messages(session_id, dog_msgs)
        return FlowStartResponse(session_id=session_id, messages=dog_msgs)

    def run_continued_flow(self, session_id: str, user_answer: str) -> FlowContinueResponse:
        coach_msgs = self.coach.respond(session_id=session_id, user_input=user_answer, client=self.client)
        save_messages(session_id, coach_msgs)
        return FlowContinueResponse(messages=coach_msgs)

    def _generate_session_id(self) -> str:
        import uuid
        return uuid.uuid4().hex[:8]