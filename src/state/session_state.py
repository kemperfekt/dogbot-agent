from enum import Enum


# 🧠 Alle gültigen Zustände im Ablauf
class SessionState(str, Enum):
    WAITING_FOR_DOG_QUESTION = "waiting_for_dog_question"  # Hund fragt Mensch nach Symptom
    WAITING_FOR_DOG_RAG = "waiting_for_dog_rag"  # Hund analysiert Symptom mit Hilfe von Weaviate/GPT
    WAITING_FOR_DOG_TRANSITION = "waiting_for_dog_transition"  # Hund fragt, ob Mensch verstehen möchte, warum er sich so verhält
    WAITING_FOR_COACH_INTRO = "waiting_for_coach_intro"  # Coach begrüßt den Menschen und übernimmt
    WAITING_FOR_COACH_GOAL = "waiting_for_coach_goal"  # Coach fragt nach Zielbild des Menschen
    WAITING_FOR_COACH_QUESTION = "waiting_for_coach_question"  # Coach führt Anamnese durch
    WAITING_FOR_COACH_RAG = "waiting_for_coach_rag"  # Coach analysiert Anamnese & Symptom
    WAITING_FOR_COACH_TRAINING_QUESTION = "waiting_for_coach_training_question"  # Coach fragt nach Interesse am Trainingsplan
    WAITING_FOR_COACH_TRAINING = "waiting_for_coach_training"  # Coach liefert konkreten Trainingsplan
    WAITING_FOR_COMPANION_REFLECTION = "waiting_for_companion_reflection"  # Companion reflektiert Training mit Mensch
    WAITING_FOR_RESTART_DECISION = "waiting_for_restart_decision"  # Hund fragt nach weiterem Symptom oder beendet Flow
    ENDED = "ended"  # Konversation wurde explizit beendet

    @classmethod
    def next(cls, current: "SessionState") -> "SessionState":
        return VALID_TRANSITIONS.get(current, cls.ENDED)


# 🔁 Erlaubte Übergänge zwischen den Zuständen
VALID_TRANSITIONS = {
    SessionState.WAITING_FOR_DOG_QUESTION: SessionState.WAITING_FOR_DOG_RAG,
    SessionState.WAITING_FOR_DOG_RAG: SessionState.WAITING_FOR_DOG_TRANSITION,
    SessionState.WAITING_FOR_DOG_TRANSITION: SessionState.WAITING_FOR_COACH_INTRO,
    SessionState.WAITING_FOR_COACH_INTRO: SessionState.WAITING_FOR_COACH_GOAL,
    SessionState.WAITING_FOR_COACH_GOAL: SessionState.WAITING_FOR_COACH_QUESTION,
    SessionState.WAITING_FOR_COACH_QUESTION: SessionState.WAITING_FOR_COACH_RAG,
    SessionState.WAITING_FOR_COACH_RAG: SessionState.WAITING_FOR_COACH_TRAINING_QUESTION,
    SessionState.WAITING_FOR_COACH_TRAINING_QUESTION: SessionState.WAITING_FOR_COACH_TRAINING,
    SessionState.WAITING_FOR_COACH_TRAINING: SessionState.WAITING_FOR_COMPANION_REFLECTION,
    SessionState.WAITING_FOR_COMPANION_REFLECTION: SessionState.WAITING_FOR_RESTART_DECISION,
    SessionState.WAITING_FOR_RESTART_DECISION: SessionState.WAITING_FOR_DOG_QUESTION,
}