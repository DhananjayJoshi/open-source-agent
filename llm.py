"""
LLM module — factory for creating and managing language model instances.
"""

import os
from typing import Literal

from langchain_openai import ChatOpenAI


def get_llm(
    operation: Literal["discover", "analyze", "fix", "validate", "default"] = "default",
    provider: str = "ollama",
    model: str | None = None,
) -> ChatOpenAI:
    """
    Factory for language model instances supporting multiple backends.

    Args:
        operation: logical operation (currently unused, reserved for future
            per-operation configuration).
        provider: which provider to use; e.g. "openrouter" or "ollama".
        model: optional model name; each provider has a sensible default.
    """
    # decide configuration based on provider
    provider = provider.lower()
    if provider == "openrouter":
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise RuntimeError(
                "OPENROUTER_API_KEY must be set for OpenRouter provider."
            )
        base_url = "https://openrouter.ai/api/v1"
        default_model = "gpt-4o-mini"
    elif provider == "ollama":
        # Ollama runs locally; key is not used but ChatOpenAI requires api_key
        api_key = os.getenv("OLLAMA_API_KEY", "ollama")
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
        default_model = "qwen3:14b"
    else:
        raise ValueError(f"Unknown provider '{provider}'")

    if model is None:
        model = default_model

    print(
        f"   🤖 Using LLM provider '{provider}' with model '{model}' : Base URL = {base_url} : Api Key = {api_key}"
    )
    return ChatOpenAI(
        model=model,
        base_url=base_url,
        api_key=api_key,  # type: ignore
    )
