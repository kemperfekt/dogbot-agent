from src.state.session_state import SessionState
from src.state.session_store import _store, DEFAULT_STATE


class SessionStateStore:
    """
    Speichert und verwaltet den FSM-Zustand für jede Session.
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
