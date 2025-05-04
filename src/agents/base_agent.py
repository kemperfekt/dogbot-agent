# src/agents/base_agent.py

from openai import OpenAI
from src.models.agent_models import AgentMessage
from src.state.session_store import session_exists, get_history
from typing import List


class BaseAgent:
    def __init__(self, name: str):
        self.name = name.lower()
        self.greeting_text = None
        self.question_text = None

    def respond(self, *, system_prompt: str, prompt: str, client: OpenAI) -> List[AgentMessage]:
        """
        Führt die OpenAI-Kommunikation aus und gibt 1-3 Messages zurück:
        - Begrüßung (wenn Agent bisher nicht gesprochen hat)
        - Haupttext (aus Prompt)
        - Frage (falls gesetzt)
        """
        messages = []

        # Begrüßung (nur beim ersten Mal)
        if self._should_greet():
            greeting = self._get_greeting()
            if greeting:
                messages.append(AgentMessage(sender=self.name, text=greeting))

        # Haupttext via GPT
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
        )
        main_text = response.choices[0].message.content.strip()
        messages.append(AgentMessage(sender=self.name, text=main_text))

        # Abschlussfrage (optional)
        if self.question_text:
            messages.append(AgentMessage(sender=self.name, text=self.question_text))

        return messages

    def _should_greet(self) -> bool:
        # Begrüße nur, wenn dieser Agent in der History noch nicht gesprochen hat
        # (Sessionprüfung optional, z.B. durch externen Orchestrator)
        return True  # Später an Session History koppelbar

    def _get_greeting(self) -> str | None:
        return self.greeting_text