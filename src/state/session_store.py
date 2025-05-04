import uuid
from typing import Any
from src.models.agent_models import AgentMessage

# In-Memory-Store für Sessions (kann später durch Redis etc. ersetzt werden)
_store: dict[str, dict[str, Any]] = {}


def create_session() -> str:
    session_id = str(uuid.uuid4())
    _store[session_id] = {
        "history": []
    }
    return session_id


def session_exists(session_id: str) -> bool:
    return session_id in _store


def append_message(session_id: str, message: AgentMessage | dict):
    if isinstance(message, AgentMessage):
        message = message.model_dump()
    _store[session_id]["history"].append(message)


def get_history(session_id: str) -> list[AgentMessage]:
    raw_history = _store.get(session_id, {}).get("history", [])
    messages = []
    for m in raw_history:
        if isinstance(m, AgentMessage):
            messages.append(m)
        elif isinstance(m, dict):
            try:
                messages.append(AgentMessage(**m))
            except Exception:
                continue
    return messages