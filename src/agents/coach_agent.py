from openai import OpenAI
from src.agents.base_agent import BaseAgent
from src.prompts.system_prompt_coach import system_prompt_coach
from src.models.agent_models import AgentMessage
from src.state.session_store import get_history
from src.logic.context_analyzer import ContextAnalyzer


class CoachAgent(BaseAgent):
    def __init__(self):
        super().__init__("coach")

    def build_prompt(self, user_input: str, context: dict[str, str], history: list[AgentMessage]) -> str:
        verlauf = "\n".join([f"{m.sender}: {m.text}" for m in history])
        kontext = "\n".join([f"{k}: {v}" for k, v in context.items()])
        return (
            f"{verlauf}\n\n"
            f"Nutzereingabe: {user_input}\n\n"
            f"Kontextmerkmale:\n{kontext}\n\n"
            f"Bitte antworte wie ein einfühlsamer Coach: verständlich, pragmatisch, ruhig erklärend."
        )

    def respond(self, session_id: str, user_input: str, client: OpenAI) -> AgentMessage:
        context_analyzer = ContextAnalyzer(client)
        context_info = context_analyzer.analyze(user_input)
        history = get_history(session_id)
        prompt = self.build_prompt(user_input, context_info.model_dump(), history)
        return super().respond(system_prompt=system_prompt_coach, prompt=prompt, client=client)