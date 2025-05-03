# src/agents/companion_agent.py

from openai import OpenAI
from src.agents.base_agent import BaseAgent
from src.prompts.system_prompt_companion import system_prompt_companion


class CompanionAgent(BaseAgent):
    """
    Die CompanionAgentin ist eine stille, achtsame Beobachterin.
    Sie tritt nur einmal pro Sitzung in Erscheinung, wenn sie einen wertvollen, beziehungsorientierten Impuls geben kann.
    """
    def __init__(self, client: OpenAI):
        super().__init__(name="Companion")
        self.client = client
        self.has_responded = set()  # merkt sich, ob sie für eine Session bereits gesprochen hat

    def build_prompt(self, history: list[dict]) -> str:
        """
        Erstellt den Prompt aus dem bisherigen Gesprächsverlauf.
        """
        messages = "\n".join([f"{m['sender']}: {m['text']}" for m in history])
        return (
            f"{system_prompt_companion}\n\n"
            f"Hier ist der bisherige Gesprächsverlauf:\n{messages}\n\n"
            f"Wenn du eine passende, achtsame Rückmeldung hast, formuliere sie. "
            f"Wenn nicht, gib bitte nur ein kurzes 'Nein' zurück."
        )

    def respond(self, session_id: str, history: list[dict]) -> str | None:
        """
        Analysiert das Gespräch und gibt – wenn sinnvoll – eine einmalige Rückmeldung.
        """
        if session_id in self.has_responded:
            return None

        prompt = self.build_prompt(history)
        response = self._run_gpt(prompt)

        if not response or response.strip().lower() in ["nein", ""]:
            return None

        self.has_responded.add(session_id)
        return response.strip()

    def _run_gpt(self, prompt: str) -> str:
        """
        Führt den GPT-Call mit eigenem Systemprompt aus.
        """
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Du bist eine einfühlsame, beobachtende Begleiterin."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
        )
        return response.choices[0].message.content
