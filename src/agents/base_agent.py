# src/agents/base_agent.py

import os
from abc import ABC, abstractmethod
from openai import OpenAI

class BaseAgent(ABC):
    greeted_sessions = set()  # Set zur Speicherung, wer schon begrüßt hat

    def __init__(self, name: str):
        self.name = name
        self.client = OpenAI(api_key=os.getenv("OPENAIAPIKEY"))

    @abstractmethod
    def build_prompt(self, **kwargs) -> str:
        pass

    def greet(self) -> str:
        """Jeder Agent kann seine eigene Begrüßung definieren."""
        return ""

    def respond(self, session_id: str = "default", **kwargs) -> str:
        system_prompt = self.build_prompt(**kwargs)

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": "Bitte sprich entsprechend deiner Rolle."}
                ],
                temperature=0.7
            )
            content = response.choices[0].message.content.strip()

            # Optional: Begrüßung einmal pro Session voranstellen
            if session_id not in self.greeted_sessions:
                self.greeted_sessions.add(session_id)
                return f"{self.greet()}\n\n{content}"

            return content

        except Exception as e:
            return f"[{self.name}] Fehler beim Antworten: {str(e)}"
