from groq import Groq

from dotenv import load_dotenv
import base64
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

    def _messages_for_request(self, has_image):
        if not has_image:
            return self.conversation_history

        recent_messages = self.conversation_history[1:]
        latest_image_index = next(
            (
                index
                for index in range(len(recent_messages) - 1, -1, -1)
                if isinstance(recent_messages[index]["content"], list)
            ),
            None,
        )
        if latest_image_index is not None:
            recent_messages = [
                message
                for index, message in enumerate(recent_messages)
                if not isinstance(message["content"], list)
                or index == latest_image_index
            ]

        return [self.conversation_history[0], *recent_messages[-4:]]

    def ask_llm(self, question, image_file=None):
        conversation_has_image = any(
            isinstance(message["content"], list)
            for message in self.conversation_history
        )

        if image_file is None:
            user_content = question
        else:
            image_data = base64.b64encode(image_file.getvalue()).decode("utf-8")
            user_content = [
                {"type": "text", "text": question},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{image_file.type};base64,{image_data}"
                    },
                },
            ]

        model = (
            "qwen/qwen3.8-27b"
            if image_file is not None or conversation_has_image
            else "openai/gpt-oss-120b"
        )

        self.update_conversation_history(role="user", content=user_content)

        response = self.groq_client.chat.completions.create(
            messages=self._messages_for_request(has_image=model == "qwen/qwen3.8-27b"),
            model=model,
            **({"include_reasoning": False} if image_file is None else {}),
        ).choices[0].message.content

        self.update_conversation_history(role="assistant", content=response)
        return response

    def transcribe_audio(self, audio_file):
        transcription = self.groq_client.audio.transcriptions.create(
            file=(audio_file.name, audio_file.getvalue()),
            model="whisper-large-v3-turbo",
            response_format="json",
        )
        return transcription.text


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