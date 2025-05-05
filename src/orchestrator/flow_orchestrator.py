from src.services.logging import log_flow
from openai import OpenAI
from src.agents.dog_agent import DogAgent
from src.agents.coach_agent import CoachAgent
from src.agents.companion_agent import CompanionAgent
from src.models.flow_models import FlowIntroResponse, FlowStartRequest, FlowStartResponse, FlowContinueRequest, FlowContinueResponse
from src.models.agent_models import AgentMessage
from src.state.session_store import save_messages
from src.state.session_store import create_session
from src.state.session_state import SessionState
from src.state.state_store import SessionStateStore


class FlowOrchestrator:
    def __init__(self):
        self.dog = DogAgent()
        self.coach = CoachAgent()
        self.companion = CompanionAgent()
        self.client = OpenAI()
        self.state_store = SessionStateStore()

    def run_intro(self, session_id: str) -> FlowIntroResponse:
        create_session(session_id)
        dog_msg = self.dog.introduce()
        messages = [dog_msg]
        save_messages(session_id, messages)
        return FlowIntroResponse(session_id=session_id, messages=messages)

    def run_start_flow(self, request: FlowStartRequest) -> FlowStartResponse:
        session_id = request.session_id or "sess_" + self._generate_session_id()
        # Nur Frage nach Symptom – Begrüßung erfolgte bereits in run_intro()
        messages = [self.dog.ask_about_symptom()]

        save_messages(session_id, messages)
        self.state_store.advance(session_id) 

        return FlowStartResponse(session_id=session_id, messages=messages)

    def run_continued_flow(self, session_id: str, user_answer: str) -> FlowContinueResponse:
        state = self.state_store.get(session_id)
        log_flow(f"User input: {user_answer}", session_id)
        log_flow(f"Processing state: {state}", session_id)

        if state == SessionState.WAITING_FOR_DOG_QUESTION:
            # Nur erneut ausführen, wenn vorheriger Zustand RESTART_DECISION war
            previous = self.state_store.get_previous(session_id)
            if previous == SessionState.WAITING_FOR_RESTART_DECISION:
                messages = self.dog.get_question_messages()
                self.state_store.advance(session_id)
            else:
                messages = []  # keine Wiederholung bei falschem Einstieg

        elif state == SessionState.WAITING_FOR_DOG_RAG:
            from src.state.session_store import was_processed, mark_processed

            if was_processed(session_id, state):
                # Zweiter Aufruf → jetzt in Übergabefrage übergehen
                self.state_store.set(session_id, SessionState.WAITING_FOR_COACH_INTRO)
                messages = []
            else:
                # Erster Aufruf → GPT-Antwort erzeugen und als verarbeitet markieren
                messages = self.dog.get_response_messages(user_input=user_answer, client=self.client)
                mark_processed(session_id, state)

        elif state == SessionState.WAITING_FOR_DOG_TRANSITION:
            # Hund fragt, ob Mensch verstehen möchte, warum er sich so verhält
            messages = self.dog.get_transition_prompt()
            self.state_store.advance(session_id)

        elif state == SessionState.WAITING_FOR_COACH_INTRO:
            # Coach begrüßt den Menschen und übernimmt die Gesprächsführung
            messages = self.coach.get_intro_messages()
            self.state_store.advance(session_id)

        elif state == SessionState.WAITING_FOR_COACH_GOAL:
            # Coach fragt nach dem gewünschten Zielbild
            messages = self.coach.get_goal_messages()
            self.state_store.advance(session_id)

        elif state == SessionState.WAITING_FOR_COACH_QUESTION:
            # Coach führt eine Anamnese durch (Verhalten, Umfeld, etc.)
            messages = self.coach.get_anamnesis_messages()
            self.state_store.advance(session_id)

        elif state == SessionState.WAITING_FOR_COACH_RAG:
            # Coach erstellt eine Hypothese basierend auf Wissen (RAG)
            messages = self.coach.get_diagnosis_messages(session_id=session_id, user_input=user_answer, client=self.client)
            self.state_store.advance(session_id)

        elif state == SessionState.WAITING_FOR_COACH_TRAINING_QUESTION:
            # Coach fragt, ob Interesse an einem Trainingsplan besteht
            messages = self.coach.get_training_prompt_messages(user_input=user_answer)
            self.state_store.advance(session_id)

        elif state == SessionState.WAITING_FOR_COACH_TRAINING:
            # Coach liefert den individuellen Trainingsplan
            messages = self.coach.get_training_messages(session_id=session_id, user_input=user_answer, client=self.client)
            self.state_store.advance(session_id)

        elif state == SessionState.WAITING_FOR_COMPANION_REFLECTION:
            # Companion reflektiert gemeinsam mit dem Menschen
            messages = self.companion.get_reflection_messages()
            self.state_store.advance(session_id)

        elif state == SessionState.WAITING_FOR_RESTART_DECISION:
            # Hund fragt, ob ein weiteres Symptom behandelt werden soll
            messages = self.dog.get_restart_prompt()
            self.state_store.advance(session_id)

        elif state == SessionState.ENDED:
            # Gespräch wurde beendet – keine weiteren Nachrichten
            messages = []

        save_messages(session_id, messages)
        return FlowContinueResponse(messages=messages)

    def _generate_session_id(self) -> str:
        import uuid
        return uuid.uuid4().hex[:8]

    def _is_positive(self, answer: str) -> bool:
        positive_inputs = ["ja", "yes", "klar", "okay", "mach", "bitte", "gerne", "jup", "yep", "yo", "ok"]
        return answer.strip().lower() in positive_inputs