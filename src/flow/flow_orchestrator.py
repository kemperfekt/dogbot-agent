# src/orchestrator/flow_orchestrator.py

from typing import List, Dict, Any, Callable, Awaitable
from src.models.flow_models import AgentMessage, FlowStep
from src.state.session_state import SessionState, SessionStore
from src.agents.dog_agent import DogAgent
from src.agents.companion_agent import CompanionAgent

# Handler-Typ-Definition für bessere Lesbarkeit
StepHandler = Callable[[SessionState, str], Awaitable[List[AgentMessage]]]

class FlowOrchestrator:
    """Orchestriert den Konversationsfluss über Agents"""
    
    def __init__(self, session_store_instance):
        self.session_store = session_store_instance
        self.dog_agent = DogAgent()
        self.companion_agent = CompanionAgent()
        
        # Tracking für Feedback-Antworten
        self.feedback_responses = {}
        
        # Mapping von Schritten zu Handlern für bessere Struktur
        self.step_handlers: Dict[FlowStep, StepHandler] = {
            FlowStep.GREETING: self._handle_greeting,
            FlowStep.WAIT_FOR_SYMPTOM: self._handle_symptom_input,
            FlowStep.WAIT_FOR_CONFIRMATION: self._handle_confirmation,
            FlowStep.WAIT_FOR_CONTEXT: self._handle_context_input,
            FlowStep.ASK_FOR_EXERCISE: self._handle_exercise_request,
            FlowStep.END_OR_RESTART: self._handle_end_or_restart,
            FlowStep.FEEDBACK_Q1: self._handle_feedback_q1,
            FlowStep.FEEDBACK_Q2: self._handle_feedback_q2,
            FlowStep.FEEDBACK_Q3: self._handle_feedback_q3,
            FlowStep.FEEDBACK_Q4: self._handle_feedback_q4,
            FlowStep.FEEDBACK_Q5: self._handle_feedback_q5,
        }
    
    async def handle_message(self, session_id: str, user_input: str) -> List[AgentMessage]:
        """
        Verarbeitet eine Benutzernachricht über die Agent-Architektur.
        
        Args:
            session_id: ID der Session
            user_input: Nachricht des Benutzers
            
        Returns:
            Liste von Antwort-Nachrichten
        """
        # Session holen
        state = self.session_store.get_or_create(session_id)
        
        # Benutzernachricht zur Session hinzufügen, wenn nicht leer
        if user_input:
            state.messages.append(AgentMessage(sender="user", text=user_input))
        
        user_input = user_input.strip().lower() if user_input else ""

        # Spezialkommandos für Neustart
        if user_input in ["neu", "restart", "von vorne"]:
            return await self._handle_restart(state)

        # Step-basierten Handler auswählen und ausführen
        handler = self.step_handlers.get(state.current_step)
        if handler:
            try:
                messages = await handler(state, user_input)
            except Exception as e:
                print(f"❌ Fehler im Handler für {state.current_step}: {e}")
                import traceback
                traceback.print_exc()
                
                # Support über CompanionAgent
                messages = await self.companion_agent.provide_support("error occurred")
                state.current_step = FlowStep.GREETING
        else:
            # Fallback über CompanionAgent
            messages = await self.companion_agent.provide_support("confused")
            state.current_step = FlowStep.GREETING

        # Nachrichten zur Session hinzufügen
        state.messages.extend(messages)
        return messages
    
    async def _handle_restart(self, state: SessionState) -> List[AgentMessage]:
        """Behandelt einen Neustart-Request"""
        state.current_step = FlowStep.GREETING
        state.active_symptom = ""
        # Reset feedback tracking
        if state.session_id in self.feedback_responses:
            del self.feedback_responses[state.session_id]
        
        return [AgentMessage(
            sender=self.dog_agent.role,
            text="Okay, wir starten neu. Was möchtest du mir erzählen?"
        )]
    
    async def _handle_greeting(self, state: SessionState, user_input: str) -> List[AgentMessage]:
        """Behandelt den Begrüßungsschritt"""
        state.current_step = FlowStep.WAIT_FOR_SYMPTOM
        return [AgentMessage(
            sender=self.dog_agent.role,
            text="Hallo! Schön, dass Du da bist. Ich erkläre Dir Hundeverhalten aus der Hundeperspektive. Bitte beschreibe ein Verhalten oder eine Situation!"
        )]
    
    async def _handle_symptom_input(self, state: SessionState, user_input: str) -> List[AgentMessage]:
        """Behandelt die Eingabe eines Symptoms über DogAgent"""
        
        # NEUE ARCHITEKTUR: Content-Moderation über CompanionAgent
        moderation_result = await self.companion_agent.moderate_content(user_input)
        if not moderation_result["is_appropriate"]:
            # DogAgent antwortet (nicht CompanionAgent) und bleibt im gleichen Zustand
            return [AgentMessage(
                sender=self.dog_agent.role,  # DogAgent antwortet!
                text="Hey, lass uns lieber über Hundeverhalten sprechen. Beschreib mir bitte ein Verhalten deines Hundes!"
            )]
            # State bleibt WAIT_FOR_SYMPTOM - kein Zustandswechsel
        
        # NEUE ARCHITEKTUR: Symptom-Verarbeitung über DogAgent
        try:
            messages = await self.dog_agent.react_to_symptom(user_input)
            
            # NUR bei erfolgreichem Aufruf State ändern!
            if messages and not any("Schwierigkeiten" in msg.text or "Problem" in msg.text for msg in messages):
                state.active_symptom = user_input
                
                # Prüfe, ob es ein "kein Match" oder "Neustart" Fall war
                last_message_text = messages[-1].text.lower() if messages else ""
                
                if any(phrase in last_message_text for phrase in ["von vorne beginnen", "anderes verhalten", "versuch's mal anders"]):
                    # Bleibt im WAIT_FOR_SYMPTOM Zustand
                    state.current_step = FlowStep.WAIT_FOR_SYMPTOM
                else:
                    # Erfolgreiche Antwort - zur Bestätigung
                    state.current_step = FlowStep.WAIT_FOR_CONFIRMATION
            else:
                # Bei Fehlern: State NICHT ändern - bleibt WAIT_FOR_SYMPTOM
                print(f"⚠️ DogAgent react_to_symptom hatte Probleme, State bleibt unverändert")
            
            return messages
            
        except Exception as e:
            print(f"❌ Fehler bei der Symptomanalyse: {e}")
            # State NICHT ändern - bleibt WAIT_FOR_SYMPTOM
            return [AgentMessage(
                sender=self.dog_agent.role,
                text="Entschuldige, ich hatte Schwierigkeiten. Kannst du das Verhalten noch einmal beschreiben?"
            )]
        
    async def _handle_confirmation(self, state: SessionState, user_input: str) -> List[AgentMessage]:
        """Behandelt die Bestätigung über DogAgent"""
        try:
            context = {
                "flow_step": "wait_for_confirmation",
                "symptom": state.active_symptom
            }
            messages = await self.dog_agent.continue_flow(user_input, context)
            
            # Nächsten Schritt basierend auf Antwort setzen
            if "ja" in user_input.lower():
                state.current_step = FlowStep.WAIT_FOR_CONTEXT
            elif "nein" in user_input.lower():
                state.current_step = FlowStep.END_OR_RESTART
            # Sonst bleibt im aktuellen Schritt für Wiederholung
            
            return messages
            
        except Exception as e:
            print(f"❌ Fehler bei Bestätigung: {e}")
            return await self.companion_agent.provide_support("error in confirmation")
    
    async def _handle_context_input(self, state: SessionState, user_input: str) -> List[AgentMessage]:
        """Behandelt die Kontexteingabe über DogAgent"""
        try:
            context = {
                "flow_step": "wait_for_context",
                "symptom": state.active_symptom
            }
            messages = await self.dog_agent.continue_flow(user_input, context)
            
            # Nach erfolgreicher Diagnose zur Übungsfrage
            state.current_step = FlowStep.ASK_FOR_EXERCISE
            return messages
            
        except Exception as e:
            print(f"❌ Fehler bei der Kontextverarbeitung: {e}")
            return await self.companion_agent.provide_support("error in context processing")
    
    async def _handle_exercise_request(self, state: SessionState, user_input: str) -> List[AgentMessage]:
        """Behandelt die Anfrage nach einer Übung über DogAgent"""
        try:
            context = {
                "flow_step": "ask_for_exercise",
                "symptom": state.active_symptom
            }
            messages = await self.dog_agent.continue_flow(user_input, context)
            
            # Nächsten Schritt basierend auf Antwort setzen
            if "ja" in user_input.lower():
                state.current_step = FlowStep.END_OR_RESTART
            elif "nein" in user_input.lower():
                # Direkt zum Feedback springen
                state.current_step = FlowStep.FEEDBACK_Q1
                self.feedback_responses[state.session_id] = []
                
                # Feedback über CompanionAgent starten
                feedback_messages = await self.companion_agent.handle_feedback_step(1)
                return messages + feedback_messages
            
            return messages
            
        except Exception as e:
            print(f"❌ Fehler beim Abrufen der Übung: {e}")
            return await self.companion_agent.provide_support("error in exercise generation")
    
    async def _handle_end_or_restart(self, state: SessionState, user_input: str) -> List[AgentMessage]:
        """Behandelt das Ende oder einen Neustart über DogAgent"""
        try:
            context = {
                "flow_step": "end_or_restart",
                "symptom": state.active_symptom
            }
            messages = await self.dog_agent.continue_flow(user_input, context)
            
            if "ja" in user_input.lower():
                state.current_step = FlowStep.WAIT_FOR_SYMPTOM
                state.active_symptom = ""  # Reset für neues Symptom
            elif "nein" in user_input.lower():
                # Zum Feedback
                state.current_step = FlowStep.FEEDBACK_Q1
                self.feedback_responses[state.session_id] = []
                
                # Feedback über CompanionAgent starten
                feedback_messages = await self.companion_agent.handle_feedback_step(1)
                return messages + feedback_messages
            
            return messages
            
        except Exception as e:
            print(f"❌ Fehler bei Ende/Restart: {e}")
            return await self.companion_agent.provide_support("error in end/restart")
    
    # ===============================================
    # FEEDBACK-HANDLER ÜBER COMPANIONAGENT
    # ===============================================
    
    async def _handle_feedback_q1(self, state: SessionState, user_input: str) -> List[AgentMessage]:
        """Behandelt die erste Feedback-Frage über CompanionAgent"""
        # Antwort speichern
        if state.session_id not in self.feedback_responses:
            self.feedback_responses[state.session_id] = []
        self.feedback_responses[state.session_id].append(user_input)
        
        state.current_step = FlowStep.FEEDBACK_Q2
        return await self.companion_agent.handle_feedback_step(2)
    
    async def _handle_feedback_q2(self, state: SessionState, user_input: str) -> List[AgentMessage]:
        """Behandelt die zweite Feedback-Frage über CompanionAgent"""
        self.feedback_responses[state.session_id].append(user_input)
        state.current_step = FlowStep.FEEDBACK_Q3
        return await self.companion_agent.handle_feedback_step(3)
    
    async def _handle_feedback_q3(self, state: SessionState, user_input: str) -> List[AgentMessage]:
        """Behandelt die dritte Feedback-Frage über CompanionAgent"""
        self.feedback_responses[state.session_id].append(user_input)
        state.current_step = FlowStep.FEEDBACK_Q4
        return await self.companion_agent.handle_feedback_step(4)
    
    async def _handle_feedback_q4(self, state: SessionState, user_input: str) -> List[AgentMessage]:
        """Behandelt die vierte Feedback-Frage über CompanionAgent"""
        self.feedback_responses[state.session_id].append(user_input)
        state.current_step = FlowStep.FEEDBACK_Q5
        return await self.companion_agent.handle_feedback_step(5)
    
    async def _handle_feedback_q5(self, state: SessionState, user_input: str) -> List[AgentMessage]:
        """Behandelt die fünfte Feedback-Frage und beendet über CompanionAgent"""
        self.feedback_responses[state.session_id].append(user_input)
        
        # Feedback speichern über CompanionAgent
        try:
            messages = await self.companion_agent.finalize_feedback(
                state.session_id, 
                self.feedback_responses[state.session_id], 
                state.messages
            )
            
            # Cleanup
            del self.feedback_responses[state.session_id]
            state.current_step = FlowStep.GREETING
            
            return messages
            
        except Exception as e:
            print(f"❌ Fehler beim Finalisieren des Feedbacks: {e}")
            return [AgentMessage(
                sender=self.companion_agent.role,
                text="Danke für Dein Feedback! 🐾"
            )]


# Wird von main.py aufgerufen, um den Orchestrator zu initialisieren
orchestrator = None

def init_orchestrator(session_store_instance):
    global orchestrator
    orchestrator = FlowOrchestrator(session_store_instance)
    return orchestrator

# Diese Funktion ist diejenige, die von extern importiert wird
async def handle_message(session_id: str, user_input: str) -> List[AgentMessage]:
    """
    Wrapper-Funktion, die die handle_message Methode des Orchestrators aufruft.
    
    Args:
        session_id: ID der Session
        user_input: Nachricht des Benutzers
        
    Returns:
        Liste von Antwort-Nachrichten
    """
    if orchestrator is None:
        raise RuntimeError("Orchestrator wurde nicht initialisiert. Rufe init_orchestrator() auf.")
    
    return await orchestrator.handle_message(session_id, user_input)