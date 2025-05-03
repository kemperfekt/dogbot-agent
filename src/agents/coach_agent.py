from openai import OpenAI
from src.agents.base_agent import BaseAgent
from src.prompts.system_prompt_coach import system_prompt_coach
from src.services.retrieval import get_symptom_info, get_instinkt_rueckfrage
from src.logic.context_analyzer import ContextAnalyzer
from src.models.symptom_models import SymptomInfo, Diagnose
from src.models.context_models import ContextInfo
from src.models.agent_models import AgentMessage
import json

class CoachAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Coach")

    def build_prompt(self, symptom_info: SymptomInfo, user_input: str, client: OpenAI) -> AgentMessage:
        if not symptom_info.instinktvarianten:
            return AgentMessage(
                sender="coach",
                question="Ich konnte noch kein klares Bild erkennen. Magst du mir die Situation etwas ausführlicher beschreiben?"
            )

        analyzer = ContextAnalyzer(client)
        context_info: ContextInfo = analyzer.analyze(user_input)
        fehlende = [k for k, v in context_info.model_dump().items() if v == "nicht enthalten"]

        if fehlende:
            fragen_mapping = {
                "Ort": "Wo ist die Situation passiert?",
                "Beteiligte": "Wer war sonst noch dabei – andere Hunde, Menschen?",
                "Zeit_davor": "Weißt du noch, was kurz vorher passiert ist?",
                "Zeit_danach": "Wie ging es danach weiter?",
                "Ressourcen": "War etwas im Spiel, das ihm wichtig war – z. B. ein Ball, Leckerli oder ähnliches?"
            }
            fragen = [fragen_mapping[k] for k in fehlende if k in fragen_mapping]
            rückfrage = " ".join(fragen)

            return AgentMessage(
                sender="coach",
                question=rückfrage
            )

        instinktinfo = get_instinkt_rueckfrage(symptom_info)
        if instinktinfo:
            diagnose = Diagnose(
                instinkt=instinktinfo["instinkt"],
                kommentar=f"Ich vermute, dein Hund zeigt dieses Verhalten, weil ihm in dieser Situation etwas besonders wichtig war – vermutlich im Bereich {instinktinfo['instinkt']}."
            )
            return AgentMessage(
                sender="coach",
                diagnosis=diagnose
            )

        return AgentMessage(
            sender="coach",
            question=f"Wie genau zeigt sich das Verhalten '{symptom_info.symptom_name}' bei deinem Hund?"
        )

    def respond(self, session_id: str, user_input: str, client: OpenAI) -> str:
        symptom_info = get_symptom_info(user_input)
        msg: AgentMessage = self.build_prompt(symptom_info, user_input, client)

    # Direkte Übergabe an BaseAgent für LLM-Output (nur wenn 'text' leer ist)
        if not msg.text and msg.question:
            # Frage durch LLM formulieren
            return super().respond(prompt=msg.question, system_prompt=system_prompt_coach, client=client).model_dump_json()

        # Wenn Diagnose oder fertiger Text vorliegt, direkt zurückgeben
        return msg.model_dump_json()