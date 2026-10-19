from groq import Groq

from dotenv import load_dotenv
import os
from pathlib import Path


def read_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


class ConversationAgent:
    def __init__(self):
        load_dotenv()
        api_key = os.environ.get("GROQ_KEY") or os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "La variable d'environnement GROQ_KEY ou GROQ_API_KEY n'est pas définie."
            )

        self.groq_client = Groq(api_key=api_key)
        self.conversation_history = [
            {
                "role": "system",
                "content": read_file(
                    file_path=Path(__file__).with_name("context.txt")
                ),
            }
        ]

    def update_conversation_history(self, role, content):
        self.conversation_history.append(
            {
                "role": role,
                "content": content,
            }
        )

    def ask_llm(self, question):
        self.update_conversation_history(role="user", content=question)

        response = self.groq_client.chat.completions.create(
            messages=self.conversation_history,
            model="openai/gpt-oss-120b",
            include_reasoning=False,
        ).choices[0].message.content

        self.update_conversation_history(role="assistant", content=response)
        return response


_agent = None


def get_agent():
    global _agent
    if _agent is None:
        _agent = ConversationAgent()
    return _agent


def ask_llm(question):
    return get_agent().ask_llm(question)






if __name__ == "__main__":
    agent = ConversationAgent()
    question = input("Pose ta question :\n")
    response = agent.ask_llm(question)
    print("\n")
    print(response)