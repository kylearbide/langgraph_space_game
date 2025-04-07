"""Utility & helper functions."""

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_ollama import ChatOllama

def get_message_text(msg: BaseMessage) -> str:
    """Get the text content of a message."""
    content = msg.content
    if isinstance(content, str):
        return content
    elif isinstance(content, dict):
        return content.get("text", "")
    else:
        txts = [c if isinstance(c, str) else (c.get("text") or "") for c in content]
        return "".join(txts).strip()


def load_chat_model(
        model_provider: str, 
        model_name:str, 
        ollama_base_url: str | None = None
    ) -> BaseChatModel:
    """Load a chat model from a specific model provider and model name.

    Args:
        model_provider: The name of the model provider (openai).
        model_name: The name of the model (gpt-4o).
    """
    if model_provider != "ollama":
        return init_chat_model(model_name, model_provider=model_provider)
    else:
        return ChatOllama(
            base_url=ollama_base_url,
            model=model_name,
            temperature=0.5
        )
