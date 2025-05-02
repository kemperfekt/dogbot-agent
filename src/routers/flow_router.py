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
    messages: List[AgentMessage]

@router.post("/flow_start", response_model=FlowStartResponse)
def start_flow(request: FlowStartRequest):
    result = orchestrator.run_initial_flow(request.symptom)
    return FlowStartResponse(
        messages=[
            AgentMessage(sender="dog", text=result["dog_response"]),
            AgentMessage(sender="mentor", text=result["mentor_response"]),
            AgentMessage(sender="coach", text=result["coach_question"]),
            AgentMessage(sender="companion", text=result["companion_reflection"])
        ]
    )

@router.post("/flow_continue", response_model=FlowStartResponse)
def continue_flow(request: FlowContinueRequest):
    # Platzhalterantwort bis Session-Handling und Verlauf implementiert sind
    return FlowStartResponse(
        messages=[
            AgentMessage(sender="mentor", text="Danke für deine Antwort. Ich erkläre dir noch etwas Wichtiges dazu."),
            AgentMessage(sender="coach", text="Hier ist eine passende Übung für euch zwei.")
        ]
    )
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
    messages: List[AgentMessage]

@router.post("/flow_start", response_model=FlowStartResponse)
def start_flow(request: FlowStartRequest):
    result = orchestrator.run_initial_flow(request.symptom)
    return FlowStartResponse(
        messages=[
            AgentMessage(sender="dog", text=result["dog_response"]),
            AgentMessage(sender="mentor", text=result["mentor_response"]),
            AgentMessage(sender="coach", text=result["coach_question"]),
            AgentMessage(sender="companion", text=result["companion_reflection"])
        ]
    )

@router.post("/flow_continue", response_model=FlowStartResponse)
def continue_flow(request: FlowContinueRequest):
    # Platzhalterantwort bis Session-Handling und Verlauf implementiert sind
    return FlowStartResponse(
        messages=[
            AgentMessage(sender="mentor", text="Danke für deine Antwort. Ich erkläre dir noch etwas Wichtiges dazu."),
            AgentMessage(sender="coach", text="Hier ist eine passende Übung für euch zwei.")
        ]
    )
