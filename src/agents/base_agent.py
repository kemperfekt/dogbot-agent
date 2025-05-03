from abc import ABC, abstractmethod
from openai import OpenAI
from src.models.agent_models import AgentMessage

class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name

    def respond(self, prompt: str, system_prompt: str, client: OpenAI) -> AgentMessage:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )
        text = response.choices[0].message.content.strip()
        return AgentMessage(sender=self.name.lower(), text=text)