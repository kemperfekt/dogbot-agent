# src/routers/flow_router.py

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from src.orchestrator.flow_orchestrator import FlowOrchestrator

router = APIRouter()
orchestrator = FlowOrchestrator()

# Eingabemodell für den ersten Schritt
class FlowStartRequest(BaseModel):
    symptom: str

# Eingabemodell für Folgefrage
class FlowContinueRequest(BaseModel):
    session_id: str
    answer: str

# Antwortmodell für alle Nachrichten
class AgentMessage(BaseModel):
    sender: str
    text: str

class FlowStartResponse(BaseModel):
    session_id: str
    messages: List[AgentMessage]

@router.post("/flow_start", response_model=FlowStartResponse)
def start_flow(request: FlowStartRequest):
    result = orchestrator.run_initial_flow(request.symptom)
    return FlowStartResponse(
        session_id=result["session_id"],
        messages=[AgentMessage(**msg) for msg in result["messages"]]
    )

@router.post("/flow_continue", response_model=FlowStartResponse)
def continue_flow(request: FlowContinueRequest):
    result = orchestrator.run_continued_flow(
        session_id=request.session_id,
        user_answer=request.answer
    )
    return FlowStartResponse(
        session_id=result["session_id"],
        messages=[AgentMessage(**msg) for msg in result["messages"]]
    )
