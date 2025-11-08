from openai import OpenAI
from security.config import API_KEY
from ai_agents.llm.base import LLM
import base64


client = OpenAI(api_key=API_KEY)


class OpenAI_LLM(LLM):
    """Implementation of the LLM interface for OpenAI's GPT models."""

    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def chat(self, messages: list, model: str = "gpt-4o"):  # type: ignore
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            stream=False,  # Ensures response isn't streamed
            temperature=0,
        )
        return response.choices[0].message.content

    def chat_stream(self, messages: list, model: str = "gpt-4o"):  # type: ignore
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True,
        )
        for chunk in response:
            delta = chunk.choices[0].delta
            # Only send the actual text content as a string
            if delta.content:
                yield delta.content

    def generate_json(self, messages: list, schema: dict, model: str = "gpt-4o"):  # type: ignore
        """
        FIXED: Now properly uses structured output with JSON schema
        """
        print(" I am in generate Json")
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "resume_extraction",
                    "strict": True,
                    "schema": schema,
                },
            },
            stream=False,
            temperature=0,
        )
        return response

    def generate_stream_json(self, messages: list, model: str = "gpt-4o"):  # type: ignore
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            response_format={"type": "json_object"},
            stream=True,  # Ensures response isn't streamed
            temperature=0,
        )
        for chunk in response:
            if chunk.choices[0].delta.content or chunk.choices[0].finish_reason:
                yield {
                    "content": chunk.choices[0].delta.content,
                    "finish_reason": chunk.choices[0].finish_reason,
                }

    def extract_text_from_image(self, img_bytes: base64) -> str:  # type: ignore
        response = client.responses.create(
            model="gpt-4.1",
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": "Extract text clearly from this image.",
                        },
                        {
                            "type": "input_image",
                            "image_url": f"data:image/jpeg;base64,{img_bytes}",
                        },
                    ],
                }  # type: ignore
            ],
            temperature=0,
        )
        # self.api_calls += 1
        return response.output_text  # type: ignore
