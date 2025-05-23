# src/services/rag_service.py
import json
from typing import Dict, Any, Optional, List
from src.services.weaviate_service import query_agent_service
from src.config.prompts import (
    INSTINCT_SEARCH_PROMPT, 
    format_prompt,
    get_error_response
)
from src.services.gpt_service import ask_gpt
from src.core.error_handling import with_error_handling, RAGServiceError, GPTServiceError

# Einfaches In-Memory-Cache für schnellere Antworten
_analysis_cache = {}
_dog_perspective_cache = {}

# Fallback-Analyse außerhalb der Klasse definieren
def get_fallback_analysis() -> Dict[str, Any]:
    """Gibt eine Fallback-Analyse zurück, wenn ein Fehler auftritt"""
    return {
        "primary_instinct": "unbekannter Instinkt",
        "primary_description": "Ich konnte keine Diagnose erstellen aufgrund eines technischen Problems.",
        "all_instincts": {
            "jagd": "Der Jagdinstinkt lässt mich Dinge verfolgen und fangen wollen.",
            "rudel": "Der Rudelinstinkt regelt mein soziales Verhalten in der Gruppe.",
            "territorial": "Der territoriale Instinkt lässt mich mein Gebiet und meine Ressourcen schützen.",
            "sexual": "Der Sexualinstinkt steuert mein Fortpflanzungsverhalten."
        },
        "exercise": "Eine grundlegende Übung ist, mit dem Hund an seiner Impulskontrolle zu arbeiten und klare Grenzen zu setzen.",
        "confidence": 0.3,
        "success": False
    }

