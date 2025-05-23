from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from src.models.flow_models import AgentMessage
from src.flow.flow_orchestrator import handle_message, init_orchestrator
from src.state.session_state import SessionStore

router = APIRouter()

# Globale Session-Store initialisieren
session_store = SessionStore()
init_orchestrator(session_store)


class FlowIntroResponse(BaseModel):
    session_id: str
    messages: List[AgentMessage]


class FlowStartRequest(BaseModel):
    symptom: str
    session_id: Optional[str] = None


class FlowContinueRequest(BaseModel):
    answer: str
    session_id: str


class FlowResponse(BaseModel):
    session_id: str
    messages: List[AgentMessage]
    done: Optional[bool] = False


@router.post("/flow_intro", response_model=FlowIntroResponse)
async def flow_intro():
    """Startet eine neue Session und gibt Begrüßung zurück"""
    # Session über SessionStore erstellen (nicht direkt)
    session = session_store.create_session()
    
    # ✅ SAUBERE ARCHITEKTUR: Greeting über flow_orchestrator vom DogAgent
    try:
        messages = await handle_message(session.session_id, "")
        return FlowIntroResponse(session_id=session.session_id, messages=messages)
    except Exception as e:
        print(f"❌ Fehler bei flow_intro: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/flow_start", response_model=FlowResponse)
async def flow_start(request: FlowStartRequest):
    """
    ✅ KORRIGIERT: Nutzt jetzt flow_orchestrator statt direkten DogAgent-Aufruf
    """
    session_id = request.session_id
    if not session_id:
        # Neue Session erstellen falls keine ID gegeben
        session = session_store.create_session()
        session_id = session.session_id
    
    try:
        # ✅ RICHTIG: Über flow_orchestrator statt direktem DogAgent
        messages = await handle_message(session_id, request.symptom)
        return FlowResponse(session_id=session_id, messages=messages)
    except Exception as e:
        print(f"❌ Fehler in flow_start: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/flow_continue", response_model=FlowResponse)
async def flow_continue(request: FlowContinueRequest):
    """
    ✅ KORRIGIERT: Nutzt jetzt flow_orchestrator statt direkten DogAgent-Aufruf
    """
    # Session-Existenz prüfen
    session = session_store.sessions.get(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    print(f"📨 Eingegangene Antwort von Mensch: {request.answer}")
    print(f"📨 Session-ID: {request.session_id}")

    try:
        # ✅ RICHTIG: Über flow_orchestrator statt direktem DogAgent
        messages = await handle_message(request.session_id, request.answer)

        print("✅ Flow Orchestrator hat folgende Nachrichten zurückgegeben:")
        for m in messages:
            print(f"- {m.sender}: {m.text}")

        return FlowResponse(session_id=request.session_id, messages=messages, done=False)
    except Exception as e:
        print(f"❌ Fehler beim Verarbeiten der Folgeantwort: {e}")
        raise HTTPException(status_code=500, detail=str(e))