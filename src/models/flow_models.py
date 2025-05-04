from pydantic import BaseModel
from typing import List
from src.models.agent_models import AgentMessage


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