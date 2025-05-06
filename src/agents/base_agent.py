from openai import OpenAI
from src.models.agent_models import AgentMessage
from typing import List


class BaseAgent:
    def __init__(self, name: str):
        # Store the original name without lowercase conversion
        self.name = name
        self.greeting_text: str | None = None
        self.question_text: str | None = None

    def respond(
        self,
        *,
        system_prompt: str,
        prompt: str,
        client: OpenAI,
        include_greeting: bool = True,
        include_question: bool = False
    ) -> List[AgentMessage]:
        """
        Gibt 1–3 AgentMessage-Objekte zurück:
        1. Begrüßung (optional)
        2. GPT-generierte Hauptantwort
        3. Abschlussfrage (optional)
        """
        messages = []

        if include_greeting and self.greeting_text:
            messages.append(AgentMessage(sender=self.name, text=self.greeting_text))

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
        )
        main_text = response.choices[0].message.content.strip()
        messages.append(AgentMessage(sender=self.name, text=main_text))

        if include_question and self.question_text:
            messages.append(AgentMessage(sender=self.name, text=self.question_text))

        for i, m in enumerate(messages):
            if not m.sender or m.sender not in {"dog", "coach", "companion", "user", "system", "error", "bot", "Dog", "Coach", "Companion"}:
                print(f"[Warn] Invalid sender in message {i}: {m}")
                m.sender = self.name

        return messages