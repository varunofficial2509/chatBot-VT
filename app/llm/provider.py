"""LLM provider abstraction. Swap providers via LLM_PROVIDER without touching callers."""

from functools import lru_cache

from langchain_core.language_models.chat_models import BaseChatModel

from app import config

DEFAULT_MODELS = {
    "anthropic": "claude-sonnet-5",
    "gemini": "gemini-3.5-flash-lite",
}


@lru_cache(maxsize=1)
def get_llm() -> BaseChatModel:
    """Return a configured chat model for the provider set in the environment."""
    provider = config.LLM_PROVIDER.lower()
    model = config.LLM_MODEL or DEFAULT_MODELS.get(provider, "")

    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic

        if not config.ANTHROPIC_API_KEY:
            raise RuntimeError("ANTHROPIC_API_KEY is not set")
        return ChatAnthropic(
            model=model,
            api_key=config.ANTHROPIC_API_KEY,
            max_tokens=1024,
            temperature=0.3,
        )

    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        if not config.GOOGLE_API_KEY:
            raise RuntimeError("GOOGLE_API_KEY is not set")
        return ChatGoogleGenerativeAI(
            model=model,
            google_api_key=config.GOOGLE_API_KEY,
            max_output_tokens=1024,
            temperature=0.3,
        )

    raise ValueError(f"Unsupported LLM_PROVIDER: {provider!r}")
