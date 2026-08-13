"""LLM provider abstraction. Swap providers via LLM_PROVIDER without touching callers."""

import streamlit as st
from langchain_core.language_models.chat_models import BaseChatModel

from src.config import settings

DEFAULT_MODELS = {
    "anthropic": "claude-sonnet-5",
    "gemini": "gemini-3.5-flash-lite",
}


@st.cache_resource(show_spinner=False)
def get_llm() -> BaseChatModel:
    """Return a configured chat model for the provider set in the environment."""
    provider = settings.LLM_PROVIDER.lower()
    model = settings.LLM_MODEL or DEFAULT_MODELS.get(provider, "")

    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic

        if not settings.ANTHROPIC_API_KEY:
            raise RuntimeError("ANTHROPIC_API_KEY is not set")
        return ChatAnthropic(
            model=model,
            api_key=settings.ANTHROPIC_API_KEY,
            max_tokens=1024,
            temperature=0.3,
        )

    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        if not settings.GOOGLE_API_KEY:
            raise RuntimeError("GOOGLE_API_KEY is not set")
        return ChatGoogleGenerativeAI(
            model=model,
            google_api_key=settings.GOOGLE_API_KEY,
            max_output_tokens=1024,
            temperature=0.3,
        )

    raise ValueError(f"Unsupported LLM_PROVIDER: {provider!r}")
