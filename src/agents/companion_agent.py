# src/agents/companion_agent.py
import json
import os
from datetime import datetime, UTC, timedelta
from pathlib import Path
from typing import List, Dict, Any
from src.models.flow_models import AgentMessage
from src.services.redis_service import RedisService

class CompanionAgent:
    def __init__(self):
        self.role = "companion"
        # DSGVO-konformere Formulierung der letzten Frage
        self.feedback_questions = [
            "Hast Du das Gefühl, dass Dir die Beratung bei Deinem Anliegen weitergeholfen hat?",
            "Wie fandest Du die Sichtweise des Hundes – was hat Dir daran gefallen oder vielleicht irritiert?",
            "Was denkst Du über die vorgeschlagene Übung – passt sie zu Deiner Situation?",
            "Auf einer Skala von 0-10: Wie wahrscheinlich ist es, dass Du Wuffchat weiterempfiehlst?",
            "Optional: Deine E-Mail oder Telefonnummer für eventuelle Rückfragen. Diese wird ausschließlich für Rückfragen zu deinem Feedback verwendet und nach 3 Monaten automatisch gelöscht.",
        ]
        # Redis-Service initialisieren
        self.redis_service = RedisService.get_instance()
        
        # Aufbewahrungsdauer in Tagen (z.B. 90 Tage = 3 Monate)
        self.retention_days = 90
    
    # ===============================================
    # NEUE METHODEN FÜR FLOW_ORCHESTRATOR
    # ===============================================
    
    async def handle_feedback_step(self, step_number: int, user_input: str = None) -> List[AgentMessage]:
        """
        Behandelt einen Feedback-Schritt. 
        Wird vom flow_orchestrator aufgerufen.
        
        Args:
            step_number: Welcher Feedback-Schritt (1-5)
            user_input: Antwort des Users (None für erste Frage)
            
        Returns:
            Liste von AgentMessages
        """
        try:
            if step_number == 1:
                # Erste Feedback-Frage
                return [AgentMessage(
                    sender=self.role,
                    text="Ich würde mich freuen, wenn du mir noch ein kurzes Feedback gibst."
                ), AgentMessage(
                    sender=self.role,
                    text=self.feedback_questions[0]
                )]
            
            elif 2 <= step_number <= 5:
                # Folgefragen (2-5)
                question_index = step_number - 1
                if question_index < len(self.feedback_questions):
                    return [AgentMessage(
                        sender=self.role,
                        text=self.feedback_questions[question_index]
                    )]
                else:
                    # Ende des Feedbacks
                    return [AgentMessage(
                        sender=self.role,
                        text="Danke für Dein Feedback! 🐾"
                    )]
            else:
                # Unbekannter Step
                return [AgentMessage(
                    sender=self.role,
                    text="Danke für Dein Feedback! 🐾"
                )]
                
        except Exception as e:
            print(f"❌ Fehler in handle_feedback_step: {e}")
            return [AgentMessage(
                sender=self.role,
                text="Danke für Dein Feedback! 🐾"
            )]
    
    async def finalize_feedback(self, session_id: str, feedback_responses: List[str], messages: List[AgentMessage]) -> List[AgentMessage]:
        """
        Speichert das finale Feedback und beendet die Session.
        Wird vom flow_orchestrator nach der letzten Feedback-Antwort aufgerufen.
        """
        try:
            await self.save_feedback(session_id, feedback_responses, messages)
            return [AgentMessage(
                sender=self.role,
                text="Danke für Dein Feedback! 🐾"
            )]
        except Exception as e:
            print(f"⚠️ Fehler beim Speichern des Feedbacks: {e}")
            return [AgentMessage(
                sender=self.role,
                text="Danke für Dein Feedback! 🐾"
            )]
    
    async def moderate_content(self, content: str) -> Dict[str, Any]:
        """
        Moderiert Benutzerinhalte auf Angemessenheit.
        Kann vom flow_orchestrator aufgerufen werden.
        
        Returns:
            {"is_appropriate": bool, "reason": str, "suggested_response": str}
        """
        try:
            # Einfache Regel-basierte Moderation
            inappropriate_words = ["arsch", "fuck", "scheiß", "verdammt", "idiot", "blöd"]
            content_lower = content.lower()
            
            for word in inappropriate_words:
                if word in content_lower:
                    return {
                        "is_appropriate": False,
                        "reason": f"Inappropriate language detected: {word}",
                        "suggested_response": "Hey, lass uns lieber über Hundeverhalten sprechen. Beschreib mir bitte ein Verhalten deines Hundes!"
                    }
            
            # Zu kurzer Content
            if len(content.strip()) < 3:
                return {
                    "is_appropriate": False,
                    "reason": "Content too short",
                    "suggested_response": "Das ist mir zu kurz. Kannst du mir mehr erzählen?"
                }
            
            return {
                "is_appropriate": True,
                "reason": "Content is appropriate",
                "suggested_response": None
            }
            
        except Exception as e:
            print(f"❌ Fehler bei Content-Moderation: {e}")
            return {
                "is_appropriate": True,  # Im Fehlerfall eher erlauben
                "reason": "Error in moderation",
                "suggested_response": None
            }
    
    async def provide_support(self, context: str) -> List[AgentMessage]:
        """
        Bietet Unterstützung oder Hilfe basierend auf Kontext.
        Kann vom flow_orchestrator bei Problemen aufgerufen werden.
        """
        try:
            if "error" in context.lower() or "problem" in context.lower():
                return [AgentMessage(
                    sender=self.role,
                    text="Es scheint, als gäbe es ein kleines Problem. Lass uns von vorne beginnen - beschreibe einfach ein Hundeverhalten."
                )]
            
            elif "confused" in context.lower() or "verwirrt" in context.lower():
                return [AgentMessage(
                    sender=self.role,
                    text="Kein Problem! Du kannst mir einfach ein Verhalten deines Hundes beschreiben, und ich erkläre es dir aus Hundesicht."
                )]
            
            else:
                return [AgentMessage(
                    sender=self.role,
                    text="Wenn du Hilfe brauchst, beschreibe einfach ein Hundeverhalten - ich helfe gerne!"
                )]
                
        except Exception as e:
            print(f"❌ Fehler in provide_support: {e}")
            return [AgentMessage(
                sender=self.role,
                text="Wenn du Hilfe brauchst, beschreibe einfach ein Hundeverhalten - ich helfe gerne!"
            )]
    
    # ===============================================
    # URSPRÜNGLICHE METHODEN (für Kompatibilität)
    # ===============================================
        
    def _prepare_feedback_data(self, session_id: str, responses: List[str], messages: List[AgentMessage]) -> Dict[str, Any]:
        """
        Bereitet die Feedback-Daten zur Speicherung vor.
        """
        # Ablaufdatum berechnen (DSGVO-konform)
        expiration_date = (datetime.now(UTC) + timedelta(days=self.retention_days)).isoformat()
        
        # Feedback-Antworten vorbereiten
        prepared_responses = []
        
        for i, (question, answer) in enumerate(zip(self.feedback_questions, responses)):
            prepared_responses.append({
                "question": question,
                "answer": answer
            })
        
        # Feedback-Daten zusammenstellen
        return {
            "session_id": session_id,
            "timestamp": datetime.now(UTC).isoformat(),
            "expiration_date": expiration_date,  # DSGVO-Löschfrist
            "responses": prepared_responses,
            "messages": [msg.model_dump() if hasattr(msg, 'model_dump') else {"sender": msg.sender, "text": msg.text} for msg in messages], 
        }

    async def save_feedback(self, session_id: str, responses: List[str], messages: List[AgentMessage]):
        """Speichert die Antworten in Redis mit DSGVO-konformer Ablaufzeit"""
        try:
            # Feedback-Daten vorbereiten
            feedback_data = self._prepare_feedback_data(session_id, responses, messages)
            
            print(f"✅ Speichere Feedback für Session {session_id}")
            
            # Redis-Schlüssel definieren
            redis_key = f"feedback:{session_id}"
            
            # Ablaufzeit in Sekunden berechnen (für Redis-Schlüsselablauf)
            expire_seconds = self.retention_days * 24 * 60 * 60
            
            # In Redis speichern MIT Ablaufzeit
            if self.redis_service.is_connected():
                success = self.redis_service.set(redis_key, feedback_data, expire=expire_seconds)
                
                if success:
                    print(f"✅ Feedback erfolgreich in Redis gespeichert: {redis_key}")
                    print(f"✅ Automatische Löschung nach {self.retention_days} Tagen eingestellt")
                    
                    # Zum Feedback-Index hinzufügen für einfache Abfrage aller Feedbacks
                    all_feedback_key = "all_feedback_ids"
                    all_ids = self.redis_service.get(all_feedback_key) or []
                    if session_id not in all_ids:
                        all_ids.append(session_id)
                        self.redis_service.set(all_feedback_key, all_ids)
                    
                    return
                else:
                    print("⚠️ Fehler beim Speichern in Redis")
            else:
                print("⚠️ Redis nicht verbunden, Feedback kann nicht gespeichert werden")
            
            # Lokale Speicherung als Fallback
            base_path = os.environ.get("SESSION_LOG_PATH", "data")
            feedback_dir = Path(base_path)
            
            try:
                # Verzeichnis erstellen, falls es nicht existiert
                feedback_dir.mkdir(parents=True, exist_ok=True)
                
                # Feedback als JSON speichern
                file_path = feedback_dir / f"feedback_{session_id}.json"
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(feedback_data, f, ensure_ascii=False, indent=2)
                
                print(f"✅ Feedback lokal gespeichert: {file_path}")
            except Exception as e:
                print(f"❌ Fehler bei der lokalen Speicherung: {e}")
                raise
        
        except Exception as e:
            print(f"⚠️ Fehler beim Speichern des Feedbacks: {e} — Feedback wird nicht gespeichert.")

    def get_intro_messages(self) -> List[AgentMessage]:
        return [
            AgentMessage(sender=self.role, text="Ich würde mich freuen, wenn du mir noch ein kurzes Feedback gibst."),
            *[
                AgentMessage(sender=self.role, text=question)
                for question in self.feedback_questions
            ],
        ]
        
    async def cleanup_expired_feedback(self):
        """Löscht abgelaufene Feedback-Daten (DSGVO-Compliance)"""
        if not self.redis_service.is_connected():
            print("⚠️ Redis nicht verbunden, Bereinigung nicht möglich")
            return
            
        all_ids = self.redis_service.get("all_feedback_ids") or []
        current_date = datetime.now(UTC)
        removed_ids = []
        
        for session_id in all_ids:
            feedback = self.redis_service.get(f"feedback:{session_id}")
            if not feedback:
                removed_ids.append(session_id)
                continue
                
            # Prüfen, ob das Ablaufdatum erreicht ist
            expiration_date = feedback.get("expiration_date")
            if expiration_date:
                try:
                    exp_date = datetime.fromisoformat(expiration_date)
                    if current_date > exp_date:
                        # Feedback löschen
                        self.redis_service.delete(f"feedback:{session_id}")
                        removed_ids.append(session_id)
                        print(f"🗑️ Abgelaufenes Feedback gelöscht: {session_id}")
                except (ValueError, TypeError):
                    pass
        
        # Bereinigte IDs aus dem Index entfernen
        if removed_ids:
            updated_ids = [id for id in all_ids if id not in removed_ids]
            self.redis_service.set("all_feedback_ids", updated_ids)
            print(f"🧹 {len(removed_ids)} abgelaufene Feedback-Einträge bereinigt")