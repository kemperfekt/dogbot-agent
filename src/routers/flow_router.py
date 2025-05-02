from fastapi import APIRouter
from pydantic import BaseModel
from src.orchestrator.flow_orchestrator import FlowOrchestrator
from typing import List

router = APIRouter()
orchestrator = FlowOrchestrator()

# Eingabe-Modell für die Anfrage
class FlowStartRequest(BaseModel):
    symptom: str

# Modell für jede Nachricht, die zurückgegeben wird
class AgentMessage(BaseModel):
    sender: str
    text: str

# Antwort-Modell mit einer Liste von Nachrichten
class FlowStartResponse(BaseModel):
    messages: List[AgentMessage]

@router.post("/flow_start", response_model=FlowStartResponse)
def start_flow(request: FlowStartRequest):
    result = orchestrator.run_initial_flow(request.symptom)
    
    # Rückgabe der Nachrichten aus den Agenten
    return FlowStartResponse(
        messages=[
            {"sender": "dog", "text": result["dog_response"]},
            {"sender": "coach", "text": result["coach_question"]},
            {"sender": "mentor", "text": result["mentor_response"]},
            {"sender": "companion", "text": result["companion_reflection"]}
        ]
    )
