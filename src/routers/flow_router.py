# routers/flow_router.py

from fastapi import APIRouter
from pydantic import BaseModel
from src.orchestrator.flow_orchestrator import FlowOrchestrator

router = APIRouter()
orchestrator = FlowOrchestrator()

class FlowStartRequest(BaseModel):
    symptom: str

class FlowStartResponse(BaseModel):
    dog_response: str
    mentor_response: str
    coach_question: str
    companion_reflection: str

@router.post("/flow_start", response_model=FlowStartResponse)
def start_flow(request: FlowStartRequest):
    result = orchestrator.run_initial_flow(request.symptom)
    return FlowStartResponse(**result)