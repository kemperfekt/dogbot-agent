from fastapi import APIRouter
from src.orchestrator.flow_orchestrator import FlowOrchestrator
from src.models.flow_models import FlowStartRequest, FlowStartResponse, FlowContinueRequest, FlowContinueResponse
from src.models.agent_models import AgentMessage

router = APIRouter()
orchestrator = FlowOrchestrator()


@router.post("/flow_start", response_model=FlowStartResponse)
def start_flow(request: FlowStartRequest):
    result = orchestrator.run_initial_flow(request.symptom)

    # Stelle sicher, dass alle Nachrichten einzelne AgentMessage-Instanzen oder dicts sind
    messages = []
    for m in result["messages"]:
        if isinstance(m, AgentMessage):
            messages.append(m.model_dump())
        elif isinstance(m, dict):
            messages.append(m)
        else:
            raise ValueError("Unerwartetes Nachrichtenformat in flow_start")

    return FlowStartResponse(session_id=result["session_id"], messages=messages)


@router.post("/flow_continue", response_model=FlowContinueResponse)
def continue_flow(request: FlowContinueRequest):
    result = orchestrator.run_continued_flow(request.session_id, request.answer)

    messages = []
    for m in result["messages"]:
        if isinstance(m, AgentMessage):
            messages.append(m.model_dump())
        elif isinstance(m, dict):
            messages.append(m)
        else:
            raise ValueError("Unerwartetes Nachrichtenformat in flow_continue")

    return FlowContinueResponse(messages=messages)