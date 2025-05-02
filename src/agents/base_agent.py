# src/agents/base_agent.py

from abc import ABC, abstractmethod
from openai import OpenAI
import os

class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name
        self.client = OpenAI(api_key=os.getenv("OPENAIAPIKEY"))

    @abstractmethod
    def build_prompt(self, **kwargs) -> str:
        ...

    def respond(self, system_prompt: str, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
