

LOGGING_ENABLED = True  # Globaler Schalter zur Aktivierung/Deaktivierung

def log_flow(message: str, session_id: str | None = None):
    """Einfacher Logging-Hook für den Flow-Orchestrator."""
    if LOGGING_ENABLED:
        prefix = f"[Flow][{session_id}]" if session_id else "[Flow]"
        print(f"{prefix} {message}")