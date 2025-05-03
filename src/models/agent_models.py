from pydantic import BaseModel
from typing import Literal, Optional
from src.models.symptom_models import Diagnose

class AgentMessage(BaseModel):
    sender: Literal["dog", "coach", "user"]
    text: Optional[str] = None
    question: Optional[str] = None
    diagnosis: Optional[Diagnose] = None