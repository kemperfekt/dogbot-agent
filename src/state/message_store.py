from src.models.agent_models import AgentMessage

# In-Memory-Store für Nachrichtenverlauf
_store: dict[str, list[dict]] = {}


def create_session(session_id: str):
    if session_id not in _store:
        _store[session_id] = []


def append_message(session_id: str, message: AgentMessage | dict):
    if session_id not in _store:
        create_session(session_id)
    if isinstance(message, AgentMessage):
        message = message.model_dump()
    _store[session_id].append(message)


def save_messages(session_id: str, messages: list[AgentMessage]):
    for msg in messages:
        append_message(session_id, msg)


def get_history(session_id: str) -> list[AgentMessage]:
    raw = _store.get(session_id, [])
    return [AgentMessage(**m) for m in raw if isinstance(m, dict)]