from abc import ABC, abstractmethod


class LLM(ABC):
    """
    Abstract class for Large Language Models (LLMs).
    This class defines a common interface for different LLM providers.
    """

    @abstractmethod
    def chat(self, messages: list, model: str = "default_model"):
        """Abstract method to send messages to the LLM and receive responses."""
        pass

    @abstractmethod
    def chat_stream(self, messages: list, model: str = "default_model"):
        """Abstract method to send messages to the LLM and receive responses."""
        pass

    @abstractmethod
    def generate_json(self, messages: list, model: str = "default_model"):
        """Abstract method to send messages to the LLM and receive responses."""
        pass
