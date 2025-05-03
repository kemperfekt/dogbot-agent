from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from src.orchestrator.flow_orchestrator import FlowOrchestrator
from src.models.agent_models import AgentMessage

router = APIRouter()
orchestrator = FlowOrchestrator()

class FlowStartRequest(BaseModel):
    symptom: str

class FlowStartResponse(BaseModel):
    session_id: str
    messages: List[AgentMessage]

class FlowContinueRequest(BaseModel):
    session_id: str
    answer: str

class FlowContinueResponse(BaseModel):
    messages: List[AgentMessage]

@router.post("/flow_start", response_model=FlowStartResponse)
def start_flow(request: FlowStartRequest) -> FlowStartResponse:
    result = orchestrator.run_initial_flow(request.symptom)
    return FlowStartResponse(
        session_id=result["session_id"],
        messages=result["messages"]
    )

@router.post("/flow_continue", response_model=FlowContinueResponse)
def continue_flow(request: FlowContinueRequest) -> FlowContinueResponse:
    result = orchestrator.run_continued_flow(
        session_id=request.session_id,
        user_answer=request.answer
    )
    return FlowContinueResponse(messages=result["messages"])