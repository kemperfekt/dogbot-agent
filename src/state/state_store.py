from src.state.session_state import SessionState

_store: dict[str, dict[str, str]] = {}

DEFAULT_STATE = SessionState.WAITING_FOR_DOG_QUESTION


class SessionStateStore:
    """
    Speichert und verwaltet den FSM-Zustand für jede Session.
    """
    def get(self, session_id: str) -> SessionState:
        raw = _store.get(session_id, {}).get("state", DEFAULT_STATE.value)
        return SessionState(raw)

    def set_state(self, session_id: str, new_state: SessionState):
        if session_id not in _store:
            _store[session_id] = {}
        _store[session_id]["state"] = new_state.value

    def advance(self, session_id: str):
        if session_id not in _store:_store[session_id] = {}
        current = self.get(session_id)
        next_state = SessionState.next(current)
        _store[session_id]["state"] = next_state.value

    def end(self, session_id: str):
        _store[session_id]["state"] = SessionState.ENDED.value