class RAGService:
    """Verbesserte RAG-Service-Klasse für effiziente Weaviate-Abfragen"""
    
    @staticmethod
    async def generate_diagnosis_intro() -> str:
        """
        Generiert eine dynamische Einleitung für die Diagnose.
        """
        try:
            from src.config.prompts import DIAGNOSIS_INTRO_PROMPT, format_prompt
            from src.services.gpt_service import ask_gpt
            
            intro_prompt = format_prompt(DIAGNOSIS_INTRO_PROMPT)
            return await ask_gpt(intro_prompt)
        except Exception as e:
            print(f"❌ Fehler bei der Intro-Generierung: {e}")
            return "Lass mich erklären, was in mir vorgeht:"

    @staticmethod
    @with_error_handling(RAGServiceError, get_fallback_analysis())
    async def get_comprehensive_analysis(symptom: str, context: str = "") -> Dict[str, Any]:
        """
        Führt eine umfassende Analyse eines Hundeverhaltens durch mit dem Query Agent.
        Mit Caching für schnellere Antworten.
        """
        # Cache-Schlüssel generieren
        cache_key = f"{symptom}:{context}"
        
        # Cache prüfen
        if cache_key in _analysis_cache:
            print("✅ Lade Analyse aus Cache")
            return _analysis_cache[cache_key]
            
        # Verwende den neuen strukturierten Prompt
        query = format_prompt(
            INSTINCT_SEARCH_PROMPT, 
            symptom=symptom, 
            context=context
        )
        
        # Instinktveranlagung-Collection für beste Ergebnisse
        result = await query_agent_service.query(
            query=query,
            collection_name="Instinktveranlagung"  # Änderung zur präziseren Collection
        )
        
        # Überprüfen auf Fehler
        if "error" in result and result["error"]:
            print(f"⚠️ Fehler bei der RAG-Analyse: {result['error']}")
            return get_fallback_analysis()
        
        # Daten aus dem Ergebnis extrahieren
        if "data" in result and result["data"]:
            # Versuche, strukturierte Daten aus der Antwort zu extrahieren
            try:
                # Wenn das Ergebnis ein String ist, versuche es zu parsen
                if isinstance(result["data"], str):
                    # Extrahiere die Informationen aus dem Text
                    text = result["data"]
                    
                    # Einfacher Parser für strukturierten Text
                    primary_instinct = None
                    primary_description = None
                    all_instincts = {}
                    exercise = None
                    confidence = 0.5
                    
                    lines = text.split('\n')
                    for line in lines:
                        line = line.strip()
                        if line.startswith("primary_instinct:") or line.startswith("- primary_instinct:"):
                            primary_instinct = line.split(":", 1)[1].strip()
                        elif line.startswith("primary_description:") or line.startswith("- primary_description:"):
                            primary_description = line.split(":", 1)[1].strip()
                        elif line.startswith("confidence:") or line.startswith("- confidence:"):
                            try:
                                confidence = float(line.split(":", 1)[1].strip())
                            except:
                                pass
                    
                    parsed_result = {
                        "primary_instinct": primary_instinct or "unbekannter Instinkt",
                        "primary_description": primary_description or "Keine Beschreibung verfügbar",
                        "all_instincts": {
                            "jagd": "Der Jagdinstinkt lässt mich Dinge verfolgen und fangen wollen.",
                            "rudel": "Der Rudelinstinkt regelt mein soziales Verhalten in der Gruppe.",
                            "territorial": "Der territoriale Instinkt lässt mich mein Gebiet und meine Ressourcen schützen.",
                            "sexual": "Der Sexualinstinkt steuert mein Fortpflanzungsverhalten."
                        },
                        "exercise": "Übe mit deinem Hund Impulskontrolle durch kurze, regelmäßige Trainingseinheiten.",
                        "confidence": confidence,
                        "success": True
                    }
                    
                    # Ergebnis cachen
                    _analysis_cache[cache_key] = parsed_result
                    return parsed_result
                    
                elif isinstance(result["data"], dict):
                    # Wenn das Ergebnis bereits ein Dict ist
                    parsed_result = {
                        "primary_instinct": result["data"].get("primary_instinct", "unbekannter Instinkt"),
                        "primary_description": result["data"].get("primary_description", "Keine Beschreibung verfügbar"),
                        "all_instincts": result["data"].get("all_instincts", {}),
                        "exercise": result["data"].get("exercise", "Keine Übung verfügbar"),
                        "confidence": result["data"].get("confidence", 0.5),
                        "success": True
                    }
                    
                    # Ergebnis cachen
                    _analysis_cache[cache_key] = parsed_result
                    return parsed_result
            except Exception as e:
                print(f"⚠️ Fehler bei der Verarbeitung der RAG-Antwort: {e}")
        
        # Fallback-Werte zurückgeben
        return get_fallback_analysis()
    
    @staticmethod
    @with_error_handling(GPTServiceError, "Als Hund spüre ich verschiedene innere Impulse. Manchmal ist es schwer, sie zu beschreiben, aber sie leiten mich in meinem Verhalten.")
    async def generate_dog_perspective(symptom: str, analysis: Dict[str, Any]) -> str:
        """
        Generiert eine Hundeperspektive basierend auf der RAG-Analyse.
        Mit Caching für schnellere Antworten.
        """
        # Cache-Schlüssel generieren
        primary_instinct = analysis.get("primary_instinct", "unbekannt")
        cache_key = f"{symptom}:{primary_instinct}"
        
        # Cache prüfen
        if cache_key in _dog_perspective_cache:
            print("✅ Lade Hundeperspektive aus Cache")
            return _dog_perspective_cache[cache_key]
        
        try:
            # NEUE LOGIK: Nutze die verbesserten Prompts aus prompts.py
            from src.config.prompts import SYMPTOM_SEARCH_PROMPT, DOG_PERSPECTIVE_PROMPT, format_prompt
            
            # 1. Suche Schnelldiagnose in Symptome-Collection
            result = await query_agent_service.query(
                query=format_prompt(SYMPTOM_SEARCH_PROMPT, symptom=symptom),
                collection_name="Symptome"
            )
            
            if "data" in result and result["data"] and result["data"] != "NO_MATCH":
                # 2. Wandle Schnelldiagnose in Hundeperspektive um
                schnelldiagnose = result["data"]
                dog_perspective_prompt = format_prompt(DOG_PERSPECTIVE_PROMPT, match=schnelldiagnose)
                
                # 3. GPT formatiert in Hundeperspektive
                from src.services.gpt_service import ask_gpt
                dog_perspective = await ask_gpt(dog_perspective_prompt)
                
                # Ergebnis cachen
                _dog_perspective_cache[cache_key] = dog_perspective
                return dog_perspective
            else:
                # Kein Match gefunden
                from src.config.prompts import get_error_response
                no_match_response = get_error_response("no_match")
                _dog_perspective_cache[cache_key] = no_match_response
                return no_match_response
                
        except Exception as e:
            print(f"⚠️ Fehler bei der Hundeperspektive: {e}")
        
        # Fallback
        fallback_response = "Dazu fällt mir nichts ein. Versuch's mal anders?"
        _dog_perspective_cache[cache_key] = fallback_response
        return fallback_response
    
    @staticmethod
    async def generate_exercise_recommendation(symptom: str, analysis: Dict[str, Any]) -> str:
        """
        Generiert eine Lernaufgabe basierend auf Weaviate-Daten und formatiert sie in Hundeperspektive.
        """
        try:
            # NEUE LOGIK: Nutze die verbesserten Prompts aus prompts.py
            from src.config.prompts import EXERCISE_SEARCH_PROMPT, EXERCISE_PROMPT, format_prompt
            
            # 1. Suche Übung in Erziehung-Collection
            result = await query_agent_service.query(
                query=format_prompt(EXERCISE_SEARCH_PROMPT, symptom=symptom),
                collection_name="Erziehung"
            )
            
            if "data" in result and result["data"]:
                # 2. Formatiere Übung in Hundeperspektive
                raw_exercise = result["data"]
                exercise_prompt = format_prompt(EXERCISE_PROMPT, match=raw_exercise)
                
                # 3. GPT formatiert aus Hundeperspektive  
                from src.services.gpt_service import ask_gpt
                formatted_exercise = await ask_gpt(exercise_prompt)
                return formatted_exercise
            else:
                # Fallback aus der Analyse verwenden
                exercise_from_analysis = analysis.get("exercise", "")
                if exercise_from_analysis and exercise_from_analysis != "Keine Übung verfügbar":
                    # Auch das durch den Hundeperspektive-Prompt schicken
                    exercise_prompt = format_prompt(EXERCISE_PROMPT, match=exercise_from_analysis)
                    formatted_exercise = await ask_gpt(exercise_prompt)
                    return formatted_exercise
                
        except Exception as e:
            print(f"⚠️ Fehler bei der Übungsgenerierung: {e}")
        
        # Letzter Fallback
        return "Geh mit mir an einen ruhigen Ort und lass uns gemeinsam entspannen."
    
    @staticmethod
    async def generate_diagnosis_intro() -> str:
        """
        Generiert eine dynamische Einleitung für die Diagnose.
        """
        try:
            from src.config.prompts import DIAGNOSIS_INTRO_PROMPT, format_prompt
            from src.services.gpt_service import ask_gpt
            
            intro_prompt = format_prompt(DIAGNOSIS_INTRO_PROMPT)
            return await ask_gpt(intro_prompt)
        except Exception as e:
            print(f"❌ Fehler bei der Intro-Generierung: {e}")
            return "Lass mich erklären, was in mir vorgeht:"
        """
        Führt mehrere Abfragen in einem Batch aus, um die Anzahl der API-Aufrufe zu reduzieren.
        
        Args:
            questions: Liste von Dictionaries im Format {"id": "unique_id", "query": "abfragetext"}
            collection_name: Optional, der Name der Collection
            
        Returns:
            Dictionary mit Antworten, wobei die Schlüssel die IDs aus den Fragen sind
        """
        try:
            combined_query = "Beantworte folgende Fragen im JSON-Format mit einem Feld für jede Frage-ID:\n\n"
            
            for q in questions:
                combined_query += f"Frage '{q['id']}': {q['query']}\n"
            
            combined_query += "\nFormatiere die Antwort als JSON-Objekt mit den Frage-IDs als Schlüssel."
            
            result = await query_agent_service.query(
                query=combined_query,
                collection_name=collection_name
            )
            
            if "error" in result and result["error"]:
                print(f"⚠️ Fehler bei der Batch-Abfrage: {result['error']}")
                return {"error": result["error"]}
            
            if "data" in result and result["data"]:
                # Versuche, das Ergebnis als strukturiertes JSON zu interpretieren
                try:
                    if isinstance(result["data"], dict):
                        return result["data"]
                    else:
                        return json.loads(result["data"])
                except (json.JSONDecodeError, TypeError):
                    # Wenn das nicht funktioniert, gib das Ergebnis als Rohtext zurück
                    return {"raw_result": result["data"]}
            
            return {"error": "Keine Daten in der Antwort"}
        except Exception as e:
            print(f"⚠️ Fehler bei der Batch-Abfrage: {e}")
            return {"error": str(e)}