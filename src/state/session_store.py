# src/state/session_store.py

import uuid
from typing import Dict, List

# Datenstruktur für Nachrichten einer Session
SessionData = Dict[str, List[Dict[str, str]]]

# Einfacher in-memory-Store
_store: SessionData = {}

def create_session() -> str:
    """Erzeugt eine neue Session-ID und legt leere Historie an."""
    session_id = str(uuid.uuid4())
    _store[session_id] = []
    return session_id

def append_message(session_id: str, sender: str, text: str) -> None:
    """Fügt eine Nachricht zur Session-Historie hinzu."""
    if session_id in _store:
        _store[session_id].append({"sender": sender, "text": text})
    else:
        raise KeyError(f"Session {session_id} existiert nicht.")

def get_history(session_id: str) -> List[Dict[str, str]]:
    """Liefert die komplette Historie einer Session."""
    return _store.get(session_id, [])

def session_exists(session_id: str) -> bool:
    """Prüft, ob eine Session existiert."""
    return session_id in _store
