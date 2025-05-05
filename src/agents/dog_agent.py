from openai import OpenAI
from src.agents.base_agent import BaseAgent
from src.prompts.system_prompt_dog import system_prompt_dog
from src.models.agent_models import AgentMessage


class DogAgent(BaseAgent):
    def __init__(self):
        super().__init__("dog")
        self.greeting_text = "Wuff! Ich bin's, Dein Hund. Hier können wir in Deiner Sprache miteinander reden. Möchtest Du erfahren, wie ich die Welt erlebe?"
        self.question_text = "Beschreibe ein Verhalten, das Du von mir kennst und ich erzähle Dir, was dabei in mir vorgeht."

    def introduce(self) -> AgentMessage:
        return AgentMessage(
            sender=self.name,
            text=self.greeting_text
        )
    
    def ask_about_symptom(self) -> AgentMessage:
        return AgentMessage(
            sender=self.name,
            text=self.question_text
        )
    
    def build_prompt(self, symptom: str) -> str:
        return (
            f"{symptom} entspringt meinen Instinkten, ich mache es nicht einfach so.\n\n"
            f"Sprich in meiner Stimme – freundlich, emotional und nahbar. "
            f"Keine Fachbegriffe. Beschreibe, wie es sich für mich anfühlt. "
            f"Keine Besserwisserei. Fass Dich kurz, nicht mehr als 10 Sätze aber stelle am Ende **keine Rückfrage.**"
        )

    def respond(self, symptom: str, client: OpenAI) -> list[AgentMessage]:
        prompt = self.build_prompt(symptom=symptom)
        return super().respond(
            system_prompt=system_prompt_dog,
            prompt=prompt,
            client=client,
            include_greeting=False
        )

    # Nur beim Start: Begrüßung + Einstiegsfrage
    def get_initial_messages(self) -> list[AgentMessage]:
        return [
            self.introduce(),
            self.ask_about_symptom()
        ]

    # Nur Frage ohne Begrüßung – für erneuten Start oder Folge-Symptome
    def get_question_messages(self) -> list[AgentMessage]:
        return [self.ask_about_symptom()]

    # Verarbeitet die Nutzerantwort auf das Symptom mit GPT (RAG)
    def get_response_messages(self, user_input: str, client: OpenAI) -> list[AgentMessage]:
        # Gibt nur die GPT-basierte Antwort zurück – keine Wiederholung der Frage
        messages = super().respond(
            system_prompt=system_prompt_dog,
            prompt=self.build_prompt(symptom=user_input),
            client=client,
            include_greeting=False,
            include_question=False
        )
        messages.append(AgentMessage(
            sender=self.name,
            text="\n\nMöchtest Du verstehen, warum ich mich so verhalte?"
        ))
        return messages

    # Fragt den Menschen, ob er ein weiteres Symptom beschreiben möchte
    def get_restart_prompt(self) -> list[AgentMessage]:
        return [
            AgentMessage(sender=self.name, text="Möchtest Du mir noch ein weiteres Verhalten beschreiben?")
        ]

    # Übergabe an den Coach: Hund fragt, ob Mensch mehr über die Ursache erfahren möchte
    def get_transition_prompt(self) -> list[AgentMessage]:
        return [
            AgentMessage(
                sender=self.name,
                text="Möchtest Du verstehen, warum ich mich so verhalte?"
            )
        ]