from fastapi import APIRouter
from src.orchestrator.flow_orchestrator import FlowOrchestrator
from src.models.flow_models import (
    FlowIntroResponse,
    FlowStartRequest,
    FlowStartResponse,
    FlowContinueRequest,
    FlowContinueResponse,
)
from src.models.agent_models import AgentMessage

router = APIRouter()
orchestrator = FlowOrchestrator()


def ensure_dict_list(messages: list) -> list[dict]:
    result = []
    for m in messages:
        if isinstance(m, AgentMessage):
            result.append(m.model_dump())
        elif isinstance(m, dict):
            result.append(m)
        else:
            print("❌ Unerwartetes Nachrichtenformat:", type(m), m)
            raise ValueError("Unerwartetes Nachrichtenformat in Nachrichtenliste")
    return result


@router.post("/flow_intro", response_model=FlowIntroResponse)
def flow_intro():
    result = orchestrator.run_intro_only()
    messages = ensure_dict_list(result["messages"])
    return FlowIntroResponse(session_id=result["session_id"], messages=messages)


@router.post("/flow_start", response_model=FlowStartResponse)
def start_flow(request: FlowStartRequest):
    result = orchestrator.run_initial_flow(request.symptom, request.session_id)
    messages = ensure_dict_list(result["messages"])
    return FlowStartResponse(session_id=result["session_id"], messages=messages)


@router.post("/flow_continue", response_model=FlowContinueResponse)
def continue_flow(request: FlowContinueRequest):
    result = orchestrator.run_continued_flow(request.session_id, request.answer)
    messages = ensure_dict_list(result["messages"])
    return FlowContinueResponse(messages=messages)