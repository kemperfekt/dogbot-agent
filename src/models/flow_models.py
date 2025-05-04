# --- src/models/flow_models.py ---

from pydantic import BaseModel
from typing import List
from src.models.agent_models import AgentMessage


class FlowIntroResponse(BaseModel):
    session_id: str
    messages: List[AgentMessage]


class FlowStartRequest(BaseModel):
    symptom: str
    session_id: str | None = None  # Optional: Session aus flow_intro wiederverwenden


class FlowStartResponse(BaseModel):
    session_id: str
    messages: List[AgentMessage]


class FlowContinueRequest(BaseModel):
    session_id: str
    answer: str


class FlowContinueResponse(BaseModel):
    messages: List[AgentMessage]



class InstinktEintrag(BaseModel):
    instinkt: str
    beschreibung: str
