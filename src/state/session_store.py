import uuid
from typing import Dict, List
from src.orchestrator.states import DialogState
from src.models.agent_models import AgentMessage

SessionData = Dict[str, Dict[str, any]]
_store: Dict[str, Dict] = {}

def create_session() -> str:
    session_id = str(uuid.uuid4())
    _store[session_id] = {
        "history": [],
        "state": DialogState.START,
        "diagnose_progress": {
            "asked_instincts": [],
            "symptom": None
        }
    }
    return session_id

def append_message(session_id: str, message: AgentMessage) -> None:
    if session_id in _store:
        _store[session_id]["history"].append(message.model_dump())
    else:
        raise KeyError(f"Session {session_id} existiert nicht.")

def get_history(session_id: str) -> List[Dict[str, str]]:
    return _store.get(session_id, {}).get("history", [])

def session_exists(session_id: str) -> bool:
    return session_id in _store

def get_last_message(session_id: str) -> dict | None:
    history = _store.get(session_id, {}).get("history", [])
    return history[-1] if history else None

def get_state(session_id: str) -> DialogState:
    return _store.get(session_id, {}).get("state", DialogState.START)

def set_state(session_id: str, state: DialogState) -> None:
    if session_id in _store:
        _store[session_id]["state"] = state

def get_diagnose_progress(session_id: str) -> Dict:
    return _store[session_id].get("diagnose_progress", {"asked_instincts": [], "symptom": None})

def set_diagnose_progress(session_id: str, progress: Dict) -> None:
    if session_id in _store:
        _store[session_id]["diagnose_progress"] = progress
