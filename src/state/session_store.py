import uuid
from typing import Any
from src.models.agent_models import AgentMessage
from src.state.session_state import SessionState

# In-Memory-Store für Sessions (später evtl. Redis oder DB)
_store: dict[str, dict[str, Any]] = {}

# Standardzustand für neue Sessions
DEFAULT_STATE = SessionState.WAITING_FOR_SYMPTOM


def create_session() -> str:
    """
    Erstellt eine neue Session mit leerem Verlauf und initialem FSM-Zustand.
    """
    session_id = str(uuid.uuid4())
    _store[session_id] = {
        "history": [],
        "state": DEFAULT_STATE.value
    }
    return session_id


def session_exists(session_id: str) -> bool:
    return session_id in _store


def append_message(session_id: str, message: AgentMessage | dict):
    """
    Hängt eine Nachricht an die Session-History an (automatisch Pydantic-serialisiert).
    """
    if isinstance(message, AgentMessage):
        message = message.model_dump()
    _store[session_id]["history"].append(message)


def get_history(session_id: str) -> list[AgentMessage]:
    """
    Gibt alle Nachrichten der Session als AgentMessage-Objekte zurück.
    """
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


# ───── FSM-spezifische Erweiterungen ─────

def get_state(session_id: str) -> SessionState:
    """
    Gibt den aktuellen Zustand der Session zurück (Enum).
    """
    raw = _store.get(session_id, {}).get("state", DEFAULT_STATE.value)
    return SessionState(raw)


def set_state(session_id: str, new_state: SessionState):
    """
    Aktualisiert den FSM-Zustand der Session.
    """
    if session_id in _store:
        _store[session_id]["state"] = new_state.value