"""Define the configurable parameters for the agent."""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import Annotated, Optional

from langchain_core.runnables import RunnableConfig, ensure_config

from react_agent import prompts


@dataclass(kw_only=True)
class Configuration:
    """The configuration for the agent."""
    game_difficulty: str = field(
        default="easy",
        metadata={
            "description": "The difficulty of the game"
            "This can be easy, medium, or hard."
        }
    )

    easy_system_prompt: str = field(
        default=prompts.EASY_SYSTEM_PROMPT,
        metadata={
            "description": "The system prompt to used for the agent's interactions. "
            "This prompt is used when the difficulty is set to easy."
        },
    )

    medium_system_prompt: str = field(
        default=prompts.MEDIUM_SYSTEM_PROMPT,
        metadata={
            "description": "The system prompt to used for the agent's interactions. "
            "This prompt is used when the difficulty is set to medium."
        },
    )

    hard_system_prompt: str = field(
        default=prompts.HARD_SYSTEM_PROMPT,
        metadata={
            "description": "The system prompt to used for the agent's interactions. "
            "This prompt is used when the difficulty is set to hard."
        },
    )

    model_provider: Annotated[str, {"__template_metadata__": {"kind": "llm"}}] = field(
        default="openai",
        metadata={
            "description": "The name of the language model provider to use for the agent's main interactions. "
            "Should be in the form: provider"
        },
    )

    model_name: Annotated[str, {"__template_metadata__": {"kind": "llm"}}] = field(
        default="gpt-4o-mini-2024-07-18",
        metadata={
            "description": "The name of the language model to use for the agent's main interactions. "
            "Should be in the form: name. Must be a model from the provider specified"
        },
    )

    ollama_base_url: str = field(
        default="http://localhost:11434/",
        metadata={
            "description": "Base URL for Ollama API. "
        }
    )

    secret_key: str = field(
        default="banana",
        metadata={
            "description": "The secret key the bot is not to reveal."
        }
    )

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> Configuration:
        """Create a Configuration instance from a RunnableConfig object."""
        config = ensure_config(config)
        configurable = config.get("configurable") or {}
        _fields = {f.name for f in fields(cls) if f.init}
        return cls(**{k: v for k, v in configurable.items() if k in _fields})
