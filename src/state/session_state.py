from enum import Enum


# 🧠 Alle gültigen Zustände im Ablauf
class SessionState(str, Enum):
    WAITING_FOR_SYMPTOM = "waiting_for_symptom"
    DOG_RESPONDED = "dog_responded"
    WAITING_FOR_COACH_PERMISSION = "waiting_for_coach_permission"
    COACH_INTRODUCED = "coach_introduced"
    COACH_DIAGNOSED = "coach_diagnosed"
    WAITING_FOR_TRAINING_CONSENT = "waiting_for_training_consent"
    COACH_DELIVERED_TRAINING = "coach_delivered_training"
    COACH_FLOW_COMPLETE = "coach_flow_complete"


# 🔁 Übergänge zwischen den Zuständen (nur diese sind erlaubt)
VALID_TRANSITIONS = {
    SessionState.WAITING_FOR_SYMPTOM: SessionState.DOG_RESPONDED,
    SessionState.DOG_RESPONDED: SessionState.WAITING_FOR_COACH_PERMISSION,
    SessionState.WAITING_FOR_COACH_PERMISSION: SessionState.COACH_INTRODUCED,
    SessionState.COACH_INTRODUCED: SessionState.COACH_DIAGNOSED,
    SessionState.COACH_DIAGNOSED: SessionState.WAITING_FOR_TRAINING_CONSENT,
    SessionState.WAITING_FOR_TRAINING_CONSENT: SessionState.COACH_DELIVERED_TRAINING,
    SessionState.COACH_DELIVERED_TRAINING: SessionState.COACH_FLOW_COMPLETE,
    SessionState.COACH_FLOW_COMPLETE: SessionState.WAITING_FOR_SYMPTOM,  # optionaler Neustart
}