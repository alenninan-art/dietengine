import os

from openai import OpenAI


DEFAULT_OPENAI_MODEL = "gpt-4o-mini"
DEFAULT_OPENAI_TIMEOUT = 20.0
DEFAULT_OPENAI_MAX_RETRIES = 0
DEFAULT_NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
# Chosen from the live NVIDIA model list so the same provider can handle text chat and vision.
DEFAULT_NVIDIA_MODEL = "meta/llama-3.2-90b-vision-instruct"


def get_openai_settings() -> dict[str, str | None]:
    openai_api_key = os.getenv("OPENAI_API_KEY")
    nvidia_api_key = os.getenv("NVIDIA_API_KEY")
    use_nvidia_compat = bool(nvidia_api_key) and not openai_api_key

    return {
        "provider": "nvidia" if use_nvidia_compat else "openai",
        "api_key": openai_api_key or nvidia_api_key,
        "base_url": os.getenv("OPENAI_BASE_URL") or (DEFAULT_NVIDIA_BASE_URL if use_nvidia_compat else None),
        "model": os.getenv("OPENAI_MODEL") or (DEFAULT_NVIDIA_MODEL if use_nvidia_compat else DEFAULT_OPENAI_MODEL),
        "timeout": os.getenv("OPENAI_TIMEOUT_SECONDS"),
        "max_retries": os.getenv("OPENAI_MAX_RETRIES"),
    }


def get_openai_client() -> OpenAI | None:
    settings = get_openai_settings()
    api_key = settings["api_key"]
    if not api_key:
        return None

    client_kwargs = {"api_key": api_key}
    if settings["base_url"]:
        client_kwargs["base_url"] = settings["base_url"]
    client_kwargs["timeout"] = float(settings["timeout"] or DEFAULT_OPENAI_TIMEOUT)
    client_kwargs["max_retries"] = int(settings["max_retries"] or DEFAULT_OPENAI_MAX_RETRIES)

    return OpenAI(**client_kwargs)


def get_llm_diagnostics() -> dict[str, object]:
    settings = get_openai_settings()
    return {
        "openai": {
            "configured": bool(settings["api_key"]),
            "provider": settings["provider"],
            "base_url_configured": bool(settings["base_url"]),
            "model": settings["model"] or DEFAULT_OPENAI_MODEL,
            "timeout_seconds": float(settings["timeout"] or DEFAULT_OPENAI_TIMEOUT),
            "max_retries": int(settings["max_retries"] or DEFAULT_OPENAI_MAX_RETRIES),
        },
        "gemini": {
            "configured": bool(os.getenv("GEMINI_API_KEY")),
            "model": os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
        },
    }
