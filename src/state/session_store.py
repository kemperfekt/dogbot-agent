import uuid
from typing import Any
from src.models.agent_models import AgentMessage
from src.state.session_state import SessionState

# In-Memory-Store für Sessions (später evtl. Redis oder DB)
_store: dict[str, dict[str, Any]] = {}

# Standardzustand für neue Sessions
DEFAULT_STATE = SessionState.WAITING_FOR_DOG_QUESTION


def create_session(session_id: str):
    """
    Erstellt eine Session mit gegebener ID, falls sie noch nicht existiert.
    """
    if session_id not in _store:
        _store[session_id] = {
            "history": [],
            "state": DEFAULT_STATE.value
        }


def session_exists(session_id: str) -> bool:
    return session_id in _store


def append_message(session_id: str, message: AgentMessage | dict):
    """
    Hängt eine Nachricht an die Session-History an (automatisch Pydantic-serialisiert).
    """
    if isinstance(message, AgentMessage):
        message = message.model_dump()
    _store[session_id]["history"].append(message)


def save_messages(session_id: str, messages: list[AgentMessage]):
    """
    Speichert mehrere Nachrichten in einer Session-History.
    """
    for msg in messages:
        append_message(session_id, msg)


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


def was_processed(session_id: str, state: SessionState) -> bool:
    session = _store.get(session_id, {})
    result = session.get("processed", {}).get(state.value, False)
    print(f"[DEBUG] was_processed({session_id}, {state}) -> {result}")
    return result

def mark_processed(session_id: str, state: SessionState):
    print(f"[DEBUG] mark_processed({session_id}, {state})")
    if session_id not in _store:
        return
    if "processed" not in _store[session_id]:
        _store[session_id]["processed"] = {}
    _store[session_id]["processed"][state.value] = True
    # Keine separate Persistierung nötig – _store ist ein globales, veränderbares Dict


# ───── SessionStateStore-Klasse ─────
class SessionStateStore:
    """
    Einfache Speicherklasse für den FSM-Zustand pro Session.
    """
    def get(self, session_id: str) -> SessionState:
        raw = _store.get(session_id, {}).get("state", DEFAULT_STATE.value)
        return SessionState(raw)

    def advance(self, session_id: str):
        current = self.get(session_id)
        next_state = SessionState.next(current)
        _store[session_id]["state"] = next_state.value

    def end(self, session_id: str):
        _store[session_id]["state"] = SessionState.ENDED.value
