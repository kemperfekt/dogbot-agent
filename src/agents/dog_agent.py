# src/agents/dog_agent.py
from typing import List, Dict, Optional, Any
from src.agents.base_agent import BaseAgent
from src.models.flow_models import AgentMessage
from src.services.gpt_service import ask_gpt
from src.services.retrieval import get_symptom_info
from src.services.rag_service import RAGService
from src.state.session_state import sessions
from src.config.prompts import DOG_PERSPECTIVE_TEMPLATE, EXERCISE_TEMPLATE
from src.core.error_handling import with_error_handling, GPTServiceError, RAGServiceError
from src.services.weaviate_service import query_agent_service

class DogAgent(BaseAgent):
    """Agent, der aus Hundeperspektive antwortet"""
    
    def __init__(self):
        super().__init__(name="Hund", role="dog")
        self.greeting_text = "Wuff! Schön, dass Du da bist. Bitte nenne mir ein Verhalten und ich schildere dir, wie ich es erlebe."
    
    # ===============================================
    # NEUE METHODEN FÜR FLOW_ORCHESTRATOR
    # ===============================================
    
    async def react_to_symptom(self, symptom: str) -> List[AgentMessage]:
        """
        Reagiert auf die erste Symptom-Eingabe des Users.
        Wird vom flow_orchestrator für flow_start aufgerufen.
        """
        try:
            # Validierung wird bereits im flow_orchestrator gemacht - hier überflüssig
            
            # 1. Prüfe, ob das Symptom zu vage ist
            if len(symptom.strip()) < 10:
                return [AgentMessage(
                    sender=self.role,
                    text="Das ist mir zu ungenau. Kannst du beschreiben, was genau ich mache?"
                )]
            
            # 2. Hole Hundeperspektive über RAGService
            analysis = await RAGService.get_comprehensive_analysis(symptom, "")
            dog_perspective = await RAGService.generate_dog_perspective(symptom, analysis)
            
            # 3. Prüfe auf "kein Match"
            if "fällt mir nichts ein" in dog_perspective.lower() or "versuch's mal anders" in dog_perspective.lower():
                return [
                    AgentMessage(sender=self.role, text=dog_perspective),
                    AgentMessage(sender=self.role, text="Möchtest du ein anderes Verhalten beschreiben oder von vorne beginnen?")
                ]
            
            # 4. Erfolgreiche Antwort mit Folgefrage
            return [
                AgentMessage(sender=self.role, text=dog_perspective),
                AgentMessage(sender=self.role, text="Magst Du mehr erfahren, warum ich mich so verhalte?")
            ]
            
        except Exception as e:
            print(f"❌ Fehler in react_to_symptom: {e}")
            return [AgentMessage(
                sender=self.role,
                text="Entschuldige, ich hatte Schwierigkeiten. Magst du es noch einmal versuchen?"
            )]
    
    async def continue_flow(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> List[AgentMessage]:
        """
        Setzt den Konversationsfluss fort basierend auf User-Input und Kontext.
        Wird vom flow_orchestrator für verschiedene Flow-Schritte aufgerufen.
        """
        context = context or {}
        
        try:
            # Kontext auswerten um den richtigen Flow-Schritt zu bestimmen
            flow_step = context.get("flow_step", "unknown")
            symptom = context.get("symptom", "")
            
            if flow_step == "wait_for_confirmation":
                return await self._handle_confirmation(user_input)
            
            elif flow_step == "wait_for_context":
                return await self._handle_context_input(user_input, symptom)
            
            elif flow_step == "ask_for_exercise":
                return await self._handle_exercise_request(user_input, symptom)
            
            elif flow_step == "end_or_restart":
                return await self._handle_end_or_restart(user_input)
            
            else:
                # Fallback für unbekannte Schritte
                return [AgentMessage(
                    sender=self.role,
                    text="Ich bin kurz verwirrt... lass uns neu starten. Was möchtest du mir erzählen?"
                )]
                
        except Exception as e:
            print(f"❌ Fehler in continue_flow: {e}")
            return [AgentMessage(
                sender=self.role,
                text="Es tut mir leid, ich habe gerade ein technisches Problem. Kannst du es später noch einmal versuchen?"
            )]
    
    # ===============================================
    # FLOW-HANDLER METHODEN
    # ===============================================
    
    async def _handle_confirmation(self, user_input: str) -> List[AgentMessage]:
        """Behandelt die Bestätigung für mehr Details"""
        if "ja" in user_input.lower():
            return [AgentMessage(
                sender=self.role,
                text="Gut, dann brauche ich ein bisschen mehr Informationen. Bitte beschreibe, wie es zu der Situation kam, wer dabei war und was sonst noch wichtig sein könnte."
            )]
        elif "nein" in user_input.lower():
            return [AgentMessage(
                sender=self.role,
                text="Okay, kein Problem. Wenn du es dir anders überlegst, sag einfach Bescheid."
            )]
        else:
            return [AgentMessage(
                sender=self.role,
                text="Magst du mir einfach 'Ja' oder 'Nein' sagen?"
            )]
    
    async def _handle_context_input(self, user_input: str, symptom: str) -> List[AgentMessage]:
        """Behandelt zusätzliche Kontext-Informationen und gibt Diagnose"""
        if len(user_input.strip()) < 5:
            return [AgentMessage(
                sender=self.role,
                text="Ich brauch noch ein bisschen mehr Info… Wo war das genau, was war los?"
            )]
        
        try:
            # Umfassende Analyse mit Kontext
            analysis = await RAGService.get_comprehensive_analysis(symptom, user_input)
            
            # Dynamische Diagnose-Einleitung
            intro = await RAGService.generate_diagnosis_intro()
            
            # Strukturierte Diagnose aus der Analyse
            primary_description = analysis.get("primary_description", "Ich spüre verschiedene Impulse in meinem Verhalten.")
            
            # Formatiere die Diagnose richtig (nicht den Rohtext)
            if primary_description and not primary_description.startswith("- primary_instinct"):
                diagnosis_text = f"{intro} {primary_description}"
            else:
                # Falls Rohtext von Weaviate kommt, formatiere ihn über RAGService
                diagnosis_text = f"{intro} Ich erkenne verschiedene innere Impulse in meinem Verhalten."
            
            return [
                AgentMessage(sender=self.role, text=diagnosis_text),
                AgentMessage(sender=self.role, text="Möchtest du eine Lernaufgabe, die dir in dieser Situation helfen kann?")
            ]
            
        except Exception as e:
            print(f"❌ Fehler bei Kontext-Verarbeitung: {e}")
            return [
                AgentMessage(sender=self.role, text="Danke. Ich verstehe jetzt besser, warum ich mich so verhalte."),
                AgentMessage(sender=self.role, text="Möchtest du eine Lernaufgabe, die dir in dieser Situation helfen kann?")
            ]
    
    async def _handle_exercise_request(self, user_input: str, symptom: str) -> List[AgentMessage]:
        """Behandelt Anfrage nach Lernaufgabe"""
        if "ja" in user_input.lower():
            try:
                # Hole Analyse und generiere Übung über RAGService
                analysis = await RAGService.get_comprehensive_analysis(symptom, "")
                exercise = await RAGService.generate_exercise_recommendation(symptom, analysis)
                
                return [
                    AgentMessage(sender=self.role, text=exercise),
                    AgentMessage(sender=self.role, text="Möchtest du ein weiteres Hundeverhalten verstehen?")
                ]
                
            except Exception as e:
                print(f"❌ Fehler bei Übungsgenerierung: {e}")
                return [
                    AgentMessage(sender=self.role, text="Geh mit mir an einen ruhigen Ort und lass uns gemeinsam entspannen."),
                    AgentMessage(sender=self.role, text="Möchtest du ein weiteres Hundeverhalten verstehen?")
                ]
        
        elif "nein" in user_input.lower():
            return [AgentMessage(
                sender=self.role,
                text="Okay. Möchtest du ein weiteres Hundeverhalten verstehen oder sollen wir aufhören?"
            )]
        
        else:
            return [AgentMessage(
                sender=self.role,
                text="Bitte antworte mit 'Ja' oder 'Nein' - möchtest du eine Lernaufgabe?"
            )]
    
    async def _handle_end_or_restart(self, user_input: str) -> List[AgentMessage]:
        """Behandelt Ende oder Neustart"""
        if "ja" in user_input.lower():
            return [AgentMessage(
                sender=self.role,
                text="Super! Beschreibe mir bitte ein anderes Verhalten."
            )]
        elif "nein" in user_input.lower():
            return [AgentMessage(
                sender=self.role,
                text="Okay, dann sind wir fertig. Danke, dass du mit mir gesprochen hast! 🐾"
            )]
        else:
            return [AgentMessage(
                sender=self.role,
                text="Sag einfach 'Ja' für ein neues Verhalten oder 'Nein' zum Beenden."
            )]
    
    # ===============================================
    # URSPRÜNGLICHE RESPOND-METHODE (für Kompatibilität)
    # ===============================================
    
    async def respond(self, 
                     user_input: str, 
                     session_id: str, 
                     context: Optional[Dict[str, Any]] = None) -> List[AgentMessage]:
        """
        Verarbeitet eine Benutzereingabe und generiert Antworten.
        Kompatibilitäts-Methode für bestehenden Code.
        """
        context = context or {}
        messages = []
        
        # Session-Zustand abrufen
        state = sessions.get_or_create(session_id)
        is_first_message = context.get("is_first_message", False)
        
        # Begrüßung bei erster Nachricht
        if is_first_message:
            return self._get_greeting_messages()
        
        # Prüfe, ob Nutzer "ja" antwortet auf "Nochmal von vorne?"
        if user_input.lower() == "ja" and getattr(self, 'last_bot_message', "") == "Nochmal von vorne?":
            return self._get_greeting_messages()
        
        # Spezielle Kontextflags prüfen
        is_first_response = context.get("is_first_response", False)
        is_diagnose = context.get("is_diagnose", False)
        exercise_only = context.get("exercise_only", False)
        additional_context = context.get("additional_context", "")
            
        try:
            # Verkürzter Flow für bestimmte Anfragen
            if exercise_only:
                # Nur eine Übungsempfehlung zurückgeben
                symptom = context.get("symptom", user_input)
                analysis = await RAGService.get_comprehensive_analysis(symptom, "")
                exercise = await RAGService.generate_exercise_recommendation(symptom, analysis)
                return [AgentMessage(sender=self.role, text=exercise)]
            
            # Schritt 1: Verhaltensanalyse mit RAG durchführen
            symptom_info = await get_symptom_info(user_input)
            
            if not symptom_info or "keine spezifischen Informationen" in symptom_info.lower():
                # Bessere "Kein Match" Behandlung
                return await self._handle_no_match(user_input)
            
            # Schritt 2: Umfassende RAG-Analyse durchführen
            analysis = await RAGService.get_comprehensive_analysis(user_input, additional_context)
            
            # Falls nur erste Antwort gewünscht (erste Phase im Flow)
            if is_first_response:
                dog_view = await RAGService.generate_dog_perspective(user_input, analysis)
                return [AgentMessage(sender=self.role, text=dog_view)]
            
            # Falls Diagnose gewünscht (nach Kontexteingabe)
            if is_diagnose:
                intro = await RAGService.generate_diagnosis_intro()
                diagnosis = analysis.get("primary_description", "Keine Diagnose verfügbar")
                
                formatted_diagnosis = f"{intro} {diagnosis}"
                return [AgentMessage(sender=self.role, text=formatted_diagnosis)]
            
            # Standardfall: Vollständige Antwort
            
            # Schritt 3: Hundeperspektive generieren
            dog_view = await RAGService.generate_dog_perspective(user_input, analysis)
            messages.append(AgentMessage(sender=self.role, text=dog_view))
            
            # Schritt 4: Übung vorschlagen
            exercise = await RAGService.generate_exercise_recommendation(user_input, analysis)
            messages.append(AgentMessage(
                sender=self.role,
                text=f"Hier ist eine Übung, die zu deinem Fall passt: {exercise}. Gibt es ein weiteres Verhalten, das Du mit mir besprechen möchtest?"
            ))
            
            # Diagnose-Angebot
            messages.append(AgentMessage(
                sender=self.role,
                text="Nochmal von vorne?"
            ))
            
            # Session-State aktualisieren
            if state:
                state.active_symptom = user_input
            
            # Letzte Nachricht speichern
            self.last_bot_message = "Nochmal von vorne?"
            
        except Exception as e:
            print(f"❌ Fehler bei der Verarbeitung: {e}")
            import traceback
            traceback.print_exc()
            messages.append(AgentMessage(
                sender=self.role,
                text="Es tut mir leid, ich habe gerade ein technisches Problem. Kannst du es später noch einmal versuchen?"
            ))
        
        return messages
    
    # ===============================================
    # HILFSMETHODEN
    # ===============================================
    
    async def _handle_no_match(self, user_input: str) -> List[AgentMessage]:
        """Behandelt Situationen, wo kein Match gefunden wurde"""
        # Versuchen mit Allgemein-Collection
        general_info = await self._get_general_info(user_input)
        if general_info:
            return [AgentMessage(sender=self.role, text=general_info)]
        
        # Intelligente Alternativen anbieten
        if len(user_input) < 10:
            response = "Das ist mir zu ungenau. Kannst du beschreiben, was genau ich mache?"
        else:
            response = "Dazu fällt mir nichts ein. Versuch's mal anders?"
        
        return [
            AgentMessage(sender=self.role, text=response),
            AgentMessage(sender=self.role, text="Möchtest du von vorne beginnen oder ein anderes Verhalten beschreiben?")
        ]
    
    def _get_greeting_messages(self) -> List[AgentMessage]:
        """Gibt die Begrüßungsnachrichten zurück"""
        return [
            AgentMessage(sender=self.role, text=self.greeting_text),
            AgentMessage(sender=self.role, text="Was ist los? Beschreib mir bitte, was du beobachtet hast.")
        ]
    
    async def _get_general_info(self, query: str) -> Optional[str]:
        """Sucht allgemeine Informationen in der Allgemein-Collection"""
        try:
            result = await query_agent_service.query(
                query=f"Beschreibe als Hund, wie ich folgendes Verhalten erlebe: {query}",
                collection_name="Allgemein"
            )
            
            if "error" in result and result["error"]:
                return None
                
            if "data" in result and result["data"]:
                return result["data"]
            
            return None
        except Exception as e:
            print(f"❌ Fehler bei der Allgemein-Suche: {e}")
            return None